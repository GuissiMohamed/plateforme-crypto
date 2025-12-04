# backend/alert_checker.py
import time
from datetime import datetime
import requests
from sqlalchemy.orm import Session

from db import SessionLocal, Asset, Price, Alert, Notification, User

# 🔔 Mets ici ton vrai webhook Discord
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1445956170010595479/MrXYLb2UV6VdZ_EifB8LRtseR_7kjZr07FxdSa8VrXFNdd9JDSejJDB13CGAVDZxqhBh"  # ← remplace par le tien

def send_discord(message: str):
    """
    Envoie un message au webhook Discord.
    """
    if not DISCORD_WEBHOOK:
        print("⚠ Aucun webhook Discord configuré")
        return

    try:
        requests.post(DISCORD_WEBHOOK, json={"content": message})
        print("📨 Notification Discord envoyée")
    except Exception as e:
        print("❌ Erreur Discord :", e)

def check_alerts_once():
    """
    Vérifie toutes les alertes et déclenche si nécessaire.
    """
    db: Session = SessionLocal()

    print(f"\n[{datetime.utcnow()}] Vérification des alertes…")

    alerts = db.query(Alert).all()

    for alert in alerts:
        asset_id = alert.asset_id

        # Récupérer dernier prix
        price = (
            db.query(Price)
            .filter(Price.asset_id == asset_id)
            .order_by(Price.timestamp.desc())
            .first()
        )

        if not price:
            continue

        triggered = False

        # === Conditions d’alertes ===
        if alert.alert_type == "above" and price.price_usd > alert.target_value:
            triggered = True

        if alert.alert_type == "below" and price.price_usd < alert.target_value:
            triggered = True

        if alert.alert_type == "change_24h" and price.change_24h_pct is not None:
            if abs(price.change_24h_pct) >= alert.target_value:
                triggered = True

        if triggered:
            # → Création d’une notification interne
            notif = Notification(
                user_id=alert.user_id,
                asset_id=alert.asset_id,
                message=f"Alerte : {asset_id} a atteint {alert.target_value}",
            )
            db.add(notif)
            db.commit()

            # → Notification Discord
            send_discord(f"🔔 Alerte Crypto : {asset_id} a atteint {alert.target_value} USD !")

            print(f"⚡ Alerte déclenchée pour {asset_id} !")

    db.close()


def main():
    """
    Boucle continue : vérifie toutes les X secondes.
    """
    interval_seconds = 60  # vérifie toutes les minutes

    print("🚀 Vérificateur d’alertes démarré")
    print("⚡ Contrôle automatique toutes les 60 secondes")

    while True:
        try:
            check_alerts_once()
        except Exception as e:
            print("❌ Erreur dans le vérificateur :", e)

        time.sleep(interval_seconds)


if __name__ == "__main__":
    main()
