from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from elasticsearch import Elasticsearch
from minio import Minio
import json
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, select, func, desc
from utils import get_db, get_current_user_id, User, Likes, Reviews, Purchases, SECRET_KEY, ALGORITHM
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

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

class SearchRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    authors: Optional[str] = None
    subjects: Optional[str] = None
    paid: Optional[bool] = None
    free: Optional[bool] = None


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/search")
def searchAll(request: SearchRequest):

    if all(value is None for value in request.model_dump().values()):
        return JSONResponse(content=[])
    
    index_name = "bookverse_books"

    query = {
        "query": {
            "bool": {
                "must": []
            }
        }
    }

    # Only include non-empty fields
    if request.title is not None:
        query["query"]["bool"]["must"].append({
            "match": {
                "title": {
                    "query": request.title,
                    "operator": "and",  # ensure partial and full text match
                    "fuzziness": "AUTO"  # Allows minor typos and variations
                }
            }
        })
    
    if request.description is not None:
        query["query"]["bool"]["must"].append({
            "match": {
                "description": {
                    "query": request.description,
                    "operator": "and",  # ensure partial and full text match
                    "fuzziness": "AUTO"  # Allows minor typos and variations
                }
            }
        })

    if request.authors is not None:
        authors = [a.strip() for a in request.authors.split(",") if a.strip()]
        for author in authors:
            query["query"]["bool"]["must"].append({
                "match": {
                    "authors": {
                        "query": author,
                        "operator": "and",  # ensure partial and full text match
                        "fuzziness": "AUTO"  # Allows minor typos and variations
                    }
                }
            })

    if request.subjects is not None:
        subjects = [s.strip() for s in request.subjects.split(",") if s.strip()]
        for subject in subjects:
            query["query"]["bool"]["must"].append({
                "match": {
                    "subjects": {
                        "query": subject,
                        "operator": "and",  # ensure partial and full text match
                        "fuzziness": "AUTO"  # Allows minor typos and variations
                    }
                }
            })

    
    if request.paid is not None and request.free is not None:
        if request.paid and request.free: # both true
            print("no specification")
        elif request.paid:
            query["query"]["bool"]["must"].append({"match": {"paid": request.paid}})
        elif request.free:
            query["query"]["bool"]["must"].append({"match": {"paid": not request.free}})
        else:   # both false
            print("no specification")
        
    elif request.paid is None and request.free is None:
        print("no specification")
    elif request.paid is not None:
        query["query"]["bool"]["must"].append({"match": {"paid": request.paid}})
    elif request.free is not None:
        query["query"]["bool"]["must"].append({"match": {"paid": not request.free}})

    res = []

    results = es.search(index=index_name, body=query)
    for hit in results["hits"]["hits"]:
        doc = hit["_source"]
        formatted_doc = {
            "key": doc.get("key"),
            "author_name": doc.get("authors"),
            "cover_image_available": doc.get("cover_image_available"),
            "edition_count": doc.get("edition_count"),
            "first_publish_year": doc.get("first_publish_year"),
            "title": doc.get("title"),
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
        doc["paid"] = False
    
    res = {
        "description": doc.get("description"),
        "title": doc.get("title"),
        "cover_image_available": doc.get("cover_image_available"),
        "subject_places": doc.get("subject_places"),
        "subject_times": doc.get("subject_times"),
        "subjects": doc.get("subjects"),
        "paid": doc.get("paid"),
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


@app.get("/most_liked")
async def most_liked_works(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    # Check if the user has already liked the work
    result = await db.execute(
        select(Likes.book_id, func.count().label("like_count"))
        .group_by(Likes.book_id)
        .order_by(desc("like_count"))
        .limit(10)
    )

    top_10_books = result.all()
    result_docs = []

    for book in top_10_books:
        bucket_name = "book-metadata"
        object_name = f"{book.book_id}.json"

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