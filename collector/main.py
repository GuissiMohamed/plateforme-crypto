# collector/main.py

import time
from datetime import datetime

from db import init_db
from core import collect_once


def main():
    print("Initialisation de la base de données…")
    init_db()

    interval_minutes = 5  # change à 1 pour tester plus vite

    print(f"Collecte périodique démarrée (toutes les {interval_minutes} minutes).")
    print("Appuie sur Ctrl+C pour arrêter le programme.")

    while True:
        try:
            collect_once()
        except Exception as e:
            print("Erreur pendant la collecte :", e)

        print(f"[{datetime.utcnow()}] Pause de {interval_minutes} minute(s)…")
        time.sleep(interval_minutes * 60)


if __name__ == "__main__":
    main()
