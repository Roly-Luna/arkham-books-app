# Arkham Books

Bookstore and reader community application for PC3.

## Architecture

- Streamlit: web interface for catalog and community
- FastAPI: REST API and business rules
- PostgreSQL: users, products, publishers and orders
- MongoDB: posts, comments, reactions and follows

## Requirements

- Python 3.11 or newer
- uv
- PostgreSQL
- MongoDB 7 or Docker Compose

## Local setup

```bash
git clone https://github.com/Roly-Luna/arkham-books-app.git
cd arkham-books-app
uv sync
cp .env.example .env
```

Edit .env with your local database credentials. MongoDB is optional for the catalog API, but required for community endpoints.

## Run FastAPI

```bash
uv run uvicorn backend.main:app --reload
```

API documentation: http://127.0.0.1:8000/docs

## Run Streamlit

```bash
uv run streamlit run frontend/app.py
```

## Main API routes

- GET /health
- GET /health/database
- GET /products
- GET /products/publishers
- GET /community/health
- GET /community/feed
- POST /community/posts
- GET /community/posts/{post_id}/comments
- POST /community/posts/{post_id}/comments
- PUT /community/posts/{post_id}/reaction
- DELETE /community/posts/{post_id}/reaction/{user_id}
- POST /community/follow

Community write requests validate that user IDs exist in PostgreSQL. The current PC3 endpoints do not yet implement login or token-based authorization. Add authentication before exposing write operations publicly.

## Database deployment

Follow the data-tier repository instructions. Apply the additive PostgreSQL migration after backing up the existing database. Deploy MongoDB on VM1 and permit port 27017 only from VM2 over the private network.

## Images

The interface uses remote Unsplash image URLs for editorial decoration and sample book covers. Replace these with licensed project assets before a public commercial launch.
