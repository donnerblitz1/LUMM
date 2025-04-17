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

    Filtert vorher alle Einträge raus, bei denen sowohl MAIL_NULL als auch WEB_NULL ist.
    Existiert die Datei noch nicht, wird zuerst immer die vollständige
    Kopfzeile (HEADER) ausgegeben.
    """

    file_exists = os.path.exists(filename)

    # Nur die gültigen Einträge behalten
    filtered_data = []
    for entry in data_list:
        email = entry.get("email") or "MAIL_NULL"
        website = entry.get("website") or "WEB_NULL"
        if email != "MAIL_NULL" or website != "WEB_NULL":
            filtered_data.append(entry)

    # Datei schreiben (überschreiben!)
    with open(filename, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=HEADER,
            delimiter=";",
            quotechar="\"",
            quoting=csv.QUOTE_ALL,
            restval=""  # Leerstring für Felder, die nicht im Dict vorhanden sind
        )

        # Header schreiben
        writer.writeheader()

        for entry in filtered_data:
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
