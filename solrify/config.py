from pydantic import BaseModel


class SolrConfig(BaseModel):
    host: str
    endpoint: str
    id_field: str = "id"
    page_size: int = 10
    timeout: int = 30
    retries: int = 10
    backoff_factor: float = 4
