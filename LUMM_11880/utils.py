# utils.py
import csv
import os

def save_to_csv(data_list, filename="ergebnisse.csv"):
    """
    Speichert eine Liste von Dicts in eine CSV-Datei:
    Dict sollte mind. die Keys "name", "email", "website" haben.
    """
    file_exists = os.path.exists(filename)

    with open(filename, mode="a", newline="", encoding="utf-8") as csv_file:
        fieldnames = ["name", "email", "website"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for entry in data_list:
            writer.writerow(entry)
