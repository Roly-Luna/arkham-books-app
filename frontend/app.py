import os
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv


# define la ruta del archivo de variables de entorno
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

# carga las variables de entorno
load_dotenv(ENV_PATH)


# obtiene la direccion de la api
API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
)


# configura la pagina principal
st.set_page_config(
    page_title="Arkham Books",
    layout="wide",
)


# muestra el encabezado de la aplicacion
st.title("Arkham Books")
st.write("Catalogo de libros y revistas")


# recibe el titulo que desea buscar el usuario
search = st.text_input(
    "Buscar por titulo",
    placeholder="Ejemplo: Dune",
)


try:
    # solicita los productos a la api
    response = requests.get(
        f"{API_BASE_URL}/products/",
        params={"search": search} if search else {},
        timeout=5,
    )

    response.raise_for_status()

    # convierte la respuesta de la api
    products = response.json()

    # muestra los productos encontrados
    if products:
        st.dataframe(
            products,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No se encontraron productos.")

except requests.RequestException:
    # muestra un mensaje cuando la api no responde
    st.error("No se pudo conectar con el servidor de aplicaciones.")