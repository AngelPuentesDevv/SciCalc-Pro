"""
E2E test fixtures for SciCalcPro.

Requirements:
- DATABASE_URL env var must point to a real PostgreSQL instance.
- Google Chrome must be installed; webdriver-manager downloads ChromeDriver automatically.
- Run with: pytest tests/e2e/ -m e2e
"""
import sys
import asyncio

# Must be set before any asyncio/uvicorn import on Windows.
# asyncpg 0.31.x requires SelectorEventLoop; ProactorEventLoop (Windows default) breaks
# SCRAM-SHA-256 authentication and manifests as InvalidPasswordError.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import threading
import time

import httpx
import pytest
import uvicorn
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "http://127.0.0.1:8001"
E2E_EMAIL = "e2e_user@scicalc.test"
E2E_PASSWORD = "E2eTest1!"
E2E_NAME = "E2E User"


# ── Live server ───────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def live_server():
    """
    Start the FastAPI app in a background daemon thread on port 8001.
    DATABASE_URL must be set in the environment before running E2E tests.
    """
    config = uvicorn.Config(
        "src.main:app",
        host="127.0.0.1",
        port=8001,
        log_level="warning",
    )
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    # Wait until the server is ready (max 10 seconds)
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            httpx.get(f"{BASE_URL}/health", timeout=1)
            break
        except Exception:
            time.sleep(0.2)

    yield BASE_URL

    server.should_exit = True
    thread.join(timeout=5)


# ── WebDriver ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def driver(live_server):
    """
    Headless Chrome WebDriver — fresh instance per test for full isolation.
    """
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")

    d = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=opts,
    )
    yield d
    d.quit()


# ── E2E user ──────────────────────────────────────────────────────────────────

# Shared mutable state so e2e_user teardown can use the auth token
_e2e_user_state: dict = {}


@pytest.fixture(scope="session")
def e2e_user(live_server):
    """
    Register a dedicated test user at session start, delete at session end.
    Uses the REST API directly (no direct DB access).
    """
    with httpx.Client(base_url=live_server) as client:
        # Register
        params = {
            "email": E2E_EMAIL,
            "password": E2E_PASSWORD,
            "display_name": E2E_NAME,
        }
        reg_response = client.post("/api/v1/auth/register", params=params)
        # Accept 201 (created) or 400 (already exists from a previous interrupted run)
        if reg_response.status_code == 201:
            user_id = reg_response.json()["id"]
        else:
            # User already exists — log in to retrieve id
            login_data = {"username": E2E_EMAIL, "password": E2E_PASSWORD}
            tok_response = client.post(
                "/api/v1/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            tok_response.raise_for_status()
            token = tok_response.json()["access_token"]
            me = client.get(
                "/api/v1/users/me",
                headers={"Authorization": f"Bearer {token}"},
            )
            me.raise_for_status()
            user_id = me.json()["user_id"]

        # Login to get a token for teardown
        login_data = {"username": E2E_EMAIL, "password": E2E_PASSWORD}
        tok_response = client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        tok_response.raise_for_status()
        access_token = tok_response.json()["access_token"]

        _e2e_user_state["user_id"] = user_id
        _e2e_user_state["access_token"] = access_token

    yield {
        "email": E2E_EMAIL,
        "password": E2E_PASSWORD,
        "user_id": user_id,
        "access_token": access_token,
    }

    # Teardown — delete the test user
    with httpx.Client(base_url=live_server) as client:
        uid = _e2e_user_state.get("user_id")
        tok = _e2e_user_state.get("access_token")
        if uid and tok:
            client.delete(
                f"/api/v1/users/{uid}",
                headers={"Authorization": f"Bearer {tok}"},
            )


@pytest.fixture(scope="session")
def auth_token(live_server, e2e_user):
    """Return the access_token for the session-scoped E2E user."""
    return e2e_user["access_token"]
