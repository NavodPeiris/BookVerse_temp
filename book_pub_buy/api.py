from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from elasticsearch import Elasticsearch
from minio import Minio
import json
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, select, func
from utils import get_db, get_current_user_id, User, Likes, Reviews, Purchases, SECRET_KEY, ALGORITHM
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid
from io import BytesIO

es = Elasticsearch("http://localhost:9200")

# Initialize the MinIO client
client = Minio(
    "localhost:9000",  # or your MinIO server address
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False  # Set to True if using HTTPS
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BookPublishRequest(BaseModel):
    first_publish_year: str
    title: str
    subtitle: str
    cover_image_available: bool
    authors: str
    subjects: str
    subject_places: Optional[str] = None
    subject_times: Optional[str] = None
    description: str
    #latest_revision: int
    edition_count: int
    #created: datetime
    #last_modified: datetime
    price: float
    #paid: bool


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/buy")
async def buy(book_id: str, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):

    # TODO: handle payment in frontend and when it is successful only, call this endpoint
    # TODO: 5% of payment price should come to bookverse organization account

    result = await db.execute(select(Purchases).where(Likes.user_id == user_id, Likes.book_id == book_id))
    existing_purchases = result.scalar()

    if existing_purchases:
        return JSONResponse(content={"message": "book was already owned"})

    # Add the like
    new_purchase = Purchases(user_id=user_id, book_id=book_id)
    db.add(new_purchase)
    await db.commit()

    return JSONResponse(content={"message": "book purchased successfully"})


@app.post("/publish")
def publish(request: BookPublishRequest, user_id: int = Depends(get_current_user_id)):

    # TODO: handle payment in frontend and when it is successful only, call this endpoint

    book_obj = {
        "key": str(uuid.uuid4()),
        "first_publish_year": request.first_publish_year,
        "title": request.title,
        "subtitle": request.subtitle,
        "cover_image_available": request.cover_image_available,
        "authors": request.authors,
        "subjects": request.subjects,
        "description": request.description,
        "latest_revision": request.edition_count,
        "edition_count": request.edition_count,
        "created": datetime.utcnow(),
        "last_modified": datetime.utcnow(),
        "price": request.price,
        "paid": True if request.price > 0 else False,
        "author_id": user_id
    }

    if request.subject_places is not None:
        book_obj["subject_places"] = request.subject_places

    if request.subject_times is not None:
        book_obj["subject_times"] = request.subject_times

    index_name = "bookverse_books"
    es.index(index=index_name, id=book_obj["key"], document=book_obj)

    # Convert dict to JSON and encode to bytes
    json_data = json.dumps(book_obj).encode('utf-8')
    json_stream = BytesIO(json_data)

    bucket_name = "book-metadata"
    object_name = f"{book_obj["key"]}.json"

    # Upload the object
    client.put_object(
        bucket_name=bucket_name,
        object_name=object_name,
        data=json_stream,
        length=len(json_data),
        content_type='application/json'
    )

    print(f"Uploaded {object_name} to {bucket_name}")
