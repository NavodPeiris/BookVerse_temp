from elasticsearch import Elasticsearch
import json
import os

es = Elasticsearch("http://localhost:9200")

index_name = "bookverse_books"

# delete index if it exists
if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)

mapping = {
    "mappings": {
        "properties": {
            "title": {"type": "text"},
            "description": {"type": "text"},
            "authors": {"type": "text"},
            "subjects": {"type": "text"},
            "paid": {"type": "boolean"}
        }
    }
}

es.indices.create(index=index_name, body=mapping)

def normalize_document(doc):
    if isinstance(doc.get("description"), dict):
        doc["description"] = doc["description"].get("value", "")
    if isinstance(doc.get("created"), dict):
        doc["created"] = doc["created"].get("value", "")
    if isinstance(doc.get("last_modified"), dict):
        doc["last_modified"] = doc["last_modified"].get("value", "")
    return doc

# Load and index JSON files
folder = "openlibrary_json"
for filename in os.listdir(folder):
    with open(os.path.join(folder, filename), "r", encoding="utf-8") as f:
        doc = json.load(f)
        doc_id = filename.split(".")[0]
        print(doc_id)

        # Clean up nested fields
        doc = normalize_document(doc)

        es.index(index=index_name, id=doc_id, document=doc)
