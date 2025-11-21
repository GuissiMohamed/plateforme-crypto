# Plateforme de Surveillance et d’Analyse des Marchés de Cryptomonnaies

Ce projet consiste à concevoir et développer une plateforme complète de suivi, d’analyse
et de prévision des marchés de cryptomonnaies. La plateforme repose sur deux applications :

- Une **application console** de collecte et de gestion des données (APIs publiques de cryptomonnaies).
- Une **application web** interactive d’analyse, de visualisation et de simulation (tableaux de bord, alertes, portefeuille virtuel).

## Objectifs

- Collecter périodiquement les données de marché (prix, volume, capitalisation, variations…).
- Stocker ces données dans une base de données.
- Fournir une API backend pour exposer les données aux clients web.
- Offrir une interface web permettant la visualisation, la configuration d’alertes,
  la prévision simple et la gestion d’un portefeuille virtuel.
- Mettre en place un processus complet de développement logiciel (Agile, tests, CI/CD, DevOps).

## Stack technique (prévisionnelle)

- **Backend / Collector** : Python, FastAPI, Celery
- **Base de données** : PostgreSQL
- **Frontend** : React
- **Conteneurisation** : Docker
- **Orchestration** : Kubernetes (Minikube / Kind)
- **CI/CD** : GitHub Actions ou GitLab CI
- **Monitoring** : Prometheus, Grafana

## Structure du projet

- `collector/` : application console de collecte des données
- `backend/`   : API backend (FastAPI)
- `frontend/`  : application web (React)
- `docs/`      : documentation, diagrammes, schémas
- `devops/`    : scripts et configurations Docker / Kubernetes / CI/CD

## Méthodologie

Le projet suit une approche Agile (Scrum ou Kanban) avec :

- backlog de user stories,
- gestion des tâches via un tableau (Trello, GitHub Projects, GitLab Boards),
- documentation continue.

## À faire (roadmap haute niveau)

- Phase 1 : Collecte des données et stockage en base.
- Phase 2 : API backend (authentification, endpoints de données, alertes).
- Phase 3 : Application web (visualisation, portefeuille virtuel, alertes).
- Phase 4 : Tests (unitaires, intégration, performance, sécurité).
- Phase 5 : DevOps (Docker, CI/CD, Kubernetes, monitoring).
