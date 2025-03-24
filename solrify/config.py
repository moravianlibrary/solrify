from pydantic import BaseModel


class SolrConfig(BaseModel):
    host: str
    endpoint: str
    page_size: int = 10
    timeout: int = 30
