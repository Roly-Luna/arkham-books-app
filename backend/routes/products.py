import psycopg
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.database import get_connection


# define las rutas relacionadas con productos
router = APIRouter(
    prefix="/products",
    tags=["products"],
)


# representa un producto del catalogo
class Product(BaseModel):
    id: int
    title: str
    price: float
    stock: int
    rating: int | None
    publisher: str
    product_type: str


# obtiene los productos almacenados en postgresql
@router.get("", response_model=list[Product])
def get_products(
    search: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
    ),
):
    query = """
        SELECT
            p.id_producto AS id,
            p.titulo AS title,
            p.precio AS price,
            p.stock,
            p.rating,
            e.nombre_edit AS publisher,
            CASE
                WHEN l.id_producto IS NOT NULL THEN 'libro'
                WHEN r.id_producto IS NOT NULL THEN 'revista'
                ELSE 'sin tipo'
            END AS product_type
        FROM producto AS p
        JOIN editorial AS e
            ON p.id_editorial = e.id_editorial
        LEFT JOIN libro AS l
            ON p.id_producto = l.id_producto
        LEFT JOIN revista AS r
            ON p.id_producto = r.id_producto
    """

    parameters = []

    # agrega el filtro cuando existe una busqueda
    if search:
        query += """
            WHERE p.titulo ILIKE %s
        """
        parameters.append(f"%{search}%")

    query += """
        ORDER BY p.id_producto
        LIMIT 100;
    """

    try:
        # ejecuta la consulta sobre arkham books
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, parameters)
                products = cursor.fetchall()

        return products

    except psycopg.Error as error:
        raise HTTPException(
            status_code=503,
            detail="Database query failed",
        ) from error