# landing/ — the Caelum marketing site

One static page. No build step, no framework, no dependencies: open
`index.html` and it works.

**Why it is not a route in `Frontend/`**: it has to load fast for a stranger on
a mid-range phone, deploy independently of the product, and survive the app
being rebuilt. Bundling it behind Vite buys nothing and costs all three.

The copy, palette, typography and voice are decided in `../BRAND.md`. Read that
before changing a word of it — particularly §5, whose test is *"could a
competitor put their name on this sentence?"*

---

## Preview it

```bash
python -m http.server 4173 --directory landing
```

Then open <http://localhost:4173>. Any static server will do; the page has no
API of its own.

---

## Before it goes live

Four things, in the order they will bite you.

### 1. Wire the form

`ENDPOINT` at the top of the `<script>` in `index.html` is an empty string, and
the form says so out loud rather than pretending to succeed. A form that
silently swallows leads is the worst possible default — you find out months
later, from the silence.

Set it to anything that accepts a `POST` of JSON:

```js
var ENDPOINT = "https://formspree.io/f/xxxxxxx";
```

It posts `{cafe, city, seats, phone}`. Formspree, Basin, a Cloudflare Worker or
your own endpoint all work unchanged.

### 2. Confirm the price

`₹1,999/outlet/month` is a **proposal** from `BRAND.md` §3, not a decision. It
appears in four places on the page and once in the meta description. Open
question 2 in `BRAND.md` still stands: does that number survive your own time
being worth something, once you are supporting twenty cafes yourself?

### 3. Point the domain at it

`caelum.cafe` is a placeholder and **nothing is registered**. It appears in the
canonical link, the Open Graph URL, `robots.txt`, `sitemap.xml` and the contact
address. Search and replace it once the real domain exists.

### 4. Add a social preview image

The Open Graph tags are in place but there is no `og:image`. Most platforms
will not render an SVG for one, so this needs a 1200×630 PNG — then:

```html
<meta property="og:image" content="https://caelum.cafe/og.png">
<meta property="twitter:image" content="https://caelum.cafe/og.png">
```

Until it exists, a shared link renders as plain text. That is a real cost on
WhatsApp, which is where this link will actually travel.

---

## The honesty rule

`BRAND.md` §3 makes this non-negotiable: **every claim is marked `live` or
`next`, and both have to be true.**

It cuts in both directions. This page was first written when the POS half did
not exist, and it said so. Building it made the page *understate* the product —
a "next" on something that ships today is as wrong as a "live" on something
that doesn't.

Every claim on the page was checked against the code before it was written.
Some deliberately stayed in "next" even though a column for them exists:

| Claimed | Reality |
|---|---|
| Menu, orders, KOT, GST billing, part payment, day close | live — `Backend/app/services/orderService.py`, `utils/tax.py` |
| Split-shift attendance, PF & ESI, incentives, increments, documents | live |
| Inventory movement ledger, low-stock | live |
| Multi-outlet | live |
| Recipes → COGS | **next** — nothing links a menu item to an ingredient yet |
| Reports and exports | **next** — `invoice_lines` makes them possible; nothing reads it |
| Split bills | **next** — the API takes several payments per invoice; the till takes one |
| Offline billing | **next** — the app is entirely online |
| Aggregators, printer, cash drawer, e-invoicing | **next** |

Two claims were removed rather than downgraded, because the words promised more
than the code does: "modifiers" (order lines carry free-text notes, not
structured modifiers) and "a Z-report you can hand to your accountant" (day
close derives revenue and profit; it is not a till reconciliation).

When you ship something on that list, move it — and move it in the page's own
roadmap section too, and in `../docs/ROADMAP.md`. Same information, three
places, and they have to agree.

---

## Deploy

It is four static files. Netlify, Cloudflare Pages, GitHub Pages, S3, or nginx:

```
landing/
├── index.html
├── favicon.svg
├── robots.txt
└── sitemap.xml
```

No build command. Publish directory: `landing`.
