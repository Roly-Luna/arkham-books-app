from fastapi import FastAPI

from backend.routes.products import router as products_router


# crea la aplicacion principal de fastapi
app = FastAPI(
    title="Arkham Books API",
    version="1.0.0",
)


# verifica que la api se encuentre disponible
@app.get("/health")
def health_check():
    return {"status": "ok"}


# registra las rutas de productos
app.include_router(products_router)