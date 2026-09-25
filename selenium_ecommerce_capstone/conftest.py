"""
conftest.py
-----------
Shared pytest fixtures:
- Starts one Chrome browser per test class.
- Supports headless execution through the HEADLESS environment variable.
- Automatically takes a screenshot when a test fails.
"""

import os

import pytest
from selenium import webdriver

from utils import take_screenshot


HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"


@pytest.fixture(scope="class")
def driver(request):
    """Create and manage a Chrome WebDriver for the test class."""

    options = webdriver.ChromeOptions()

    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("--window-size=1920,1080")

    if HEADLESS:
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    chrome_driver = webdriver.Chrome(options=options)

    # Use explicit waits in the tests.
    chrome_driver.implicitly_wait(0)

    # Make the driver available as self.driver
    # inside the test class.
    request.cls.driver = chrome_driver

    yield chrome_driver

    chrome_driver.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Take a screenshot automatically when a test fails."""

    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:

        test_driver = getattr(
            item.instance,
            "driver",
            None
        )

        if test_driver is not None:

            screenshot_path = take_screenshot(
                test_driver,
                f"FAILURE_{item.name}"
            )

            print(
                f"\n[Screenshot on failure saved] "
                f"{screenshot_path}"
            )

