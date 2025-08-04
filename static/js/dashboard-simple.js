/**
 * Dashboard Simples - Foco apenas nas métricas
 */

// Dados das métricas (simulando dados reais)
const metricsData = {
  new: { value: 42, change: '+12%', trend: 'positive' },
  pending: { value: 11, change: '-8%', trend: 'negative' },
  progress: { value: 37, change: '+5%', trend: 'positive' },
  resolved: { value: 64, change: '+18%', trend: 'positive' }
};

const levelsData = {
  n1: { new: 15, progress: 12, pending: 4, resolved: 28 },
  n2: { new: 12, progress: 15, pending: 4, resolved: 18 },
  n3: { new: 8, progress: 6, pending: 2, resolved: 10 },
  n4: { new: 6, progress: 4, pending: 1, resolved: 6 }
};

// Função para trocar tema
function changeTheme(theme, element) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('dashboard-theme', theme);
  
  // Atualizar botões ativos
  document.querySelectorAll('.theme-btn').forEach(btn => btn.classList.remove('active'));
  element.classList.add('active');
  
  showNotification(`Tema alterado para ${theme}`, 'Visualização atualizada', 'success');
}

// Função para filtrar por status
function filterByStatus(status) {
  // Destacar card selecionado
  document.querySelectorAll('.metric-card').forEach(card => {
    card.classList.remove('active');
  });
  
  const selectedCard = document.querySelector(`[data-type="${status}"]`);
  if (selectedCard) {
    selectedCard.classList.add('active');
  }
  
  showNotification(`Filtro aplicado`, `Mostrando apenas chamados: ${status}`, 'info');
}

// Função para mostrar detalhes do nível
function showLevelDetail(level) {
  const data = levelsData[level.toLowerCase()];
  const total = data.new + data.progress + data.pending + data.resolved;
  
  showNotification(
    `Detalhes ${level}`, 
    `Total: ${total} chamados | Novos: ${data.new} | Em progresso: ${data.progress} | Pendentes: ${data.pending} | Resolvidos: ${data.resolved}`, 
    'info'
  );
}

// Função para mudar período
function changePeriod(period, element) {
  document.querySelectorAll('.period-btn').forEach(btn => btn.classList.remove('active'));
  element.classList.add('active');
  
  showNotification(`Período alterado`, `Visualizando dados: ${period}`, 'success');
}

// Função para atualizar
function forceRefresh() {
  showNotification('Atualizando...', 'Buscando dados mais recentes', 'info');
  
  // Simular carregamento
  setTimeout(() => {
    // Atualizar valores com pequenas variações
    document.getElementById('newTickets').textContent = Math.floor(Math.random() * 10) + 40;
    document.getElementById('pendingTickets').textContent = Math.floor(Math.random() * 5) + 8;
    document.getElementById('progressTickets').textContent = Math.floor(Math.random() * 10) + 35;
    document.getElementById('resolvedTickets').textContent = Math.floor(Math.random() * 15) + 60;
    
    showNotification('Atualizado!', 'Dados atualizados com sucesso', 'success');
  }, 1000);
}

// Função para toggle de filtros (placeholder)
function toggleFilters() {
  showNotification('Filtros', 'Painel de filtros em desenvolvimento', 'info');
}

// Função para busca
function handleSearch(query) {
  if (query.length < 2) return;
  
  // Simular resultados de busca
  setTimeout(() => {
    showNotification('Busca realizada', `Encontrados resultados para: "${query}"`, 'info');
  }, 300);
}

function showSearchResults() {
  // Implementação simples para mostrar resultados
}

function hideSearchResults() {
  // Implementação simples para esconder resultados
}

