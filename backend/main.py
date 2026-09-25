import psycopg
from fastapi import FastAPI, HTTPException

from backend.database import check_database_connection
from backend.routes.products import router as products_router


# crea la aplicacion principal
app = FastAPI(
    title="Arkham Books API",
    version="1.0.0",
)


# verifica el estado de la api
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "arkham-books-api",
    }


# verifica la conexion con postgresql
@app.get("/health/database")
def database_health_check():
    try:
        check_database_connection()

        return {
            "status": "ok",
            "database": "connected",
        }

    except psycopg.Error as error:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed",
        ) from error


# registra las rutas de productos
app.include_router(products_router)