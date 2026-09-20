# STRUCTURE.md — file map & placement rules

Find the right file in one hop, without scanning the repo. Counts verified
2026-09-19.

---

## 1. Repo root

```
CafeManagementSystem/
├── README.md              how to run it
├── LICENSE
├── STRUCTURE.md           this file
├── BRAND.md               positioning, palette, voice
├── docs/
│   ├── ARCHITECTURE.md    read first: rules, reusable primitives, traps
│   └── ROADMAP.md         what is built, what is next, what is not being built
├── Backend/               FastAPI app
├── Frontend/              React + Vite app
├── landing/               the marketing site — static, standalone, no build step
├── .github/workflows/     lint · tests · build · migrations on real Postgres · images
├── docker-compose.yml     db + api + web, one command
├── .env.example           every setting, with a note on why it matters
├── Run_backend.bat        uvicorn app.main:app --reload
├── Run_frontend.bat       npm run dev
└── venv/                  local virtualenv (gitignored)
```

---

## 2. Backend

```
Backend/
├── pyproject.toml          runtime vs dev dependencies, ruff, mypy, pytest
├── requirements.txt        runtime only. One Postgres driver (psycopg 3).
├── Dockerfile              multi-stage, non-root, health-checked
├── alembic.ini
├── alembic/
│   ├── env.py              imports app.models.* so autogenerate sees every table
│   └── versions/           9 migrations
├── manage.py               CLI: seed-all, seed-menu, seed-roles, seed-tables, …
├── .env                    gitignored — see .env.example
└── app/
    ├── main.py             app, CORS, request-id logging, /health + /health/ready
    ├── core/               config · database engine · security primitives      3
    ├── dependencies/       auth: current user, outlet, module guards            1
    ├── models/             ORM, PascalCase files, every one inherits Common    33
    ├── schemas/            Pydantic contracts, XCreate/XUpdate/XOut            30
    ├── repositories/       every SQLAlchemy query + the outlet scope           31
    ├── services/           the rules and the transaction boundary              32
    ├── controllers/        per-request wiring + the pagination envelope        31
    ├── routes/             HTTP binding only                                   33
    ├── utils/              pure helpers — no I/O, no ORM                       11
    │   ├── tax.py          ★ the GST engine: discount before tax, CGST/SGST
    │   ├── money.py        Decimal helpers, ROUND_HALF_UP, never a float
    │   ├── permissions.py  ★ the role/module/action matrix
    │   ├── state_machine.py declared status transitions
    │   ├── pagination.py   one paginate(), not twenty-two copies
    │   ├── filters.py  media.py  rate_limiter.py  logging.py  exceptions.py  audit.py
    ├── commands/           9 seeders
    └── media/documents/    uploaded files (gitignored, served behind auth)

Backend/tests/              10 test files + conftest, SQLite in memory
    conftest.py             db_session / client / make_user / login fixtures
    test_authorization.py   walks the live route table; an unguarded router fails here
    test_layers.py          a repository with no service fails here
    test_tax.py             the bill arithmetic, on its own
    test_order_spine.py     order → KOT → serve → bill → settle, end to end
    test_invariants.py  test_correctness.py  test_tenancy.py  test_crud.py
    test_authentication.py  test_media.py
```

### Where new backend code goes

| You are adding… | Put it in |
|---|---|
| A new entity | `models/X.py` + register in `models/__init__.py` + `schemas/x.py` + repository + service + controller + `routes/x.py` + mount it in `routes/__init__.py` **with a guard** + an alembic revision |
| A business rule | `services/xService.py` — never a route, never a Pydantic validator |
| A query or filter | `repositories/xRepository.py` |
| A pure helper | `utils/` — check `money.py` and `tax.py` first |
| Anything touching an order's money | `services/orderService.py`, with the arithmetic in `utils/tax.py` where it is testable without a database |
| An auth or permission check | `dependencies/` and `utils/permissions.py` |
| A CLI or seed job | `commands/` |

---

## 3. Frontend

