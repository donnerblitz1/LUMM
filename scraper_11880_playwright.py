from playwright.sync_api import sync_playwright
from models import Business
from logger import log
import time
from utils import export_to_csv, is_website_old

def scrape_11880(query: str, city: str, max_pages=1) -> list[Business]:
    businesses = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            main_page = context.new_page()

            for page_num in range(1, max_pages + 1):
                url = f"https://www.11880.com/suche/{query}/{city}?page={page_num}"
                log(f"Scrape: {url}")
                main_page.goto(url, timeout=60000)
                main_page.wait_for_timeout(2000)

                detail_links = main_page.locator("a.result-list-entry-title.entry-detail-link")
                count = detail_links.count()
                log(f"Gefundene Firmen auf Seite {page_num}: {count}")

                for i in range(count):
                    try:
                        title = detail_links.nth(i).text_content()
                        href = detail_links.nth(i).get_attribute("href")
                        if not href:
                            continue

                        full_url = "https://www.11880.com" + href
                        log(f"[{i+1}/{count}] {title.strip()} → {full_url}")

                        business = scrape_detail_page(context, full_url)
                        if business:
                            log(f"✅ Gespeichert: {business.name} | {business.website}")
                            businesses.append(business)
                        else:
                            log(f"⚠️ Kein Business-Objekt zurückgegeben für {full_url}")

                        time.sleep(1)

                    except KeyboardInterrupt:
                        log("🛑 Abbruch innerhalb des Scrapes erkannt – Rückgabe der Ergebnisse", level="WARNING")
                        browser.close()
                        return businesses

            browser.close()
    except KeyboardInterrupt:
        log("🛑 Scraper komplett abgebrochen", level="WARNING")
        return businesses
    except Exception as e:
        log(f"❌ Fehler beim Scrape: {e}", level="ERROR")

    return businesses



def scrape_detail_page(context, url: str) -> Business | None:
    log(f"→ Öffne Detailseite: {url}")
    try:
        page = context.new_page()
        page.goto(url, timeout=10000)

        # Warte auf Seitentitel
        try:
            page.wait_for_selector("h1", timeout=3000)
        except:
            log("❗️Timeout beim Laden der Seite – kein <h1> gefunden", level="WARNING")
            page.close()
            return None

        # Hilfsfunktionen
        def safe_text(selector: str, timeout=2000):
            try:
                return page.locator(selector).first.text_content(timeout=timeout).strip()
            except:
                return None

        def safe_attr(selector: str, attr: str, timeout=2000):
            try:
                return page.locator(selector).first.get_attribute(attr)
            except:
                return None

        name = safe_text("h1", timeout=1000)
        phone = safe_text("a.mod-Communication__PhoneNumber")
        address = safe_text("div.entry-detail-list__label >> nth=1")

        # Website-Link wie vorher
        try:
            page.wait_for_selector("a.tracking--entry-detail-website-link", timeout=3000)
            website_el = page.locator("a.tracking--entry-detail-website-link")
            website = website_el.first.get_attribute("href") if website_el.count() > 0 else None
        except:
            website = None

        # 📧 E-Mail von Detailseite extrahieren
        try:
            page.wait_for_selector("#box-email-link", timeout=2000)
            email = page.locator("#box-email-link .entry-detail-list__label").first.text_content().strip()
        except:
            email = None

        log(f"🔎 Detaildaten: name={name}, phone={phone}, email={email}, website={website}, address={address}")

        page.close()

        return Business(
            name=name or "Unbekannt",
            address=address,
            phone=phone,
            email=email,
            website=website,
            source="11880"
        )

    except Exception as e:
        log(f"Fehler bei Detailseite {url}: {e}", level="ERROR")
        return None



