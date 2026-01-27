from playwright.sync_api import sync_playwright, expect

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            # Go to home page
            page.goto("http://localhost:5000")

            # Check title
            expect(page).to_have_title("FashionHub")

            # Check for header
            expect(page.get_by_role("heading", name="FashionHub")).to_be_visible()

            # Check for products
            expect(page.get_by_text("Classic White T-Shirt")).to_be_visible()
            expect(page.get_by_text("Blue Denim Jeans")).to_be_visible()

            # Check navbar cart
            expect(page.get_by_text("Cart (0)")).to_be_visible()

            # Take screenshot
            page.screenshot(path="verification/home.png")
            print("Verification successful, screenshot saved.")
        except Exception as e:
            print(f"Verification failed: {e}")
            raise e
        finally:
            browser.close()

if __name__ == "__main__":
    run()
