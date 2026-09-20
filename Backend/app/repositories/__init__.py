"""Data access. Every SQLAlchemy query in the application lives in this package.

A repository is constructed with a Session and never commits — it `flush()`es so
the caller can read generated ids, and leaves the transaction boundary to the
service. That is the whole point: a data-access class that commits inside
`create`, `update` and `remove` leaves a service that wrote three rows and
failed on the fourth with the first three already saved and no way to undo
them.
"""

from app.repositories.baseRepository import BaseRepository

__all__ = ["BaseRepository"]
