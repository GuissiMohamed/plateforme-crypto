# Plateforme Crypto — DevOps & CI/CD

## Architecture
- **collector** : collecte des données de marché
- **backend** : API FastAPI + métriques `/metrics`
- **frontend** : web UI React (build Nginx)
- **postgres** : base de données
- **redis** : cache/queue optionnel

## Arborescence
```
.
├── backend/
├── collector/
├── frontend/
├── infra/                # scripts d’infra (kind/ingress/deploy)
├── k8s/                  # manifests Kubernetes (app + backups)
├── observability/        # valeurs Helm + dashboards + règles
├── .github/workflows/
├── docker-compose.yml
├── .dockerignore
├── .env.example
└── README.md
```

## Prérequis
- Docker + Docker Compose
- kubectl
- Helm
- Kind ou Minikube

## Démarrage local (Docker)
```bash
cp .env.example .env
docker compose up --build
```

Services :
- Frontend : http://localhost:5173
- Backend : http://localhost:8000
- Postgres : localhost:5432

## Déploiement Kubernetes (Kind)
```bash
make -f infra/Makefile kind-up
make -f infra/Makefile ingress

cp k8s/base/secret.env.example k8s/base/secret.env
kubectl apply -f k8s/base/namespace.yaml
```

Chargement images locales (optionnel) :
```bash
make -f infra/Makefile load-images
```

Accès :
- Frontend : http://plateforme-crypto.local (ingress)
- Backend : http://plateforme-crypto.local/api

Ajoutez une entrée `/etc/hosts` :
```
127.0.0.1 plateforme-crypto.local grafana.plateforme-crypto.local
```

## Observabilité (Prometheus + Grafana + Loki)
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

kubectl -n plateforme-crypto create secret generic grafana-admin \
  --from-literal=admin-user=admin \
  --from-literal=admin-password=change_me

helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace plateforme-crypto \
  --values observability/values-prometheus.yaml

helm upgrade --install loki grafana/loki-stack \
  --namespace plateforme-crypto \
  --values observability/values-loki.yaml
```

Puis déployer l’application :
```bash
kubectl apply -k k8s
```

Accès Grafana :
- http://grafana.plateforme-crypto.local

Vérifications :
```bash
kubectl -n plateforme-crypto get pods
kubectl -n plateforme-crypto port-forward svc/kube-prometheus-stack-prometheus 9090:9090
kubectl -n plateforme-crypto port-forward svc/loki 3100:3100
```

## Backups PostgreSQL
Le CronJob `postgres-backup` réalise un dump quotidien (rétention 7 jours).

Restauration :
```bash
./infra/restore-db.sh /path/to/backup.sql
```

Export des configs/secrets :
```bash
./infra/backup-configs.sh
```

## CI/CD (GitHub Actions)
Le pipeline `.github/workflows/cicd.yml` :
- lint + tests
- build & push images
- scan Trivy
- déploiement automatique

Secrets requis :
- `KUBECONFIG_STAGING`
- `KUBECONFIG_PROD`

Branches :
- `develop` → staging
- `main` → production

## Troubleshooting
- **Ingress** : vérifier `kubectl -n ingress-nginx get pods`
- **Images** : `docker images` + `kind load docker-image`
- **PVC** : `kubectl -n plateforme-crypto get pvc`
- **Grafana** : `kubectl -n plateforme-crypto port-forward svc/kube-prometheus-stack-grafana 3000:3000`
