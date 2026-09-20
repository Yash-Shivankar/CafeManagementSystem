# Architecture — Cafe Management System ("Caelum")

> Read this file **first**, then `STRUCTURE.md`. Do not scan the whole repo before you start.
> `ROADMAP.md` holds what is built and what is not.

---

## 1. What this is

A cafe system: a point of sale (menu, orders, kitchen display, GST billing, settlement) on top
of a back office (users, employees with HR/payroll, customers, inventory, invoices, payments,
P&L), multi-outlet throughout. Monorepo, two apps, one Postgres DB.

| | Stack |
|---|---|
| Backend | Python 3.12 · FastAPI 0.123 · SQLAlchemy 2.0 (sync) · Pydantic v2 · Alembic · PostgreSQL · Typer CLI |
| Frontend | React 19 · Vite (rolldown) · Redux Toolkit + **RTK Query** · Tailwind 3 · react-router 7 · lucide-react · react-toastify |
| Auth | JWT (PyJWT, HS256, 60 min access + 30 day httpOnly refresh cookie, rotated) · argon2 |
| API base | `/api/v1` · media behind a Bearer token or a short-lived signed URL |
| Routes | `/` landing · `/app` the SPA · `/api/v1` the API |

Run: `Run_backend.bat` (uvicorn) and `Run_frontend.bat` (vite), or `docker compose up` for the
whole stack including Postgres. Seed data: `python manage.py seed-all`.

**The front door is the landing page.** `/` serves `landing/`; the product is at `/app`. The Vite
dev server does this with a middleware and nginx does it with two locations, so the two behave the
same. Anything that navigates the browser by hand — a redirect after logout, the error boundary —
must go through `appUrl()` in `config/config.js`; a bare `"/login"` now lands on the marketing page.

Install: `pip install -e ".[dev]"` in Backend, `npm install` in Frontend.
Test: `pytest` in Backend (613), `npm test` in Frontend (168).
Lint: `ruff check . && ruff format --check .` · `npm run lint`.

---

## 2. Golden rules

1. **Reuse before you write.** This codebase is deliberately component-driven. Section 4 and 5 list
   every reusable primitive that already exists. Creating a second table, modal, form, or button is
   a defect, not a feature. If a primitive is 80% right, **extend it with a new prop** — never fork it.
2. **Follow the layering** in section 3. Routes stay thin.
3. **One pattern per concern.** If you introduce a new way to paginate, validate, or fetch, migrate
   the others or don't do it.
4. **Never change a rule without saying why.** The code is deliberately light on comments, so
   §7 of this file and `ROADMAP.md` are where the reasoning lives. If you add a rule whose
   violation would be invisible in review, it belongs in §7.
5. **Don't guess at domain rules.** Money, stock, attendance, payroll and the order lifecycle all
   have invariants, and they are enforced in the service layer — not in a route, not in a Pydantic
   validator (a rule hidden in a validator cannot be unit tested, cannot be called from a job, and
   silently rewrites its input; two money bugs lived there). If you need a new rule, put it in the
   service and write the test that names what it protects.
6. **Don't commit `.env`, `venv/`, `node_modules/`, `app/media/`.** Already in `.gitignore` — keep it that way.

---

## 3. Backend layering

```
routes/        HTTP only: path, query/body binding, status codes, response_model. No SQL, no math.
controllers/   Per-request wiring (session, user, outlet) + the pagination envelope.
services/      Business rules, orchestration, transactions. Owns the "why".
repositories/  All SQLAlchemy queries. Owns the "how we read/write", and the outlet scope.
schemas/       Pydantic request/response contracts. Never leak ORM objects past this line.
models/        SQLAlchemy ORM. PascalCase filenames, one model per file.
utils/         Pure helpers, no I/O (pagination, money, dates, enums).
dependencies/  FastAPI Depends providers (db session, current user, RBAC guards).
core/          config, database engine, security primitives.
commands/      Typer seed/admin commands.
```

**Current reality:** this is now the actual shape, not a target — `test_layers.py` fails the build
if an entity has a repository with no service, or if a route file starts carrying weight.
`crud/base.py` is superseded by `repositories/baseRepository.py`.

**Frontend layering:**
```
pages/         Route-level screens. Composition + page-specific config only.
components/    Shared, presentational, prop-driven. No API calls inside.
services/      Non-Redux side effects (auth/token/storage).
app/           Redux store + RTK Query API slices.
config/        Static config: themes, fonts, menu, permissions.
utils/         Pure helpers. `format.js` holds every money/date/enum formatter — look there
               before writing another; the four that existed before it disagreed with each other.
```

---

## 4. Reusable frontend components — USE THESE

Path: `Frontend/src/components/`. Props are the contract; respect them.

