"""Request handling. Controllers sit between a route and a service.

A controller turns HTTP-shaped input (query parameters, path ids, a validated
body) into a service call, and turns the result back into the response envelope
the API promises. It holds no business rules — if a decision is being made, it
belongs one layer down in `app/services/`.

Controllers are FastAPI dependencies: a route declares
`controller: DepartmentController = Depends()` and gets one already wired to the
request's session and current user.
"""

from app.controllers.baseController import BaseController

__all__ = ["BaseController"]
