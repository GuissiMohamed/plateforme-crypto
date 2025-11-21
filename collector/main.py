# collector/main.py

import time
import logging
import requests
from datetime import datetime

from db import SessionLocal, init_db, Asset, Price

# URL CoinGecko de base (sans les paramètres dans la chaîne)
API_URL = "https://api.coingecko.com/api/v3/coins/markets"

# Intervalle entre deux collectes (en minutes)
COLLECTION_INTERVAL_MINUTES = 5

# Configuration du logging (afficher des infos lisibles dans la console)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def fetch_assets():
    """
    Appelle l'API CoinGecko et renvoie la liste des cryptomonnaies.
    """
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",        # classer par market cap
        "per_page": 100,                   # top 100
        "page": 1,
        "price_change_percentage": "24h",  # inclure la variation sur 24h
    }

    headers = {
        "Accept": "application/json",
        "User-Agent": "crypto-collector-student-project/1.0",
    }

    response = requests.get(API_URL, params=params, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()
    return data  # CoinGecko renvoie directement une liste de cryptos


def save_assets_to_db(assets_data):
    """
    Sauvegarde les cryptos et leurs prix dans la base de données.
    """
    session = SessionLocal()

    try:
        for item in assets_data:
            asset_id = item["id"]              # ex: "bitcoin"
            symbol = item["symbol"].upper()    # ex: "BTC"
            name = item["name"]                # ex: "Bitcoin"

            # Prix et autres infos
            price_usd = item.get("current_price")
            market_cap_usd = item.get("market_cap")
            volume_24h_usd = item.get("total_volume")
            change_24h_pct = item.get("price_change_percentage_24h")

            # Vérifier si l'asset existe déjà
            asset = session.get(Asset, asset_id)
            if asset is None:
                asset = Asset(
                    id=asset_id,
                    symbol=symbol,
                    name=name,
                )
                session.add(asset)

            # Historique des prix
            price = Price(
                asset_id=asset_id,
                price_usd=price_usd,
                market_cap_usd=market_cap_usd,
                volume_24h_usd=volume_24h_usd,
                change_24h_pct=change_24h_pct,
                timestamp=datetime.utcnow(),
            )
            session.add(price)

        session.commit()
        logger.info("Enregistrement en base OK pour %s cryptos", len(assets_data))
    except Exception:
        session.rollback()
        logger.exception("Erreur lors de l'enregistrement en base")
        raise
    finally:
        session.close()


def run_collection_once():
    """
    Effectue une collecte complète : API -> base de données.
    """
    logger.info("Récupération des données depuis CoinGecko…")
    assets = fetch_assets()
    logger.info("%s cryptomonnaies récupérées.", len(assets))

    logger.info("Enregistrement en base de données…")
    save_assets_to_db(assets)
    logger.info("Collecte terminée ✅")


def main():
    logger.info("Initialisation de la base de données…")
    init_db()

    logger.info(
        "Démarrage de la collecte périodique toutes les %s minutes",
        COLLECTION_INTERVAL_MINUTES,
    )

    while True:
        try:
            run_collection_once()
        except Exception:
            # On logue l'erreur mais on ne casse pas la boucle
            logger.error("La collecte a échoué, on réessaiera au prochain intervalle.")

        logger.info(
            "Pause de %s minutes avant la prochaine collecte…",
            COLLECTION_INTERVAL_MINUTES,
        )
        time.sleep(COLLECTION_INTERVAL_MINUTES * 60)


if __name__ == "__main__":
    main()
