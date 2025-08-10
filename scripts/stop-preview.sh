#!/bin/bash
# Script para parar ambiente de preview

echo " Parando Ambiente de Preview"
echo "============================="

# Parar backend
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    echo " Parando backend (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null || true
    rm backend.pid
    echo " Backend parado"
else
    echo "  Arquivo backend.pid não encontrado"
    pkill -f "python.*main.py" || true
fi

# Parar frontend
if [ -f "frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend.pid)
    echo " Parando frontend (PID: $FRONTEND_PID)..."
    kill $FRONTEND_PID 2>/dev/null || true
    rm frontend.pid
    echo " Frontend parado"
else
    echo "  Arquivo frontend.pid não encontrado"
    pkill -f "vite" || true
fi

# Limpar arquivos temporários
echo " Limpando arquivos temporários..."
rm -f frontend/.env.local

echo "\n Ambiente de preview parado com sucesso!"