// Sistema de notificações
function showNotification(title, message, type = 'info') {
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  notification.style.position = 'fixed';
  notification.style.top = '20px';
  notification.style.right = '20px';
  notification.style.zIndex = '2000';
  notification.style.padding = '16px 20px';
  notification.style.background = 'var(--surface)';
  notification.style.border = '1px solid var(--border)';
  notification.style.borderRadius = '12px';
  notification.style.boxShadow = 'var(--shadow-lg)';
  notification.style.maxWidth = '400px';
  notification.style.animation = 'slideInRight 0.3s ease-out';
  
  // Cores baseadas no tipo
  let borderColor = 'var(--primary)';
  if (type === 'success') borderColor = 'var(--accent-green)';
  if (type === 'error') borderColor = 'var(--accent-red)';
  if (type === 'warning') borderColor = 'var(--accent-amber)';
  
  notification.style.borderLeft = `4px solid ${borderColor}`;
  
  notification.innerHTML = `
    <div style="display: flex; align-items: center; gap: 12px;">
      <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : 'info-circle'}" style="color: ${borderColor};"></i>
      <div style="flex: 1;">
        <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 4px;">${title}</div>
        <div style="font-size: 14px; color: var(--text-secondary);">${message}</div>
      </div>
      <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; color: var(--text-muted); cursor: pointer; padding: 4px; border-radius: 4px;">
        <i class="fas fa-times"></i>
      </button>
    </div>
  `;
  
  document.body.appendChild(notification);
  
  // Auto remover após 5 segundos
  setTimeout(() => {
    if (notification.parentElement) {
      notification.remove();
    }
  }, 5000);
}

// Relógio
function updateClock() {
  const now = new Date();
  const timeString = now.toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
  
  const clockElement = document.getElementById('currentTime');
  if (clockElement) {
    clockElement.textContent = timeString;
  }
}

// Criar sparklines simples (usando Canvas)
function createSparkline(canvasId, data) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  const width = canvas.width = canvas.offsetWidth * 2; // Para retina
  const height = canvas.height = canvas.offsetHeight * 2;
  canvas.style.width = canvas.offsetWidth + 'px';
  canvas.style.height = canvas.offsetHeight + 'px';
  
  ctx.scale(2, 2);
  
  // Dados de exemplo para sparkline
  const sparklineData = [10, 15, 8, 20, 18, 25, 22, 30, 28, 35];
  const max = Math.max(...sparklineData);
  const min = Math.min(...sparklineData);
  
  ctx.strokeStyle = getSparklineColor(canvasId);
  ctx.lineWidth = 2;
  ctx.beginPath();
  
  sparklineData.forEach((value, index) => {
    const x = (index / (sparklineData.length - 1)) * (width / 2);
    const y = (height / 2) - ((value - min) / (max - min)) * (height / 2);
    
    if (index === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
  });
  
  ctx.stroke();
}

function getSparklineColor(canvasId) {
  if (canvasId.includes('new')) return '#3b82f6';
  if (canvasId.includes('pending')) return '#f59e0b';
  if (canvasId.includes('progress')) return '#10b981';
  if (canvasId.includes('resolved')) return '#8b5cf6';
  return '#64748b';
}

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
  // Aplicar tema salvo
  const savedTheme = localStorage.getItem('dashboard-theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);
  
  // Atualizar botão ativo do tema
  document.querySelectorAll('.theme-btn').forEach(btn => {
    btn.classList.remove('active');
    if (btn.onclick.toString().includes(savedTheme)) {
      btn.classList.add('active');
    }
  });
  
  // Inicializar relógio
  updateClock();
  setInterval(updateClock, 1000);
  
  // Criar sparklines
  setTimeout(() => {
    createSparkline('newSparkline');
    createSparkline('pendingSparkline');
    createSparkline('progressSparkline');
    createSparkline('resolvedSparkline');
  }, 500);
  
  // Mostrar notificação de boas-vindas
  setTimeout(() => {
    showNotification('Dashboard Carregado', 'Sistema de monitoramento ativo', 'success');
  }, 1000);
});

// Animação de entrada
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.animationPlayState = 'running';
    }
  });
});

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.fade-in').forEach(el => {
    observer.observe(el);
  });
});