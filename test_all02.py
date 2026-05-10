# ================================
# FILE: test_terminalx_e2e.py
# ================================

import pytest

from playwright.sync_api import (
    Page,
    sync_playwright,
    expect,
    TimeoutError
)

BASE_URL = "https://www.terminalx.com/"


# =========================================
# FIXTURE
# =========================================

@pytest.fixture(scope="class")
def shared_page():

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False,
            slow_mo=400
        )

        context = browser.new_context(
            viewport={
                "width": 1280,
                "height": 800
            }
        )

        page = context.new_page()

        yield page

        context.close()
        browser.close()


# =========================================
# HELPERS
# =========================================

def handle_popups(page: Page):

    print("Handling popups...")

    try:
        popup_close = page.locator(
            '[data-test-id="qa-popup-close-button"]'
        )

        popup_close.wait_for(
            state="visible",
            timeout=3000
        )

        popup_close.click()

        print("Popup closed successfully")

    except TimeoutError:

        print("Popup was not displayed")

    try:
        cookies_btn = page.locator(
            'button:has-text("הבנתי"), button:has-text("סגור")'
        ).first

        cookies_btn.click(timeout=2000)

        print("Cookies popup closed")

    except TimeoutError:

        print("Cookies popup was not displayed")


def do_login(page: Page):

    print("Starting login process...")

    try:

        profile_btn = page.locator(
            '[data-test-id="qa-header-profile-button"]'
        )

        if profile_btn.is_visible(timeout=3000):

            print("User already logged in")

            return

    except:

        pass

    page.goto(BASE_URL)

    handle_popups(page)

    login_btn = page.locator(
        '[data-test-id="qa-header-login-button"]'
    )

    login_btn.click()

    email_input = page.locator(
        '[data-test-id="qa-login-email-input"]'
    )

    password_input = page.locator(
        '[data-test-id="qa-login-password-input"]'
    )

    submit_btn = page.locator(
        '[data-test-id="qa-login-submit"]'
    )

    email_input.wait_for(
        state="visible",
        timeout=15000
    )

    email_input.fill("doron.cohen@nice.com")

    password_input.fill("12345678")

    submit_btn.click()

    page.wait_for_load_state("networkidle")

    print("Login completed successfully")


def search_product(page: Page, product_name: str):

    print(f"Searching for product: {product_name}")

    search_btn = page.locator(
        '[data-test-id="qa-header-search-button"]'
    )

    search_btn.click()

    search_input = page.locator(
        '[data-test-id="qa-search-box-input"]'
    )

    search_input.fill(product_name)

    search_input.press("Enter")

    page.wait_for_load_state("networkidle")

    print("Search completed successfully")


# =========================================
# TESTS
# =========================================

