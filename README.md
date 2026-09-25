# Selenium E-Commerce Capstone

Automates https://demo.nopcommerce.com/ : register -> login -> search ->
add to cart (with quantity) -> update quantity -> verify cart.

## Install
```
pip install -r requirements.txt
```

## Run
```
pytest
```
This runs Chrome visibly and writes `reports/execution_report.html`.
Run headless (e.g. on a server/CI) with:
```
HEADLESS=true pytest
```

## Notes
- Google Chrome must be installed; `webdriver-manager` downloads the matching
  chromedriver automatically - no manual driver setup needed.
- demo.nopcommerce.com is a public shared demo store. If its team ever
  changes the page markup, a locator or two in `test_ecommerce_capstone.py`
  may need a small update (e.g. a class name), but the overall flow and
  file structure stay the same.
- Screenshots land in `screenshots/`, the HTML report in `reports/`.
