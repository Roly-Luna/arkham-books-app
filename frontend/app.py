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


# obtiene el mensaje de error de la api
def get_error_message(response):
    try:
        data = response.json()
        return data.get("detail", "Request failed")
    except ValueError:
        return "Request failed"


# obtiene los productos desde la api
def load_products(search=None):
    params = {}

    if search:
        params["search"] = search

    response = requests.get(
        f"{API_BASE_URL}/products",
        params=params,
        timeout=10,
    )

    response.raise_for_status()
    return response.json()


# obtiene las editoriales desde la api
def load_publishers():
    response = requests.get(
        f"{API_BASE_URL}/products/publishers",
        timeout=10,
    )

    response.raise_for_status()
    return response.json()


# muestra el encabezado principal
st.title("Arkham Books")
st.write("Gestion de productos")


# verifica la conexion con postgresql
try:
    response = requests.get(
        f"{API_BASE_URL}/health/database",
        timeout=5,
    )

    response.raise_for_status()

    st.success("Conexion con PostgreSQL activa")

except requests.RequestException:
    st.error("No se pudo conectar con PostgreSQL.")
    st.stop()


# carga los datos necesarios
try:
    publishers = load_publishers()

except requests.RequestException:
    st.error("No se pudieron obtener las editoriales.")
    st.stop()


publisher_names = {
    publisher["id"]: publisher["name"]
    for publisher in publishers
}


# organiza las operaciones crud
read_tab, create_tab, update_tab, delete_tab = st.tabs(
    [
        "Consultar",
        "Registrar",
        "Actualizar",
        "Eliminar",
    ]
)


# consulta productos
with read_tab:
    st.subheader("Consultar productos")

    search = st.text_input(
        "Buscar por titulo",
        placeholder="Ejemplo: fundacion",
        key="search_product",
    )

    try:
        products = load_products(search)

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


# registra productos
with create_tab:
    st.subheader("Registrar producto")

    with st.form("create_product_form"):
        title = st.text_input(
            "Titulo",
            value="producto prueba pc2",
        )

        price = st.number_input(
            "Precio",
            min_value=0.0,
            value=50.0,
            step=1.0,
        )

        stock = st.number_input(
            "Stock",
            min_value=0,
            value=10,
            step=1,
        )

        rating = st.selectbox(
            "Rating",
            options=[1, 2, 3, 4, 5],
            index=3,
        )

        publisher_id = st.selectbox(
            "Editorial",
            options=list(publisher_names.keys()),
            format_func=lambda value: publisher_names[value],
        )

        create_button = st.form_submit_button(
            "Registrar producto"
        )

    if create_button:
        payload = {
            "title": title,
            "price": price,
            "stock": stock,
            "rating": rating,
            "publisher_id": publisher_id,
        }

        try:
            response = requests.post(
                f"{API_BASE_URL}/products",
                json=payload,
                timeout=10,
            )

            if response.status_code == 201:
                product = response.json()

                st.success(
                    "Producto registrado correctamente. "
                    f"ID: {product['id']}"
                )

            else:
                st.error(get_error_message(response))

        except requests.RequestException:
            st.error("No se pudo registrar el producto.")


# actualiza productos
with update_tab:
    st.subheader("Actualizar producto")

    try:
        products = load_products()

        if not products:
            st.info("No existen productos disponibles.")

        else:
            product_ids = [
                product["id"]
                for product in products
            ]

            selected_id = st.selectbox(
                "Producto",
                options=product_ids,
                format_func=lambda product_id: next(
                    (
                        f"{product['id']} - {product['title']}"
                        for product in products
                        if product["id"] == product_id
                    ),
                    str(product_id),
                ),
                key="update_product",
            )

            selected_product = next(
                product
                for product in products
                if product["id"] == selected_id
            )

            with st.form("update_product_form"):
                update_title = st.text_input(
                    "Titulo",
                    value=selected_product["title"],
                )

                update_price = st.number_input(
                    "Precio",
                    min_value=0.0,
                    value=float(selected_product["price"]),
                    step=1.0,
                )

                update_stock = st.number_input(
                    "Stock",
                    min_value=0,
                    value=int(selected_product["stock"]),
                    step=1,
                )

                current_rating = (
                    selected_product["rating"]
                    if selected_product["rating"]
                    else 1
                )

                update_rating = st.selectbox(
                    "Rating",
                    options=[1, 2, 3, 4, 5],
                    index=current_rating - 1,
                    key="update_rating",
                )

                publisher_ids = list(
                    publisher_names.keys()
                )

                current_publisher = (
                    selected_product["publisher_id"]
                )

                publisher_index = publisher_ids.index(
                    current_publisher
                )

                update_publisher = st.selectbox(
                    "Editorial",
                    options=publisher_ids,
                    index=publisher_index,
                    format_func=lambda value: (
                        publisher_names[value]
                    ),
                    key="update_publisher",
                )

                update_button = st.form_submit_button(
                    "Actualizar producto"
                )

            if update_button:
                payload = {
                    "title": update_title,
                    "price": update_price,
                    "stock": update_stock,
                    "rating": update_rating,
                    "publisher_id": update_publisher,
                }

                response = requests.put(
                    f"{API_BASE_URL}/products/{selected_id}",
                    json=payload,
                    timeout=10,
                )

                if response.ok:
                    st.success(
                        "Producto actualizado correctamente."
                    )
                    st.rerun()

                else:
                    st.error(get_error_message(response))

    except requests.RequestException:
        st.error("No se pudieron cargar los productos.")


# elimina productos
with delete_tab:
    st.subheader("Eliminar producto")

    st.warning(
        "Utilizar esta opcion solamente con "
        "registros creados para las pruebas de PC2."
    )

    try:
        products = load_products()

        if not products:
            st.info("No existen productos disponibles.")

        else:
            product_ids = [
                product["id"]
                for product in products
            ]

            delete_id = st.selectbox(
                "Producto a eliminar",
                options=product_ids,
                format_func=lambda product_id: next(
                    (
                        f"{product['id']} - {product['title']}"
                        for product in products
                        if product["id"] == product_id
                    ),
                    str(product_id),
                ),
                key="delete_product",
            )

            confirm_delete = st.checkbox(
                "Confirmo que deseo eliminar este producto"
            )

            if st.button("Eliminar producto"):
                if not confirm_delete:
                    st.warning(
                        "Debe confirmar la eliminacion."
                    )

                else:
                    response = requests.delete(
                        f"{API_BASE_URL}/products/{delete_id}",
                        timeout=10,
                    )

                    if response.ok:
                        st.success(
                            "Producto eliminado correctamente."
                        )
                        st.rerun()

                    else:
                        st.error(
                            get_error_message(response)
                        )

    except requests.RequestException:
        st.error("No se pudieron cargar los productos.")