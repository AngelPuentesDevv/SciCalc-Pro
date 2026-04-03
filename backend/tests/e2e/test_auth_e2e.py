"""
E2E tests — E2E-002 (register flow) and E2E-003 (login flow).
"""
import uuid

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

pytestmark = pytest.mark.e2e

WAIT_TIMEOUT = 10  # seconds


# ── Register flow (E2E-002) ───────────────────────────────────────────────────

def test_register_new_user(driver, live_server):
    """E2E-002a: Registering a new unique user shows success message."""
    unique_email = f"test_{uuid.uuid4().hex[:8]}@scicalc.test"
    driver.get(f"{live_server}/web/register")

    driver.find_element(By.CSS_SELECTOR, "input[name='username']").send_keys("Test User")
    driver.find_element(By.CSS_SELECTOR, "input[name='email']").send_keys(unique_email)
    driver.find_element(By.CSS_SELECTOR, "input[name='password']").send_keys("Secure1234!")
    driver.find_element(By.ID, "btn-register").click()

    result_locator = (By.ID, "result")
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.text_to_be_present_in_element(result_locator, "registrado")
    )
    result_text = driver.find_element(By.ID, "result").text
    assert "registrado" in result_text.lower()


def test_register_duplicate_email(driver, live_server, e2e_user):
    """E2E-002b: Registering with an already-registered email shows an error."""
    driver.get(f"{live_server}/web/register")

    driver.find_element(By.CSS_SELECTOR, "input[name='username']").send_keys("Dup User")
    driver.find_element(By.CSS_SELECTOR, "input[name='email']").send_keys(e2e_user["email"])
    driver.find_element(By.CSS_SELECTOR, "input[name='password']").send_keys(e2e_user["password"])
    driver.find_element(By.ID, "btn-register").click()

    result_locator = (By.ID, "result")
    # Wait for any non-empty text in result
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        lambda d: d.find_element(By.ID, "result").text.strip() != ""
    )
    result_text = driver.find_element(By.ID, "result").text
    assert "registrado" not in result_text.lower() or "error" in result_text.lower()


# ── Login flow (E2E-003) ──────────────────────────────────────────────────────

def test_login_valid_credentials(driver, live_server, e2e_user):
    """E2E-003a: Valid credentials log in successfully and store the token."""
    driver.get(f"{live_server}/web/login")

    driver.find_element(By.CSS_SELECTOR, "input[name='email']").send_keys(e2e_user["email"])
    driver.find_element(By.CSS_SELECTOR, "input[name='password']").send_keys(e2e_user["password"])
    driver.find_element(By.ID, "btn-login").click()

    result_locator = (By.ID, "result")
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.text_to_be_present_in_element(result_locator, "exitoso")
    )
    result_text = driver.find_element(By.ID, "result").text
    assert "exitoso" in result_text.lower()

    token = driver.execute_script("return sessionStorage.getItem('access_token')")
    assert token is not None and token != ""


def test_login_invalid_password(driver, live_server, e2e_user):
    """E2E-003b: Wrong password shows an error and does NOT store a token."""
    driver.get(f"{live_server}/web/login")

    driver.find_element(By.CSS_SELECTOR, "input[name='email']").send_keys(e2e_user["email"])
    driver.find_element(By.CSS_SELECTOR, "input[name='password']").send_keys("WrongPass!")
    driver.find_element(By.ID, "btn-login").click()

    result_locator = (By.ID, "result")
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        lambda d: d.find_element(By.ID, "result").text.strip() != ""
    )
    result_text = driver.find_element(By.ID, "result").text
    assert "exitoso" not in result_text.lower()

    token = driver.execute_script("return sessionStorage.getItem('access_token')")
    assert token is None or token == ""
