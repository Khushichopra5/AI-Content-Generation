import pytest

from apps.authentication.models import APIToken, User


@pytest.mark.django_db
def test_register_login_me_and_token_lifecycle(api_client):
    register_response = api_client.post(
        "/api/v1/auth/register/",
        {
            "email": "new@example.com",
            "name": "New User",
            "password": "StrongPass123!",
        },
        format="json",
    )
    assert register_response.status_code == 201
    issued_token = register_response.json()["token"]

    me_client = api_client
    me_client.credentials(HTTP_AUTHORIZATION=f"Bearer {issued_token}")
    me_response = me_client.get("/api/v1/auth/me/")
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "new@example.com"

    login_response = api_client.post(
        "/api/v1/auth/login/",
        {
            "email": "new@example.com",
            "password": "StrongPass123!",
            "token_name": "cli",
        },
        format="json",
    )
    assert login_response.status_code == 200
    assert login_response.json()["user"]["email"] == "new@example.com"

    token_create_response = me_client.post(
        "/api/v1/auth/tokens/",
        {"name": "secondary"},
        format="json",
    )
    assert token_create_response.status_code == 201
    token_record_id = token_create_response.json()["token_record"]["id"]

    revoke_response = me_client.post(f"/api/v1/auth/tokens/{token_record_id}/revoke/")
    assert revoke_response.status_code == 200
    assert revoke_response.json()["revoked_at"] is not None

    logout_response = me_client.post("/api/v1/auth/logout/")
    assert logout_response.status_code == 204


@pytest.mark.django_db
def test_registration_is_throttled(api_client, settings):
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["anon"] = "1/min"

    first = api_client.post(
        "/api/v1/auth/register/",
        {
            "email": "first@example.com",
            "name": "First",
            "password": "StrongPass123!",
        },
        format="json",
    )
    second = api_client.post(
        "/api/v1/auth/register/",
        {
            "email": "second@example.com",
            "name": "Second",
            "password": "StrongPass123!",
        },
        format="json",
    )

    assert first.status_code == 201
    assert second.status_code == 429


@pytest.mark.django_db
def test_bearer_token_auth_rejects_revoked_token(api_client, user: User):
    issued = APIToken.issue_for_user(user, name="revoked")
    issued.token.revoke()

    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {issued.key}")
    response = api_client.get("/api/v1/auth/me/")

    assert response.status_code == 403
