from typing import ClassVar, Generator, Generic, List, Type

from requests import Session
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from .config import SolrConfig
from .definitions import FacetResult, MappingEnum, SolrEntity
from .query import SearchQuery


class SolrClient(Generic[SolrEntity]):
    """
    A generic client for interacting with a Solr instance.

    This client provides an interface to search and facet documents
    stored in a Solr index using a `SolrEntity`-compatible Pydantic model.

    Attributes
    ----------
    document_type : Type[SolrEntity]
        The class of the document type returned by the Solr index.

    Methods
    -------
    close()
        Closes the HTTP session used for requests.
    is_available() -> bool
        Checks if the Solr instance is available.
    num_found(query: SearchQuery) -> int
        Returns the number of documents matching the search query.
    get_one_or_none(
        query: SearchQuery, fl: List[str] | None = None
    ) -> SolrEntity | None
        Retrieves one document matching the query,
        or None if no or multiple matches exist.
    search(
        query: SearchQuery, fl: List[str] | None = None
    ) -> Generator[SolrEntity, None, None]
        Performs a paginated search and yields results.
    facet(query: SearchQuery, field: MappingEnum) -> FacetResult
        Executes a faceting query on a given field and returns facet results.
    """

    document_type: ClassVar[Type[SolrEntity]]

    def __init__(self, config: SolrConfig):
        """
        Initializes the SolrClient with the provided Solr configuration.

        Parameters
        ----------
        config: SolrConfig
            Configuration for the Solr connection, including host, endpoint,
            timeout, and retry settings.

        Raises
        ------
        ValueError
            If the `document_type` is not defined on the subclass.
        """

        if not self.__class__.document_type:
            raise ValueError(
                "The 'document_type' has not been set for "
                f"{self.__class__.__name__}."
            )

        self._config = config

        adapter = HTTPAdapter(
            max_retries=Retry(
                total=config.retries,
                backoff_factor=config.backoff_factor,
                status_forcelist=[500, 502, 503, 504],
                allowed_methods=[
                    "HEAD",
                    "GET",
                    "OPTIONS",
                    "POST",
                ],
            )
        )

        self._session = Session()
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)
        self._session = Session()

        self._session.timeout = config.timeout

    def close(self):
        """
        Close the HTTP session.

        This method should be used to release resources associated
        with the session.
        """

        if self._session:
            self._session.close()

    def __del__(self):
        """
        Destructor to ensure the session is closed upon object deletion.
        """
        self.close()

    def is_available(self) -> bool:
        """
        Check if the Solr instance is available.

        Returns
        -------
        bool
            `True` if the Solr endpoint responds with a 200 OK status,
            otherwise `False`.
        """

        try:
            response = self._session.get(
                f"{self._config.host}/{self._config.endpoint}"
            )
            return response.status_code == 200
        except Exception:
            return False

    def num_found(self, query: SearchQuery) -> int:
        """
        Return the number of documents matching the search query.

        Parameters
        ----------
        query : SearchQuery
            The query to send to the Solr server.

        Returns
        -------
        int
            Number of matching documents found.
        """
        params = {"q": str(query), "rows": 0}

        response = self._session.get(
            f"{self._config.host}/{self._config.endpoint}", params=params
        )

        response.raise_for_status()

        return response.json()["response"]["numFound"]

    def get_one_or_none(
        self, query: SearchQuery, fl: List[str] | None = None
    ) -> SolrEntity | None:
        """
        Get one document matching the query,
        or None if no or multiple matches exist.

        Parameters
        ----------
        query : SearchQuery
            The search query.
        fl : list of str, optional
            List of fields to fetch.

        Returns
        -------
        SolrEntity or None
            A single matching document,
            or None if there are 0 or more than 1 matches.
        """
        params = {"q": str(query), "rows": 1, "fl": fl}

        response = self._session.get(
            f"{self._config.host}/{self._config.endpoint}", params=params
        )

        response.raise_for_status()

        num_found = response.json()["response"]["numFound"]

        if num_found == 1:
            return self.__class__.document_type.model_validate(
                response.json()["response"]["docs"][0]
            )

        return None

    def search(
        self, query: SearchQuery, fl: List[str] | None = None
    ) -> Generator[SolrEntity, None, None]:
        """
        Perform a paginated search and yield results.

        Parameters
        ----------
        query : SearchQuery
            The query to search for.
        fl : list of str, optional
            Fields to return for each result.

        Yields
        ------
        SolrEntity
            An instance of the result document parsed into the `document_type`.
        """

        params = {
            "q": str(query),
            "rows": self._config.page_size,
            "fl": fl,
            "sort": f"{self._config.id_field} asc",
            "cursorMark": None,
        }

        curr_cursor = "*"

        while params["cursorMark"] != curr_cursor:
            params["cursorMark"] = curr_cursor
            response = self._session.get(
                f"{self._config.host}/{self._config.endpoint}", params=params
            )

            response.raise_for_status()

            response_data = response.json()
            documents = response_data["response"]["docs"]

            for document in documents:
                yield self.__class__.document_type.model_validate(document)

            next_cursor = response_data.get("nextCursorMark", None)
            if next_cursor is not None:
                curr_cursor = next_cursor

    def facet(self, query: SearchQuery, field: MappingEnum) -> FacetResult:
        """
        Execute a faceting query on a given field.

        Parameters
        ----------
        query : SearchQuery
            The query to filter documents before faceting.
        field : MappingEnum
            The field on which to perform faceting.

        Returns
        -------
        FacetResult
            A list of (facet_value, count) tuples representing facet buckets.
        """
        params = {
            "q": str(query),
            "rows": 0,
            "facet": "true",
            "facet.field": field.alias,
        }

        response = self._session.get(
            f"{self._config.host}/{self._config.endpoint}", params=params
        )

        response.raise_for_status()

        return response.json()["facet_counts"]["facet_fields"][field.alias]