class TestTerminalX:


    # =====================================
    # TEST 01 - HOMEPAGE
    # =====================================

    def test_01_homepage_load(self, shared_page: Page):

        print("\n=== TEST 01: HOMEPAGE LOAD ===")

        shared_page.goto(BASE_URL)

        handle_popups(shared_page)

        assert shared_page.title() != ""

        print("Homepage loaded successfully")


    # =====================================
    # TEST 02 - LOGIN
    # =====================================

    def test_02_login(self, shared_page: Page):

        print("\n=== TEST 02: LOGIN ===")

        do_login(shared_page)

        profile_btn = shared_page.locator(
            '[data-test-id="qa-header-profile-button"]'
        )

        expect(profile_btn).to_be_visible(timeout=15000)

        print("Login test passed")


    # =====================================
    # TEST 03 - SEARCH
    # =====================================

    def test_03_search(self, shared_page: Page):

        print("\n=== TEST 03: SEARCH ===")

        shared_page.goto(BASE_URL)

        search_product(shared_page, "nike")

        assert "nike" in shared_page.url.lower()

        print("Search test passed")


    # =====================================
    # TEST 04 - SEARCH RESULTS
    # =====================================

    def test_04_search_results(self, shared_page: Page):

        print("\n=== TEST 04: SEARCH RESULTS ===")

        products = shared_page.locator(
            '[data-test-id="qa-product-link"]'
        )

        count = products.count()

        print(f"Found {count} products")

        assert count > 0

        print("Search results test passed")


    # =====================================
    # TEST 05 - OPEN PRODUCT
    # =====================================

    def test_05_open_product(self, shared_page: Page):

        print("\n=== TEST 05: OPEN PRODUCT ===")

        first_product = shared_page.locator(
            '[data-test-id="qa-product-link"]'
        ).first

        first_product.wait_for(
            state="visible",
            timeout=15000
        )

        first_product.click(force=True)

        shared_page.wait_for_load_state("networkidle")

        add_to_cart_btn = shared_page.locator(
            '[data-test-id="qa-add-to-cart-button"]'
        )

        expect(add_to_cart_btn).to_be_visible(timeout=15000)

        print("Product page opened successfully")


    # =====================================
    # TEST 06 - ADD TO CART
    # =====================================

    def test_06_add_to_cart(self, shared_page: Page):

        print("\n=== TEST 06: ADD TO CART ===")

        size_item = shared_page.locator(
            '[data-test-id="qa-size-item"]'
        ).first

        size_item.wait_for(
            state="visible",
            timeout=10000
        )

        size_item.click()

        print("Size selected")

        add_btn = shared_page.locator(
            '[data-test-id="qa-add-to-cart-button"]'
        )

        add_btn.click()

        print("Clicked Add To Cart")

        shared_page.wait_for_load_state("networkidle")

        checkout_text = shared_page.locator(
            'text=לתשלום'
        )

        expect(checkout_text.first).to_be_visible(timeout=15000)

        print("Product added to cart successfully")


    # =====================================
    # TEST 07 - OPEN CART
    # =====================================

    def test_07_open_cart(self, shared_page: Page):

        print("\n=== TEST 07: OPEN CART ===")

        try:

            # פתיחת עמוד העגלה
            shared_page.goto(
                "https://www.terminalx.com/checkout/cart",
                wait_until="networkidle"
            )

            shared_page.wait_for_timeout(3000)

            current_url = shared_page.url

            print(f"Current URL: {current_url}")

            # וידוא שאנחנו באזור של cart
            assert "cart" in current_url.lower()

            # כמה אפשרויות שונות לאימות שהעגלה קיימת
            checkout_btn = shared_page.locator(
                'button:has-text("לתשלום")'
            )

            cart_items = shared_page.locator(
                '[data-test-id="qa-cart-item"]'
            )

            quantity_dropdown = shared_page.locator(
                'select'
            )

            empty_cart_text = shared_page.locator(
                'text=סל הקניות שלך ריק'
            )

            # אם אחד מהם קיים → הטסט עובר
            cart_exists = (
                checkout_btn.count() > 0 or
                cart_items.count() > 0 or
                quantity_dropdown.count() > 0 or
                empty_cart_text.count() > 0
            )

            assert cart_exists

            print("Cart page opened successfully")

        except Exception as e:

            print(f"TEST FAILED: {e}")

            # צילום מסך אוטומטי
            shared_page.screenshot(
                path="error_test_07_cart.png"
            )

            raise


    # =====================================
    # TEST 08 - CHANGE QUANTITY
    # =====================================

    def test_08_change_quantity(self, shared_page: Page):

        print("\n=== TEST 08: CHANGE QUANTITY ===")

        shared_page.goto(
            "https://www.terminalx.com/checkout/cart"
        )

        shared_page.wait_for_load_state("networkidle")

        quantity_dropdown = shared_page.locator(
            'select'
        ).first

        try:

            quantity_dropdown.select_option("4")

            print("Quantity changed successfully")

        except Exception as error:

            pytest.fail(
                f"Failed to update quantity: {error}"
            )

        print("Quantity update test passed")


    # =====================================
    # TEST 09 - REMOVE ITEM
    # =====================================

    def test_09_remove_item(self, shared_page: Page):

        print("\n=== TEST 09: REMOVE ITEM ===")

        shared_page.goto(
            "https://www.terminalx.com/checkout/cart"
        )

        shared_page.wait_for_load_state("networkidle")

        remove_btn = shared_page.locator(
            'button.remove_wqPe'
        ).first

        remove_btn.click(force=True)

        shared_page.wait_for_load_state("networkidle")

        shared_page.wait_for_timeout(3000)

        is_empty = shared_page.get_by_text(
            "סל הקניות שלך ריק"
        ).is_visible()

        redirected = (
            "checkout/cart" not in shared_page.url
        )

        assert is_empty or redirected

        print("Item removed successfully")


    # =====================================
    # TEST 10 - NAVIGATION MENU
    # =====================================

    def test_10_navigation_menu(self, shared_page: Page):

        print("\n=== TEST 10: NAVIGATION MENU ===")

        shared_page.goto(BASE_URL)

        women_menu = shared_page.get_by_role(
            "link",
            name="נשים"
        ).first

        women_menu.hover()

        dresses_link = shared_page.get_by_role(
            "link",
            name="שמלות"
        ).first

        dresses_link.click()

        shared_page.wait_for_load_state("networkidle")

        assert "women" in shared_page.url.lower()

        print("Navigation menu test passed")


    # =====================================
    # TEST 11 - ADD TO WISHLIST
    # =====================================

    def test_11_add_to_wishlist(self, shared_page: Page):

        print("\n=== TEST 11: ADD TO WISHLIST ===")

        shared_page.goto(BASE_URL)

        handle_popups(shared_page)

        search_product(shared_page, "nike")

        products = shared_page.locator(
            '[data-test-id="qa-product-link"]'
        )

        products.first.click()

        shared_page.wait_for_load_state("networkidle")

        print("Product page opened")

        wishlist_btn = shared_page.locator(
            '[class*="wishlist"], [class*="favorite"], [data-test-id*="wish"]'
        )

        try:

            wishlist_btn.first.wait_for(
                state="visible",
                timeout=10000
            )

            wishlist_btn.first.click(force=True)

            print("Wishlist button clicked")

        except TimeoutError:

            pytest.fail(
                "Wishlist button was not found"
            )

        shared_page.wait_for_timeout(3000)

        print("Wishlist test passed")
