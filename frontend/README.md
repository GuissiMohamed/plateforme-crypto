📝 README – Plateforme Crypto
🚀 Présentation

Cette application est une plateforme d’analyse crypto complète comprenant :

Une API backend FastAPI

Une interface frontend React

Un collector CryptoRabbit (collecte des prix via API externe)

Un système d’alertes / notifications Discord

Une base de données PostgreSQL

Une orchestration Docker complète

🔧 1. Technologies utilisées
Composant	Technologie
Frontend	React + TailwindCSS
Backend	FastAPI + SQLAlchemy
Base de données	PostgreSQL
Collecte prix	CryptoRabbit (Python)
Alertes	Alert Checker Python + Discord Webhook
Conteneurs	Docker & Docker Compose
📦 2. Installation (mode manuel)
2.1. Cloner le projet
git clone https://github.com/GuissiMohamed/plateforme-crypto.git
cd plateforme-crypto

2.2. Installer la base de données PostgreSQL
MacOS (Homebrew) :
brew install postgresql
brew services start postgresql

Créer l’utilisateur + base :
psql
CREATE USER crypto_user WITH PASSWORD 'crypto_pass';
CREATE DATABASE cryptodb OWNER crypto_user;

2.3. Installer l’environnement backend
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt


Toutes les dépendances seront installées : FastAPI, SQLAlchemy, bcrypt, passlib, pydantic, requests, etc.

2.4. Installer le frontend
cd ../frontend
npm install

▶️ 3. Démarrage manuel de l’application
3.1. Démarrer le backend
cd backend
source .venv/bin/activate
uvicorn main:app --reload


Backend accessible ici :

👉 http://127.0.0.1:8000

👉 http://127.0.0.1:8000/docs
 (Swagger)

3.2. Démarrer le frontend
cd frontend
npm start


Frontend accessible ici :

👉 http://localhost:3000

3.3. Démarrer CryptoRabbit (collector)
cd collector
source ../backend/.venv/bin/activate
python main.py


Ce service :

✔ récupère les prix de +100 cryptos
✔ met à jour la base toutes les 5 minutes
✔ enregistre MarketCap, Volume, Price, Change24h

3.4. Démarrer l’Alert Checker
cd backend
source .venv/bin/activate
python alert_checker.py


Ce service :

✔ surveille les alertes (above / below / change_24h)
✔ envoie des notifications dans la DB
✔ envoie dans Discord via webhook si configuré

🐳 4. Démarrage via Docker (recommandé)

Le projet inclut un docker-compose.yml permettant de lancer :

✔ backend
✔ frontend
✔ PostgreSQL
✔ collector
✔ alert checker

🌐 Démarrer toute la plateforme :
docker-compose up --build


Ensuite :

Service	URL
Backend FastAPI	http://localhost:8000

Swagger	http://localhost:8000/docs

Frontend React	http://localhost:3000

PostgreSQL	localhost:5432
Collector CryptoRabbit	(service Python auto-démarré)
Alert Checker	(service Python auto-démarré)
⚙️ 5. Variables d’environnement

Créer un fichier .env à la racine :

POSTGRES_USER=crypto_user
POSTGRES_PASSWORD=crypto_pass
POSTGRES_DB=cryptodb

DATABASE_URL=postgresql+psycopg2://crypto_user:crypto_pass@db:5432/cryptodb

SECRET_KEY="super_secret_key_change_me"

📂 6. Structure du projet
plateforme-crypto/
│
├── backend/
│   ├── main.py
│   ├── auth.py
│   ├── db.py
│   ├── alert_checker.py
│   ├── schemas.py
│   ├── requirements.txt
│
├── collector/
│   ├── core.py
│   ├── main.py
│   ├── db.py
│
├── frontend/
│   ├── src/
│   ├── package.json
│
├── docker-compose.yml
├── README.md

🧪 7. Tests API rapides
Vérifier que le backend tourne :
curl http://localhost:8000/health


Réponse :

{"status": "ok"}

Tester le login :
curl -X POST http://localhost:8000/auth/login \
  -d "username=test@test.com&password=123456"

🚀 8. Déploiement

Tu pourras facilement déployer via :

✔ Docker Compose sur un VPS
✔ Railway / Render
✔ AWS ECS
✔ Heroku (container)

Je peux te préparer un script de déploiement, si tu veux.

🎯 9. Commandes utiles
Redémarrer PostgreSQL (MacOS) :
brew services restart postgresql

Supprimer tout Docker :
docker-compose down -v

Rebuild complet :
docker-compose up --build