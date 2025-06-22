# Keepa FastAPI Service

A minimal FastAPI application that fetches product data from the Keepa API and stores it in PostgreSQL.

## Prerequisites

- **Docker** — to run a local PostgreSQL instance
- **Python 3.12** (or newer) — for running the app

---

## 1 · Start PostgreSQL (Docker)

```bash
docker run -d   --name keepa-postgres   -e POSTGRES_USER=user   -e POSTGRES_PASSWORD=password   -e POSTGRES_DB=keepa   -p 5432:5432   postgres:16
```

The database will now be available at **`postgresql://user:password@localhost:5432/keepa`**.

---

## 2 · Create and activate a virtual environment

```bash
python3.12 -m venv venv
source venv/bin/activate
```

---

## 3 · Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4 · Run the API with hot‑reload

```bash
uvicorn app.main:app --reload
```

Now open **<http://localhost:8000/docs>** to explore the interactive Swagger UI.

---

## Environment variables (optional)

| Variable        | Default          | Description                       |
| --------------- | ---------------- | --------------------------------- |
| `DATABASE_URL`  | `postgresql://…` | Override the default Postgres URL |
| `KEEPA_API_KEY` | —                | Your Keepa API key                |

You can create a `.env` file or export variables before running Uvicorn if you need custom values.
