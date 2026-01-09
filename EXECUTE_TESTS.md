# 🚀 Guide Complet d'Exécution des Tests

## 📋 Table des matières

1. [Prérequis](#prérequis)
2. [Configuration API](#configuration-api)
3. [Tests Fonctionnels](#tests-fonctionnels)
4. [Tests de Performance](#tests-de-performance)
5. [Analyse Qualité](#analyse-qualité)
6. [Interprétation Résultats](#interprétation-résultats)

---

## 🔧 Prérequis

### Vérifier les installations

```bash
# Python 3.12+
python3 --version

# pip
pip3 --version

# Node.js (pour k6 et sonar-scanner)
node --version
npm --version

# Git
git --version
```

### Installation des dépendances

```bash
# Backend - Tests et dépendances
cd /Users/guississ/Documents/GitHub/plateforme-crypto/backend
pip install -r requirements.txt
pip install pytest pytest-cov locust

# k6 (si pas encore installé)
brew install k6  # macOS
# ou
sudo apt-get install k6  # Linux

# SonarQube Scanner (si pas installé)
npm install -g sonarqube-scanner
```

---

## 🌐 Configuration API

### Terminal 1: Démarrer l'API

```bash
cd /Users/guississ/Documents/GitHub/plateforme-crypto/backend

# Activer l'environnement virtuel
source env/bin/activate

# Démarrer FastAPI
python main.py
```

**Sortie attendue:**

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete
```

Vérifier avec:

```bash
curl http://localhost:8000/health
# Réponse: {"status":"ok","timestamp":"..."}
```

---

## ✅ Tests Fonctionnels

### Terminal 2: Exécuter les tests pytest

```bash
cd /Users/guississ/Documents/GitHub/plateforme-crypto/backend

# Tests simples
pytest test_main.py -v

# Avec couverture
pytest test_main.py --cov=. --cov-report=html

# Tests spécifiques
pytest test_main.py::TestAuthRegister -v
pytest test_main.py::TestPrices -v
pytest test_main.py::TestMocksExternalAPIs -v

# Tests avec sortie détaillée
pytest test_main.py -vv -s
```

### Résultats attendus

```
test_main.py::TestAuthRegister::test_register_success PASSED
test_main.py::TestAuthLogin::test_login_success PASSED
test_main.py::TestAssets::test_get_assets PASSED
... (77 tests total)

✅ 77 passed in 5.23s
Coverage: 60% of lines
```

### Ouvrir le rapport de couverture

```bash
open htmlcov/index.html  # macOS
# ou
xdg-open htmlcov/index.html  # Linux
```

---

## 📊 Tests de Performance

### Option 1: Script Automatisé (Recommandé)

```bash
cd /Users/guississ/Documents/GitHub/plateforme-crypto

# Mode interactif
./run_performance_tests.sh

# Ou directement
./run_performance_tests.sh both    # Locust + k6
./run_performance_tests.sh locust  # Locust seulement
./run_performance_tests.sh k6      # k6 seulement
```

---

### Option 2: Locust (Interface Web)

#### Terminal 2: Lancer Locust

```bash
cd /Users/guississ/Documents/GitHub/plateforme-crypto/backend

# Mode web (interface interactive)
locust -f locustfile.py --host=http://localhost:8000 --web

# Sortie:
# [2024-01-09 16:10:00,000] Starting web UI at http://0.0.0.0:8089
```

#### Accéder à l'interface

```bash
open http://localhost:8089
```

#### Configurer le test

1. **Number of users**: `100`
2. **Spawn rate**: `10` (users/sec)
3. **Run time**: `10m` ou laisser vide

Cliquer sur "Start swarming"

#### Monitorer les métriques

- **Response times**: Voir les temps de réponse en temps réel
- **Requests/sec**: Throughput du serveur
- **Failure rate**: Pourcentage d'erreurs
- **Type**: Type de requêtes (GET, POST, etc.)

---

### Option 3: Locust (Mode Headless)

```bash
cd /Users/guississ/Documents/GitHub/plateforme-crypto/backend

# Léger (100 utilisateurs, 10 minutes)
locust -f locustfile.py \
  --host=http://localhost:8000 \
  --headless \
  --users 100 \
  --spawn-rate 10 \
  --run-time 10m \
  --csv=results/locust_100

# Lourd (200 utilisateurs, 15 minutes)
locust -f locustfile.py \
  --host=http://localhost:8000 \
  --headless \
  --users 200 \
  --spawn-rate 20 \
  --run-time 15m \
  --csv=results/locust_200

# Stress test (500 utilisateurs, 5 minutes)
locust -f locustfile.py \
  --host=http://localhost:8000 \
  --headless \
  --users 500 \
  --spawn-rate 50 \
  --run-time 5m
```

---

### Option 4: k6 (Performance Testing)

#### Terminal 3: Lancer k6

```bash
cd /Users/guississ/Documents/GitHub/plateforme-crypto/backend

# Test standard (~23 minutes)
k6 run loadtest_k6.js

# Avec résultats JSON
k6 run loadtest_k6.js --out json=results/k6_results.json

# Avec résultats personnalisés
k6 run loadtest_k6.js \
  --out json=results/k6_detailed.json \
  --summary-export=results/k6_summary.json

# Test rapide (custom stages)
k6 run loadtest_k6.js \
  --stage 0s:0 \
  --stage 30s:50 \
  --stage 1m:100 \
  --stage 30s:0
```

#### Sortie k6

```
     data_received..................: 1.5 MB   1.2 MB/s
     data_sent......................: 850 kB   710 kB/s
     http_req_blocked...............: avg=2.54ms    min=0s       max=58.23ms   p(90)=5ms     p(95)=8.5ms
     http_req_connecting............: avg=1.23ms    min=0s       max=35.21ms   p(90)=2.5ms   p(95)=4.2ms
     http_req_duration..............: avg=145.12ms  min=5ms      max=1.2s      p(90)=250ms   p(95)=380ms
     http_req_failed................: 2.5%   ✓ (expected < 10%)
     http_req_receiving.............: avg=12.54ms   min=1ms      max=250ms     p(90)=20ms    p(95)=45ms
     http_req_sending...............: avg=8.21ms    min=0s       max=120ms     p(90)=12ms    p(95)=25ms
     http_req_tls_handshaking.......: avg=0s        min=0s       max=0s        p(90)=0s      p(95)=0s
     http_req_waiting...............: avg=124.37ms  min=2ms      max=980ms     p(90)=200ms   p(95)=310ms
     http_reqs......................: 12,500  10.42/s
     iteration_duration.............: avg=2.1s      min=1.5s     max=4.2s      p(90)=2.8s    p(95)=3.5s
     iterations.....................: 2,500   2.08/s
     vus............................: 45      min=0  max=200
     vus_max........................: 200     min=200 max=200
```

---

## 🔍 Analyse Qualité

### SonarQube Setup

#### Terminal 3: Vérifier SonarQube

```bash
# Vérifier si SonarQube tourne
curl http://localhost:9001 || echo "SonarQube not running"

# Lancer SonarQube en Docker
docker ps | grep sonarqube || docker run -d \
  --name sonarqube \
  -p 9001:9000 \
  sonarqube:latest
```

#### Accéder à SonarQube

```bash
open http://localhost:9001
# Login: admin / admin (par défaut)
```

#### Exécuter le scan

```bash
cd /Users/guississ/Documents/GitHub/plateforme-crypto

# Avec token généré
sonar-scanner \
  -Dsonar.projectKey=plateforme-crypto \
  -Dsonar.sources=backend \
  -Dsonar.exclusions='**/__pycache__/**,**/venv/**,**/env/**' \
  -Dsonar.host.url=http://localhost:9001 \
  -Dsonar.token=squ_be8230eec593a304257e706480cd1d1187980965

# Ou via bash
./quality_analysis.sh
```

#### Résultats SonarQube

Attendre ~2-3 minutes et vérifier:

```
http://localhost:9001/dashboard?id=plateforme-crypto
```

Métriques disponibles:

- **Code Smells**: Issues de maintenabilité
- **Bugs**: Bugs détectés
- **Vulnerabilities**: Failles sécurité
- **Coverage**: Couverture de tests
- **Duplications**: Code dupliqué
- **Maintainability**: Indice de maintenabilité

---

### Analyse Statique

```bash
cd /Users/guississ/Documents/GitHub/plateforme-crypto/backend

# Pylint (qualité générale)
pylint main.py auth.py db.py --output-format=parseable

# Flake8 (style et erreurs)
flake8 . --max-line-length=100 --count

# Bandit (sécurité)
bandit -r . -f json -o results/bandit_results.json
```

---

## 📈 Interprétation Résultats

### Métriques Clés

#### ✅ Acceptable

- **Response time p95**: < 500ms
- **Error rate**: < 10%
- **Throughput**: > 100 req/s
- **Code coverage**: > 60%
- **Pylint score**: > 7/10

#### ⚠️ À améliorer

- **Response time p99**: > 1000ms
- **Error rate**: 10-30%
- **Throughput**: 50-100 req/s
- **Code coverage**: 40-60%
- **Pylint score**: 5-7/10

#### 🔴 Critique

- **Response time p95**: > 1000ms
- **Error rate**: > 30%
- **Throughput**: < 50 req/s
- **Code coverage**: < 40%
- **Pylint score**: < 5/10

---

### Exemple Rapport Complet

```
┌─────────────────────────────────────────────────────────┐
│           PLATEFORME CRYPTO - RAPPORT TEST              │
├─────────────────────────────────────────────────────────┤
│ Tests Fonctionnels                                       │
│  ✅ 77/77 tests passed (100%)                           │
│  Coverage: 60% (162/401 lines)                          │
│                                                         │
│ Performance (k6)                                        │
│  Response time p95: 380ms ✅                            │
│  Response time p99: 850ms ✅                            │
│  Error rate: 2.5% ✅                                    │
│  Throughput: 10.42 req/s ✅                             │
│                                                         │
│ Load Test (Locust - 100 users)                          │
│  Total requests: 45,000 ✅                              │
│  Failure rate: 1.2% ✅                                  │
│  Avg response time: 245ms ✅                            │
│  p95: 450ms ✅                                          │
│                                                         │
│ Code Quality (SonarQube)                                │
│  Code Smells: 12 ⚠️                                     │
│  Bugs: 0 ✅                                             │
│  Vulnerabilities: 1 🔴                                  │
│  Maintainability: A ✅                                  │
│  Coverage: 60% ✅                                       │
│                                                         │
│ Overall Status: PRODUCTION READY ✅                    │
└─────────────────────────────────────────────────────────┘
```

---

## 🐛 Dépannage

### Erreur: "Address already in use"

```bash
# Port 8000 (API)
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Port 8089 (Locust web)
lsof -i :8089 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Port 9001 (SonarQube)
lsof -i :9001 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### Erreur: "Connection refused"

```bash
# Vérifier API
curl -v http://localhost:8000/health

# Vérifier SonarQube
curl -v http://localhost:9001

# Relancer services
python backend/main.py
docker restart sonarqube
```

### Erreur: "k6 not found"

```bash
# Installer k6
brew install k6

# Vérifier installation
k6 version

# Ou utiliser avec Node
npm install -g k6
```

---

## 📚 Commandes Utiles

```bash
# Couverture complète
cd backend && pytest test_main.py --cov=. --cov-report=html && open htmlcov/index.html

# Performance test rapide (5 minutes)
k6 run loadtest_k6.js --stage 0s:0 --stage 1m:100 --stage 3m:100 --stage 1m:0

# Tous les tests + qualité
./quality_analysis.sh

# Cleaner résultats
rm -rf backend/htmlcov backend/.pytest_cache results/*
```

---

## 🎯 Checklist Exécution

- [ ] Python 3.12+ et pip installés
- [ ] Dépendances installées (`requirements.txt`)
- [ ] API démarrée sur port 8000
- [ ] Tests fonctionnels passent (77/77)
- [ ] Coverage > 60%
- [ ] k6 installé
- [ ] Locust installé
- [ ] Tests de performance exécutés
- [ ] Résultats analysés
- [ ] SonarQube running
- [ ] Scan SonarQube complété
- [ ] Rapport final généré

---

## 📞 Support

Pour plus d'informations:

- [FastAPI Docs](https://fastapi.tiangolo.com)
- [pytest Documentation](https://docs.pytest.org)
- [Locust Documentation](https://docs.locust.io)
- [k6 Documentation](https://k6.io/docs)
- [SonarQube Documentation](https://docs.sonarqube.org)
