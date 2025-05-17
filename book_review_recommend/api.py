from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from elasticsearch import Elasticsearch
from minio import Minio
import json
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base, aliased
from sqlalchemy import Column, Integer, String, select, func, distinct
from utils import get_db, get_current_user_id, User, Likes, Reviews, Purchases, SECRET_KEY, ALGORITHM, es, client
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RateRequest(BaseModel):
    book_id: str
    rate: int
    review: str


@app.get("/book-review-recommend/health")
def health_check():
    return {"status": "ok"}


@app.post("/book-review-recommend/rate")
async def rate(request: RateRequest, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Reviews).where(Reviews.user_id == user_id, Reviews.book_id == request.book_id))
    existing_rate = result.scalar()

    if existing_rate:
        existing_rate.review = request.review
        existing_rate.rate = request.rate
        return JSONResponse(content={"message": "review updated successfully"})

    # Add the like
    new_rate = Reviews(user_id=user_id, book_id=request.book_id, review=request.review, rate=request.rate)
    db.add(new_rate)
    await db.commit()

    return JSONResponse(content={"message": "work reviewed successfully"})


@app.get("/book-review-recommend/recommend")
async def recommend(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    L1 = aliased(Likes)
    L2 = aliased(Likes)

    # Subquery: books current user has liked
    liked_books_subq = select(Likes.book_id).where(Likes.user_id == user_id)

    # Main query: books liked by similar users that current user hasn't liked
    stmt = (
        select(distinct(L2.book_id))
        .select_from(L1)
        .join(L2, L1.user_id != L2.user_id)  # other users
        .where(
            L1.user_id == user_id,
            L2.book_id.notin_(liked_books_subq)
        )
    )

    result = await db.execute(stmt)
    recommended_book_ids = result.scalars().all()

    result_docs = []

    for book_id in recommended_book_ids:
        bucket_name = "book-metadata"
        object_name = f"{book_id}.json"

        # Download the file to memory
        response = client.get_object(bucket_name, object_name)

        # Parse the JSON content
        doc = json.load(response)
        
        formatted_doc = {
            "key": doc.get("key"),
            "author_name": doc.get("authors"),
            "cover_image_available": doc.get("cover_image_available"),
            "edition_count": doc.get("edition_count"),
            "first_publish_year": doc.get("first_publish_year"),
            "title": doc.get("title"),
        }

        result_docs.append(formatted_doc)

    # Close the stream
    response.close()
    response.release_conn()

    return JSONResponse(content=result_docs)

