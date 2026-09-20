# BRAND.md — Caelum positioning & identity

Decided 2026-09-14. Grounded in market research, not preference. Change it deliberately, and
say in the commit why.

---

## 1. The conflict this resolves

Before this decision the brand said two different things:

| Asset | Says |
|---|---|
| `Frontend/public/icon.svg` | *"Caelum Coffee Roasters"* — a coffee cup with steam, moon and star, brown `#4b2e20` on cream `#f2e8d5` |
| App theme (`mysticForest`) | Forest green `#22C55E` family |
| `index.html` / Navbar | "Caelum" as the software product |

Two problems. The palettes disagree outright. And more seriously, **a coffee cup is a cafe's logo,
not a cafe software's logo** — a cafe owner who sees one reads you as a coffee brand competing with
them, not a tool serving them.

**Decision:** keep the name, replace the mark, commit to green.

---

## 2. Name

**Caelum** stays. Two reasons beyond inertia:

1. It's already in the product title, the navbar and the tab. Renaming now buys nothing.
2. It has a second meaning that fits a tool far better than the celestial one. The constellation
   *Caelum* is **Caelum Scalptorium — the engraver's chisel**. A small, sharp instrument in the
   hands of someone who makes things. That is exactly what a POS is to a cafe owner, and it gives
   the brand a story that isn't generic.

The tagline carries the category, since the name doesn't: **Caelum for cafes**.

---

## 3. Positioning

> **Food cost. Labour cost. One system.**

### The gap, from research

Petpooja, Restroworks (Posist), UrbanPiper and DotPe all compete on the same axis: billing,
inventory, aggregators. Two openings are real and defensible:

**Opening 1 — nobody runs the staff.** A cafe's two controllable costs are what it buys and who it
pays. Every incumbent helps with the first and ignores the second. Caelum's HR module — split-shift
attendance, documents, performance, salary structure with PF/ESI, incentives, increments — is
already deeper than most cafe POS. That is an accident of how this codebase grew, and it is the
sharpest thing about it. **Lead with it.**

**Opening 2 — the price is a secret.** Research on the Indian market shows the recurring complaints
are opaque pricing (a demo booking instead of a number), add-on creep (loyalty, online ordering and
WhatsApp each billed separately), annual lock-in, hardware dependency, renewal increases of 10–20%,
and interfaces built for chains being sold to single cafes. First-year total commonly lands at
₹1.5–2.3 lakh.

**So: one price, on the page, everything included, monthly.** A published number is a positioning
weapon a solo founder can actually wield, and it costs nothing to deploy.

### Pricing (proposal)

- **₹1,999 / month per outlet**, + 18% GST, billed monthly, cancel any month → **₹23,988** year one
- Second outlet onward ₹1,499
- No setup fee, no add-on modules, full data export, runs on hardware you own

### Honesty constraint — non-negotiable

Every claim must be marked **live** or **next**, and the page carries an explicit early-access
banner. This is not a compromise; for a founder selling to twenty people it is better marketing
than a polished lie, and a roadmap is a reason for founding cafes to talk to you.

*Written Sep 14, when the POS half did not exist at all.* It does now — billing, KOT, GST
invoicing and settlement shipped on Sep 19 — and the constraint did not soften, it just changed
direction: the page had to be corrected for **understating** the product. Recipes and COGS,
reports, split bills, offline billing and aggregators are still `next`, and they stay marked that
way until they are not. See §6.

### Who this is not for

Chains, cloud kitchens, and anyone who needs aggregator integration on day one. Say so.

---

## 4. Visual identity

### Palette

Dominant **deep evergreen**, one **warm accent** used only on figures. Deliberately *not*
cream-and-terracotta — the default cafe look, and the one every template site
reaches for. Green also distances Caelum from the orange/red that most Indian food-tech uses, and
keeps continuity with the app's existing `mysticForest` theme.

