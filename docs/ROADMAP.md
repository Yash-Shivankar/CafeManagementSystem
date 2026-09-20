# ROADMAP

What is built, what is not, and what is deliberately not being built yet.

Keep this honest — `landing/index.html` makes public claims off the back of it,
and the rule there is that every claim is marked `live` or `next` and both have
to be true.

---

## Built

### The order spine
Menu sections and items with per-item GST slab and HSN. Orders for dine-in,
takeaway and delivery, with a declared lifecycle: `open → confirmed → served →
billed`. A kitchen display that sorts by who has waited longest. GST-correct
billing — CGST/SGST per slab, discount applied before tax and spread across
lines, taxable service charge, round-off as its own line, per-outlet invoice
serials per financial year. Settlement by cash, UPI or card, including part
payment. Day close that reads revenue from the payments actually recorded.

### The back office
Employees with split-shift attendance, documents, performance reviews, salary
structures carrying PF and ESI, incentives and increments — and payroll computed
from attendance rather than typed in. Inventory with categories, an append-only
movement ledger and a low-stock view. Customers, feedback, invoices and payments.
Profit and loss derived, never hand-entered.

### Underneath
Multi-outlet tenancy on every transactional table, enforced in the repository
layer rather than remembered per handler. A role/module/action permission matrix
enforced server-side and served to the SPA so both agree. JWT with a rotating
httpOnly refresh cookie and server-side revocation. An append-only audit trail
of who changed what. 613 backend tests and 168 frontend tests, with CI running
both plus a production build and a migration round-trip against real Postgres.

---

## Next

| | |
|---|---|
| **Recipes, COGS and reports** | Link a menu item to its ingredients so a sale depletes stock and margin is computed per item. `invoice_lines` already records what sold; nothing reads it yet. Then daily sales, item-wise, hourly and staff-wise, as CSV and PDF. |
| **Offline billing** | The app is entirely online. A till that dies with the wifi is not sellable to a cafe. Needs a local queue and a sync protocol — a project, not a task. |
| **Split bills** | The API takes several payments against one invoice; the till takes one tender for the full amount. |
| **Bulk menu import** | A cafe has 200 items and will not type them. `manage.py seed-menu` is a starter, not an import. |
| **Aggregator ingestion** | Zomato and Swiggy orders in the same queue as dine-in. `Order.order_type` already has `delivery`, so the shape is there. |
| **Hardware** | Thermal printer (ESC/POS), cash drawer, a wall-mounted kitchen display. |
| **Row-level scoping within an outlet** | A customer seeing only their own orders and invoices. The hook exists and sessions and the audit trail use it; nothing else does. |
| **e-invoicing** | Required above the turnover threshold. |
| **i18n** | Nothing is translated; strings are inline. |

---

## Deliberately not doing

- **Competing on feature parity with the large POS vendors.** See `BRAND.md` §3.
  The defensible ground is payroll depth and a published price, not matching a
  feature list.
- **Chains and cloud kitchens** as a target on day one.
- **Selling hardware.** It runs on the tablet and printer a cafe already owns.

---

## Known soft spots

- `mypy` runs in CI with `continue-on-error`. The codebase is not annotated end
  to end, and a gate nobody can pass is a gate everybody learns to ignore.
  Remove the flag once the backlog is clear.
- No load testing. Pagination does a full `COUNT(*)` per list request; the
  indexes are there, but nothing has been measured under a real day's volume.
- The kitchen display and the order list poll. A websocket is the right answer
  once two tills are in use at once.
