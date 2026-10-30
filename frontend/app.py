import os
from datetime import datetime

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
REQUEST_TIMEOUT = 12

st.set_page_config(
    page_title="Arkham Books | Biblioteca de lectores",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');
    :root { --ink:#eee9df; --muted:#aaa49a; --paper:#171714; --panel:#22221e; --line:#393830; --gold:#d5a85f; --rust:#a75d42; }
    html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
    .stApp { background: radial-gradient(circle at 85% 0%, #343025 0, #171714 38rem); color:var(--ink); }
    [data-testid="stSidebar"] { background:#11110f; border-right:1px solid var(--line); }
    h1,h2,h3,.serif { font-family:'Playfair Display',serif !important; letter-spacing:-.025em; }
    h1 { font-size:3rem !important; }
    .eyebrow { color:var(--gold); text-transform:uppercase; letter-spacing:.19em; font-size:.72rem; font-weight:700; }
    .hero { padding:2.3rem 2.5rem; border:1px solid #4b4538; border-radius:22px; background:linear-gradient(110deg,rgba(20,19,16,.97),rgba(38,32,24,.78)),url('https://images.unsplash.com/photo-1507842217343-583bb7270b66?auto=format&fit=crop&w=1800&q=85') center/cover; min-height:300px; display:flex; flex-direction:column; justify-content:center; margin-bottom:1.5rem; }
    .hero h1 { max-width:680px; margin:.5rem 0; line-height:1.08; }
    .hero p { color:#d0c7b8; max-width:580px; font-size:1.02rem; }
    .metric-card,.surface { background:linear-gradient(145deg,#25241f,#1d1d19); border:1px solid var(--line); border-radius:16px; padding:1.1rem 1.25rem; }
    .metric-label { color:var(--muted); font-size:.78rem; text-transform:uppercase; letter-spacing:.1em; }
    .metric-value { color:var(--ink); font-size:1.8rem; font-family:'Playfair Display',serif; }
    .book-card { background:#24231f; border:1px solid #3c3931; border-radius:14px; overflow:hidden; height:100%; }
    .book-card img { width:100%; height:220px; object-fit:cover; display:block; }
    .book-card .book-info { padding:1rem; }
    .book-title { font-family:'Playfair Display',serif; font-size:1.08rem; color:#f3eee5; }
    .book-meta { color:#aaa49a; font-size:.82rem; margin:.3rem 0; }
    .tag { color:#e0bd83; font-size:.7rem; text-transform:uppercase; letter-spacing:.12em; }
    .post { background:linear-gradient(145deg,#26251f,#1d1d19); border:1px solid #403d34; border-radius:16px; padding:1.2rem 1.35rem; margin:.6rem 0 1rem; }
    .post-author { color:#e3bb79; font-weight:700; }
    .post-date { color:#918b80; font-size:.78rem; }
    .post-content { color:#eee9df; font-size:1rem; line-height:1.65; margin:.8rem 0; white-space:pre-wrap; }
    .stButton>button, .stFormSubmitButton>button { border-radius:10px; border:1px solid #92754b; background:#b78b4c; color:#171714; font-weight:700; }
    .stButton>button:hover,.stFormSubmitButton>button:hover { background:#d2a761; color:#171714; border-color:#d2a761; }
    [data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea,[data-testid="stNumberInput"] input { background:#1d1d19; border-color:#49453a; color:#f1ece3; }
    [data-baseweb="tab-list"] { gap:.4rem; }
    [data-baseweb="tab"] { background:#24231f; border-radius:9px 9px 0 0; padding:.7rem 1rem; }
    .divider { border-top:1px solid #393830; margin:1rem 0; }
    a { color:#e2b875 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


def api_get(path, params=None):
    response = requests.get(
        f"{API_BASE_URL}{path}",
        params=params,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def api_write(method, path, payload=None):
    response = requests.request(
        method,
        f"{API_BASE_URL}{path}",
        json=payload,
        timeout=REQUEST_TIMEOUT,
    )
    if not response.ok:
        try:
            detail = response.json().get("detail", "No se pudo completar la operacion")
        except ValueError:
            detail = "No se pudo completar la operacion"
        raise RuntimeError(detail)
    return response.json() if response.content else {}


def money(value):
    return f"S/ {float(value):,.2f}"


def cover_for(title, index):
    covers = [
        "photo-1543002588-bfa74002ed7e",
        "photo-1512820790803-83ca734da794",
        "photo-1544947950-fa07a98d237f",
        "photo-1519682337058-a94d519337bc",
        "photo-1516979187457-637abb4f9353",
        "photo-1511108690759-009324a90311",
    ]
    image_id = covers[index % len(covers)]
    return f"https://images.unsplash.com/{image_id}?auto=format&fit=crop&w=700&q=85"


def render_post(post):
    author_id = post.get("author_id", "Lector")
    content = post.get("content", "")
    kind = post.get("kind", "post").replace("_", " ").title()
    book = post.get("book_title")
    created = post.get("created_at", "")
    try:
        created = datetime.fromisoformat(created.replace("Z", "+00:00")).strftime("%d/%m/%Y · %H:%M")
    except (ValueError, AttributeError):
        created = "Recientemente"
    st.markdown(
        f"""
        <div class="post">
          <div><span class="post-author">Lector #{author_id}</span>
          <span class="post-date"> · {created}</span></div>
          <div class="tag">{kind}{(" · " + book) if book else ""}</div>
          <div class="post-content">{content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    post_id = post.get("id")
    with st.expander("Conversacion y reacciones", expanded=False):
        left, right = st.columns([2, 1])
        with left:
            comment_user = st.number_input(
                "Tu ID de usuario",
                min_value=1,
                step=1,
                key=f"comment_user_{post_id}",
            )
            comment_text = st.text_input("Escribe un comentario", key=f"comment_text_{post_id}")
            if st.button("Publicar comentario", key=f"comment_send_{post_id}"):
                try:
                    api_write("POST", f"/community/posts/{post_id}/comments", {
                        "author_id": int(comment_user),
                        "content": comment_text,
                    })
                    st.success("Comentario publicado")
                    st.rerun()
                except (requests.RequestException, RuntimeError) as error:
                    st.error(str(error))
        with right:
            reaction_user = st.number_input(
                "ID para reaccionar",
                min_value=1,
                step=1,
                key=f"reaction_user_{post_id}",
            )
            reaction = st.selectbox(
                "Reaccion",
                ["like", "love", "insightful"],
                key=f"reaction_type_{post_id}",
            )
            if st.button("Reaccionar", key=f"reaction_send_{post_id}"):
                try:
                    api_write("PUT", f"/community/posts/{post_id}/reaction", {
                        "user_id": int(reaction_user),
                        "reaction": reaction,
                    })
                    st.success("Reaccion guardada")
                except (requests.RequestException, RuntimeError) as error:
                    st.error(str(error))
        try:
            comments = api_get(f"/community/posts/{post_id}/comments")
            if comments:
                for comment in comments:
                    st.caption(f"Lector #{comment['author_id']} · {comment['content']}")
            else:
                st.caption("Todavia no hay comentarios")
        except requests.RequestException:
            st.caption("No se pudieron cargar los comentarios")


with st.sidebar:
    st.markdown('<div class="eyebrow">Tu espacio de lectura</div>', unsafe_allow_html=True)
    st.markdown("## ARKHAM BOOKS")
    st.caption("Una biblioteca para descubrir historias y encontrar lectores.")
    page = st.radio(
        "Navegacion",
        ["Inicio", "Explorar libros", "Comunidad", "Gestion de catalogo"],
        label_visibility="collapsed",
    )
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.caption("ESTADO DE SERVICIOS")
    try:
        api_get("/health")
        st.success("API conectada")
    except requests.RequestException:
        st.error("API desconectada")
    try:
        api_get("/health/database")
        st.success("PostgreSQL conectado")
    except requests.RequestException:
        st.warning("PostgreSQL no disponible")
    try:
        api_get("/community/health")
        st.success("MongoDB conectado")
    except requests.RequestException:
        st.warning("MongoDB no disponible")


if page == "Inicio":
    st.markdown(
        """
        <section class="hero">
          <div class="eyebrow">Lee. Descubre. Comparte.</div>
          <h1>Las historias tambien se viven en comunidad.</h1>
          <p>Explora nuevos libros, encuentra tu siguiente lectura y conversa con personas que disfrutan las mismas historias.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    try:
        products = api_get("/products")
        posts = api_get("/community/feed", {"limit": 5}).get("items", [])
        c1, c2, c3 = st.columns(3)
        for column, label, value in [
            (c1, "EN EL CATALOGO", len(products)),
            (c2, "PUBLICACIONES", len(posts)),
            (c3, "EXPERIENCIAS", "Sin limites"),
        ]:
            with column:
                st.markdown(
                    f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>',
                    unsafe_allow_html=True,
                )
        st.markdown("### Lecturas para perderse un rato")
        if products:
            cols = st.columns(min(4, len(products)))
            for index, product in enumerate(products[:4]):
                with cols[index]:
                    st.markdown(
                        f'<div class="book-card"><img src="{cover_for(product["title"], index)}"><div class="book-info"><div class="tag">{product.get("product_type", "Libro")}</div><div class="book-title">{product["title"]}</div><div class="book-meta">{product.get("publisher", "Editorial")}</div><strong>{money(product["price"])}</strong></div></div>',
                        unsafe_allow_html=True,
                    )
        else:
            st.info("El catalogo todavia no tiene productos.")
        st.markdown("### Lo que esta pasando en la comunidad")
        for post in posts[:3]:
            render_post(post)
    except requests.RequestException:
        st.error("No se pudo cargar la informacion. Verifica FastAPI y las bases de datos.")


elif page == "Explorar libros":
    st.markdown('<div class="eyebrow">Catalogo editorial</div>', unsafe_allow_html=True)
    st.title("Encuentra tu proxima historia")
    search = st.text_input("Buscar por titulo", placeholder="Prueba con Dune, historia, fantasia...")
    try:
        products = api_get("/products", {"search": search} if search else None)
        st.caption(f"{len(products)} resultados")
        if products:
            for start in range(0, len(products), 3):
                cols = st.columns(3)
                for offset, product in enumerate(products[start:start + 3]):
                    index = start + offset
                    with cols[offset]:
                        st.markdown(
                            f'<div class="book-card"><img src="{cover_for(product["title"], index)}"><div class="book-info"><div class="tag">{product.get("product_type", "Producto")}</div><div class="book-title">{product["title"]}</div><div class="book-meta">{product.get("publisher", "Editorial")}</div><div class="book-meta">Stock: {product["stock"]} · Rating: {product.get("rating") or "Sin rating"}</div><strong>{money(product["price"])}</strong></div></div>',
                            unsafe_allow_html=True,
                        )
        else:
            st.info("No encontramos libros con esa busqueda.")
    except requests.RequestException:
        st.error("No se pudo consultar el catalogo.")


elif page == "Comunidad":
    st.markdown('<div class="eyebrow">El club de lectores</div>', unsafe_allow_html=True)
    st.title("La conversacion empieza aqui")
    st.markdown("Comparte una lectura, recomienda un libro o publica una resena.")
    with st.form("new_post_form", clear_on_submit=True):
        user_id = st.number_input("ID de usuario (PostgreSQL)", min_value=1, step=1)
        kind = st.selectbox("Tipo de publicacion", ["post", "review", "recommendation"])
        book_title = st.text_input("Libro relacionado (opcional)")
        content_text = st.text_area("Que quieres compartir", max_chars=2000, height=130)
        publish = st.form_submit_button("Publicar en la comunidad")
    if publish:
        try:
            api_write("POST", "/community/posts", {
                "author_id": int(user_id),
                "content": content_text,
                "kind": kind,
                "book_title": book_title or None,
            })
            st.success("Tu publicacion ya forma parte de la comunidad.")
            st.rerun()
        except (requests.RequestException, RuntimeError) as error:
            st.error(str(error))
    st.markdown("---")
    st.subheader("Feed de lectores")
    try:
        feed = api_get("/community/feed", {"limit": 30}).get("items", [])
        if not feed:
            st.info("Todavia no hay publicaciones. Inicia la conversacion.")
        for post in feed:
            render_post(post)
    except requests.RequestException:
        st.warning("La comunidad necesita que MongoDB este conectado.")


else:
    st.markdown('<div class="eyebrow">Administracion editorial</div>', unsafe_allow_html=True)
    st.title("Gestion de catalogo")
    st.caption("Operaciones conectadas al API REST y PostgreSQL.")
    tabs = st.tabs(["Consultar", "Registrar", "Actualizar", "Eliminar"])
    try:
        publishers = api_get("/products/publishers")
        publisher_map = {item["id"]: item["name"] for item in publishers}
        with tabs[0]:
            search = st.text_input("Filtrar productos", key="admin_search")
            products = api_get("/products", {"search": search} if search else None)
            st.dataframe(products, use_container_width=True, hide_index=True)
        with tabs[1]:
            with st.form("create_product"):
                title = st.text_input("Titulo")
                price = st.number_input("Precio (S/)", min_value=0.0, step=1.0)
                stock = st.number_input("Stock", min_value=0, step=1)
                rating = st.selectbox("Rating", [None, 1, 2, 3, 4, 5], format_func=lambda x: "Sin rating" if x is None else str(x))
                publisher_id = st.selectbox("Editorial", list(publisher_map), format_func=lambda x: publisher_map[x])
                submitted = st.form_submit_button("Registrar producto")
            if submitted:
                try:
                    api_write("POST", "/products", {
                        "title": title, "price": price, "stock": stock,
                        "rating": rating, "publisher_id": publisher_id,
                    })
                    st.success("Producto registrado")
                    st.rerun()
                except (requests.RequestException, RuntimeError) as error:
                    st.error(str(error))
        with tabs[2]:
            products = api_get("/products")
            if products:
                selected = st.selectbox("Producto", products, format_func=lambda p: f'{p["id"]} · {p["title"]}')
                with st.form("update_product"):
                    title = st.text_input("Titulo", value=selected["title"])
                    price = st.number_input("Precio (S/)", min_value=0.0, value=float(selected["price"]), step=1.0)
                    stock = st.number_input("Stock", min_value=0, value=int(selected["stock"]), step=1)
                    rating = st.selectbox("Rating", [None, 1, 2, 3, 4, 5], index=([None, 1, 2, 3, 4, 5].index(selected["rating"]) if selected["rating"] in [None, 1, 2, 3, 4, 5] else 0), format_func=lambda x: "Sin rating" if x is None else str(x))
                    publisher_id = st.selectbox("Editorial", list(publisher_map), index=list(publisher_map).index(selected["publisher_id"]), format_func=lambda x: publisher_map[x])
                    submitted = st.form_submit_button("Guardar cambios")
                if submitted:
                    try:
                        api_write("PUT", f'/products/{selected["id"]}', {
                            "title": title, "price": price, "stock": stock,
                            "rating": rating, "publisher_id": publisher_id,
                        })
                        st.success("Producto actualizado")
                        st.rerun()
                    except (requests.RequestException, RuntimeError) as error:
                        st.error(str(error))
            else:
                st.info("No hay productos para actualizar.")
        with tabs[3]:
            products = api_get("/products")
            if products:
                selected = st.selectbox("Producto a eliminar", products, format_func=lambda p: f'{p["id"]} · {p["title"]}', key="delete_selection")
                confirm = st.checkbox("Confirmo que deseo eliminar este producto")
                if st.button("Eliminar producto"):
                    if not confirm:
                        st.warning("Confirma la eliminacion antes de continuar.")
                    else:
                        try:
                            api_write("DELETE", f'/products/{selected["id"]}')
                            st.success("Producto eliminado")
                            st.rerun()
                        except (requests.RequestException, RuntimeError) as error:
                            st.error(str(error))
            else:
                st.info("No hay productos para eliminar.")
    except requests.RequestException:
        st.error("No se pudo cargar el catalogo. Verifica PostgreSQL.")
