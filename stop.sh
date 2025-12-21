#!/bin/bash

echo "🛑 Arrêt des services..."

# Tuer les processus uvicorn
pkill -f "uvicorn main:app"

# Tuer le collector
pkill -f "collector/main.py"

# Tuer l’alert checker
pkill -f "alert_checker.py"

# Tuer React
pkill -f "react-scripts"
pkill -f "vite"

echo "✔️ Tous les services ont été arrêtés."
