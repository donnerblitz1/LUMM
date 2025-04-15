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



#### checken ob die website möglicherweise veraltett is
def is_website_old(url: str) -> bool:
    if not url:
        return True  # keine Website = alt by default

    try:
        res = requests.get(url, timeout=5)
        html = res.text.lower()

        # Check: Mobiloptimierung
        if '<meta name="viewport"' not in html:
            return True

        # Check: Kein <title> oder völlig leer?
        if "<title>" not in html or "<title></title>" in html:
            return True

        return False  # modern genug
    except:
        return True  # Fehler = potenziell alt/kaputt



#def filter_bad_websites(businesses: list[Business]) -> list[Business]:
#    return [b for b in businesses if not b.website or is_website_old(b.website)]








##### CSV Dateien erstellen aus der Analyse
def clean_text(text: str) -> str:
    if not text:
        return ""
    return " ".join(text.split()).strip()  # entfernt Zeilenumbrüche, Tabs, doppelte Leerzeichen

def export_to_csv(data: list[Business], filename="export.csv"):
    if not data:
        log(f"[!] Export fehlgeschlagen: keine Daten für {filename}", level="WARNING")
        return

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=",")  # Optional: delimiter=";" für Excel in DE
        writer.writerow(["Name", "Adresse", "Telefon", "Website", "E-Mail", "Quelle"])

        for b in data:
            writer.writerow([
                clean_text(b.name),
                clean_text(b.address),
                clean_text(b.phone),
                clean_text(b.website),
                clean_text(b.email),
                clean_text(b.source),
            ])

    log(f"[✓] Daten exportiert nach {filename}")
