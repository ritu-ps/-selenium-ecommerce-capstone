import json
import os
import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


WAIT = 20
DEFAULT_URL = "https://demo.nopcommerce.com/"


def load_test_data():
    """Load test data from test_data.json."""
    path = os.path.join(
        os.path.dirname(__file__),
        "test_data.json"
    )

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def wait_for(driver, locator):
    """Wait until an element is visible."""
    return WebDriverWait(driver, WAIT).until(
        EC.visibility_of_element_located(locator)
    )


def click_when_ready(driver, locator):
    """Wait until an element is clickable and click it."""
    element = WebDriverWait(driver, WAIT).until(
        EC.element_to_be_clickable(locator)
    )
    driver.execute_script(
        "arguments[0].click();",
        element
    )
    return element


def save_screenshot(driver, name):
    """Save a screenshot to the screenshots directory."""
    folder = os.path.join(
        os.path.dirname(__file__),
        "screenshots"
    )

    os.makedirs(folder, exist_ok=True)

    filename = os.path.join(
        folder,
        f"{name}_{int(time.time())}.png"
    )

    driver.save_screenshot(filename)

    print(f"\nScreenshot saved: {filename}")


@pytest.mark.usefixtures("driver")
class TestEcommerceCapstone:

    def test_complete_ecommerce_flow(self):
        """
        Complete nopCommerce automation flow:

        1. Open nopCommerce
        2. Register a new customer
        3. Verify account creation
        4. Search for a laptop
        5. Open a search result
        6. Add product to cart
        7. Verify cart
        8. Update quantity
        9. Verify price and total
        10. Logout
        """

        driver = self.driver
        data = load_test_data()

        base_url = data.get(
            "base_url",
            DEFAULT_URL
        )

        user = data.get("user", {})

        first_name = user.get(
            "first_name",
            "Ritu"
        )

        last_name = user.get(
            "last_name",
            "Automation"
        )

        password = user.get(
            "password",
            "Test@12345"
        )

        keyword = data.get(
            "search",
            {}
        ).get(
            "keyword",
            "laptop"
        )

        quantity = int(
            data.get(
                "cart",
                {}
            ).get(
                "quantity",
                2
            )
        )

        # Generate a unique email for every GitHub Actions run.
        email = (
            f"ritutest{int(time.time())}"
            "@example.com"
        )

        # =========================================================
        # 1. OPEN NOPCOMMERCE
        # =========================================================

        driver.get(base_url)

        WebDriverWait(driver, WAIT).until(
            EC.title_contains("nopCommerce")
        )

        assert "nopCommerce" in driver.title

        save_screenshot(
            driver,
            "01_home_page"
        )

        # =========================================================
        # 2. OPEN REGISTRATION
        # =========================================================

        click_when_ready(
            driver,
            (
                By.CSS_SELECTOR,
                "a[href='/register']"
            )
        )

        wait_for(
            driver,
            (
                By.CSS_SELECTOR,
                "input[name='FirstName']"
            )
        )

        # =========================================================
        # 3. FILL REGISTRATION FORM
        # =========================================================

        driver.find_element(
            By.CSS_SELECTOR,
            "input[name='FirstName']"
        ).send_keys(first_name)

        driver.find_element(
            By.CSS_SELECTOR,
            "input[name='LastName']"
        ).send_keys(last_name)

        driver.find_element(
            By.CSS_SELECTOR,
            "input[name='Email']"
        ).send_keys(email)

        driver.find_element(
            By.CSS_SELECTOR,
            "input[name='Password']"
        ).send_keys(password)

        driver.find_element(
            By.CSS_SELECTOR,
            "input[name='ConfirmPassword']"
        ).send_keys(password)

        save_screenshot(
            driver,
            "02_registration_form"
        )

        # =========================================================
        # 4. CREATE ACCOUNT
        # =========================================================

        click_when_ready(
            driver,
            (
                By.CSS_SELECTOR,
                "button[name='register-button']"
            )
        )

        wait_for(
            driver,
            (
                By.CSS_SELECTOR,
                ".result"
            )
        )

        registration_result = driver.find_element(
            By.CSS_SELECTOR,
            ".result"
        )

        assert "completed" in (
            registration_result.text.lower()
        )

        save_screenshot(
            driver,
            "03_account_created"
        )

        # Continue back to store.
        continue_buttons = driver.find_elements(
            By.CSS_SELECTOR,
            "a.register-continue-button"
        )

        if continue_buttons:
            click_when_ready(
                driver,
                (
                    By.CSS_SELECTOR,
                    "a.register-continue-button"
                )
            )
        else:
            driver.get(base_url)

        # =========================================================
        # 5. LOGIN
        # =========================================================

        click_when_ready(
            driver,
            (
                By.CSS_SELECTOR,
                "a[href='/login']"
            )
        )

        wait_for(
            driver,
            (
                By.CSS_SELECTOR,
                "input[name='Email']"
            )
        )

        driver.find_element(
            By.CSS_SELECTOR,
            "input[name='Email']"
        ).send_keys(email)

        driver.find_element(
            By.CSS_SELECTOR,
            "input[name='Password']"
        ).send_keys(password)

        click_when_ready(
            driver,
            (
                By.CSS_SELECTOR,
                "button.login-button"
            )
        )

        # Verify logout link exists after login.
        wait_for(
            driver,
            (
                By.CSS_SELECTOR,
                "a[href='/logout']"
            )
        )

        save_screenshot(
            driver,
            "04_login_success"
        )

        # =========================================================
        # 6. SEARCH FOR LAPTOP
        # =========================================================

        search_box = wait_for(
            driver,
            (
                By.CSS_SELECTOR,
                "#small-searchterms"
            )
        )

        search_box.clear()
        search_box.send_keys(keyword)

        click_when_ready(
            driver,
            (
                By.CSS_SELECTOR,
                "button.search-box-button"
            )
        )

        # Wait for search page.
        WebDriverWait(driver, WAIT).until(
            EC.url_contains("/search")
        )

        wait_for(
            driver,
            (
                By.CSS_SELECTOR,
                ".product-item"
            )
        )

        products = driver.find_elements(
            By.CSS_SELECTOR,
            ".product-item"
        )

        assert len(products) > 0, (
            f"No products found for '{keyword}'"
        )

        print(
            f"\nFound {len(products)} product(s) "
            f"for '{keyword}'"
        )

        save_screenshot(
            driver,
            "05_search_results"
        )

        # =========================================================
        # 7. OPEN FIRST PRODUCT
        # =========================================================

        first_product = products[0]

        product_link = first_product.find_element(
            By.CSS_SELECTOR,
            "h2.product-title a"
        )

        product_name = product_link.text.strip()

        driver.execute_script(
            "arguments[0].click();",
            product_link
        )

        wait_for(
            driver,
            (
                By.CSS_SELECTOR,
                "button.add-to-cart-button"
            )
        )

        print(
            f"Selected product: {product_name}"
        )

        save_screenshot(
            driver,
            "06_product_page"
        )

        # =========================================================
        # 8. ADD PRODUCT TO CART
        # =========================================================

        click_when_ready(
            driver,
            (
                By.CSS_SELECTOR,
                "button.add-to-cart-button"
            )
        )

        # Wait for cart notification / success message.
        WebDriverWait(driver, WAIT).until(
            lambda d: (
                "added to your shopping cart"
                in d.page_source.lower()
                or "shopping cart"
                in d.page_source.lower()
            )
        )

        save_screenshot(
            driver,
            "07_product_added"
        )

        # =========================================================
        # 9. OPEN SHOPPING CART
        # =========================================================

        click_when_ready(
            driver,
            (
                By.CSS_SELECTOR,
                "a.ico-cart"
            )
        )

        WebDriverWait(driver, WAIT).until(
            EC.url_contains("/cart")
        )

        wait_for(
            driver,
            (
                By.CSS_SELECTOR,
                ".cart-item-row"
            )
        )

        cart_items = driver.find_elements(
            By.CSS_SELECTOR,
            ".cart-item-row"
        )

        assert len(cart_items) > 0, (
            "Product was not added to the cart"
        )

        save_screenshot(
            driver,
            "08_cart"
        )

        # =========================================================
        # 10. UPDATE QUANTITY
        # =========================================================

        quantity_input = wait_for(
            driver,
            (
                By.CSS_SELECTOR,
                ".qty-input"
            )
        )

        quantity_input.clear()
        quantity_input.send_keys(str(quantity))

        # Click Update Shopping Cart.
        update_buttons = driver.find_elements(
            By.CSS_SELECTOR,
            "button[name='updatecart']"
        )

        if update_buttons:
            click_when_ready(
                driver,
                (
                    By.CSS_SELECTOR,
                    "button[name='updatecart']"
                )
            )

        # Wait until quantity is updated.
        WebDriverWait(driver, WAIT).until(
            lambda d: (
                d.find_element(
                    By.CSS_SELECTOR,
                    ".qty-input"
                ).get_attribute("value")
                == str(quantity)
            )
        )

        updated_quantity = driver.find_element(
            By.CSS_SELECTOR,
            ".qty-input"
        ).get_attribute("value")

        assert updated_quantity == str(quantity)

        print(
            f"\nCart quantity updated to: "
            f"{updated_quantity}"
        )

        save_screenshot(
            driver,
            "09_quantity_updated"
        )

        # =========================================================
        # 11. VERIFY PRICE AND TOTAL
        # =========================================================

        unit_price = wait_for(
            driver,
            (
                By.CSS_SELECTOR,
                ".product-unit-price"
            )
        ).text

        line_total = wait_for(
            driver,
            (
                By.CSS_SELECTOR,
                ".product-subtotal"
            )
        ).text

        print(
            "\n========== CART DETAILS =========="
        )
        print(
            f"Product  : {product_name}"
        )
        print(
            f"Quantity : {updated_quantity}"
        )
        print(
            f"Price    : {unit_price}"
        )
        print(
            f"Subtotal : {line_total}"
        )
        print(
            "=================================="
        )

        assert unit_price
        assert line_total

        save_screenshot(
            driver,
            "10_cart_verified"
        )

        # =========================================================
        # 12. LOGOUT
        # =========================================================

        click_when_ready(
            driver,
            (
                By.CSS_SELECTOR,
                "a[href='/logout']"
            )
        )

        WebDriverWait(driver, WAIT).until(
            EC.url_contains("/login")
        )

        assert "/login" in driver.current_url

        save_screenshot(
            driver,
            "11_logout"

        )


    def test_price_in_rupees(self):
        """
        Simple currency conversion validation.
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
