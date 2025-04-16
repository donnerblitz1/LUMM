from config import SEARCH_TERMS, CITIES, MAX_PAGES
from scraper_11880_playwright import scrape_11880
from utils import export_to_csv, is_website_old
from logger import log

all_results = []

try:
    for term in SEARCH_TERMS:
        for city in CITIES:
            log(f"[•] Suche: {term} in {city}")
            results = scrape_11880(term, city, MAX_PAGES)
            if results:
                all_results.extend(results)

except KeyboardInterrupt:
    log("🛑 Manuell abgebrochen – speichere bisherigen Stand", level="WARNING")

finally:
    log(f"[✓] Gesamt gefunden: {len(all_results)}")

    if all_results:
        export_to_csv(all_results, "firmen_alle.csv")

        ohne_website = [b for b in all_results if not b.website]
        veraltet = [b for b in all_results if b.website and is_website_old(b.website)]

        export_to_csv(ohne_website, "firmen_ohne_website.csv")
        export_to_csv(veraltet, "firmen_veraltet.csv")

        log("[💾] Alle CSVs erfolgreich exportiert.")
    else:
        log("[!] Keine Daten zum Exportieren.", level="WARNING")
