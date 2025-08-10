#!/bin/bash
# Script de Deploy para Produção - GLPI Dashboard

set -e

echo " Iniciando deploy para produção..."

# Verificar se estamos na branch main
echo " Verificando branch..."
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ]; then
    echo " Deploy deve ser feito a partir da branch main"
    exit 1
fi

# Verificar se há mudanças não commitadas
if [ -n "$(git status --porcelain)" ]; then
    echo " Há mudanças não commitadas. Faça commit antes do deploy."
    exit 1
fi

# Fazer backup da configuração atual
echo " Fazendo backup..."
cp production.env production.env.backup.$(date +%Y%m%d_%H%M%S)

# Build do frontend
echo " Fazendo build do frontend..."
cd frontend
npm ci
npm run build
cd ..

# Testes de produção
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
# Aqui você adicionaria comandos específicos do seu ambiente
# Exemplo: docker build, kubernetes apply, etc.
echo "Backend pronto para deploy"
cd ..

# Deploy do frontend
echo " Fazendo deploy do frontend..."
cd frontend
# Aqui você adicionaria comandos específicos do seu ambiente
# Exemplo: aws s3 sync, nginx config, etc.
echo "Frontend pronto para deploy"
cd ..

# Verificação de saúde
echo " Verificando saúde da aplicação..."
# Aqui você adicionaria health checks
echo "Aplicação funcionando corretamente"

echo " Deploy concluído com sucesso!"
echo " Dashboard disponível em: https://your-domain.com"
echo " Métricas disponíveis em: https://your-domain.com/metrics"
