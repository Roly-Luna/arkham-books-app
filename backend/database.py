from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row

from backend.config import DATABASE_CONFIG


# crea y administra una conexion con postgresql
@contextmanager
def get_connection():
    with psycopg.connect(
        **DATABASE_CONFIG,
        row_factory=dict_row,
    ) as connection:
        yield connection


# verifica la conexion con postgresql
def check_database_connection() -> bool:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            cursor.fetchone()

    return True