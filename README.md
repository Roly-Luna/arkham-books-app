# Arkham Books

Aplicacion web desarrollada para la capa de aplicacion de Arkham Books.

## Requisitos

- Python
- uv
- Git

## Clonar el proyecto

git clone URL_DEL_REPOSITORIO
cd arkham-books-app

## Instalar dependencias

uv sync

## Configurar variables de entorno

Crear un archivo .env usando .env.example como referencia.

## Ejecutar FastAPI

uv run uvicorn backend.main:app --reload

## Ejecutar Streamlit

uv run streamlit run frontend/app.py