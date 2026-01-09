# Automatisation des scans de sécurité

Ce document explique comment exécuter des scans automatisés de sécurité avec **OWASP ZAP** et **Snyk**, localement ou en CI.

## Prérequis

- Docker (pour OWASP ZAP)
- Node.js + npm (pour installer `snyk` si nécessaire)
- `snyk` CLI installé: `npm i -g snyk`
- (Optionnel) `SNYK_TOKEN` dans l'environnement pour auth non-interactive

## Emplacements des résultats

Tous les rapports sont sauvegardés dans:

```
results/security/
```

## OWASP ZAP (baseline)

### Commande locale (via Docker)

```bash
# Scan baseline
./security_zap.sh http://localhost:8000

# Rapports produits:
# results/security/zap_report.html
# results/security/zap_report.json
```

### CI (exemple GitHub Actions)

```yaml
- name: OWASP ZAP baseline scan
  uses: docker://owasp/zap2docker-stable
  with:
    entrypoint: ["zap-baseline.py"]
  env:
    TARGET: http://localhost:8000
  run: |
    zap-baseline.py -t ${{ env.TARGET }} -r zap_report.html -J zap_report.json -v
```

## Snyk (dépendances + vulnérabilités)

### Commande locale

```bash
export SNYK_TOKEN=your_token_here  # optional
./security_snyk.sh
# Résultat: results/security/snyk_results.json
```

### CI (exemple GitHub Actions)

```yaml
- name: Run Snyk
  uses: snyk/actions/setup@master
  with:
    version: "latest"
- name: Test with Snyk
  run: |
    snyk test --file=backend/requirements.txt --json > results/security/snyk_results.json || true
  env:
    SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

## Analyse & Priorisation

- Ouvrez `results/security/zap_report.html` pour visualiser les findings ZAP.
- Triez les vulnérabilités Snyk par `severity` et `cvss`.
- Corrigez les vulnérabilités `CRITICAL` puis `HIGH` en priorité.

## Notes

- Les scans automatisés ne remplacent pas un audit manuel.
- Pour les endpoints protégés, exécutez les scans contre un environnement de staging avec des données non sensibles.
- Configurez des règles d'exclusion si nécessaire (ex: endpoints d'administration interne).