| Component | Props | Notes |
|---|---|---|
| `Button` | `label, onClick, type, variant(primary\|secondary\|outline\|danger\|ghost), size(sm\|md\|lg), disabled, loading, icon, className, title, ariaLabel` | Icon is a lucide component, not an element. An icon-only button needs `title` or `ariaLabel`. |
| `DataTable` | `data[], columns[{key,label,render?}], onEdit, onDelete, pagination{currentPage,totalPages,total?}, onPageChange, loading, caption, emptyMessage, emptyHint, emptyAction, getRowId, rowActions` | Renders its own Actions column + pager, skeletons while loading, and a card layout below `md`. |
| `DynamicForm` | `fields[{name,label,type,options?,required?,help?,placeholder?,…}], initialValues, onSubmit, onCancel, submitLabel, submitting, errors{}` | `type`: text/number/date/password/select/textarea/**stars**/file. Submits only declared fields. |
| `FilterBar` | `filters[{name,label,type,placeholder?,options?}], values, onChange, onApply, onReset` | `type`: text/select/date. |
| `Modal` | `title, onClose, children` | Focus trap, Escape, restored focus, `aria-modal`. Backdrop click closes; a drag that ends there does not. |
| `Tabs` | `tabs[{key,label}], activeKey, onChange, label` | Proper tablist with arrow keys. Every `*Tabs.jsx` uses it. |
| `ConfirmProvider` / `useConfirm` | `confirm({title,message,tone,confirmLabel,reasonLabel?})` | Replaces `window.confirm`. With `reasonLabel` it collects a reason and resolves to that string. |
| `ErrorBoundary` | — | Wraps the app; a render crash shows a way back instead of a white page. |
| `StatsCard` | `label, value, description, icon, iconSize(sm..xxl), loading, className` | Dashboard KPI tile, has skeleton state. |
| `StarInput` / `StarDisplay` | `value, max, onChange` / `value, max` | Ratings. |
| `MainLayout` | — | Navbar + Sidebar + `<Outlet/>`. |
| `Navbar`, `Sidebar` | — | Sidebar reads `config/sidebarMenu.js`. |
| `ProtectedRoute` | `children, module?` | Session + module permission. A *navigation* guard only — the API enforces the same matrix on every request. |
| `AppInitializer` | `children` | Restores the session from the refresh cookie, then the theme and font. Owns the appearance defaults — the pickers do not create them. |
| `ThemeSwitcher`, `FontSelector` | — | Write a chosen value through the `PUT /settings/{key}` upsert. Swatches, not a dropdown of names. |
| `OutletSwitcher` | — | Sets the branch; `baseQuery` sends it as `X-Outlet-Id` on every request. |

