from decimal import Decimal

from fastapi import APIRouter, Query
from pydantic import BaseModel

from backend.data.mock_products import PRODUCTS


# define las rutas relacionadas con productos
router = APIRouter(
    prefix="/products",
    tags=["products"],
)


# representa la informacion de un producto
class Product(BaseModel):
    id: int
    title: str
    price: Decimal
    stock: int
    product_type: str


# obtiene todos los productos o filtra por titulo
@router.get("/", response_model=list[Product])
def get_products(
    search: str | None = Query(default=None, min_length=1),
):
    if not search:
        return PRODUCTS

    search_value = search.lower()

    # filtra los productos que coinciden con la busqueda
    return [
        product
        for product in PRODUCTS
        if search_value in product["title"].lower()
    ]