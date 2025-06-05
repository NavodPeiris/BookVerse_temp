import io
from fastapi import FastAPI, Depends, HTTPException, File, Form, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from elasticsearch import Elasticsearch
from minio import Minio
import json
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, select, func
from utils import get_db, get_current_user_id, User, Likes, Reviews, Purchases, SECRET_KEY, ALGORITHM, es, client
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid
from io import BytesIO
import stripe
from dotenv import load_dotenv
import os

app = FastAPI()
load_dotenv()

stripe.api_key = os.getenv("stripe_api_key")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BookBuyRequest(BaseModel):
    book_id: str

class CreateCheckoutSessionRequest(BaseModel):
    book_id: str
    price: float
    
@app.get("/book-pub-buy/health")
def health_check():
    return {"status": "ok"}

@app.post("/book-pub-buy/create-checkout-session")
async def create_checkout_session(request: CreateCheckoutSessionRequest):

    book_id = request.book_id
    price = request.price

    bucket_name = "book-metadata"
    object_name = f"{book_id}.json"

    # Download the file to memory
    response = client.get_object(bucket_name, object_name)

    # Parse the JSON content
    doc = json.load(response)

    title = doc.get("title", "Unknown Book")

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"Book : {title}"},
                    "unit_amount": int(price * 100),
                },
                "quantity": 1,
            }],
            mode='payment',
            
            success_url=f"http://localhost:3000/success?book_id={book_id}",
            cancel_url="http://localhost:3000/cancel",
        )

        print("returning url:", session.url)
        return {"url": session.url}
        #return JSONResponse({"url": session.url})
    except Exception as e:
        return {"error": str(e)}

@app.post("/book-pub-buy/buy")
async def buy(request: BookBuyRequest, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):

    # TODO: handle payment in frontend and when it is successful only, call this endpoint
    # TODO: 5% of payment price should come to bookverse organization account

    result = await db.execute(select(Purchases).where(Likes.user_id == user_id, Likes.book_id == request.book_id))
    existing_purchases = result.scalar()

    if existing_purchases:
        return JSONResponse(content={"message": "book was already owned"})

    # Add the like
    new_purchase = Purchases(user_id=user_id, book_id=request.book_id)
    db.add(new_purchase)
    await db.commit()

    return JSONResponse(content={"message": "book purchased successfully"})


@app.post("/book-pub-buy/publish")
async def publish(
    first_publish_year: str = Form(...),
    title: str = Form(...),
    subtitle: str = Form(...),
    cover_image_available: bool = Form(...),
    authors: str = Form(...),
    subjects: str = Form(...),
    subject_places: Optional[str] = Form(None),
    subject_times: Optional[str] = Form(None),
    description: str = Form(...),
    edition_count: int = Form(...),
    price: float = Form(...),
    doc: UploadFile = File(...),
    img: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id)):

    # TODO: handle payment in frontend and when it is successful only, call this endpoint

    book_obj = {
        "key": str(uuid.uuid4()),
        "first_publish_year": first_publish_year,
        "title": title,
        "subtitle": subtitle,
        "cover_image_available": cover_image_available,
        "authors": authors,
        "subjects": subjects,
        "description": description,
        "latest_revision": edition_count,
        "edition_count": edition_count,
        "created": datetime.utcnow(),
        "last_modified": datetime.utcnow(),
        "price": price,
        "paid": True if price > 0 else False,
        "author_id": user_id
    }

    if subject_places is not None:
        book_obj["subject_places"] = subject_places

    if subject_times is not None:
        book_obj["subject_times"] = subject_times

    index_name = "bookverse_books"
    es.index(index=index_name, id=book_obj["key"], document=book_obj)

    # Convert dict to JSON and encode to bytes
    json_data = json.dumps(book_obj).encode('utf-8')
    json_stream = BytesIO(json_data)

    metadata_bucket_name = "book-metadata"
    book_pdf_bucket_name = "book-pdfs"
    book_cover_image_bucket_name = "book-cover-images"

    # Read content from UploadFile
    doc_bytes = await doc.read()
    img_bytes = await img.read()

    try:
        # Upload the object
        client.put_object(
            bucket_name=metadata_bucket_name,
            object_name=f"{book_obj['key']}.json",
            data=json_stream,
            length=len(json_data),
            content_type='application/json'
        )

        client.put_object(
            bucket_name=book_cover_image_bucket_name,
            object_name=f"{title}.jpg",
            data=io.BytesIO(img_bytes),
            length=len(img_bytes),
            content_type=doc.content_type
        )

        client.put_object(
            bucket_name=book_pdf_bucket_name,
            object_name=f"{title}.pdf",
            data=io.BytesIO(doc_bytes),
            length=len(doc_bytes),
            content_type=doc.content_type
        )


        return JSONResponse(content={"message": "book published successfully"})
        
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="something went wrong")
