#!/usr/bin/env bash
# ==============================================================================
# Cat AI - Script de lancement pour macOS
# ==============================================================================
cd "$(dirname "$0")"

if ! command -v python3 &> /dev/null; then
    echo "[Cat AI] Erreur: Python 3 est requis pour lancer Cat AI."
    echo "Installez Python 3 ou via Homebrew: brew install python"
    exit 1
fi

python3 main.py
