# scraper_11880.py

import time
from playwright.sync_api import sync_playwright

def scrape_11880(keyword: str, city: str, max_pages: int, max_entries: int = None):
    """
    1. Konstruiert für jede Seite eine URL wie: https://www.11880.com/suche/{keyword}/{city}?page={page_num}
    2. Ruft jede Suchergebnisseite auf und sammelt die Detail-Links
    3. Öffnet jede Detail-Seite und extrahiert Name, Website und E-Mail
    4. Gibt eine Liste von Dicts zurück: [{'name':..., 'email':..., 'website':...}, ...]
    """

    all_results = []
    entries_counter = 0

    with sync_playwright() as p:
        # Im sichtbaren Modus starten, damit du siehst, was passiert:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        for page_num in range(1, max_pages + 1):
            if max_entries is not None and entries_counter >= max_entries:
                break

            # Direkte URL zur Suchergebnisseite
            search_url = f"https://www.11880.com/suche/{keyword}/{city}?page={page_num}"
            print(f"Rufe auf: {search_url}")
            page.goto(search_url, timeout=60000)

            # Evtl. Cookie-Banner wegklicken
            time.sleep(2)
            try:
                page.locator("button:has-text('Akzeptieren')").click(timeout=3000)
                print("Cookie-Banner geklickt.")
                time.sleep(1)
            except:
                pass

            # Ergebnis-Links finden
            links = page.locator("a.result-list-entry-title.entry-detail-link")
            count = links.count()
            print(f"Gefundene Einträge auf Seite {page_num}: {count}")

            for i in range(count):
                if max_entries is not None and entries_counter >= max_entries:
                    break

                title = links.nth(i).text_content() or "Unbekannt"
                href = links.nth(i).get_attribute("href")
                if not href:
                    continue

                detail_url = "https://www.11880.com" + href
                print(f"[{i+1}/{count}] {title.strip()} → {detail_url}")

                # Jetzt die Detailseite öffnen und auswerten
                data = scrape_detail_page(context, detail_url)
                if data:
                    all_results.append(data)
                    entries_counter += 1

            time.sleep(1)  # kleine Pause zwischen den Seiten

        browser.close()

    return all_results


def scrape_detail_page(context, url: str):
    page = context.new_page()
    try:
        page.goto(url, timeout=15000)
        page.wait_for_load_state("networkidle")

        name = "Unbekannt"
        email = None
        website = None
        address = None

        # (Beispiel) Name:
        name_elem = page.locator("h1.company-name, h1")
        if name_elem.count() > 0:
            name = name_elem.first.text_content().strip()

        # (Beispiel) E-Mail:
        email_label = page.locator("#box-email-link .entry-detail-list__label")
        if email_label.count() > 0:
            raw_text = email_label.first.text_content().strip()
            if "@" in raw_text:
                email = raw_text

        # (Beispiel) Website:
        website_el = page.locator("a.tracking--entry-detail-website-link")
        if website_el.count() > 0:
            website = website_el.first.get_attribute("href")

        if not website:
            fallback_website = page.locator('[data-track-event="URL"]')
            if fallback_website.count() > 0:
                website = fallback_website.first.get_attribute("href")

        # (Neu) Adresse als ganzer Block
        address_container = page.locator('div[title="Adresse"]')
        if address_container.count() > 0:
            raw_address = address_container.first.inner_text()
            # Leerzeichen/Sonderzeichen aufräumen (Zeilenumbrüche etc.)
            # Für Excel oder CSV wollen wir das oft in einer Zeile
            address = " ".join(raw_address.split())

        page.close()

        return {
            "name": name,
            "email": email,
            "website": website,
            "address": address
        }

    except Exception as e:
        print(f"Fehler bei Detailseite {url}: {e}")
        page.close()
        return None
