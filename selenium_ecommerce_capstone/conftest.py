"""
conftest.py
-----------
Shared pytest fixtures:
  - `driver`: starts one Chrome browser per test CLASS (so the login
    session carries through the whole shopping flow) and quits it at the end.
  - A hook that automatically saves a screenshot whenever a test fails.
"""

import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from utils import take_screenshot

HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"


@pytest.fixture(scope="class")
def driver(request):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    if HEADLESS:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    chrome_driver = webdriver.Chrome(service=service, options=options)
    chrome_driver.implicitly_wait(0)  # we use explicit waits everywhere instead

    # Attach the driver to the test class so every test method can use self.driver
    request.cls.driver = chrome_driver

    yield chrome_driver

    chrome_driver.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Automatically capture a screenshot when a test fails."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        test_driver = getattr(item.instance, "driver", None)
        if test_driver is not None:
            screenshot_path = take_screenshot(test_driver, f"FAILURE_{item.name}")
            if hasattr(report, "extra"):
                pass  # kept simple on purpose - no pytest-html extras plugin required
            print(f"\n[Screenshot on failure saved] {screenshot_path}")
