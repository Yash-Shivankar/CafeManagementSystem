"""Cross-cutting helpers with no knowledge of the domain.

Nothing in this package may import from `app.routes`, `app.controllers`,
`app.services` or `app.repositories` — utils sit at the bottom of the
dependency graph so that every layer above can use them freely.
"""
