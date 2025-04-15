import re
import requests
from bs4 import BeautifulSoup
import csv
from models import Business
from logger import log




#### Email adresse von der Seite lesen
def extract_email_from_website(url):
    try:
        r = requests.get(url, timeout=5)
        emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", r.text)
        return emails[0] if emails else None
    except:
        return None




##### CSV Dateien erstellen aus der Analyse
def export_to_csv(data: list[Business], filename="export.csv"):
    if not data:
        log(f"[!] Export fehlgeschlagen: keine Daten für {filename}", level="WARNING")
        return

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";", quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["Name", "Adresse", "Telefon", "Website", "E-Mail", "Quelle"])
        for b in data:
            writer.writerow([
                b.name or "",
                b.address or "",
                b.phone or "",
                b.website or "",
                b.email or "",
                b.source or ""
            ])

    log(f"[✓] Daten exportiert nach {filename}")

def is_website_old(url: str) -> bool:
    try:
        res = requests.get(url, timeout=5)
        html = res.text.lower()
        return '<meta name="viewport"' not in html or "<title>" not in html
    except:
        return True