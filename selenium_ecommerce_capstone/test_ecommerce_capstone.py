import json
import os
import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


WAIT = 20
BASE_URL = "https://automationexercise.com"


def load_test_data():
    """Read test data from test_data.json."""
    path = os.path.join(os.path.dirname(__file__), "test_data.json")

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def take_screenshot(driver, name):
    """Save a screenshot in the screenshots folder."""
    folder = os.path.join(os.path.dirname(__file__), "screenshots")
    os.makedirs(folder, exist_ok=True)

    filename = os.path.join(
        folder,
        f"{name}_{int(time.time())}.png"
    )

    driver.save_screenshot(filename)
    print(f"\nScreenshot saved: {filename}")


def click_when_ready(driver, locator):
    """Wait until an element is clickable and click it."""
    wait = WebDriverWait(driver, WAIT)
    element = wait.until(
        EC.element_to_be_clickable(locator)
    )
    element.click()
    return element


def visible_element(driver, locator):
    """Wait until an element is visible."""
    wait = WebDriverWait(driver, WAIT)
    return wait.until(
        EC.visibility_of_element_located(locator)
    )


@pytest.mark.usefixtures("driver")
class TestEcommerceCapstone:

    def test_complete_ecommerce_flow(self):
        """
        Complete e-commerce automation flow:

        1. Launch website
        2. Register a new user
        3. Verify login
        4. Search for a product
        5. Add product to cart
        6. Verify cart
        7. Update quantity
        8. Verify price and total
        9. Take screenshots
        10. Logout
        """

        driver = self.driver
        wait = WebDriverWait(driver, WAIT)

        # ---------------------------------------------------------
        # READ TEST DATA
        # ---------------------------------------------------------

        data = load_test_data()

        user_data = data.get("user", {})

        first_name = user_data.get("first_name", "Ritu")
        last_name = user_data.get("last_name", "Test")
        password = user_data.get("password", "Test@12345")

        quantity = int(
            data.get("cart", {}).get("quantity", 2)
        )

        search_keyword = data.get(
            "search", {}
        ).get(
            "keyword", "top"
        )

        # Generate a unique email for every run
        email = (
            f"seleniumtest{int(time.time())}"
            "@example.com"
        )

        # ---------------------------------------------------------
        # 1. OPEN WEBSITE
        # ---------------------------------------------------------

        driver.get(BASE_URL)

        wait.until(
            EC.title_contains("Automation Exercise")
        )

        assert "Automation Exercise" in driver.title

        take_screenshot(
            driver,
            "01_home_page"
        )

        # ---------------------------------------------------------
        # 2. REGISTER
        # ---------------------------------------------------------

        click_when_ready(
            driver,
            (By.CSS_SELECTOR, "a[href='/login']")
        )

        visible_element(
            driver,
            (
                By.XPATH,
                "//h2[contains(text(),'New User Signup')]"
            )
        )

        # Name
        visible_element(
            driver,
            (
                By.CSS_SELECTOR,
                "input[data-qa='signup-name']"
            )
        ).send_keys(first_name)

        # Email
        driver.find_element(
            By.CSS_SELECTOR,
            "input[data-qa='signup-email']"
        ).send_keys(email)

        # Signup
        click_when_ready(
            driver,
            (
                By.CSS_SELECTOR,
                "button[data-qa='signup-button']"
            )
        )

        # ---------------------------------------------------------
        # 3. ACCOUNT INFORMATION
        # ---------------------------------------------------------

        visible_element(
            driver,
            (
                By.XPATH,
                "//b[contains(text(),'Enter Account Information')]"
            )
        )

        # Gender
        try:
            driver.find_element(
                By.ID,
                "id_gender1"
            ).click()
        except Exception:
            pass

        # Password
        driver.find_element(
            By.CSS_SELECTOR,
            "input[data-qa='password']"
        ).send_keys(password)

        # Date of birth
        try:
            Select(
                driver.find_element(
                    By.CSS_SELECTOR,
                    "#days"
                )
            ).select_by_value("10")

            Select(
                driver.find_element(
                    By.CSS_SELECTOR,
                    "#months"
                )
            ).select_by_value("5")

            Select(
                driver.find_element(
                    By.CSS_SELECTOR,
                    "#years"
                )
            ).select_by_value("2004")

        except Exception:
            pass

        # Newsletter
        try:
            driver.find_element(
                By.ID,
                "newsletter"
            ).click()
        except Exception:
            pass

        # ---------------------------------------------------------
        # 4. ADDRESS INFORMATION
        # ---------------------------------------------------------

        driver.find_element(
            By.CSS_SELECTOR,
            "input[data-qa='first_name']"
        ).send_keys(first_name)

        driver.find_element(
            By.CSS_SELECTOR,
            "input[data-qa='last_name']"
        ).send_keys(last_name)

        driver.find_element(
            By.CSS_SELECTOR,
            "input[data-qa='address']"
        ).send_keys("Test Address")

        # Country
        try:
            Select(
                driver.find_element(
                    By.CSS_SELECTOR,
                    "select[data-qa='country']"
                )
            ).select_by_visible_text("India")
        except Exception:
            pass

        driver.find_element(
            By.CSS_SELECTOR,
            "input[data-qa='state']"
        ).send_keys("West Bengal")

        driver.find_element(
            By.CSS_SELECTOR,
            "input[data-qa='city']"
        ).send_keys("Kolkata")

        driver.find_element(
            By.CSS_SELECTOR,
            "input[data-qa='zipcode']"
        ).send_keys("700001")

        driver.find_element(
            By.CSS_SELECTOR,
            "input[data-qa='mobile_number']"
        ).send_keys("9000000000")

        # Create account
        click_when_ready(
            driver,
            (
                By.CSS_SELECTOR,
                "button[data-qa='create-account']"
            )
        )

        # Verify account created
        visible_element(
            driver,
            (
                By.XPATH,
                "//b[contains(text(),'Account Created')]"
            )
        )

        take_screenshot(
            driver,
            "02_account_created"
        )

        # Continue
        click_when_ready(
            driver,
            (
                By.CSS_SELECTOR,
                "a[data-qa='continue-button']"
            )
        )

        # ---------------------------------------------------------
        # 5. VERIFY LOGIN
        # ---------------------------------------------------------

        logged_in_text = visible_element(
            driver,
            (
                By.XPATH,
                "//a[contains(text(),'Logged in as')]"
            )
        )

        assert "Logged in as" in logged_in_text.text

        take_screenshot(
            driver,
            "03_login_success"
        )

        # ---------------------------------------------------------
        # 6. SEARCH PRODUCT
        # ---------------------------------------------------------

        click_when_ready(
            driver,
            (
                By.CSS_SELECTOR,
                "a[href='/products']"
            )
        )

        visible_element(
            driver,
            (
                By.XPATH,
                "//h2[contains(text(),'All Products')]"
            )
        )

        search_box = visible_element(
            driver,
            (
                By.ID,
                "search_product"
            )
        )

        search_box.clear()
        search_box.send_keys(search_keyword)

        click_when_ready(
            driver,
            (
                By.ID,
                "submit_search"
            )
        )

        # Verify search results
        visible_element(
            driver,
            (
                By.XPATH,
                "//h2[contains(text(),'Searched Products')]"
            )
        )

        products = driver.find_elements(
            By.CSS_SELECTOR,
            ".productinfo"
        )

        assert len(products) > 0, (
            f"No products found for '{search_keyword}'"
        )

        take_screenshot(
            driver,
            "04_search_results"
        )

        # ---------------------------------------------------------
        # 7. ADD PRODUCT TO CART
        # ---------------------------------------------------------

        first_product = products[0]

        add_button = first_product.find_element(
            By.CSS_SELECTOR,
            "a.add-to-cart"
        )

        driver.execute_script(
            "arguments[0].click();",
            add_button
        )

        # Wait for confirmation
        visible_element(
            driver,
            (
                By.XPATH,
                "//p[contains(text(),'Your product has been added')]"
            )
        )

        take_screenshot(
            driver,
            "05_product_added"
        )

        # Open cart
        click_when_ready(
            driver,
            (
                By.XPATH,
                "//u[contains(text(),'View Cart')]"
            )
        )

        # ---------------------------------------------------------
        # 8. VERIFY CART
        # ---------------------------------------------------------

        visible_element(
            driver,
            (
                By.ID,
                "cart_info_table"
            )
        )

        cart_rows = driver.find_elements(
            By.CSS_SELECTOR,
            "#cart_info_table tbody tr"
        )

        assert len(cart_rows) >= 1, (
            "Product was not found in the cart"
        )

        take_screenshot(
            driver,
            "06_cart"
        )

        # ---------------------------------------------------------
        # 9. UPDATE QUANTITY
        # ---------------------------------------------------------

        quantity_input = visible_element(
            driver,
            (
                By.CSS_SELECTOR,
                "input.cart_quantity_input"
            )
        )

        quantity_input.clear()
        quantity_input.send_keys(str(quantity))

        # Trigger change event
        driver.execute_script(
            """
            arguments[0].dispatchEvent(
                new Event('change', { bubbles: true })
            );
            """,
            quantity_input
        )

        # Wait for expected value
        wait.until(
            EC.text_to_be_present_in_element_value(
                (
                    By.CSS_SELECTOR,
                    "input.cart_quantity_input"
                ),
                str(quantity)
            )
        )

        updated_quantity = quantity_input.get_attribute(
            "value"
        )

        assert updated_quantity == str(quantity), (
            f"Expected quantity {quantity}, "
            f"but found {updated_quantity}"
        )

        take_screenshot(
            driver,
            "07_quantity_updated"
        )

        # ---------------------------------------------------------
        # 10. VERIFY PRICE AND TOTAL
        # ---------------------------------------------------------

        price_elements = driver.find_elements(
            By.CSS_SELECTOR,
            ".cart_price"
        )

        total_elements = driver.find_elements(
            By.CSS_SELECTOR,
            ".cart_total"
        )

        assert len(price_elements) > 0, (
            "Product price was not displayed"
        )

        assert len(total_elements) > 0, (
            "Product total was not displayed"
        )

        print(
            "\n========== CART DETAILS =========="
        )
        print(
            f"Product quantity : {updated_quantity}"
        )
        print(
            f"Product price    : {price_elements[0].text}"
        )
        print(
            f"Product total    : {total_elements[0].text}"
        )
        print(
            "=================================="
        )

        take_screenshot(
            driver,
            "08_cart_verified"
        )

        # ---------------------------------------------------------
        # 11. LOGOUT
        # ---------------------------------------------------------

        click_when_ready(
            driver,
            (
                By.CSS_SELECTOR,
                "a[href='/logout']"
            )
        )

        wait.until(
            EC.url_contains("/login")
        )

        assert "/login" in driver.current_url

        take_screenshot(
            driver,
            "09_logout"
        )

    def test_price_in_rupees(self):
        """
        Independent currency conversion test.
        """

        usd_to_inr = 88.0
        eur_to_inr = 103.0

        usd_amount = 100
        eur_amount = 100

        usd_inr = usd_amount * usd_to_inr
        eur_inr = eur_amount * eur_to_inr

        print(
            "\n========== CURRENCY CONVERSION =========="
        )
        print(
            f"$100 USD = Rs.{usd_inr:.2f}"
        )
        print(
            f"€100 EUR = Rs.{eur_inr:.2f}"
        )
        print(
            "========================================="
        )

        assert usd_inr > 0
        assert eur_inr > 0
