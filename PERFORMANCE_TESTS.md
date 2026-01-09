# 📊 Tests de Performance - Plateforme Crypto

**Date:** 9 janvier 2026  
**Objectif:** Évaluer scalabilité, latence et débit du système

---

## 🎯 Résumé des Tests

### Outils Utilisés

| Outil      | Type       | Cas d'Usage                                          |
| ---------- | ---------- | ---------------------------------------------------- |
| **Locust** | Python     | Test de charge progressif, simulation d'utilisateurs |
| **k6**     | JavaScript | Test de performance haut-débit, metrics temps réel   |

### Scénarios Testés

| Scénario          | VUs    | Durée | Objectif     |
| ----------------- | ------ | ----- | ------------ |
| Health Check      | 10-50  | 30s   | Baseline     |
| Charge Progressif | 0→200  | 30m   | Ramp test    |
| Stress Test       | 50-200 | 10m   | Peak load    |
| Endurance         | 100    | 1h    | Long-running |

---

## 🚀 Démarrer les Tests

### Prerequis

```bash
# Locust (déjà installé)
pip install locust

# k6 (installation)
brew install k6  # macOS
# ou
wget https://github.com/grafana/k6/releases/download/v0.47.0/k6-v0.47.0-macos-arm64.zip
```

### API Doit Tourner

```bash
cd backend
python main.py
# OU
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📝 Exécuter les Tests

### **Test 1: Locust (Interface Web)**

```bash
cd /Users/guississ/Documents/GitHub/plateforme-crypto/backend

locust -f locustfile.py \
  --host=http://localhost:8000 \
  --web
```

**Puis aller à:** http://localhost:8089

**Dans l'interface:**

- Number of users: 100
- Spawn rate: 10 (par seconde)
- Duration: 10 minutes
- Cliquer "Start"

---

### **Test 2: Locust (Headless)**

```bash
locust -f locustfile.py \
  --host=http://localhost:8000 \
  --headless \
  --users 100 \
  --spawn-rate 10 \
  --run-time 10m \
  --csv=results/locust_results
```

**Résultats dans:** `results/locust_results_stats.csv`

---

### **Test 3: k6**

```bash
cd /Users/guississ/Documents/GitHub/plateforme-crypto/backend

# Test de charge progressif (par défaut)
k6 run loadtest_k6.js

# Test avec rapport JSON
k6 run loadtest_k6.js \
  --out json=results/k6_results.json \
  --summary-export=results/k6_summary.json
```

---

### **Test 4: k6 Stress Test (haute charge)**

```bash
k6 run loadtest_k6.js \
  --stage 0s:0 \
  --stage 30s:200 \
  --stage 1m:300 \
  --stage 30s:0
```

---

## 📊 Métriques Clés

### Locust Produit

```
Metric Name          │ Value    │ Status
─────────────────────┼──────────┼────────
Requests/s           │ 150      │ ✅ Bon
Avg Response Time    │ 245ms    │ ✅ Bon
95% Response Time    │ 450ms    │ ✅ Bon
99% Response Time    │ 850ms    │ ✅ Acceptable
Failure Rate         │ 0.5%     │ ✅ Bon
```

### k6 Produit

```
Metric               │ Value    │ Seuil    │ Status
─────────────────────┼──────────┼──────────┼────────
http_req_duration    │ 250ms    │ <500ms   │ ✅ Bon
p(95)                │ 450ms    │ <500ms   │ ✅ Bon
p(99)                │ 900ms    │ <1000ms  │ ✅ Bon
http_req_failed      │ 0.5%     │ <10%     │ ✅ Excellent
http_requests/s      │ 150      │ >100     │ ✅ Bon
```

---

## 🔍 Scénarios Détaillés

### Scénario 1: Load Test (Charge Progressive)

```
Phase 1: Ramp-up (5 min)
  Users: 0 → 50
  Rate: 10 users/sec
  → Voir quand le système commence à ralentir

Phase 2: Maintien (10 min)
  Users: 50 → 100
  Rate: Constant
  → Vérifier stabilité

Phase 3: Spike (5 min)
  Users: 100 → 200
  Rate: 20 users/sec
  → Tester résilience pic charge

Phase 4: Ramp-down (5 min)
  Users: 200 → 0
  Rate: 40 users/sec
  → Vérifier récupération
```

**Metrics à Surveiller:**

- ✅ Response time reste < 500ms
- ✅ Error rate reste < 5%
- ✅ Memory usage stable
- ✅ Database connections < max

---

### Scénario 2: Stress Test

```
Phase 1: Baseline (1 min)
  Users: 10
  → Reference point

Phase 2: Stress (5 min)
  Users: 50 → 300
  Rate: Constant high
  → Trouver breaking point

Phase 3: Recovery (3 min)
  Users: 300 → 0
  → Vérifier récupération complète
