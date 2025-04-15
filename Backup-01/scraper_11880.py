import requests
from bs4 import BeautifulSoup
import time
from models import Business
from logger import log

BASE_URL = "https://www.11880.com"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def scrape_11880(query: str, city: str, max_pages=2) -> list[Business]:
    businesses = []

    for page in range(1, max_pages + 1):
        url = f"{BASE_URL}/suche/{query}/{city}?page={page}"
        log(f"Scrape: {url}")

        res = requests.get(url, headers=HEADERS)
        if res.status_code != 200:
            log(f"Fehler bei Anfrage: {url}", level="ERROR")
            continue

        soup = BeautifulSoup(res.text, "html.parser")
        results = soup.find_all("article", class_="mod-ResultList__Item")

        if not results:
            log(f"Keine Einträge gefunden auf Seite {page} für {query} in {city}", level="WARNING")
            continue

        for item in results:
            # Link zur Detailseite extrahieren
            link_tag = item.find("a", class_="mod-ResultList__TitleLink")
            if not link_tag or "href" not in link_tag.attrs:
                continue

            detail_url = BASE_URL + link_tag["href"]
            business = scrape_11880_detail(detail_url)
            if business:
                businesses.append(business)

        time.sleep(1)

    return businesses


def scrape_11880_detail(detail_url: str) -> Business | None:
    log(f"→ Detail: {detail_url}")

    try:
        res = requests.get(detail_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        name_tag = soup.find("h1")
        name = name_tag.get_text(strip=True) if name_tag else "Unbekannt"

        address_tag = soup.find("div", class_="mod-AdresseKompakt__Adresse")
        address = address_tag.get_text(strip=True) if address_tag else None

        phone_tag = soup.find("a", class_="mod-Communication__PhoneNumber")
        phone = phone_tag.get_text(strip=True) if phone_tag else None

        website_tag = soup.find("a", class_="tracking--entry-detail-website-link")
        website = website_tag["href"] if website_tag and "href" in website_tag.attrs else None

        return Business(
            name=name,
            address=address,
            phone=phone,
            website=website,
            source="11880"
        )
    except Exception as e:
        log(f"Fehler bei Detailseite: {detail_url} – {e}", level="ERROR")
        return None
