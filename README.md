README – Plateforme Crypto
1. Présentation

Ce projet est une plateforme complète de suivi et d’analyse des cryptomonnaies, développée dans un cadre académique.
Il met en œuvre une architecture moderne intégrant un backend API, un frontend web, un système de collecte automatisée des données, un mécanisme d’alertes, ainsi qu’une démarche complète de tests et de qualité logicielle.

La plateforme comprend :

Une API Backend développée avec FastAPI

Une interface Frontend développée avec React

Un collector de données de marché (CryptoRabbit)

Un système d’alertes et de notifications (Discord)

Une base de données relationnelle PostgreSQL

Une orchestration via Docker et Docker Compose

Un pipeline de tests et de contrôle qualité automatisé

2. Technologies utilisées
Composant	Technologie
Frontend	React, Vite, TailwindCSS
Backend	FastAPI, SQLAlchemy
Base de données	PostgreSQL
Collecte des données	Python (CryptoRabbit)
Alertes	Python, Discord Webhook
Tests	Pytest, pytest-cov, k6
CI/CD	GitHub Actions
Conteneurisation	Docker, Docker Compose
3. Installation (mode manuel)
3.1 Clonage du projet
git clone https://github.com/GuissiMohamed/plateforme-crypto.git
cd plateforme-crypto

3.2 Installation de PostgreSQL

Sous macOS (Homebrew) :

brew install postgresql
brew services start postgresql


Création de l’utilisateur et de la base :

CREATE USER crypto_user WITH PASSWORD 'crypto_pass';
CREATE DATABASE cryptodb OWNER crypto_user;

3.3 Installation du backend
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

3.4 Installation du frontend
cd frontend
npm install

4. Démarrage manuel de l’application
4.1 Backend FastAPI
cd backend
source .venv/bin/activate
uvicorn main:app --reload


L’API est accessible à l’adresse suivante :

http://127.0.0.1:8000

Documentation Swagger : http://127.0.0.1:8000/docs

4.2 Frontend React
cd frontend
npm run dev


Le frontend est accessible à l’adresse :

http://localhost:5173

4.3 Collector de données
cd collector
source ../backend/.venv/bin/activate
python main.py


Fonctionnalités :

Récupération automatique des données de marché

Mise à jour périodique des prix

Enregistrement des prix, volumes et capitalisations

4.4 Alert Checker
cd backend
source .venv/bin/activate
python alert_checker.py


Fonctionnalités :

Surveillance des seuils définis par l’utilisateur

Génération de notifications

Envoi optionnel vers Discord

5. Démarrage via Docker

L’ensemble de la plateforme peut être démarré via Docker Compose :

docker-compose up --build

Service	URL
Backend API	http://localhost:8000

Swagger	http://localhost:8000/docs

Frontend	http://localhost:5173

PostgreSQL	localhost:5432
6. Variables d’environnement

Créer un fichier .env à la racine du projet :

POSTGRES_USER=crypto_user
POSTGRES_PASSWORD=crypto_pass
POSTGRES_DB=cryptodb

DATABASE_URL=postgresql+psycopg2://crypto_user:crypto_pass@db:5432/cryptodb
SECRET_KEY=super_secret_key_change_me

7. Structure du projet
plateforme-crypto/
├── backend/
│   ├── main.py
│   ├── auth.py
│   ├── db.py
│   ├── alert_checker.py
│   ├── schemas.py
│   ├── tests/
│
├── collector/
│   ├── core.py
│   ├── main.py
│   ├── tasks.py
│   ├── tests/
│
├── frontend/
│   ├── src/
│
├── k6/
│   ├── smoke.js
│
├── docker-compose.yml
├── quality_check.sh
├── README.md

8. Tests et qualité logicielle
8.1 Tests unitaires et d’intégration
python -m pytest -q


Les tests couvrent :

Les fonctionnalités critiques du backend (authentification, utilisateurs, assets, alertes)

Le pipeline de collecte des données

Les interactions avec la base de données

L’utilisation de mocks pour les services externes

8.2 Couverture de tests
python -m pytest --cov=backend --cov=collector --cov-report=term-missing --cov-report=xml


Résultats :

Couverture globale d’environ 86 %

Rapport généré : coverage.xml

8.3 Tests de performance

Les tests de performance sont réalisés avec k6 :

k6 run k6/smoke.js


Scénario :

10 utilisateurs virtuels

30 secondes

Endpoints testés : /health, /assets

Résultats :

Temps de réponse p95 inférieur à 20 ms

Aucun échec de requête

8.4 Sécurité

Une démarche de tests de sécurité automatisés est prévue à l’aide d’outils de type OWASP ZAP (scan passif).
Les limitations techniques (environnement Docker) sont documentées et la méthodologie est reproductible.

9. CI/CD

Un pipeline CI/CD est mis en place avec GitHub Actions :

Exécution automatique des tests

Vérification de la couverture

Génération des rapports

Validation à chaque push

10. Déploiement

Le projet peut être déployé sur tout environnement compatible Docker :

VPS

Plateformes cloud (Railway, Render)

Infrastructure AWS (ECS)

11. Conclusion

Ce projet met en œuvre une démarche complète de développement logiciel incluant :

Une architecture modulaire

Des tests automatisés

Une analyse de performance

Une approche sécurité

Une intégration continue

Il répond aux exigences de qualité, de maintenabilité et de robustesse attendues dans un contexte professionnel.
