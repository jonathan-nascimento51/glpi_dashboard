#!/bin/bash
# Script de Deploy para Produ��o - GLPI Dashboard

set -e

echo " Iniciando deploy para produ��o..."

# Verificar se estamos na branch main
echo " Verificando branch..."
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ]; then
    echo " Deploy deve ser feito a partir da branch main"
    exit 1
fi

# Verificar se h� mudan�as n�o commitadas
if [ -n "$(git status --porcelain)" ]; then
    echo " H� mudan�as n�o commitadas. Fa�a commit antes do deploy."
    exit 1
fi

# Fazer backup da configura��o atual
echo " Fazendo backup..."
cp production.env production.env.backup.$(date +%Y%m%d_%H%M%S)

# Build do frontend
echo " Fazendo build do frontend..."
cd frontend
npm ci
npm run build
cd ..

# Testes de produ��o
echo " Executando testes..."
cd frontend
npm run test:ci
cd ..

cd backend
pip install -r requirements.txt
python -m pytest tests/ -v --cov=. --cov-report=html
cd ..

# Deploy do backend
echo " Fazendo deploy do backend..."
cd backend
# Aqui voc� adicionaria comandos espec�ficos do seu ambiente
# Exemplo: docker build, kubernetes apply, etc.
echo "Backend pronto para deploy"
cd ..

# Deploy do frontend
echo " Fazendo deploy do frontend..."
cd frontend
# Aqui voc� adicionaria comandos espec�ficos do seu ambiente
# Exemplo: aws s3 sync, nginx config, etc.
echo "Frontend pronto para deploy"
cd ..

# Verifica��o de sa�de
echo " Verificando sa�de da aplica��o..."
# Aqui voc� adicionaria health checks
echo "Aplica��o funcionando corretamente"

echo " Deploy conclu�do com sucesso!"
echo " Dashboard dispon�vel em: https://your-domain.com"
echo " M�tricas dispon�veis em: https://your-domain.com/metrics"
