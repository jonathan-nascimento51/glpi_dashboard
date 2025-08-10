#!/bin/bash
# Script para configurar ambiente de preview para testes E2E

set -e

echo " Configurando Ambiente de Preview para E2E"
echo "==========================================="

# Verificar se as portas estão disponíveis
echo "\n🔍 Verificando portas disponíveis..."
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "  Porta 8000 já está em uso"
    echo "Parando processo na porta 8000..."
    pkill -f "python.*main.py" || true
    sleep 2
fi

if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Porta 3000 já está em uso"
    echo "Parando processo na porta 3000..."
    pkill -f "vite" || true
    sleep 2
fi

# Configurar backend para preview
echo "\n🚀 Iniciando backend em modo preview..."
cd backend

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python -m venv venv
fi

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
echo " Instalando dependências do backend..."
pip install -r requirements.txt

# Configurar variáveis de ambiente para preview
export ENVIRONMENT=preview
export DEBUG=true
export CORS_ORIGINS="http://localhost:3000,http://localhost:3001"
export LOG_LEVEL=INFO

# Iniciar backend em background
echo " Iniciando servidor backend..."
python main.py &
BACKEND_PID=$!
echo $BACKEND_PID > ../backend.pid

cd ..

# Aguardar backend inicializar
echo "⏳ Aguardando backend inicializar..."
sleep 5

# Verificar se backend está rodando
if curl -f http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ Backend rodando em http://localhost:8000"
else
    echo " Falha ao iniciar backend"
    exit 1
fi

# Configurar frontend para preview
echo "\n Configurando frontend para preview..."
cd frontend

# Instalar dependências
echo " Instalando dependências do frontend..."
npm ci

# Gerar cliente API
echo " Gerando cliente API..."
npm run api:generate

# Configurar variáveis de ambiente para preview
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local
echo "VITE_ENVIRONMENT=preview" >> .env.local

# Iniciar frontend em modo preview
echo " Iniciando servidor frontend..."
npm run dev -- --host 0.0.0.0 --port 3000 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../frontend.pid

cd ..

# Aguardar frontend inicializar
echo " Aguardando frontend inicializar..."
sleep 10

# Verificar se frontend está rodando
if curl -f http://localhost:3000 >/dev/null 2>&1; then
    echo " Frontend rodando em http://localhost:3000"
else
    echo " Falha ao iniciar frontend"
    exit 1
fi

echo "\n Ambiente de preview configurado com sucesso!"
echo " Serviços disponíveis:"
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:3000"
echo "   API Docs: http://localhost:8000/docs"
echo "\n Para executar testes E2E:"
echo "  cd frontend && npm run test:e2e"
echo "\n Para parar os serviços:"
echo "  ./scripts/stop-preview.sh"
