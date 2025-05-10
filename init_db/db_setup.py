import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/bookverse_db"
engine = create_async_engine(DATABASE_URL, echo=True)

async def run_sql_file(file_path: str):
    with open(file_path, "r") as f:
        sql = f.read()

    async with engine.begin() as conn:
        # Use exec_driver_sql for raw SQL strings
        await conn.exec_driver_sql(sql)

async def main():
    # Run SQL files
    await run_sql_file("statements/create_users.sql")
    await run_sql_file("statements/create_likes.sql")
    await run_sql_file("statements/create_reviews.sql")
    await run_sql_file("statements/create_purchases.sql")

# Run at startup
if __name__ == "__main__":
    asyncio.run(main())
