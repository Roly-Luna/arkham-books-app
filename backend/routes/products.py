from decimal import Decimal

from fastapi import APIRouter, Query
from pydantic import BaseModel

from backend.database import get_connection


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


# obtiene productos y permite buscarlos por titulo
@router.get("/", response_model=list[Product])
def get_products(
    search: str | None = Query(default=None, min_length=1),
):
    query = """
        SELECT
            p.id_producto AS id,
            p.titulo AS title,
            p.precio AS price,
            p.stock AS stock,
            CASE
                WHEN l.id_producto IS NOT NULL THEN 'libro'
                WHEN r.id_producto IS NOT NULL THEN 'revista'
                ELSE 'otro'
            END AS product_type
        FROM Producto AS p
        LEFT JOIN Libro AS l
            ON p.id_producto = l.id_producto
        LEFT JOIN Revista AS r
            ON p.id_producto = r.id_producto
    """

    parameters = []

    # agrega el filtro cuando existe una busqueda
    if search:
        query += """
            WHERE p.titulo ILIKE %s
        """
        parameters.append(f"%{search}%")

    # ordena los productos por su identificador
    query += """
        ORDER BY p.id_producto;
    """

    # ejecuta la consulta en postgresql
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, parameters)
            products = cursor.fetchall()

    return products