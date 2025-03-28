from typing import ClassVar, Generator, Generic, List, Type

from requests import Session

from .config import SolrConfig
from .custom_types import FacetResult, MappingEnum, SolrEntity
from .query import SearchQueryField


class SolrClient(Generic[SolrEntity]):
    """
    SolrClient is a client for interacting with a Solr instance.
    It allows performing searches, adding, updating,
    and deleting documents in Solr.
    """

    document_type: ClassVar[Type[SolrEntity]]

    def __init__(self, config: SolrConfig):
        """
        Initializes the SolrClient with the provided Solr configuration.

        Args:
            config (SolrConfig):
            The configuration object containing Solr host, endpoint, etc.
        """

        self._config = config
        self._session = Session()
        self._session.timeout = config.timeout

        if not self.__class__.document_type:
            raise ValueError(
                "The 'document_type' has not been set for "
                f"{self.__class__.__name__}."
            )

    def close(self):
        """Closes the HTTP session."""

        if self._session:
            self._session.close()

    def __del__(self):
        """Ensures the session is closed when the client is deleted."""
        self.close()

    def is_available(self) -> bool:
        """
        Checks if the Solr instance is available
        by making a request to the search endpoint.

        Returns:
            bool: True if Solr is available (status code 200), False otherwise.
        """

        try:
            response = self._session.get(
                f"{self._config.host}/{self._config.endpoint}"
            )
            return response.status_code == 200
        except Exception:
            return False

    def num_found(self, query: SearchQueryField) -> int:
        params = {"q": str(query), "rows": 0}

        response = self._session.get(
            f"{self._config.host}/{self._config.endpoint}", params=params
        )

        response.raise_for_status()

        return response.json()["response"]["numFound"]

    def get_one_or_none(
        self, query: SearchQueryField, fl: List[str] | None = None
    ) -> SolrEntity | None:
        params = {"q": str(query), "rows": 1, "fl": fl}

        response = self._session.get(
            f"{self._config.host}/{self._config.endpoint}", params=params
        )

        response.raise_for_status()

        num_found = response.json()["response"]["numFound"]

        return (
            response.json()["response"]["docs"][0] if num_found == 1 else None
        )

    def search(
        self, query: SearchQueryField, fl: List[str] | None = None
    ) -> Generator[SolrEntity, None, None]:
        """
        Performs a Solr search and yields results as entities.

        Args:
            query (SearchQueryField): The query to search for.
            sort (str): The sorting order for the results.

        Yields:
            Entity: The search results as entities.
        """

        params = {
            "q": str(query),
            "rows": self._config.page_size,
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

            response_data = response.json()["response"]
            documents = response_data["docs"]

            for document in documents:
                yield self.__class__.document_type.model_validate(document)

            if "cursorMark" in response_data:
                curr_cursor = response_data["cursorMark"]

    def facet(
        self, query: SearchQueryField, field: MappingEnum
    ) -> FacetResult:
        params = {
            "q": str(query),
            "rows": 0,
            "facet": "true",
            "facet.field": field.map_to,
        }

        response = self._session.get(
            f"{self._config.host}/{self._config.endpoint}", params=params
        )

        response.raise_for_status()

        return response.json()["facet_counts"]["facet_fields"][field.map_to]
