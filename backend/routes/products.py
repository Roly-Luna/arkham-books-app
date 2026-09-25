from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from psycopg import Error
from psycopg.errors import ForeignKeyViolation

from backend.database import get_connection


# define las rutas relacionadas con productos
router = APIRouter(
    prefix="/products",
    tags=["products"],
)


# representa los datos necesarios para crear o actualizar
class ProductInput(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    price: float = Field(ge=0)
    stock: int = Field(ge=0)
    rating: int | None = Field(default=None, ge=1, le=5)
    publisher_id: int = Field(gt=0)


# representa un producto devuelto por la api
class Product(BaseModel):
    id: int
    title: str
    price: float
    stock: int
    rating: int | None
    publisher_id: int
    publisher: str
    product_type: str


# representa una editorial
class Publisher(BaseModel):
    id: int
    name: str


# obtiene un producto por su identificador
def get_product_by_id(cursor, product_id: int):
    query = """
        SELECT
            p.id_producto AS id,
            p.titulo AS title,
            p.precio::float AS price,
            p.stock,
            p.rating,
            p.id_editorial AS publisher_id,
            e.nombre_edit AS publisher,
            CASE
                WHEN l.id_producto IS NOT NULL THEN 'libro'
                WHEN r.id_producto IS NOT NULL THEN 'revista'
                ELSE 'producto'
            END AS product_type
        FROM producto AS p
        JOIN editorial AS e
            ON p.id_editorial = e.id_editorial
        LEFT JOIN libro AS l
            ON p.id_producto = l.id_producto
        LEFT JOIN revista AS r
            ON p.id_producto = r.id_producto
        WHERE p.id_producto = %s;
    """

    cursor.execute(query, (product_id,))
    return cursor.fetchone()


# obtiene todas las editoriales
@router.get("/publishers", response_model=list[Publisher])
def get_publishers():
    query = """
        SELECT
            id_editorial AS id,
            nombre_edit AS name
        FROM editorial
        ORDER BY nombre_edit;
    """

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()

    except Error as error:
        raise HTTPException(
            status_code=503,
            detail="Database query failed",
        ) from error


# consulta productos y permite buscar por titulo
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
            p.precio::float AS price,
            p.stock,
            p.rating,
            p.id_editorial AS publisher_id,
            e.nombre_edit AS publisher,
            CASE
                WHEN l.id_producto IS NOT NULL THEN 'libro'
                WHEN r.id_producto IS NOT NULL THEN 'revista'
                ELSE 'producto'
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
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, parameters)
                return cursor.fetchall()

    except Error as error:
        raise HTTPException(
            status_code=503,
            detail="Database query failed",
        ) from error


# registra un nuevo producto
@router.post("", response_model=Product, status_code=201)
def create_product(product: ProductInput):
    query = """
        INSERT INTO producto (
            titulo,
            precio,
            stock,
            rating,
            id_editorial
        )
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id_producto;
    """

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        product.title,
                        product.price,
                        product.stock,
                        product.rating,
                        product.publisher_id,
                    ),
                )

                product_id = cursor.fetchone()["id_producto"]

                created_product = get_product_by_id(
                    cursor,
                    product_id,
                )

                return created_product

    except ForeignKeyViolation as error:
        raise HTTPException(
            status_code=400,
            detail="Publisher does not exist",
        ) from error

    except Error as error:
        raise HTTPException(
            status_code=503,
            detail="Database operation failed",
        ) from error


# actualiza un producto existente
@router.put("/{product_id}", response_model=Product)
def update_product(
    product_id: int,
    product: ProductInput,
):
    query = """
        UPDATE producto
        SET
            titulo = %s,
            precio = %s,
            stock = %s,
            rating = %s,
            id_editorial = %s
        WHERE id_producto = %s
        RETURNING id_producto;
    """

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        product.title,
                        product.price,
                        product.stock,
                        product.rating,
                        product.publisher_id,
                        product_id,
                    ),
                )

                updated = cursor.fetchone()

                if not updated:
                    raise HTTPException(
                        status_code=404,
                        detail="Product not found",
                    )

                updated_product = get_product_by_id(
                    cursor,
                    product_id,
                )

                return updated_product

    except HTTPException:
        raise

    except ForeignKeyViolation as error:
        raise HTTPException(
            status_code=400,
            detail="Publisher does not exist",
        ) from error

    except Error as error:
        raise HTTPException(
            status_code=503,
            detail="Database operation failed",
        ) from error


# elimina un producto
@router.delete("/{product_id}")
def delete_product(product_id: int):
    query = """
        DELETE FROM producto
        WHERE id_producto = %s
        RETURNING id_producto, titulo;
    """

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (product_id,),
                )

                deleted_product = cursor.fetchone()

                if not deleted_product:
                    raise HTTPException(
                        status_code=404,
                        detail="Product not found",
                    )

                return {
                    "message": "Product deleted",
                    "product": deleted_product,
                }

    except HTTPException:
        raise

    except ForeignKeyViolation as error:
        raise HTTPException(
            status_code=409,
            detail=(
                "Product has related records "
                "and cannot be deleted"
            ),
        ) from error

    except Error as error:
        raise HTTPException(
            status_code=503,
            detail="Database operation failed",
        ) from error