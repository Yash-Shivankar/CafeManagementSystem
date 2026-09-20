"""Deprecated — kept so nothing breaks while the last references are removed.

`CRUDBase` has become `app.repositories.baseRepository.BaseRepository`
(decision the class was good reuse; the problem was that routes called
it directly). Two things changed in the move:

* it is constructed with a Session instead of taking one per call, and
* it does not commit — services own the transaction now.

Nothing in the application imports this module any more. It is here only so an
external script or notebook of yours does not break on the next `git pull`.
Delete `app/crud/` once you are sure nothing outside this repo uses it.
"""

import warnings

from app.repositories.baseRepository import BaseRepository

warnings.warn(
    "app.crud.base.CRUDBase is deprecated; use "
    "app.repositories.baseRepository.BaseRepository instead.",
    DeprecationWarning,
    stacklevel=2,
)

CRUDBase = BaseRepository

__all__ = ["CRUDBase", "BaseRepository"]
