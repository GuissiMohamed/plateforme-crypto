# collector/tasks.py

from celery import Celery
from collector.db import init_db
from collector.core import collect_once


# Configuration de l'application Celery
# 'broker' : adresse de RabbitMQ (guest/guest est le compte par défaut)
app = Celery(
    "crypto_collector",
    broker="amqp://guest:guest@localhost:5672//",
    backend="rpc://",
)

# Optionnel : timezone
app.conf.timezone = "UTC"


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """
    Fonction appelée au démarrage de Celery pour configurer les tâches périodiques.
    Ici, on programme la tâche 'collect_market_data' toutes les 300 secondes (5 min).
    """
    sender.add_periodic_task(
        300.0,                      # toutes les 300 secondes = 5 minutes
        collect_market_data.s(),    # la tâche à exécuter
        name="Collecte des données de marché toutes les 5 minutes",
    )


@app.task
def collect_market_data():
    """
    Tâche Celery qui initialise la base (au cas où)
    puis lance une collecte.
    """
    init_db()
    collect_once()
