# eval_websites.py

"""
Erweiterte Version, um veraltete Websites mit zusätzlichen Heuristiken
auszuwerten.  
Neue Kriterien (jeweils Boolean‑Flag + Score‑Beitrag):
  * uses_bootstrap_css      (+10)
  * uses_jquery             (+10)
  * uses_deprecated_tags    (+15)  <font>, <center>, …
  * missing_semantic_html5  (+15)  Fehlen von <header>, <main>, …
  * uses_table_layout       (+20)  viele <table>-Tags als Layout‑Indikator
  * large_page_size         (+15)  > 2 MB Gesamtgröße
  * missing_meta_charset    (+5)
Die bisherigen Kriterien (https, viewport, HTML 4 Doctype) bleiben bestehen.

Gewichtungen sind bewusst grob gehalten und können je nach Bedarf angepasst
werden.
"""

import csv
import os
import re
from typing import Dict

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Kern‑Funktion --------------------------------------------------------------
# ---------------------------------------------------------------------------

def evaluate_website(url: str) -> Dict[str, object]:
    """Bewertet eine Website anhand vieler einfacher Heuristiken."""

    # Basis‑Kriterium A – HTTPS?
    uses_https = url.lower().startswith("https://")

    try:
        resp = requests.get(url, timeout=10, verify=False)
        resp.raise_for_status()
    except Exception as exc:
        print(f"Fehler beim Aufruf von {url}: {exc}")
        # Wenn gar nicht erreichbar: Maximaler Score (unbrauchbar)
        return {
            "reachable": False,
            "uses_https": uses_https,
            "has_viewport": False,
            "doctype_html4": False,
            "uses_bootstrap_css": False,
            "uses_jquery": False,
            "uses_deprecated_tags": False,
            "missing_semantic_html5": True,
            "uses_table_layout": False,
            "large_page_size": True,
            "missing_meta_charset": True,
            "veraltet_score": 100,
        }

    html_text = resp.text
    soup = BeautifulSoup(html_text, "html.parser")
    raw_html_lower = html_text.lower()

    # Kriterium B – Meta Viewport
    has_viewport = bool(soup.find("meta", attrs={"name": "viewport"}))

    # Kriterium C – alter Doctype (HTML 4.x)
    doctype_html4 = "doctype html 4.0" in raw_html_lower or "doctype html 4.01" in raw_html_lower

    # -------------------------------------------------------------
    # Neue Kriterien
    # -------------------------------------------------------------

    # Kriterium D – Bootstrap‑CSS eingebunden?
    uses_bootstrap_css = any(
        "bootstrap" in (link.get("href") or "").lower() for link in soup.find_all("link", href=True)
    )

    # Kriterium E – jQuery (egal welche Version)
    uses_jquery = any(
        re.search(r"jquery(\.min)?\.js", (script.get("src") or ""), re.I)
        for script in soup.find_all("script", src=True)
    )

    # Kriterium F – veraltete Tags
    deprecated_tags = ["center", "font", "marquee", "blink"]
    uses_deprecated_tags = any(soup.find(tag) for tag in deprecated_tags)

    # Kriterium G – fehlen semantischer HTML5‑Tags
    semantic_tags = ["header", "nav", "main", "section", "article", "footer"]
    missing_semantic_html5 = not any(soup.find(tag) for tag in semantic_tags)

    # Kriterium H – Tabellen‑Layout (≥ 3 <table>)
    uses_table_layout = len(soup.find_all("table")) >= 3

    # Kriterium I – Große Seite (> 2 MB)
    large_page_size = len(resp.content) > 2 * 1024 * 1024

    # Kriterium J – fehlendes <meta charset="utf-8">
    missing_meta_charset = not soup.find("meta", attrs={"charset": re.compile(r"utf-8", re.I)})

    # -------------------------------------------------------------
    # Scoring
    # -------------------------------------------------------------
    veraltet_score = 0
    if not uses_https:
        veraltet_score += 20
    if not has_viewport:
        veraltet_score += 30
    if doctype_html4:
        veraltet_score += 50
    if uses_bootstrap_css:
        veraltet_score += 10
    if uses_jquery:
        veraltet_score += 10
    if uses_deprecated_tags:
        veraltet_score += 15
    if missing_semantic_html5:
        veraltet_score += 15
    if uses_table_layout:
        veraltet_score += 20
    if large_page_size:
        veraltet_score += 15
    if missing_meta_charset:
        veraltet_score += 5

    return {
        "reachable": True,
        "uses_https": uses_https,
        "has_viewport": has_viewport,
        "doctype_html4": doctype_html4,
        "uses_bootstrap_css": uses_bootstrap_css,
        "uses_jquery": uses_jquery,
        "uses_deprecated_tags": uses_deprecated_tags,
        "missing_semantic_html5": missing_semantic_html5,
        "uses_table_layout": uses_table_layout,
        "large_page_size": large_page_size,
        "missing_meta_charset": missing_meta_charset,
        "veraltet_score": veraltet_score,
    }


# ---------------------------------------------------------------------------
# CLI / Hauptprogramm --------------------------------------------------------
# ---------------------------------------------------------------------------

def main() -> None:
    base_dir = os.path.dirname(__file__)
    csv_input_path = os.path.join(base_dir, "ergebnisse.csv")
    csv_output_path = os.path.join(base_dir, "evaluation.csv")

    results = []
    with open(csv_input_path, newline="", encoding="utf-8") as fin:
        reader = csv.DictReader(fin, delimiter=";")
        print("Erkannte Spalten im CSV:", reader.fieldnames)

        for row in reader:
            website_url = (row.get("website") or "").strip()
            if not website_url or website_url == "WEB_NULL":
                # Keine Website vorhanden – direkt markieren
                row.update({
                    "reachable": False,
                    "uses_https": False,
                    "has_viewport": False,
                    "doctype_html4": False,
                    "uses_bootstrap_css": False,
                    "uses_jquery": False,
                    "uses_deprecated_tags": False,
                    "missing_semantic_html5": True,
                    "uses_table_layout": False,
                    "large_page_size": True,
                    "missing_meta_charset": True,
                    "veraltet_score": 100,
                })
            else:
                row.update(evaluate_website(website_url))

            results.append(row)

    # CSV mit allen Ergebnissen speichern
    with open(csv_output_path, "w", newline="", encoding="utf-8") as fout:
        fieldnames = list(results[0].keys())
        writer = csv.DictWriter(
            fout,
            fieldnames=fieldnames,
            delimiter=";",
            quotechar="\"",
            quoting=csv.QUOTE_ALL,
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"Fertig! Die Auswertung wurde in '{csv_output_path}' gespeichert.")


if __name__ == "__main__":
    main()
