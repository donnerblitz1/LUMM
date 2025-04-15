from playwright.sync_api import sync_playwright


def snapshot_test(query: str, city: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        url = f"https://www.11880.com/suche/{query}/{city}?page=1"
        print(f"Gehe zu: {url}")
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)  # warte auf evtl. langsames JS

        # Screenshot
        page.screenshot(path="debug_screenshot.png", full_page=True)
        print("📸 Screenshot gespeichert als debug_screenshot.png")

        # HTML dump
        html = page.content()
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("📄 HTML gespeichert als debug_page.html")

        browser.close()


if __name__ == "__main__":
    snapshot_test("klempner", "frankfurt")
