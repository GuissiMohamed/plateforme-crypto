#!/bin/bash
# Script pour lancer les tests de performance
# Usage: ./run_performance_tests.sh [locust|k6|both]

set -e

CHOICE=${1:-"both"}
API_URL="http://localhost:8000"
PROJECT_ROOT="/Users/guississ/Documents/GitHub/plateforme-crypto"
BACKEND_DIR="$PROJECT_ROOT/backend"
RESULTS_DIR="$PROJECT_ROOT/results/performance"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         TESTS DE PERFORMANCE - PLATEFORME CRYPTO             ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Créer répertoire résultats
mkdir -p "$RESULTS_DIR"

# ================================================================
# VÉRIFIER QUE L'API TOURNE
# ================================================================
echo "🔍 Vérification API..."
if ! curl -s "$API_URL/health" > /dev/null 2>&1; then
    echo "❌ ERREUR: API n'est pas accessible à $API_URL"
    echo ""
    echo "Lancez l'API d'abord:"
    echo "  cd $BACKEND_DIR"
    echo "  python main.py"
    exit 1
fi
echo "✅ API accessible"
echo ""

# ================================================================
# FONCTION LOCUST
# ================================================================
run_locust() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔴 LOCUST - Test de Charge"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    cd "$BACKEND_DIR"
    
    echo "Options:"
    echo "  1) Mode WEB (interface interactive)"
    echo "  2) Mode Headless (100 users, 10min)"
    echo "  3) Mode Headless (200 users, 15min) - Stress"
    echo ""
    read -p "Choisir (1-3) [1]: " locust_mode
    locust_mode=${locust_mode:-1}
    
    case $locust_mode in
        1)
            echo ""
            echo "Lancement Locust WEB..."
            echo "Aller à: http://localhost:8089"
            echo ""
            locust -f locustfile.py \
                --host="$API_URL" \
                --web
            ;;
        2)
            echo "Lancement Locust Headless (100 users, 10min)..."
            locust -f locustfile.py \
                --host="$API_URL" \
                --headless \
                --users 100 \
                --spawn-rate 10 \
                --run-time 10m \
                --csv="$RESULTS_DIR/locust_100"
            ;;
        3)
            echo "Lancement Locust Headless (200 users, 15min)..."
            locust -f locustfile.py \
                --host="$API_URL" \
                --headless \
                --users 200 \
                --spawn-rate 20 \
                --run-time 15m \
                --csv="$RESULTS_DIR/locust_200"
            ;;
        *)
            echo "Option invalide"
            exit 1
            ;;
    esac
    
    echo ""
    echo "✅ Locust terminé"
    echo "Résultats: $RESULTS_DIR/"
    echo ""
}

# ================================================================
# FONCTION K6
# ================================================================
run_k6() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🟢 K6 - Test de Performance"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Vérifier si k6 est installé
    if ! command -v k6 &> /dev/null; then
        echo "⚠️  k6 n'est pas installé"
        echo ""
        echo "Installation:"
        echo "  macOS: brew install k6"
        echo "  Linux: sudo apt-get install k6"
        echo "  Windows: choco install k6"
        echo ""
        read -p "Installer k6? (y/n): " install_k6
        if [[ "$install_k6" == "y" || "$install_k6" == "Y" ]]; then
            if command -v brew &> /dev/null; then
                brew install k6
            else
                echo "⚠️  Veuillez installer k6 manuellement"
                return 1
            fi
        else
            return 1
        fi
    fi
    
    cd "$BACKEND_DIR"
    
    echo "Options:"
    echo "  1) Test standard (0→200 users)"
    echo "  2) Test stress (heavy load)"
    echo "  3) Test endurance (1000 req total)"
    echo ""
    read -p "Choisir (1-3) [1]: " k6_mode
    k6_mode=${k6_mode:-1}
    
    case $k6_mode in
        1)
            echo "Lancement k6 - Test standard..."
            k6 run loadtest_k6.js \
                --out json="$RESULTS_DIR/k6_standard.json" \
                --summary-export="$RESULTS_DIR/k6_standard_summary.json"
            ;;
        2)
            echo "Lancement k6 - Stress test..."
            k6 run loadtest_k6.js \
                --stage 0s:0 \
                --stage 1m:50 \
                --stage 3m:300 \
                --stage 1m:0 \
                --out json="$RESULTS_DIR/k6_stress.json"
            ;;
        3)
            echo "Lancement k6 - Endurance test..."
            k6 run loadtest_k6.js \
                --vus 100 \
                --duration 5m \
                --out json="$RESULTS_DIR/k6_endurance.json"
            ;;
        *)
            echo "Option invalide"
            exit 1
            ;;
    esac
    
    echo ""
    echo "✅ k6 terminé"
    echo "Résultats: $RESULTS_DIR/"
    echo ""
}

# ================================================================
# MAIN
# ================================================================

case $CHOICE in
    locust)
        run_locust
        ;;
    k6)
        run_k6
        ;;
    both)
        echo "Lancer Locust et k6? (conseillé séquentiellement)"
        echo ""
        read -p "Locust d'abord? (y/n): " run_locust_first
        
        if [[ "$run_locust_first" == "y" || "$run_locust_first" == "Y" ]]; then
            run_locust
            echo ""
            echo "Attendre 30 secondes avant k6..."
            sleep 30
            run_k6
        else
            run_k6
            echo ""
            echo "Attendre 30 secondes avant Locust..."
            sleep 30
            run_locust
        fi
        ;;
    *)
        echo "Usage: $0 [locust|k6|both]"
        exit 1
        ;;
esac

# ================================================================
# RÉSUMÉ
# ================================================================
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    TESTS TERMINÉS                            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Résultats disponibles dans: $RESULTS_DIR/"
echo ""
echo "Fichiers générés:"
if [ -f "$RESULTS_DIR/locust"* ]; then
    echo "  ✅ Locust results"
fi
if [ -f "$RESULTS_DIR/k6"* ]; then
    echo "  ✅ k6 results"
fi
echo ""
echo "📈 Pour analyser les résultats:"
echo "  1. Locust CSV: view $RESULTS_DIR/locust_*_stats.csv"
echo "  2. k6 JSON: view $RESULTS_DIR/k6_*.json"
echo ""
echo "🔗 Liens utiles:"
echo "  • Locust: http://localhost:8089 (si en mode web)"
echo "  • k6 Results: cat $RESULTS_DIR/k6_*_summary.json"
echo ""
