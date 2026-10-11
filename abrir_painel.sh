#!/usr/bin/env bash
# abrir_painel.sh — abre o painel do InvestAI no Mac ou no Linux.
# Na primeira vez, cria o venv e instala o requirements.txt (precisa de internet).
# Uso: bash abrir_painel.sh        (para desligar: Ctrl+C)
set -e
cd "$(dirname "$0")"
if [ ! -x venv/bin/python ]; then
    echo "Primeira vez: preparando o ambiente do painel (alguns minutos)..."
    python3 -m venv venv
    venv/bin/python -m pip install --upgrade pip
    venv/bin/python -m pip install -r requirements.txt
fi
venv/bin/python -c "import streamlit, plotly, pandas, scipy" 2>/dev/null \
    || venv/bin/python -m pip install -r requirements.txt
echo "Abrindo o painel em http://localhost:8501  (Ctrl+C para desligar)"
( for i in $(seq 1 120); do
      if venv/bin/python -c "import socket; socket.create_connection(('localhost', 8501), 1)" 2>/dev/null; then
          venv/bin/python -m webbrowser http://localhost:8501 >/dev/null 2>&1; break
      fi
      sleep 0.5
  done ) &
exec venv/bin/python -m streamlit run dashboard.py --server.headless true --server.port 8501
