"""Authentication: tokens, registration, refresh rotation and rate limiting."""

from datetime import timedelta

import pytest

from app.core.security import (
    TOKEN_TYPE_ACCESS,
    TOKEN_TYPE_REFRESH,
    TokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_is_not_the_password(self):
        hashed = hash_password("hunter2")
        assert hashed != "hunter2"
        assert hashed.startswith("$argon2")

    def test_verify_roundtrip(self):
        hashed = hash_password("hunter2")
        assert verify_password("hunter2", hashed)
        assert not verify_password("hunter3", hashed)

    def test_verify_against_empty_hash_is_false(self):
        assert not verify_password("anything", "")
        assert not verify_password("anything", None)


class TestTokens:
    def test_access_token_roundtrip(self):
        token = create_access_token(subject=7, role="Admin")
        payload = decode_token(token, expected_type=TOKEN_TYPE_ACCESS)
        assert payload["sub"] == "7"
        assert payload["role"] == "Admin"
        assert payload["typ"] == TOKEN_TYPE_ACCESS
        assert payload["jti"]

    def test_access_token_rejected_where_refresh_expected(self):
        """token type confusion. An access token must never be usable
        as a refresh token, or a 60-minute credential becomes a 30-day one."""
        token = create_access_token(subject=7, role="Admin")
        with pytest.raises(TokenError):
            decode_token(token, expected_type=TOKEN_TYPE_REFRESH)

    def test_refresh_token_rejected_where_access_expected(self):
        token, _, _ = create_refresh_token(subject=7)
        with pytest.raises(TokenError):
            decode_token(token, expected_type=TOKEN_TYPE_ACCESS)

    def test_expired_token_rejected(self):
        token = create_access_token(subject=7, role="Admin", expires_delta=timedelta(seconds=-10))
        with pytest.raises(TokenError):
            decode_token(token)

    def test_tampered_token_rejected(self):
        token = create_access_token(subject=7, role="Staff")
        head, payload, sig = token.split(".")
        forged = f"{head}.{payload}.{'A' * len(sig)}"
        with pytest.raises(TokenError):
            decode_token(forged)

    def test_unsigned_alg_none_token_rejected(self):
        """The classic JWT bypass: re-sign with alg=none."""
        import base64
        import json

        def b64(data: dict) -> str:
            raw = json.dumps(data).encode()
            return base64.urlsafe_b64encode(raw).decode().rstrip("=")

        forged = (
            f"{b64({'alg': 'none', 'typ': 'JWT'})}."
            f"{b64({'sub': '1', 'typ': 'access', 'role': 'SuperAdmin'})}."
        )
        with pytest.raises(TokenError):
            decode_token(forged)


class TestRegistration:
    def test_register_returns_token_and_user(self, client):
        """the old handler declared response_model=TokenSchema but
        returned no `user`, so every successful registration 500'd."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "first_name": "Walk",
                "last_name": "In",
                "email": "walkin@caelum-qa.com",
                "password": "Sup3rSecret!",
            },
        )
        assert response.status_code == 201, response.text
        body = response.json()
        assert body["access_token"]
        assert body["user"]["email"] == "walkin@caelum-qa.com"

    def test_register_always_creates_a_customer(self, client):
        """the headline privilege escalation."""
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "sneaky@caelum-qa.com", "password": "Sup3rSecret!"},
        )
        assert response.status_code == 201
        assert response.json()["user"]["role"] == "Customer"

    def test_register_rejects_a_role_id_outright(self, client):
        """`extra="forbid"` means an attacker gets a 422, not a silent
        ignore — so a client sending role_id learns it is not supported."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "attacker@caelum-qa.com",
                "password": "Sup3rSecret!",
                "role_id": 1,
            },
        )
        assert response.status_code == 422

    def test_register_rejects_weak_password(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "weak@caelum-qa.com", "password": "short"},
        )
        assert response.status_code == 422

    def test_register_rejects_duplicate(self, client):
        payload = {"email": "dupe@caelum-qa.com", "password": "Sup3rSecret!"}
        assert client.post("/api/v1/auth/register", json=payload).status_code == 201
        second = client.post("/api/v1/auth/register", json=payload)
        assert second.status_code == 400

    def test_register_requires_an_identifier(self, client):
        response = client.post("/api/v1/auth/register", json={"password": "Sup3rSecret!"})
        assert response.status_code == 422


