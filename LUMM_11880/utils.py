# utils.py

import csv
import os

def save_to_csv(data_list, filename="ergebnisse.csv"):
    import csv
    import os

    file_exists = os.path.exists(filename)

    # Wir wollen jetzt 4 Spalten
    fieldnames = ["name", "email", "website", "address"]

    with open(filename, mode="a", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file,
                                fieldnames=fieldnames,
                                delimiter=';',
                                quotechar='"',
                                quoting=csv.QUOTE_ALL)

        if not file_exists:
            writer.writeheader()

        for entry in data_list:
            # Fehlende Werte (None) durch ..._NULL ersetzen
            email_value = entry["email"] if entry.get("email") else "MAIL_NULL"
            website_value = entry["website"] if entry.get("website") else "WEB_NULL"
            address_value = entry["address"] if entry.get("address") else "ADDR_NULL"

            row = {
                "name": entry["name"] or "",
                "email": email_value,
                "website": website_value,
                "address": address_value
            }
            writer.writerow(row)
