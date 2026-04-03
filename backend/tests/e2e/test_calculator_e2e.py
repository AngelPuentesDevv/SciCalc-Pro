"""
E2E tests — E2E-004 (calculator) and E2E-005 (history).
Each test injects the auth token into sessionStorage after navigating to
/web/calculator, since sessionStorage is origin-bound and cannot be set
before the first page load.
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

pytestmark = pytest.mark.e2e

WAIT_TIMEOUT = 15  # seconds — calculation + DB write can take a moment


# ── Helpers ───────────────────────────────────────────────────────────────────

def _open_calculator(driver, live_server, token):
    """Navigate to /web/calculator and inject the auth token into sessionStorage."""
    driver.get(f"{live_server}/web/calculator")
    driver.execute_script(f"sessionStorage.setItem('access_token', '{token}')")


def _calculate(driver, expression, precision="15"):
    """Fill the expression + precision fields and click Calculate."""
    expr_input = driver.find_element(By.ID, "expression")
    expr_input.clear()
    expr_input.send_keys(expression)

    precision_select = driver.find_element(By.ID, "precision")
    for option in precision_select.find_elements(By.TAG_NAME, "option"):
        if option.get_attribute("value") == str(precision):
            option.click()
            break

    driver.find_element(By.ID, "btn-calculate").click()


# ── Calculator tests (E2E-004) ────────────────────────────────────────────────

def test_calculate_basic_arithmetic(driver, live_server, auth_token):
    """E2E-004a: 2 + 3 * 4 should evaluate to 14."""
    _open_calculator(driver, live_server, auth_token)
    _calculate(driver, "2 + 3 * 4", precision="15")

    result_locator = (By.ID, "result")
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.text_to_be_present_in_element(result_locator, "14")
    )
    result_text = driver.find_element(By.ID, "result").text
    assert "14" in result_text


def test_calculate_trig_sin90(driver, live_server, auth_token):
    """E2E-004b: sin(90) in DEG mode should evaluate to 1."""
    _open_calculator(driver, live_server, auth_token)
    _calculate(driver, "sin(90)", precision="15")

    result_locator = (By.ID, "result")
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        lambda d: d.find_element(By.ID, "result").text.strip() != ""
    )
    result_text = driver.find_element(By.ID, "result").text
    # sin(90 deg) = 1.0 — result may be "1" or "1.0" or "1.00..."
    assert result_text.strip().startswith("1")


def test_calculate_invalid_expression(driver, live_server, auth_token):
    """E2E-004c: Invalid expression '2 /' should show an error message."""
    _open_calculator(driver, live_server, auth_token)
    _calculate(driver, "2 /", precision="15")

    result_locator = (By.ID, "result")
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        lambda d: d.find_element(By.ID, "result").text.strip() != ""
    )
    result_text = driver.find_element(By.ID, "result").text
    # Should contain an error indicator — not a bare number
    assert any(
        word in result_text.lower()
        for word in ("error", "invalid", "inválid", "syntax", "unexpected")
    )


# ── History tests (E2E-005) ───────────────────────────────────────────────────

def test_history_shows_entries(driver, live_server, auth_token):
    """E2E-005a: After a calculation, history-list should contain at least one entry."""
    _open_calculator(driver, live_server, auth_token)
    _calculate(driver, "1 + 1", precision="15")

    # Wait for result to populate
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.text_to_be_present_in_element((By.ID, "result"), "2")
    )

    # Wait for at least one history entry with data-id
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        lambda d: len(
            d.find_element(By.ID, "history-list").find_elements(By.CSS_SELECTOR, "[data-id]")
        ) > 0
    )
    entries = driver.find_element(By.ID, "history-list").find_elements(
        By.CSS_SELECTOR, "div[data-id]"
    )
    assert len(entries) > 0


def test_history_delete_entry(driver, live_server, auth_token):
    """E2E-005b: Clicking Borrar removes the entry from history-list."""
    _open_calculator(driver, live_server, auth_token)
    _calculate(driver, "5 * 5", precision="15")

    # Wait for result
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.text_to_be_present_in_element((By.ID, "result"), "25")
    )

    # Wait for history to load
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        lambda d: len(
            d.find_element(By.ID, "history-list").find_elements(By.CSS_SELECTOR, "[data-id]")
        ) > 0
    )

    history_list = driver.find_element(By.ID, "history-list")
    first_entry = history_list.find_elements(By.CSS_SELECTOR, "div[data-id]")[0]
    entry_id = first_entry.get_attribute("data-id")

    # Click delete on the first entry
    delete_btn = first_entry.find_element(By.CSS_SELECTOR, ".btn-delete")
    delete_btn.click()

    # Wait for the entry to be removed from DOM (staleness)
    WebDriverWait(driver, WAIT_TIMEOUT).until(EC.staleness_of(first_entry))

    # Confirm it is no longer in the list
    remaining = driver.find_element(By.ID, "history-list").find_elements(
        By.CSS_SELECTOR, f"div[data-id='{entry_id}']"
    )
    assert len(remaining) == 0
