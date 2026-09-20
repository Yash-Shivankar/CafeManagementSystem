"""Architectural tests.

Layering that is only written down in a document decays. These tests read the
source and fail the build when a layer reaches somewhere it should not — which
is the only thing that keeps `routes → controllers → services → repositories →
utils` true six months from now.
"""

from __future__ import annotations

import ast
import io
import re
import tokenize
from pathlib import Path

import pytest

APP = Path(__file__).resolve().parents[1] / "app"

ROUTES = sorted(p for p in (APP / "routes").glob("*.py") if p.name != "__init__.py")
CONTROLLERS = sorted(p for p in (APP / "controllers").glob("*.py") if p.name != "__init__.py")
SERVICES = sorted(p for p in (APP / "services").glob("*.py") if p.name != "__init__.py")
REPOSITORIES = sorted(p for p in (APP / "repositories").glob("*.py") if p.name != "__init__.py")
UTILS = sorted(p for p in (APP / "utils").glob("*.py") if p.name != "__init__.py")


def code_only(path: Path) -> str:
    """Source with comments and string literals blanked out.

    Without this, a test that greps for `db.query(` would flag a *docstring*
    explaining that routes must not call `db.query(` — which is exactly the
    false positive this helper exists to prevent.
    """
    source = path.read_text(encoding="utf-8")
    out = []
    try:
        for token in tokenize.generate_tokens(io.StringIO(source).readline):
            if token.type in (tokenize.COMMENT, tokenize.STRING):
                continue
            out.append(token.string)
    except tokenize.TokenError:  # pragma: no cover - malformed file
        return source
    return " ".join(out)


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


class TestLayersExist:
    def test_every_layer_folder_is_populated(self):
        assert len(REPOSITORIES) >= 20, "repositories/ is thin"
        assert len(SERVICES) >= 20, "services/ is thin"
        assert len(CONTROLLERS) >= 20, "controllers/ is thin"
        assert len(UTILS) >= 5, "utils/ is thin"

    def test_every_entity_has_a_full_stack(self):
        """A repository with no service, or a service with no controller, is a
        half-finished migration. Name them and fail."""
        repos = {p.stem.replace("Repository", "") for p in REPOSITORIES} - {"base"}
        services = {p.stem.replace("Service", "") for p in SERVICES} - {"base"}
        controllers = {p.stem.replace("Controller", "") for p in CONTROLLERS} - {"base"}

        services -= {"auth"}

        assert not (repos - services), f"repositories without a service: {repos - services}"
        assert not (services - controllers), (
            f"services without a controller: {services - controllers}"
        )


class TestDependencyDirection:
    @pytest.mark.parametrize("path", SERVICES, ids=lambda p: p.name)
    def test_services_do_not_import_fastapi(self, path):
        """A service that imports FastAPI cannot be called from a Typer command
        or a scheduled job without dragging HTTP along."""
        offending = {m for m in imported_modules(path) if m.split(".")[0] == "fastapi"}
        assert not offending, f"{path.name} imports {offending}"

    @pytest.mark.parametrize("path", SERVICES, ids=lambda p: p.name)
    def test_services_do_not_import_routes_or_controllers(self, path):
        offending = {
            m
            for m in imported_modules(path)
            if m.startswith("app.routes") or m.startswith("app.controllers")
        }
        assert not offending, f"{path.name} imports {offending}"

    @pytest.mark.parametrize("path", REPOSITORIES, ids=lambda p: p.name)
    def test_repositories_only_look_downwards(self, path):
        offending = {
            m
            for m in imported_modules(path)
            if m.startswith("app.routes")
            or m.startswith("app.controllers")
            or m.startswith("app.services")
            or m.split(".")[0] == "fastapi"
        }
        assert not offending, f"{path.name} imports {offending}"

    @pytest.mark.parametrize("path", UTILS, ids=lambda p: p.name)
    def test_utils_import_nothing_from_the_layers_above(self, path):
        offending = {
            m
            for m in imported_modules(path)
            if m.startswith("app.routes")
            or m.startswith("app.controllers")
            or m.startswith("app.services")
            or m.startswith("app.repositories")
        }
        assert not offending, f"{path.name} imports {offending}"


class TestRoutesAreThin:
    @pytest.mark.parametrize("path", ROUTES, ids=lambda p: p.name)
    def test_no_route_queries_the_database(self, path):
        """A `db.query(` in a route file means data access has leaked back up
        out of the repository."""
        assert "db.query(" not in code_only(path), f"{path.name} queries the database directly"

    @pytest.mark.parametrize("path", ROUTES, ids=lambda p: p.name)
    def test_no_route_uses_the_deprecated_crud_base(self, path):
        assert not any(m.startswith("app.crud") for m in imported_modules(path)), (
            f"{path.name} still imports the deprecated CRUDBase"
        )

    @pytest.mark.parametrize("path", ROUTES, ids=lambda p: p.name)
    def test_no_route_recomputes_pagination(self, path):
        """The `(page - 1) * limit` / `ceil(total / limit)` block existed in 22
        files. It now exists in `app/utils/pagination.py` and nowhere else."""
        source = code_only(path)
        assert "ceil" not in source, f"{path.name} still does pagination maths"
        assert "page - 1" not in source, f"{path.name} still computes skip"

    def test_route_files_are_actually_smaller(self):
        """A refactor that moves code around without removing any is not a
        refactor. Route files should read as a table of contents."""
        oversized = {
            p.name: len(p.read_text(encoding="utf-8").splitlines())
            for p in ROUTES
            if len(p.read_text(encoding="utf-8").splitlines()) > 130
        }
        oversized.pop("auth.py", None)
        assert not oversized, f"route files still carrying weight: {oversized}"

    @pytest.mark.parametrize("path", ROUTES, ids=lambda p: p.name)
    def test_no_commented_out_dead_endpoints(self, path):
        """20 route files carried a commented-out older version of the list
        endpoint. Dead code that looks live is worse than no code."""
        dead = re.findall(r"^\s*#\s*@router\.", path.read_text(encoding="utf-8"), re.M)
        assert not dead, f"{path.name} has {len(dead)} commented-out endpoint(s)"


class TestTransactionOwnership:
    @pytest.mark.parametrize("path", REPOSITORIES, ids=lambda p: p.name)
    def test_repositories_never_commit(self, path):
        """the repository flushes; the service commits. A commit down
        here is what made multi-write use-cases impossible to roll back."""
        assert ".commit(" not in code_only(path), f"{path.name} commits"

    def test_get_db_does_not_commit(self):
        source = code_only(APP / "core" / "database.py")
        assert "db . commit" not in source and "db.commit" not in source, (
            "get_db() commits again — that commit would run after the response "
            "has already been sent to the client"
        )
