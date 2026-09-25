import os
from contextlib import contextmanager
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row


# define la ruta del archivo de variables de entorno
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

# carga las variables de entorno
load_dotenv(ENV_PATH)


# obtiene una variable de entorno obligatoria
def get_required_env(variable_name: str) -> str:
    value = os.getenv(variable_name)

    if not value:
        raise RuntimeError(f"Missing environment variable: {variable_name}")

    return value


# agrupa los datos necesarios para conectarse a postgresql
DATABASE_CONFIG = {
    "host": get_required_env("DB_HOST"),
    "port": int(get_required_env("DB_PORT")),
    "dbname": get_required_env("DB_NAME"),
    "user": get_required_env("DB_USER"),
    "password": get_required_env("DB_PASSWORD"),
}


# crea y cierra una conexion con postgresql
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