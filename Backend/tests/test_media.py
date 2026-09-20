"""/media/ was a public StaticFiles mount over employee ID documents."""

import time

import pytest

from app.utils.media import (
    UnsafeMediaPath,
    resolve_media_path,
    sign_media_path,
    verify_media_signature,
)

SECRET_FILE = "documents/pdf/employee-pan-card.pdf"
SECRET_BODY = b"%PDF-1.4 pretend this is an employee ID document"


@pytest.fixture
def stored_document(media_root):
    path = media_root / SECRET_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(SECRET_BODY)
    return SECRET_FILE


class TestPathSafety:
    def test_traversal_is_refused(self):
        with pytest.raises(UnsafeMediaPath):
            resolve_media_path("../../../etc/passwd")

    def test_absolute_path_cannot_escape_the_media_root(self, media_root):
        """A leading slash is stripped, so `/etc/passwd` resolves to
        `<media_root>/etc/passwd` — contained, and simply not found."""
        resolved = resolve_media_path("/etc/passwd")
        assert str(resolved).startswith(str(media_root.resolve()))

    def test_windows_style_traversal_is_refused(self):
        with pytest.raises(UnsafeMediaPath):
            resolve_media_path("..\\..\\windows\\system32\\config\\sam")

    def test_normal_path_resolves(self, media_root):
        resolved = resolve_media_path("documents/pdf/x.pdf")
        assert str(resolved).startswith(str(media_root.resolve()))


class TestSignatures:
    def test_signature_roundtrip(self):
        sig, exp = sign_media_path(SECRET_FILE)
        assert verify_media_signature(SECRET_FILE, sig, exp)

    def test_signature_is_bound_to_its_path(self):
        """A signature for one file must not unlock another."""
        sig, exp = sign_media_path(SECRET_FILE)
        assert not verify_media_signature("documents/pdf/other.pdf", sig, exp)

    def test_expired_signature_is_rejected(self):
        sig, _ = sign_media_path(SECRET_FILE)
        assert not verify_media_signature(SECRET_FILE, sig, int(time.time()) - 1)

    def test_forged_signature_is_rejected(self):
        _, exp = sign_media_path(SECRET_FILE)
        assert not verify_media_signature(SECRET_FILE, "A" * 43, exp)


class TestMediaEndpoint:
    def test_anonymous_download_is_refused(self, client, stored_document):
        """This is the exact request that used to return the PDF."""
        response = client.get(f"/media/{stored_document}")
        assert response.status_code == 403

    def test_bearer_token_is_accepted(self, client, login, stored_document):
        response = client.get(f"/media/{stored_document}", headers=login("Manager"))
        assert response.status_code == 200
        assert response.content == SECRET_BODY

    def test_signed_url_is_accepted(self, client, stored_document):
        sig, exp = sign_media_path(stored_document)
        response = client.get(f"/media/{stored_document}?sig={sig}&exp={exp}")
        assert response.status_code == 200
        assert response.content == SECRET_BODY

    def test_expired_signed_url_is_refused(self, client, stored_document):
        sig, _ = sign_media_path(stored_document)
        stale = int(time.time()) - 60
        response = client.get(f"/media/{stored_document}?sig={sig}&exp={stale}")
        assert response.status_code == 403

    def test_uploads_are_never_rendered_inline(self, client, login, stored_document):
        """A crafted SVG or HTML upload would otherwise execute on our origin."""
        response = client.get(f"/media/{stored_document}", headers=login("Manager"))
        assert response.headers["content-disposition"].startswith("attachment")
        assert response.headers["x-content-type-options"] == "nosniff"

    def test_missing_file_is_404_for_an_authorised_caller(self, client, login):
        response = client.get("/media/documents/pdf/nope.pdf", headers=login("Manager"))
        assert response.status_code == 404

    def test_mint_signed_url_requires_permission(self, client, login, stored_document):
        response = client.post(
            "/api/v1/common/media-url",
            headers=login("Manager"),
            json={"path": stored_document},
        )
        assert response.status_code == 200, response.text
        assert response.json()["url"].startswith("/media/")

    def test_mint_signed_url_is_closed_to_anonymous(self, client, stored_document):
        response = client.post("/api/v1/common/media-url", json={"path": stored_document})
        assert response.status_code == 401
