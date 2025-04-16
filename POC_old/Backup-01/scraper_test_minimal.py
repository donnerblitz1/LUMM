from playwright.sync_api import sync_playwright
from logger import log  # oder einfach "print" verwenden
import time

def test_scrape_names(query: str, city: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        url = f"https://www.11880.com/suche/{query}/{city}?page=1"
        log(f"Öffne: {url}")
        page.goto(url, timeout=60000)
        page.wait_for_timeout(3000)

        # KORREKTER SELECTOR → manuell überprüft im Dev-Tool (Stand April 2025)
        firmeneintraege = page.locator("a.entry-detail-link.result-list-entry__name")

        anzahl = firmeneintraege.count()
        log(f"Gefundene Firmeneinträge: {anzahl}")

        for i in range(anzahl):
            name = firmeneintraege.nth(i).text_content()
            log(f"→ Firma {i+1}: {name}")

        browser.close()


if __name__ == "__main__":
    test_scrape_names("klempner", "frankfurt")
