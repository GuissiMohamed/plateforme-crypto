# Résumé des tests et guide de présentation

Ce document rassemble en une page tous les tests que nous avons mis en place, et fournit une séquence de commandes pour lancer et afficher les résultats dans un navigateur lors d'une présentation.

---

## 1) Récapitulatif rapide

- Tests unitaires & d'intégration: `backend/test_main.py` — 77 tests (fixtures, auth, assets, prices, indicateurs). Passez en local avec `pytest`.
- Mocks: usage de mocks pour simuler API externes intégré dans les tests.
- Couverture: générée par `pytest --cov` → rapport HTML dans `backend/htmlcov/index.html`.
- Tests de performance:
  - Locust UI: `backend/locustfile.py` (web UI interactive → http://localhost:8089)
  - k6: `backend/loadtest_k6.js` (script JS, exécution CLI, export JSON)
- Sécurité:
  - OWASP ZAP: `security_zap.sh` (wrapper Docker ou ZAP local) → rapports dans `results/security/`
  - Snyk: `security_snyk.sh` → `results/security/snyk_results.json`

## 2) Fichiers importants

- Tests: `backend/test_main.py`
- Locust: `backend/locustfile.py`
- k6: `backend/loadtest_k6.js`
- Coverage: `backend/htmlcov/index.html`
- Security scripts: `security_zap.sh`, `security_snyk.sh`
- Quality script: `quality_analysis.sh` (inclut SonarQube invocation)
- Résultats: `results/performance/`, `results/security/`

---

## 3) Préparation (à exécuter avant la démo)

1. Ouvrir un terminal et démarrer l'API (backend) :

```bash
source env/bin/activate
cd backend
# si main.py lance uvicorn intégré
python main.py
# ou explicitement
uvicorn main:app --host 0.0.0.0 --port 8000
```

2. Vérifier l'API:

```bash
curl http://localhost:8000/health
```

---

## 4) Script de présentation — ordre recommandé

1. Afficher la page de santé (rapide) dans le terminal ou navigateur :

```bash
open "http://localhost:8000/health"
```

2. Lancer les tests unitaires et ouvrir le rapport de couverture (montrer la couverture dans le navigateur) :

```bash
cd backend
pytest test_main.py --cov=. --cov-report=html
open htmlcov/index.html
```

3. Démarrer l'interface Locust (montrer l'UI interactive) :

```bash
cd backend
locust -f locustfile.py --host=http://localhost:8000
# ouvrir dans le navigateur
open http://localhost:8089
```

Dans l'UI Locust : montrez les onglets `Statistics`, `Charts`, `Failures`, `Exceptions`, et démarrez un test en direct (users et spawn rate).

4. Exécuter un test k6 court (optionnel, montre la sortie terminal & export JSON) :

```bash
cd backend
k6 run loadtest_k6.js --out json=../results/performance/k6_results.json --summary-export=../results/performance/k6_summary.json
```

Vous pouvez ouvrir le fichier JSON ou afficher des métriques avec `jq` si besoin.

5. Montrer SonarQube (si déployé localement) :

```bash
open http://localhost:9001
```

Connectez‑vous et ouvrez le tableau de bord du projet `plateforme-crypto`.

6. OWASP ZAP (montrer les findings via GUI) :

- Si vous avez installé ZAP localement (macOS via Cask) :

```bash
open /Applications/OWASP\ ZAP.app
# ou lancer en daemon puis ouvrir l'UI
/Applications/OWASP\ ZAP.app/Contents/MacOS/owasp-zap.sh -daemon -port 8090
```

- Ou lancer le wrapper Docker (peut demander `docker login`) :

```bash
./security_zap.sh http://localhost:8000
open results/security/zap_report.html
```

7. Snyk (montrer le JSON ou l'UI Snyk si vous avez compte) :

```bash
export SNYK_TOKEN=... # si nécessaire
./security_snyk.sh
open results/security/snyk_results.json
```

---

## 5) Commandes « copy/paste » (macOS) pour la démo

```bash
# 1) start API
cd /Users/guississ/Documents/GitHub/plateforme-crypto/backend && python main.py &

# 2) run unit tests + open coverage
cd /Users/guississ/Documents/GitHub/plateforme-crypto/backend && pytest test_main.py --cov=. --cov-report=html && open htmlcov/index.html

# 3) start Locust UI
cd /Users/guississ/Documents/GitHub/plateforme-crypto/backend && locust -f locustfile.py --host=http://localhost:8000 &
open http://localhost:8089

./stop_locust.sh

./start_locust.sh --port 8090
open http://localhost:8090



# 4) run a short k6 (optional)
cd /Users/guississ/Documents/GitHub/plateforme-crypto/backend && k6 run loadtest_k6.js --out json=../results/performance/k6_results.json --summary-export=../results/performance/k6_summary.json

# 5) open SonarQube (if running)
open http://localhost:9001

# 6) open ZAP report (if produced)
open /Users/guississ/Documents/GitHub/plateforme-crypto/results/security/zap_report.html
```

---































# 1) Lancer proprement (UI sur 8090) — recommandé pour une démo
cd /Users/guississ/Documents/GitHub/plateforme-crypto/backend
nohup locust -f locustfile.py --host=http://localhost:8000 --web-port 8090 </dev/null >~/locust_nohup.log 2>&1 &
disown

# 2) Lancer headless (résultats CSV)
locust -f locustfile.py --host=http://localhost:8000 --headless -u 200 -r 20 -t 3m --csv=../results/performance/locust_run

# 3) Vérifier si un port est occupé
lsof -iTCP:8090 -sTCP:LISTEN -n -P

# 4) Tuer toutes les instances Locust (si nécessaire)
pkill -f "locust -f locustfile.py"
# si besoin forcé
pkill -9 -f "locust -f locustfile.py"

# 5) Reprendre un job suspendu (si vous l'avez lancé dans le même shell)
jobs -l
# reprendre puis détacher
kill -CONT <PID>
disown