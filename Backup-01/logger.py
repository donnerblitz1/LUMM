import datetime

LOGFILE = "scraper_log.txt"

def log(msg: str, level="INFO"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] [{level}] {msg}"
    print(entry)
    with open(LOGFILE, "a", encoding="utf-8") as f:
        f.write(entry + "\n")