```
Frontend/
├── index.html              preconnects only; the selected font is fetched on demand
├── vite.config.js          base=/app/, aliases, chunks, vitest, and the middleware
│                           that serves ../landing at / in dev
├── tailwind.config.js      maps CSS variables → Tailwind tokens
├── eslint.config.js
├── Dockerfile / nginx.conf serves landing at / and the app at /app
└── src/
    ├── main.jsx            ReactDOM root + <Provider store>
    ├── App.jsx             error boundary → initializer → confirm provider → routes
    ├── index.css           Tailwind layers, design tokens, focus ring
    ├── app/
    │   ├── store.js        auth + settings + the RTK Query reducer
    │   ├── baseApi.js      createApi + tagTypes + the re-auth base query
    │   ├── api/            14 domain modules, each baseApi.injectEndpoints
    │   ├── allSlices.js    barrel — keeps one import path for every hook
    │   ├── authSlice.js    who is signed in and what they may do
    │   └── settingsSlice.js theme + font
    ├── services/           auth (session + token) · usePermissions · media · outlet
    ├── config/
    │   ├── config.js       API base + appUrl() for browser-level navigation
    │   ├── color.js        ★ WCAG contrast maths, pure and tested
    │   ├── themes.js       8 palettes + deriveTokens() + applyTheme()
    │   ├── fonts.js        font stacks + loadFont() on demand
    │   ├── sidebarMenu.js  menu entries (label, path, icon, module)
    │   └── permissions.js  the module/action vocabulary; rules come from the server
    ├── utils/format.js     ★ money, dates, enums, names — one implementation
    ├── components/         24 shared, prop-driven, no fetching inside
    ├── test/setup.js       RTL cleanup + jest-dom matchers
    └── pages/
        ├── Login.jsx  Register.jsx  Dashboard.jsx  AppSettings.jsx  NotFound.jsx
        ├── OrderManagement/    Orders (the till) · OrderTicket · KitchenDisplay
        ├── MenuManagement/     MenuTabs → Items, Sections
        ├── UserManagement/     Users, Roles
        ├── EmployeeManagement/ Details, Attendance, Documents, Performance,
        │                       Designations, Departments
        ├── EmployeePaymentManagement/ Structures, Payslips, Incentives, Increments
        ├── CustomerManagement/ Invoices, Feedback, Services, Tables
        ├── InventoryManagement/ Items, Categories, Movements
        ├── PaymentManagement/  Payments, Earnings
        ├── OutletManagement/   Outlets
        └── ActivityLogManagement/ Sign-ins, Change history
```

### Where new frontend code goes

| You are adding… | Put it in |
|---|---|
| A new screen | `pages/<Domain>Management/X.jsx` + its `*Tabs.jsx` or `App.jsx` |
| A new API call | `app/api/<domain>Api.js`, **and its tag in `app/baseApi.js`** — a tag that is not declared there is silently ignored |
| Anything visual used twice | `components/` — prop-driven, no fetching inside |
| A formatter | `utils/format.js` — check first, it probably exists |
| A colour | a token. `text-white` and `bg-black/50` are defects; see `config/themes.js` |
| A theme, font, menu item | `config/` |

---

## 4. Request path

```
Page (useGetXQuery)
  → baseQuery (Bearer from authService, X-Outlet-Id from outletService)
    → /api/v1/<resource>/
      → routes/x.py                  binds path, query and body. Nothing else.
        → controllers/xController.py pagination envelope
          → services/xService.py     the rules, and the transaction boundary
            → repositories/xRepository.py  every query, plus the outlet scope
              → Postgres
      ← {data, total, totalPages, currentPage}
  ← DataTable + FilterBar render
```

The order spine adds one more shape, because its verbs are not CRUD:

```
POST /api/v1/orders/{id}/bill
  → routes/order.py → controllers/orderController.py → services/orderService.bill()
      → utils/tax.compute_bill()     pure; no session, no ORM
      → writes CustomerInvoice + InvoiceLine and moves the order to `billed`,
        in one transaction
```

---

## 5. Naming quick reference

| Thing | Convention | Example |
|---|---|---|
| Model file/class | PascalCase | `EmployeeDetails.py` → `class EmployeeDetails` |
| Table | snake_case plural | `employee_details` |
| Schema module | snake_case | `employee_details.py` |
| Schema classes | `XCreate/XUpdate/XOut/PaginatedXOut` | `EmployeeDetailsOut` |
| Repository / service / controller | camelCase file | `orderRepository.py` |
| Route prefix | kebab-case plural, trailing slash | `/employee-details/` |
| RTK hooks | `useGetXQuery`, `useCreateXMutation` | `useGetOrdersQuery` |
| React component file | PascalCase.jsx | `DataTable.jsx` |
| CSS variable | `--color-*`, an RGB triple | `--color-primary: 34 197 94` |

---

## 6. Layer rules

One-way dependencies. A layer may import from the layers below it, never above.

```
routes/        HTTP only: path, verb, response_model. No business rules.    33 files
  ↓
controllers/   query params → service call → response envelope              31 files
  ↓
services/      the use-cases, and the transaction boundary                  32 files
  ↓
repositories/  every SQLAlchemy query in the application                    31 files
  ↓
utils/         pure helpers. Imports nothing from the four layers above.    11 files
```

`models/`, `schemas/`, `core/` and `dependencies/` sit beside this stack and may
be imported from anywhere. `tests/test_layers.py` fails the build if an entity
has a repository with no service, or if a route file starts carrying weight.
