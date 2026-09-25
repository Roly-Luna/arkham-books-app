import os
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv


# define la ruta del archivo de entorno
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

# carga las variables de entorno
load_dotenv(ENV_PATH)


# obtiene la direccion interna de la api
API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
)


# configura la pagina principal
st.set_page_config(
    page_title="Arkham Books",
    layout="wide",
)


# muestra el encabezado principal
st.title("Arkham Books")
st.write("Catalogo de libros y revistas")


try:
    # verifica la conexion con la base de datos
    database_response = requests.get(
        f"{API_BASE_URL}/health/database",
        timeout=5,
    )

    database_response.raise_for_status()

    st.success("Conexion con PostgreSQL activa")

except requests.RequestException:
    st.error("No se pudo conectar con PostgreSQL.")
    st.stop()


# recibe el titulo que desea buscar el usuario
search = st.text_input(
    "Buscar por titulo",
    placeholder="Ejemplo: dune",
)


try:
    # solicita los productos al servidor de aplicaciones
    response = requests.get(
        f"{API_BASE_URL}/products",
        params={"search": search} if search else {},
        timeout=5,
    )

    response.raise_for_status()

    products = response.json()

    # muestra los productos obtenidos
    if products:
        st.dataframe(
            products,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No se encontraron productos.")

except requests.RequestException:
    st.error("No se pudieron obtener los productos.")