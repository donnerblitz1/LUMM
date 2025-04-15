from config import SEARCH_TERMS, CITIES, MAX_PAGES
from scraper_11880_playwright import scrape_11880
from utils import export_to_csv, filter_bad_websites
from logger import log

all_results = []

for term in SEARCH_TERMS:
    for city in CITIES:
        log(f"[•] Suche: {term} in {city}")
        results = scrape_11880(term, city, MAX_PAGES)
        all_results.extend(results)

log(f"[✓] Gesamt gefunden: {len(all_results)}")

if all_results:
    export_to_csv(all_results, "firmen_alle.csv")

    bad_sites = filter_bad_websites(all_results)
    log(f"[⚠] Veraltet/Keine Website: {len(bad_sites)}")
    export_to_csv(bad_sites, "firmen_veraltet.csv")
else:
    log("[!] Keine Daten zum Exportieren.", level="WARNING")
