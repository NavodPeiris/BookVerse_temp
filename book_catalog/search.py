from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")
index_name = "bookverse_books"

query = {
    "query": {
        "match": {
            "title": "worlds"
        }
    }
}

results = es.search(index=index_name, body=query)

for hit in results["hits"]["hits"]:
    print(hit["_source"])
