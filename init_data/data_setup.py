import asyncio
import json
from sqlalchemy.ext.asyncio import create_async_engine
import os
from elasticsearch import Elasticsearch
from minio import Minio

IS_PROD = False
INGRESS_IP = "localhost" # this is localhost as we run k8s locally

if IS_PROD:
    DATABASE_URL = f"postgresql+asyncpg://postgres:postgres@{INGRESS_IP}:5432/bookverse_db"

    es = Elasticsearch(f"http://{INGRESS_IP}:9200")

    # Initialize the MinIO client
    client = Minio(
        f"{INGRESS_IP}:9000",  # or your MinIO server address
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False  # Set to True if using HTTPS
    )
else:
    DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/bookverse_db"

    es = Elasticsearch("http://localhost:9200")

    # Initialize the MinIO client
    client = Minio(
        "localhost:9000",  # or your MinIO server address
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False  # Set to True if using HTTPS
    )


engine = create_async_engine(DATABASE_URL, echo=True)

async def run_sql_file(file_path: str):
    with open(file_path, "r") as f:
        sql = f.read()

    async with engine.begin() as conn:
        # Use exec_driver_sql for raw SQL strings
        await conn.exec_driver_sql(sql)

async def create_tables():
    await run_sql_file("statements/create_users.sql")
    await run_sql_file("statements/create_likes.sql")
    await run_sql_file("statements/create_reviews.sql")
    await run_sql_file("statements/create_purchases.sql")
    


async def upload_files():
    buckets = ["book-metadata", "book-pdfs", "book-cover-images"]

    for bucket in buckets:
        # Make the bucket if it doesn't exist
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)

        # Set bucket policy to allow public read access
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": ["s3:GetObject"],
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Resource": [f"arn:aws:s3:::{bucket}/*"],
                    "Sid": ""
                }
            ]
        }

        client.set_bucket_policy(bucket, json.dumps(policy))

        # Folder to upload
        folder_path = bucket

        # Walk through the folder and upload each file
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                object_name = os.path.relpath(file_path, folder_path).replace("\\", "/")  # Preserve folder structure in object names

                try:
                    client.fput_object(
                        bucket_name=bucket,
                        object_name=object_name,
                        file_path=file_path,
                    )
                    print(f"Uploaded: {file_path} -> {object_name}")
                except Exception as err:
                    print(f"Error uploading {file_path}: {err}")


async def index_files():
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

    # Load and index JSON files
    folder = "book-metadata"
    for filename in os.listdir(folder):
        with open(os.path.join(folder, filename), "r", encoding="utf-8") as f:
            doc = json.load(f)
            doc_id = filename.split(".")[0]
            print(doc_id)

            es.index(index=index_name, id=doc_id, document=doc)


async def main():
    # Run SQL files
    await create_tables()
    await upload_files()
    await index_files()
    

# Run at startup
if __name__ == "__main__":
    asyncio.run(main())
