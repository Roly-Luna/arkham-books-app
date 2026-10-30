import os
from pathlib import Path

from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_PATH)


def get_optional_env(variable_name: str, default: str | None = None) -> str | None:
    return os.getenv(variable_name, default)


def get_required_env(variable_name: str) -> str:
    value = get_optional_env(variable_name)
    if not value:
        raise RuntimeError(f"Missing environment variable: {variable_name}")
    return value


DATABASE_CONFIG = {
    "host": get_required_env("DB_HOST"),
    "port": int(get_optional_env("DB_PORT", "5432")),
    "dbname": get_required_env("DB_NAME"),
    "user": get_required_env("DB_USER"),
    "password": get_required_env("DB_PASSWORD"),
    "connect_timeout": 5,
}