**The standard CRUD page shape** (see `pages/EmployeeManagement/EmployeeDetails.jsx` — copy this, don't invent):

```
useState(page, showForm, editingRow, filters, appliedFilters)
  → useGetXQuery({page, limit, ...appliedFilters})
  → <FilterBar/> → <DataTable/> → {showForm && <Modal><DynamicForm/></Modal>}
  → handleSubmit: create|update → toast → close
  → handleDelete: confirm → delete → toast
```

Tab containers (`*Tabs.jsx`) hold `[{key,label,component}]` and render the active one.

---

## 5. Reusable backend primitives — USE THESE

| Primitive | Location | What it gives you |
|---|---|---|
| `BaseRepository[Model]` | `app/repositories/baseRepository.py` | Every query. `get_or_404`, `list(filters, search, relationships)`, `create`, `update`, `soft_delete`. **Flushes, never commits** — the service owns the transaction. |
| `BaseService[Model]` | `app/services/baseService.py` | The use-case: uniqueness, outlet scoping, the audit entry, the commit. Attach rules with `before_create` / `after_create` / `before_update` / `before_delete`. |
| `BaseController` | `app/controllers/baseController.py` | Injected per request with session, user and outlet. Route handlers shrink to a signature and one call. |
| `compute_bill` | `app/utils/tax.py` | The GST engine. Pure Decimal: discount before tax and spread across lines, CGST/SGST per slab, taxable service charge, round-off. Never reimplement this. |
| `money` helpers | `app/utils/money.py` | `quantise`, `add`, `subtract`, `is_positive`. `ROUND_HALF_UP`. Money never touches a float. |
| `StateMachine` | `app/utils/state_machine.py` | Declared status transitions for invoice, order, order item, booking and employee. |
| `Common` | `app/models/Common.py` | Abstract base: `created_at/updated_at/deleted_at/is_deleted/created_by/updated_by` + `created_by_user`/`updated_by_user` relations. **Every model inherits this.** |
| `Enums` | `app/models/Enums.py` | EmploymentType, EmployeeStatus, AttendanceStatus/Session, IncentiveType, InventoryChangeType, InvoiceStatus, PaymentMethod, BookingStatus. Reuse; don't define string literals. |
| `get_db` | `app/core/database.py` | Session dependency. |
| `get_current_user` | `app/dependencies/auth.py` | JWT → User. **Authentication only, no roles.** |
| `settings` | `app/core/config.py` | Pydantic settings + `DATABASE_URL` + media paths. |
| `hash_password` / `verify_password` / `create_access_token` | `app/core/security.py` | |
| `/common/upload/document/` | `app/routes/common.py` | Shared upload endpoint → returns `doc_url`. |

**The order spine** — the part that is not CRUD:

```
MenuCategory -> MenuItem            what you sell, its price, its GST slab
Order -> OrderItem                  open -> confirmed -> served -> billed (a declared machine)
CustomerInvoice -> InvoiceLine      derived once, by OrderService.bill(), never typed
```

The verbs are endpoints, not a status field: `POST /orders/{id}/confirm` (the KOT),
`/bill`, `/cancel`, `PATCH /orders/{id}/items/{id}/status` (the pass).
`OrderService` refuses a PUT that sets `status`. Screens: `pages/OrderManagement/`
(the till + the kitchen display) and `pages/MenuManagement/`.

**The standard route shape** (`app/routes/employee_details.py` is the reference):
prefix + tag → `CRUDBase[...]` instance → `POST /` · `GET /{id}` · `GET /` (paginated+filtered) ·
`PUT /{id}` · `DELETE /{id}`, returning `{data, total, totalPages, currentPage}` for lists.

---

## 6. Conventions

- **Models**: `PascalCase.py`, class = filename, `__tablename__` snake_case plural. Register in `models/__init__.py` or Alembic won't see it.
- **Schemas/routes**: `snake_case.py`. Schema names: `XCreate`, `XUpdate`, `XOut`, `PaginatedXOut`.
- **API paths**: kebab-case plural (`/employee-details/`, `/salary-structures/`). **Trailing slash on collections.**
- **RTK Query**: one endpoint group per domain in `app/allSlices.js`, exported as `useGetXQuery` / `useCreateXMutation` / …
- **Migrations**: `alembic revision --autogenerate -m "..."` then review the diff by hand before `upgrade head`.
- **Money**: `Numeric(10,2)` in models. Never float.
- **Soft delete**: never hard-delete. Every read filters `is_deleted == False`.

---

## 7. Traps that will bite you

These are the rules whose *violation* is invisible until production, which is exactly why they
are worth reading before you start. Each one has cost real time at least once.

1. **An RTK Query tag that is not in `TAG_TYPES` is silently ignored.** No warning, no error —
   the cache simply never invalidates. Add the tag to `app/baseApi.js`; `baseApi.test.js` checks.
2. **A router mounted without a guard in `routes/__init__.py` is public.** The guard lives at the
   mount, not on the endpoint, so a new router is a visible omission there. `test_authorization.py`
   walks the live route table and fails on one.
3. **A permission module must exist in `app/utils/permissions.py::MODULES`** or the app refuses to
   start. That is deliberate: a typo would otherwise silently deny everything.
4. **The service owns the transaction.** Repositories flush. Do not add a commit inside one, and do
   not rely on `get_db` to save you — it rolls back and closes, nothing more.
5. **A derived column is never writable.** `paid_amount`, `status`, stock `quantity`, `profit` and
   an invoice's totals all return 409 if you try. Record the event instead; the column follows.
6. **A ledger is append-only.** Stock movements, audit entries and invoice lines are not editable
   and not deletable. A correction is an opposite entry.
7. **Money never touches a float.** Use `app/utils/money.py`. Bill arithmetic goes through
   `app/utils/tax.py` — there is exactly one implementation and it is tested against an auditor's
   expectations, not a developer's.
8. **An order line snapshots its price.** Never read the bill's numbers through `menu_item` — a
   price change would rewrite the past.
9. **A colour that is not a token is a defect.** `text-white`, `bg-black/50` and `border-blue-500`
   were all real bugs on real themes. Use `on-primary`, `scrim`, `primary`. `themes.test.js` proves
   the contrast; it cannot prove you used it.
10. **Enums**: `SQLEnum(..., values_callable=enum_values)` stores the *value* (`full-time`).
    A new enum column without `values_callable` stores the *name* and its filters will raise
    `LookupError`. That has happened, and it is one forgotten argument away from happening
    again.
11. **A header the SPA sends must be in `allow_headers` in `main.py`.** `TestClient` does not
    enforce CORS, so a mismatch passes every test and breaks every browser.
12. **Review an autogenerated migration by hand.** The last one proposed dropping the
    refresh-token uniqueness constraint and a performance index, and adding twelve `NOT NULL`
    columns with no default to a populated table. `alembic check` in CI keeps the models and the
    schema honest; it does not review the diff for you.

---

## 8. Definition of done

A change is done when: it reuses the existing primitives · it respects the layering · `is_deleted`
is honoured · the endpoint is authenticated and authorised · a null result returns 404 ·
`ruff check`, `ruff format --check`, `pytest` and `npm run lint && npm test` are all clean ·
**it was actually run** — not just written, and not just unit tested. Several of the worst bugs
this codebase has had were invisible to a full green test suite and obvious within a minute of
opening the app: a CORS header mismatch, a console encoding crash, a page size over the server's
limit.
