# main.py

from config import SEARCH_KEYWORDS, SEARCH_CITIES, MAX_PAGES, MAX_ENTRIES
from scraper_11880 import scrape_11880
from utils import save_to_csv

def main():
    all_data = []

    for keyword in SEARCH_KEYWORDS:
        for city in SEARCH_CITIES:
            print(f"Starte Suche: Keyword={keyword}, City={city}")
            results = scrape_11880(keyword, city, MAX_PAGES, MAX_ENTRIES)

            print(f"Gefundene Datensätze für {keyword} / {city}: {len(results)}")
            # Direkt in CSV speichern, damit wir auch Zwischenergebnisse nicht verlieren
            if results:
                save_to_csv(results, filename="ergebnisse.csv")

            # Du kannst sie auch sammeln und am Ende auf einmal speichern.
            # all_data.extend(results)

    print("Alles fertig!")

if __name__ == "__main__":
    main()
