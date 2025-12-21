#!/bin/bash

echo "🚀 Lancement complet de la plateforme crypto..."

# --- BACKEND ---
echo "➡️  Démarrage du backend FastAPI..."
cd backend || exit
source .venv/bin/activate
uvicorn main:app --reload &
BACKEND_PID=$!
cd ..

# --- FRONTEND ---
echo "➡️  Démarrage du frontend React..."
cd frontend || exit
npm run dev &
FRONTEND_PID=$!
cd ..

# --- COLLECTOR ---
echo "➡️  Lancement du collector (CryptoRabbit)..."
cd collector || exit
source ../backend/.venv/bin/activate
python main.py &
COLLECTOR_PID=$!
cd ..

# --- ALERT CHECKER ---
echo "➡️  Lancement de l'alert checker..."
cd backend || exit
source .venv/bin/activate
python alert_checker.py &
ALERT_PID=$!
cd ..

echo ""
echo "🎉 Tout est lancé !"
echo "Backend PID : $BACKEND_PID"
echo "Frontend PID : $FRONTEND_PID"
echo "Collector PID : $COLLECTOR_PID"
echo "Alert Checker PID : $ALERT_PID"
echo ""
echo "➡️  Utilise ./stop.sh pour tout arrêter proprement."
