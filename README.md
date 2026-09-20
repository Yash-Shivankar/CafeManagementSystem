# Caelum

A cafe system: a point of sale — menu, orders, kitchen display, GST billing,
settlement — on top of a back office of staff, payroll, inventory, customers and
P&L. Multi-outlet throughout.

| | |
|---|---|
| Backend | Python 3.12 · FastAPI · SQLAlchemy 2.0 · PostgreSQL · Alembic |
| Frontend | React 19 · Vite · Redux Toolkit (RTK Query) · Tailwind |
| Landing | One static page, no build step |

---

## Run it

```bash
docker compose up --build
```

| | |
|---|---|
| <http://localhost:5173> | the landing page |
| <http://localhost:5173/app> | the product |
| <http://localhost:8000> | the API (`/docs` outside production) |

Copy `.env.example` to `.env` first and set `POSTGRES_PASSWORD` and `JWT_SECRET`.

### Or without Docker

```bash
cd Backend && pip install -e ".[dev]" && alembic upgrade head && python manage.py seed-all
Run_backend.bat

cd Frontend && npm install
Run_frontend.bat
```

The dev server serves the landing page at `/` and the app at `/app`, the same
way nginx does in production — so the front door is the same in both.

---

## Test it

```bash
cd Backend && pytest && ruff check . && ruff format --check .
cd Frontend && npm test && npm run lint && npm run build
```

613 backend tests, 168 frontend. CI runs both, plus a production build and
`alembic upgrade → downgrade → upgrade → check` against a real Postgres.

---

## Where things are

| | |
|---|---|
| `docs/ARCHITECTURE.md` | **read first** — the rules, the reusable primitives, and the traps |
| `STRUCTURE.md` | the file map: find the right file in one hop |
| `docs/ROADMAP.md` | what is built, what is next, what is deliberately not |
| `BRAND.md` | positioning, palette, voice |
| `landing/README.md` | the four things to do before the site goes public |
