from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, select, PrimaryKeyConstraint
from jose import JWTError, jwt
import os
from elasticsearch import Elasticsearch
from minio import Minio

IS_PROD = os.getenv("ENV") == "prod"

if IS_PROD:
    DATABASE_URL = "postgresql+asyncpg://postgres:postgres@postgres.bookverse.svc.cluster.local:5432/bookverse_db"

    es = Elasticsearch("http://elasticsearch.bookverse.svc.cluster.local:9200")

    # Initialize the MinIO client
    client = Minio(
        "minio.bookverse.svc.cluster.local:9000",  # or your MinIO server address
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

# Database config
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()

# JWT config
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    password = Column(String)
    
class Likes(Base):
    __tablename__ = "likes"
    user_id = Column(Integer)
    book_id = Column(String)

    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'book_id'),
    )

class Reviews(Base):
    __tablename__ = "reviews"
    user_id = Column(Integer)
    book_id = Column(String)
    review = Column(String)
    rate = Column(Integer)

    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'book_id'),
    )

class Purchases(Base):
    __tablename__ = "purchases"
    user_id = Column(Integer)
    book_id = Column(String)

    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'book_id'),
    )

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

bearer_scheme = HTTPBearer(auto_error=False)

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token payload invalid")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalid")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user.id