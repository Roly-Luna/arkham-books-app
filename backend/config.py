import os
from pathlib import Path

from dotenv import load_dotenv


# define la ruta del archivo de entorno
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

# carga las variables de entorno
load_dotenv(ENV_PATH)


# obtiene una variable obligatoria
def get_required_env(variable_name: str) -> str:
    value = os.getenv(variable_name)

    if not value:
        raise RuntimeError(
            f"Missing environment variable: {variable_name}"
        )

    return value


# agrupa la configuracion de postgresql
DATABASE_CONFIG = {
    "host": get_required_env("DB_HOST"),
    "port": int(get_required_env("DB_PORT")),
    "dbname": get_required_env("DB_NAME"),
    "user": get_required_env("DB_USER"),
    "password": get_required_env("DB_PASSWORD"),
    "connect_timeout": 5,
}