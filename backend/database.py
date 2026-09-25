from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row

from backend.config import DATABASE_CONFIG


# crea una conexion temporal con postgresql
@contextmanager
def get_connection():
    connection = psycopg.connect(
        **DATABASE_CONFIG,
        row_factory=dict_row,
    )

    try:
        yield connection
    finally:
        connection.close()


# verifica que postgresql responda correctamente
def check_database_connection() -> bool:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            cursor.fetchone()

    return True