| Token | Light | Dark | Role |
|---|---|---|---|
| `--forest` | `#0E4433` | `#0B3427` | hero and feature blocks — the brand color |
| `--forest-2` | `#0A3527` | `#07261C` | deepest ground |
| `--forest-ink` | `#EFF6F0` | `#EAF3EC` | text on forest |
| `--forest-dim` | `#9DBCAC` | `#8FB2A1` | secondary text on forest |
| `--leaf` | `#1C7A54` | `#4FBE8C` | interactive: links, buttons, ticks |
| `--saffron` | `#A85F10` | `#DFA45E` | **one** warm note — figures and "next" tags only |
| `--ground` | `#F2F5F1` | `#0A0F0C` | page ground (cool paper, green-biased) |
| `--ink` | `#0F1712` | `#EBF1E9` | body text |

Neutrals are green-biased, never pure grey.

### Typography

| Role | Face | Why |
|---|---|---|
| Display | **Bricolage Grotesque** 700/800 | Mixed widths and slightly irregular terminals — hand-built, not corporate. An indie product taking on Petpooja should not look like Petpooja. |
| Body | **Public Sans** 400/600 | Plain-spoken and highly legible on a mid-range Android in daylight, which is where this gets read. |
| Data | **IBM Plex Mono** | Figures, labels, eyebrows. Tabular numerals wherever money lines up. |

Deliberately **not** Inter or Space Grotesk — the two faces every generated page defaults to.

### Mark

Square frame, a tapered chisel blade, a struck line beneath it. Reads as a chisel and as a counter
edge. Abstract, one colour, works at 16px. **No coffee cup, no steam, no crescent moon.**

### Layout principles

- Square corners. No `border-radius` anywhere — it reads as an instrument, not an app-store icon.
- Hairline dividers between cells, not a drop shadow on every card.
- Structural numbering only where order is real (the recipe → margin chain, the roadmap).
- A dashed "tear line" rule, borrowed from a thermal receipt — used twice on the whole page, not as wallpaper.
- Every comparison drawn to true scale. The cost bars are 100% vs 13% because that is the actual ratio.

---

## 5. Voice

Plain, specific, unhurried. Name real things — covers, the 8:40 rush, PF and ESI, a Z-report, the
paper register. No exclamation marks, no "revolutionise", no emoji.

Test for any sentence: **could a competitor put their name on it?** If yes, rewrite it.

- **Yes:** "Every cafe POS in India tracks what you buy. Caelum also runs who you pay."
- **No:** "The all-in-one solution for modern cafes."

---

## 6. Artefacts

- **`landing/`** — the live site. One static page, no build step, no dependencies. Preview with
  `python -m http.server 4173 --directory landing`. Deployment notes and the four things to do
  before it goes public are in `landing/README.md`.
- `Frontend/` is untouched. The page stays outside the React app: it must load fast for a
  stranger on a mid-range phone, deploy independently of the product, and survive the app being
  rebuilt. Bundling it behind Vite costs all three and buys nothing.

### Keeping the claims true

The honesty rule in §3 has a maintenance cost, and it is the point rather than the price. When a
roadmap row ships, **three** places on the page change together: the `live`/`next` tag on the
feature, the roadmap row itself, and the early-access banner at the top. The table in
`landing/README.md` records what was verified against the code and when.

It cuts in both directions. The page was first written when the POS half did not exist and said
so plainly. Once billing, KOT and GST invoicing shipped, the same page was *understating* the
product — a `next` on something that works today is exactly as wrong as a `live` on something
that does not.

## 7. Open questions

Unresolved, and each one blocks something concrete.

1. **Is Caelum the software or the cafe?** The old icon said "Caelum Coffee Roasters". If the
   name belongs to a cafe, the software needs its own and this whole document moves.
2. **Is ₹1,999 sustainable** at twenty cafes supported by one person? Cheap is a wedge, not a
   business. The price has to survive the support load it creates.
3. **Domain and entity** — `caelum.cafe` is a placeholder and nothing is registered. It appears
   in five places in `landing/` (canonical, og:url, robots.txt, sitemap.xml, the contact
   address), so registering it is the change that unblocks publishing.
4. **Where does the early-access form post?** `landing/` ships with no endpoint wired, and the form
   says so rather than pretending to succeed — a form that silently swallows leads is discovered
   months later, from the silence. Any endpoint that accepts a JSON POST will do.
