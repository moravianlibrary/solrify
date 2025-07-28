from pydantic import BaseModel


class SolrConfig(BaseModel):
    """
    Configuration settings for a Solr client.

    Parameters
    ----------
    host : str
        The base URL or hostname of the Solr server
        (e.g., 'http://localhost:8983').

    endpoint : str
        The Solr core or collection endpoint to query (e.g., 'solr/mycore').

    id_field : str, default="id"
        The name of the field in Solr documents that serves
        as the unique identifier.

    page_size : int, default=10
        The number of results to return per page when paginating queries.

    timeout : int, default=30
        Timeout in seconds for Solr HTTP requests.

    retries : int, default=10
        Maximum number of retry attempts for failed Solr requests.

    backoff_factor : float, default=4
        A backoff factor to apply between retry attempts,
        controlling delay growth.
    """

    host: str
    endpoint: str
    id_field: str = "id"
    page_size: int = 10
    timeout: int = 30
    retries: int = 10
    backoff_factor: float = 4
