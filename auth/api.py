from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, select
from passlib.context import CryptContext
from jose import jwt, JWTError
from pydantic import BaseModel
from datetime import datetime, timedelta
from utils import get_db, get_current_user_id, User, Likes, Reviews, Purchases, SECRET_KEY, ALGORITHM, es, client

ACCESS_TOKEN_EXPIRE_DAYS = 7

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic Schemas
class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    expire: datetime

# Utility functions
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM), expire

# FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/auth/health")
def health_check():
    return {"status": "ok"}


@app.post("/auth/register", response_model=Token)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user.email))
    if result.scalar():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password)
    )
    db.add(new_user)
    await db.commit()

    access_token, expire = create_access_token(data={"sub": new_user.email})
    return {"access_token": access_token, "expire": expire}


@app.post("/auth/login", response_model=Token)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user.email))
    db_user = result.scalar()
    
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token, expire = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "expire": expire}


@app.get("/auth/verify-token")
async def login(user_id: int = Depends(get_current_user_id)):
    if user_id:
        return {"user_id": user_id}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")
