# eval_websites.py

import csv
import requests
from bs4 import BeautifulSoup
import os

def evaluate_website(url):
    """
    Prüft einfache Kriterien, ob eine Seite veraltet sein könnte.
    Returnt ein Dict mit Booleans / Scores oder Ähnliches.
    """
    # Kriterium A: HTTPS?
    uses_https = url.lower().startswith("https://")

    try:
        # Aufruf mit Timeout
        r = requests.get(url, timeout=10, verify=False)  # verify=False, falls du SSL-Fehler ignorieren willst
        r.raise_for_status()
    except Exception as e:
        print(f"Fehler beim Aufruf von {url}: {e}")

        # Seite nicht erreichbar => Schlechtes Zeichen / unbrauchbar
        return {
            "reachable": False,
            "uses_https": uses_https,
            "has_viewport": False,
            "doctype_html4": False,
            "veraltet_score": 100  # Riesen Score => unbrauchbar
        }

    # Wenn wir hier sind, ist die Seite "erreichbar".
    soup = BeautifulSoup(r.text, "html.parser")

    # Kriterium B: Meta viewport (für mobiles Responsives Design)
    has_viewport = bool(soup.find("meta", attrs={"name": "viewport"}))

    # Kriterium C: Alte Doctype?
    # Einfache Suche im raw HTML
    raw_html = r.text.lower()
    doctype_html4 = ('doctype html 4.0' in raw_html) or ('doctype html 4.01' in raw_html)

    # Kleiner Score, je höher desto "veralteter"
    veraltet_score = 0
    if not uses_https:
        veraltet_score += 20
    if not has_viewport:
        veraltet_score += 30
    if doctype_html4:
        veraltet_score += 50

    return {
        "reachable": True,
        "uses_https": uses_https,
        "has_viewport": has_viewport,
        "doctype_html4": doctype_html4,
        "veraltet_score": veraltet_score
    }


def main():
    # Bestimme den Pfad zur ergebnisse.csv in demselben Ordner wie dieses Skript:
    base_dir = os.path.dirname(__file__)
    csv_input_path = os.path.join(base_dir, "ergebnisse.csv")
    csv_output_path = os.path.join(base_dir, "evaluation.csv")

    # Lies die CSV. Sie sollte Felder wie name;email;website;address haben.
    results = []
    with open(csv_input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')

        # Debug: Erkennte Spaltennamen ausgeben
        print("Erkannte Spalten im CSV:", reader.fieldnames)

        for row in reader:
            website_url = row.get("website", "").strip()
            if website_url == "WEB_NULL" or not website_url:
                # Keine Website
                row["reachable"] = False
                row["uses_https"] = False
                row["has_viewport"] = False
                row["doctype_html4"] = False
                row["veraltet_score"] = 100  # Schlechtes Zeichen
            else:
                # Website evaluieren
                eval_data = evaluate_website(website_url)
                row.update(eval_data)

            results.append(row)

    # Speichere die erweiterten Daten in eine neue CSV
    with open(csv_output_path, "w", newline="", encoding="utf-8") as fout:
        # Alle Keys aus dem ersten Datensatz => Spaltennamen
        fieldnames = list(results[0].keys())
        writer = csv.DictWriter(fout, fieldnames=fieldnames, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)

        writer.writeheader()
        for r in results:
            writer.writerow(r)

    print(f"Fertig! Die Auswertung wurde in '{csv_output_path}' gespeichert.")


if __name__ == "__main__":
    main()
