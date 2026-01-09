# DevOps & CI/CD

Ce guide décrit la chaîne CI/CD, la dockerisation, le déploiement Kubernetes, la supervision et les sauvegardes.

## CI/CD (GitHub Actions)

Le workflow `.github/workflows/cicd.yml` :
- **Build & push** des images Docker (backend, frontend, collector) vers GHCR.
- **Déploiement automatisé** dans un cluster Kubernetes `kind` (exécution en CI).

Images publiées :
- `ghcr.io/<owner>/plateforme-crypto-backend:<sha>`
- `ghcr.io/<owner>/plateforme-crypto-frontend:<sha>`
- `ghcr.io/<owner>/plateforme-crypto-collector:<sha>`

## Dockerisation

Les services sont dockerisés via leurs `Dockerfile` :
- `backend/Dockerfile`
- `frontend/Dockerfile`
- `collector/Dockerfile`

Exécution locale (compose) :
```bash
docker compose up --build
```

## Kubernetes

Les manifests Kubernetes sont dans `k8s/` :
- `k8s/base` : backend, frontend, collector, alert-checker, postgres.
- `k8s/observability` : Prometheus, Alertmanager, Grafana, Loki, Promtail, Postgres exporter.
- `k8s/backups` : sauvegardes de la base et des configurations.

Déploiement :
```bash
kubectl apply -k k8s
```

### Accès (minikube/kind)
- Frontend : NodePort `30080`
- Grafana : NodePort `30090`

## Observabilité

- **Métriques** : Prometheus scrape Prometheus, Postgres exporter, et le backend si `/metrics` est exposé.
- **Logs** : Loki + Promtail (collecte des logs de pods).
- **Alertes** : Alertmanager avec une règle d’alerte `ServiceDown`.

## Sauvegardes

Deux CronJobs :
- `postgres-backup` : `pg_dump` quotidien (02:00), rétention 7 jours.
- `config-backup` : archive `ConfigMap` `app-config` quotidien (02:30), rétention 7 jours.

Les sauvegardes sont stockées sur le PVC `backup-storage`.
