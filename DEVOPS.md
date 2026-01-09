# DevOps & CI/CD

## CI/CD
Workflow : `.github/workflows/cicd.yml`
- lint + tests
- build/push images vers GHCR
- scan sécurité (Trivy)
- déploiement automatique (staging/prod)

Secrets requis :
- `KUBECONFIG_STAGING`
- `KUBECONFIG_PROD`

## Docker
- Backend : `backend/Dockerfile`
- Collector : `collector/Dockerfile`
- Frontend : `frontend/Dockerfile` (multi-stage + Nginx)

## Kubernetes
Manifests : `k8s/`
- base : services + ingress + HPA
- backups : CronJobs + PVC

## Observabilité
Helm values : `observability/`
- `values-prometheus.yaml`
- `values-loki.yaml`

## Backups
CronJob `postgres-backup` quotidien, rétention 7 jours.