class TestLogin:
    def test_login_succeeds_and_sets_refresh_cookie(self, client, make_user):
        user = make_user("Admin")
        response = client.post(
            "/api/v1/auth/login",
            json={"email": user.email, "password": "Sup3rSecret!"},
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["user"]["role"] == "Admin"
        assert "caelum_refresh" in response.cookies
        assert body["user"]["permissions"]["users"]

    def test_login_with_wrong_password_is_401(self, client, make_user):
        user = make_user("Admin")
        response = client.post(
            "/api/v1/auth/login",
            json={"email": user.email, "password": "wrong-password"},
        )
        assert response.status_code == 401

    def test_login_for_unknown_user_is_401_not_404(self, client):
        """A 404 here would turn the endpoint into a user-enumeration oracle."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@caelum-qa.com", "password": "whatever"},
        )
        assert response.status_code == 401

    def test_inactive_user_cannot_log_in(self, client, make_user):
        user = make_user("Staff", is_active=False)
        response = client.post(
            "/api/v1/auth/login",
            json={"email": user.email, "password": "Sup3rSecret!"},
        )
        assert response.status_code == 401

    def test_login_is_rate_limited(self, client, make_user):
        """Without this, login can be hammered indefinitely."""
        user = make_user("Admin")
        codes = []
        for _ in range(8):
            codes.append(
                client.post(
                    "/api/v1/auth/login",
                    json={"email": user.email, "password": "wrong"},
                ).status_code
            )
        assert 429 in codes, codes
        assert codes.count(401) <= 5

    def test_successful_login_clears_the_counter(self, client, make_user):
        user = make_user("Admin")
        for _ in range(3):
            client.post(
                "/api/v1/auth/login",
                json={"email": user.email, "password": "wrong"},
            )
        good = client.post(
            "/api/v1/auth/login",
            json={"email": user.email, "password": "Sup3rSecret!"},
        )
        assert good.status_code == 200
        again = client.post(
            "/api/v1/auth/login",
            json={"email": user.email, "password": "Sup3rSecret!"},
        )
        assert again.status_code == 200


class TestSession:
    def test_refresh_rotates_the_token(self, client, make_user):
        user = make_user("Manager")
        first = client.post(
            "/api/v1/auth/login",
            json={"email": user.email, "password": "Sup3rSecret!"},
        )
        original_cookie = first.cookies["caelum_refresh"]

        refreshed = client.post("/api/v1/auth/refresh")
        assert refreshed.status_code == 200, refreshed.text
        assert refreshed.cookies["caelum_refresh"] != original_cookie

    def test_replaying_a_rotated_refresh_token_kills_the_session(self, client, make_user):
        """Rotation only helps if replay is *detected*. Presenting an already
        rotated jti means someone has a copy, so the whole family dies."""
        user = make_user("Manager")
        login = client.post(
            "/api/v1/auth/login",
            json={"email": user.email, "password": "Sup3rSecret!"},
        )
        stolen = login.cookies["caelum_refresh"]

        assert client.post("/api/v1/auth/refresh").status_code == 200
        rotated_cookie = client.cookies["caelum_refresh"]

        client.cookies.clear()
        replay = client.post("/api/v1/auth/refresh", json={"refresh_token": stolen})
        assert replay.status_code == 401

        client.cookies.clear()
        assert (
            client.post("/api/v1/auth/refresh", json={"refresh_token": rotated_cookie}).status_code
            == 401
        )

    def test_logout_revokes_the_refresh_token(self, client, make_user):
        user = make_user("Staff")
        client.post(
            "/api/v1/auth/login",
            json={"email": user.email, "password": "Sup3rSecret!"},
        )
        assert client.post("/api/v1/auth/logout").status_code == 200
        assert client.post("/api/v1/auth/refresh").status_code == 401

    def test_refresh_without_a_token_is_401(self, client):
        assert client.post("/api/v1/auth/refresh").status_code == 401

    def test_me_returns_the_current_user(self, client, login):
        headers = login("Admin")
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        assert response.json()["role"] == "Admin"

    def test_swagger_form_login_works(self, client, make_user):
        """tokenUrl used to point at the JSON endpoint, so the Swagger
        Authorize button could never actually obtain a token."""
        user = make_user("Admin")
        response = client.post(
            "/api/v1/auth/token",
            data={"username": user.email, "password": "Sup3rSecret!"},
        )
        assert response.status_code == 200, response.text
        assert response.json()["access_token"]