```

**Objectifs:**

- Trouver le breaking point
- Vérifier recovery
- Identifier bottlenecks

---

### Scénario 3: Endurance Test

```
Durée: 1 heure
Users: 100 (constant)
Rate: ~150 req/s
```

**Objectifs:**

- Détecter memory leaks
- Vérifier stabilité DB
- Observer dégradation progressive

---

## 🎯 Points de Contrôle

### Health Endpoints

```python
GET /health
├─ Time to first byte: < 50ms
├─ Throughput: 1000+ req/s
└─ Success rate: 100%
```

### Asset Listing

```python
GET /assets
├─ Avg response: 200ms
├─ P95 response: 300ms
└─ Success rate: 99%+
```

### Price Retrieval

```python
GET /assets/{id}/prices
├─ Avg response: 250ms
├─ Database queries: < 1s
└─ Success rate: 98%+
```

### Authentication

```python
POST /auth/register
├─ Avg response: 300ms
├─ Database writes: < 500ms
└─ Success rate: 99%+

POST /auth/login
├─ Avg response: 200ms
├─ Cache hit rate: > 80%
└─ Success rate: 99%+
```

---

## 📈 Attendre & Observer

### Dans Locust

```
1. Voir graph "requests/s" en temps réel
2. Observer "response times" courbes
3. Checker "failures" onglet
4. Noter le "breaking point" (quand ça crash)
```

### Dans k6

```bash
# Sortie temps réel:
$ k6 run loadtest_k6.js

  ✓ status is 200
  ✓ response time < 500ms

  checks........................: 98.5% ✓ 1000 ✗ 15
  data_received....................: 2.5 MB
  data_sent........................: 500 KB
  http_req_duration................: avg=245ms, p(95)=450ms
  http_req_failed..................: 0.5%
  http_requests.....................: 150
```

---

## 🔧 Optimisations Recommandées

### Court Terme (Rapide)

```python
# 1. Ajouter caching
@cache.cached(timeout=300)
def get_assets():
    return Asset.query.all()

# 2. Optimiser DB queries
from sqlalchemy.orm import joinedload
assets = Asset.query.options(joinedload(Asset.prices)).all()

# 3. Limiter pagination
@app.get("/assets")
def list_assets(limit: int = 100):
    return Asset.query.limit(limit).all()
```

### Moyen Terme (Architecture)

```python
# 1. Ajouter Redis cache
from redis import Redis
cache = Redis(host='localhost', port=6379)

# 2. Connection pooling
from sqlalchemy.pool import QueuePool
engine = create_engine(
    'postgresql://...',
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40
)

# 3. Async/await
@app.get("/assets")
async def get_assets():
    return await fetch_assets_async()
```

### Long Terme (Scaling)

```yaml
# 1. Load balancer
nginx:
  upstream backend: server app1:8000;
    server app2:8000;
    server app3:8000;

# 2. Caching distributé
memcached/redis:
  nodes: 3
  replication: 2

# 3. BD réplication
postgresql:
  primary: db1
  replicas: [db2, db3]
```

---

## 📋 Checklist Performance

```
PRE-TEST:
[ ] API tourne sans erreurs
[ ] BD testée (pas de locks)
[ ] Logs configurés
[ ] Monitoring prêt

PENDANT TEST:
[ ] Surveiller CPU usage
[ ] Surveiller Memory usage
[ ] Surveiller DB connections
[ ] Surveiller Network bandwidth
[ ] Noter erreurs significatives

POST-TEST:
[ ] Analyser résultats
[ ] Créer rapport
[ ] Identifier bottlenecks
[ ] Proposer optimisations
```

---

## 📊 Résumé des Résultats Attendus

| Charge             | Réq/s | Avg Resp | P95     | P99     | Errors | Status |
| ------------------ | ----- | -------- | ------- | ------- | ------ | ------ |
| Light (50 VUs)     | 75    | 150ms    | 200ms   | 300ms   | 0%     | ✅     |
| Moderate (100 VUs) | 150   | 245ms    | 400ms   | 700ms   | 0.5%   | ✅     |
| Heavy (200 VUs)    | 250   | 400ms    | 600ms   | 1000ms  | 1%     | ⚠️     |
| Stress (300 VUs)   | 300+  | 600ms+   | 1000ms+ | 2000ms+ | 5%+    | 🔴     |

**Breaking Point:** ~250-300 concurrent users
**Recommended Capacity:** 150 concurrent users (70% headroom)

---

## 🎓 Ressources

- [Locust Docs](https://docs.locust.io/)
- [k6 Docs](https://k6.io/docs/)
- [Load Testing Best Practices](https://en.wikipedia.org/wiki/Load_testing)

---

**Status:** ✅ Tests configurés et prêts à exécuter
**Prochain Step:** Lancer les tests et analyser résultats
