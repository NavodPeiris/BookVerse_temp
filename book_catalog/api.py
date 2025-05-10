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


def normalize_document(doc):
    if isinstance(doc.get("description"), dict):
        doc["description"] = doc["description"].get("value", "")
    if isinstance(doc.get("created"), dict):
        doc["created"] = doc["created"].get("value", "")
    if isinstance(doc.get("last_modified"), dict):
        doc["last_modified"] = doc["last_modified"].get("value", "")
    return doc

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/search={text}")
def search(text: str):
    
    index_name = "bookverse_books"

    print("searching for:", text)

    query = {
        "query": {
            "match": {
                "title": text
            }
        }
    }

    res = []

    results = es.search(index=index_name, body=query)
    for hit in results["hits"]["hits"]:
        doc = hit["_source"]
        norm_doc = normalize_document(doc)
        formatted_doc = {
            "key": norm_doc.get("key"),
            "author_name": norm_doc.get("authors"),
            "cover_i": norm_doc.get("covers")[0],
            "edition_count": norm_doc.get("edition_count"),
            "first_publish_year": norm_doc.get("first_publish_year"),
            "title": norm_doc.get("title"),
        }
        res.append(formatted_doc)

    return JSONResponse(content=res)


@app.get("/works/{work_id}")
async def get_work(work_id: str, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    
    bucket_name = "book-metadata"
    object_name = f"{work_id}.json"

    # Download the file to memory
    response = client.get_object(bucket_name, object_name)

    # Parse the JSON content
    doc = json.load(response)
    norm_doc = normalize_document(doc)

    # Close the stream
    response.close()
    response.release_conn()

    resultLC = await db.execute(
        select(func.count()).select_from(Likes).where(Likes.book_id == work_id)
    )

    resultR = await db.execute(
        select(func.avg(Reviews.rate)).where(Reviews.book_id == work_id)
    )

    resultP = await db.execute(
        select(Purchases).where(
            (Purchases.book_id == work_id) & (Purchases.user_id == user_id)
        )
    )

    resultLikes = await db.execute(select(Likes).where(Likes.user_id == user_id, Likes.book_id == work_id))
    existing_like = resultLikes.scalar()

    if existing_like:
        user_liked = True
    else:
        user_liked = False

    like_count = resultLC.scalar()
    like_count = like_count if like_count is not None else 0

    rate = resultR.scalar()
    rate = rate if rate is not None else 0.0

    purchase = resultP.scalar()
    
    if purchase != None:
        norm_doc["paid"] = False
    
    res = {
        "description": norm_doc.get("description"),
        "title": norm_doc.get("title"),
        "covers": norm_doc.get("covers"),
        "subject_places": norm_doc.get("subject_places"),
        "subject_times": norm_doc.get("subject_times"),
        "subjects": norm_doc.get("subjects"),
        "paid": norm_doc.get("paid"),
        "like_count": like_count,
        "user_liked": user_liked,
        "rate": rate,
    }
       
    return JSONResponse(content=res)


@app.post("/like/{work_id}")
async def like_work(work_id: str, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    # Check if the user has already liked the work
    result = await db.execute(select(Likes).where(Likes.user_id == user_id, Likes.book_id == work_id))
    existing_like = result.scalar()

    if existing_like:
        # Unlike: delete existing like
        await db.delete(existing_like)
        await db.commit()
        return JSONResponse(content={"message": "like removed"})

    # Add the like
    new_like = Likes(user_id=user_id, book_id=work_id)
    db.add(new_like)
    await db.commit()

    return JSONResponse(content={"message": "Work liked successfully"})


@app.get("/download_book/{work_id}")
def download_file(work_id: str):
    try:
        # Get the object from MinIO
        response = client.get_object("book-pdfs", work_id)
        return StreamingResponse(
            response,
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={work_id}"}
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))