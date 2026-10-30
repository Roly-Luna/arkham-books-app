import psycopg
from fastapi import FastAPI, HTTPException

from backend.database import check_database_connection
from backend.mongodb import mongo_lifespan
from backend.routes.community import router as community_router
from backend.routes.products import router as products_router

app = FastAPI(
    title="Arkham Books API",
    description="Bookstore catalog and reader community services",
    version="2.0.0",
    lifespan=mongo_lifespan,
)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "service": "arkham-books-api"}


@app.get("/health/database", tags=["health"])
def database_health_check():
    try:
        check_database_connection()
        return {"status": "ok", "database": "postgresql"}
    except psycopg.Error as error:
        raise HTTPException(
            status_code=503,
            detail="PostgreSQL connection failed",
        ) from error


app.include_router(products_router)
app.include_router(community_router)
