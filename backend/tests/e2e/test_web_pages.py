"""
E2E tests — Phase WEB-001/002/003: page render checks.
Verifies that each /web/* route returns HTTP 200 and that all required DOM
elements are present in the rendered HTML.
"""
import pytest
from selenium.webdriver.common.by import By

pytestmark = pytest.mark.e2e


def test_login_page_renders(driver, live_server):
    """WEB-001: /web/login renders with all required input elements."""
    driver.get(f"{live_server}/web/login")
    assert driver.find_element(By.CSS_SELECTOR, "input[name='email']")
    assert driver.find_element(By.CSS_SELECTOR, "input[name='password']")
    assert driver.find_element(By.ID, "btn-login")
    assert driver.find_element(By.ID, "result")


def test_register_page_renders(driver, live_server):
    """WEB-002: /web/register renders with all required input elements."""
    driver.get(f"{live_server}/web/register")
    assert driver.find_element(By.CSS_SELECTOR, "input[name='username']")
    assert driver.find_element(By.CSS_SELECTOR, "input[name='email']")
    assert driver.find_element(By.CSS_SELECTOR, "input[name='password']")
    assert driver.find_element(By.ID, "btn-register")
    assert driver.find_element(By.ID, "result")


def test_calculator_page_renders(driver, live_server):
    """WEB-003: /web/calculator renders with all required elements."""
    driver.get(f"{live_server}/web/calculator")
    assert driver.find_element(By.ID, "expression")
    precision_select = driver.find_element(By.ID, "precision")
    assert precision_select
    options = precision_select.find_elements(By.TAG_NAME, "option")
    option_values = [o.get_attribute("value") for o in options]
    assert "10" in option_values
    assert "15" in option_values
    assert "50" in option_values
    assert driver.find_element(By.ID, "btn-calculate")
    assert driver.find_element(By.ID, "result")
    assert driver.find_element(By.ID, "history-list")
