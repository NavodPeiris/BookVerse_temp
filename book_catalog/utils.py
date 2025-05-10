from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, select, PrimaryKeyConstraint
from jose import JWTError, jwt

# JWT config
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"

# Database config
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/bookverse_db"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()

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

bearer_scheme = HTTPBearer(auto_error=True)

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = credentials.credentials
    print("Token:", token)
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