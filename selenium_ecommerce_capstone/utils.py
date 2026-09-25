"""
utils.py
--------
Small, plain helper functions shared by the tests. No classes, no
design-pattern machinery on purpose - this is a beginner-friendly project.
"""

import json
import os
import urllib.request
from datetime import datetime

from selenium.common.exceptions import TimeoutException, NoAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
TEST_DATA_FILE = os.path.join(os.path.dirname(__file__), "test_data.json")


def load_test_data(path: str = TEST_DATA_FILE) -> dict:
    """Read the test data (credentials, search keyword, quantity, etc.) from JSON."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def take_screenshot(driver, step_name: str) -> str:
    """Save a screenshot named <step_name>_<timestamp>.png and return its path."""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(SCREENSHOT_DIR, f"{step_name}_{timestamp}.png")
    driver.save_screenshot(file_path)
    return file_path


def dismiss_cookie_consent_if_present(driver, wait_seconds: int = 4) -> bool:
    """
    demo.nopcommerce.com shows an EU cookie-consent bar the first time a
    fresh browser session visits the site. This clicks 'Accept' if it is
    there and does nothing (no error) if it never shows up.
    """
    possible_locators = [
        (By.ID, "accept-consent"),
        (By.CSS_SELECTOR, ".accept-cookie-consent"),
        (By.CSS_SELECTOR, "button.eu-cookie-compliance-default-button"),
        (By.XPATH, "//button[contains(translate(text(), 'ACEPT', 'acept'), 'accept')]"),
    ]
    for locator in possible_locators:
        try:
            btn = WebDriverWait(driver, wait_seconds).until(
                EC.element_to_be_clickable(locator)
            )
            btn.click()
            return True
        except TimeoutException:
            continue
    return False  # no popup appeared - perfectly normal, nothing to do


def dismiss_native_alert_if_present(driver, wait_seconds: int = 3):
    """
    Handles a native browser alert/confirm/prompt box if one pops up
    (e.g. a JS confirm() dialog). Returns the alert text, or None if no
    alert was present within the wait window.
    """
    try:
        WebDriverWait(driver, wait_seconds).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        text = alert.text
        alert.accept()
        return text
    except (TimeoutException, NoAlertPresentException):
        return None


# ---------------------------------------------------------------------------
# Currency conversion helpers
# ---------------------------------------------------------------------------

# Fallback rates (used if the live API is unreachable)
_FALLBACK_RATES_TO_INR = {
    "USD": 84.0,
    "EUR": 92.0,
}


def get_exchange_rate(from_currency: str = "USD", to_currency: str = "INR") -> float:
    """
    Fetch the live exchange rate from `from_currency` to `to_currency` using
    the free Open Exchange Rates endpoint (no API key needed).

    Falls back to a hardcoded approximate rate if the network call fails so
    the tests can still run in offline / CI environments.

    Args:
        from_currency: ISO 4217 currency code of the source (e.g. "USD", "EUR").
        to_currency:   ISO 4217 currency code of the target (default "INR").

    Returns:
        float: How many units of `to_currency` equal 1 unit of `from_currency`.
    """
    url = f"https://open.er-api.com/v6/latest/{from_currency}"
    try:
        with urllib.request.urlopen(url, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        rate = data["rates"][to_currency]
        print(f"[Currency] Live rate: 1 {from_currency} = {rate:.4f} {to_currency}")
        return float(rate)
    except Exception as exc:  # noqa: BLE001
        fallback = _FALLBACK_RATES_TO_INR.get(from_currency, 84.0)
        print(
            f"[Currency] Could not fetch live rate ({exc}). "
            f"Using fallback: 1 {from_currency} = {fallback:.2f} {to_currency}"
        )
        return fallback


def convert_to_inr(amount: float, from_currency: str = "USD") -> float:
    """
    Convert `amount` from `from_currency` to Indian Rupees (INR).

    Args:
        amount:        Numeric price value (e.g. 1299.00).
        from_currency: Source currency code ("USD" or "EUR").

    Returns:
        float: Equivalent price in INR, rounded to 2 decimal places.
    """
    rate = get_exchange_rate(from_currency, "INR")
    inr = round(amount * rate, 2)
    print(f"[Currency] {amount:.2f} {from_currency} -> Rs.{inr:,.2f} INR (rate={rate:.4f})")
    return inr


def parse_price_text(raw: str) -> tuple:
    """
    Parse a raw price string from the website into a (float, currency_code) tuple.

    Handles formats like:
        "$1,099.00"   -> (1099.0, "USD")
        "EUR1,099.00" -> (1099.0, "EUR")
        "1099.00"     -> (1099.0, "USD")   # USD assumed when no symbol

    Args:
        raw: Raw text of a price element, e.g. driver.find_element(...).text

    Returns:
        (amount: float, currency: str)  e.g. (1099.0, "USD")
    """
    import re

    raw = raw.strip()
    if raw.startswith("\u20ac") or "EUR" in raw.upper():
        currency = "EUR"
    else:
        currency = "USD"  # nopCommerce default

    numeric_str = re.sub(r"[^\d.]", "", raw)
    amount = float(numeric_str) if numeric_str else 0.0
    return amount, currency
