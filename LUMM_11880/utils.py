import csv
import os

# Der vollständige Header für die CSV-Datei
HEADER = [
    "name", "email", "website", "address",
    "reachable", "uses_https", "has_viewport",
    "doctype_html4", "veraltet_score",
]

def save_to_csv(data_list, filename="ergebnisse.csv"):
    """Schreibt die Einträge aus *data_list* in *filename*.

    Existiert die Datei noch nicht, wird zuerst immer die vollständige
    Kopfzeile (HEADER) ausgegeben.
    """

    file_exists = os.path.exists(filename)

    # Datei anhängen (oder neu anlegen) und sicherstellen, dass wir UTF‑8 und LF verwenden
    with open(filename, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=HEADER,
            delimiter=";",
            quotechar="\"",
            quoting=csv.QUOTE_ALL,
            restval=""  # Leerstring für Felder, die nicht im Dict vorhanden sind
        )

        # Header nur schreiben, wenn die Datei gerade neu angelegt wurde
        if not file_exists:
            writer.writeheader()

        for entry in data_list:
            row = {
                "name": entry.get("name", ""),
                "email": entry.get("email") or "MAIL_NULL",
                "website": entry.get("website") or "WEB_NULL",
                "address": entry.get("address") or "ADDR_NULL",
                "reachable": entry.get("reachable", ""),
                "uses_https": entry.get("uses_https", ""),
                "has_viewport": entry.get("has_viewport", ""),
                "doctype_html4": entry.get("doctype_html4", ""),
                "veraltet_score": entry.get("veraltet_score", ""),
            }
            writer.writerow(row)
