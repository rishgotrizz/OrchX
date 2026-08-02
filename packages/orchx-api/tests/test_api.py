import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_api_healthz(client: AsyncClient):
    response = await client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "online"}


@pytest.mark.asyncio
async def test_auth_routes(client: AsyncClient):
    # Register workspace user
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "architect@orchx.ai", "password": "kernelpassword"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "architect@orchx.ai"

    # Authenticate and receive JWT
    response_login = await client.post(
        "/api/v1/auth/login",
        data={"username": "architect@orchx.ai", "password": "kernelpassword"},
    )
    assert response_login.status_code == 200
    token_data = response_login.json()
    assert "access_token" in token_data

    # Query current session profile
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response_me = await client.get("/api/v1/auth/me", headers=headers)
    assert response_me.status_code == 200
    assert response_me.json()["email"] == "architect@orchx.ai"


@pytest.mark.asyncio
async def test_dashboard_stats_and_plugins(client: AsyncClient):
    # Register first
    await client.post(
        "/api/v1/auth/register",
        json={"email": "diag@orchx.ai", "password": "securepassword"},
    )
    response_login = await client.post(
        "/api/v1/auth/login",
        data={"username": "diag@orchx.ai", "password": "securepassword"},
    )
    token = response_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch dynamic loaded plugin registry items
    response_plugins = await client.get("/api/v1/plugins/", headers=headers)
    assert response_plugins.status_code == 200
    assert isinstance(response_plugins.json(), list)

    # Fetch minimized diagnostics metrics
    response_stats = await client.get("/api/v1/dashboard/stats", headers=headers)
    assert response_stats.status_code == 200
    stats_data = response_stats.json()
    assert stats_data["status"] in ("healthy", "degraded", "unhealthy")
    assert stats_data["version"] == "0.1.0"
    assert "uptime" in stats_data
