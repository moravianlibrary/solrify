# Solrify

A Python client for interacting with a Solr search server, built on top of Pydantic models for document validation and requests sessions for robust HTTP handling.

---

## Features

* Configurable Solr connection with retries and backoff
* Search documents with typed Pydantic models
* Paginated search with cursor support
* Retrieve single or zero results safely
* Facet queries on specific fields
* Connection availability check

---

## Installation

### Installing from GitHub using version tag

You can install **solrify** directly from GitHub for a specific version tag:

```bash
pip install git+https://github.com/moravianlibrary/solrify.git@v1.2.3
```

*Replace `v1.2.3` with the desired version tag.*

To always install the most recent version, use the latest tag:

```bash
pip install git+https://github.com/moravianlibrary/solrify.git@latest
```

### Installing local dev environment

Install required dependencies using `pip`:

```bash
pip install -r requirements.txt
```

---

## Usage

### Define your document model

Create a Pydantic model representing the Solr documents you want to work with.

```python
from pydantic import BaseModel

class MyDocument(BaseModel):
    id: str
    title: str
    author: str
    # Add your fields here
```

### Configure the client

Set up your Solr configuration.

```python
from solr_client.config import SolrConfig

config = SolrConfig(
    host="http://localhost:8983",
    endpoint="solr/my_collection/select",
    id_field="id",
    page_size=10,
    timeout=30,
    retries=5,
    backoff_factor=1
)
```

### Create a client instance

```python
from solr_client import SolrClient

class MySolrClient(SolrClient[MyDocument]):
    document_type = MyDocument

client = MySolrClient(config)
```

### Performing searches

```python
from solr_client.query import SearchQuery, SearchQueryField
from solr_client.definitions import MappingEnum

query = SearchQueryField(field=MappingEnum("title"), value="example")
results = client.search(query)

for doc in results:
    print(doc.title)
```

### Faceting example

```python
facet_results = client.facet(query, MappingEnum("author"))
for value, count in facet_results:
    print(f"{value}: {count}")
```

### Check if Solr is available

```python
if client.is_available():
    print("Solr is up and running!")
else:
    print("Solr is unavailable.")
```

### Closing the client session

```python
client.close()
```

---

## API Reference

See the docstrings in the source code for detailed usage of methods such as:

* `is_available()`
* `num_found(query)`
* `get_one_or_none(query, fl=None)`
* `search(query, fl=None)`
* `facet(query, field)`
