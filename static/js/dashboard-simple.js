// Enhanced Dashboard State and Configuration
class DashboardManager {
  constructor() {
    this.autoRefreshInterval = null;
    this.refreshDelay = 30000; // 30 seconds
    this.isSearchOpen = false;
    this.isFilterPanelOpen = false;
    this.currentFilters = {
      status: null,
      level: null,
      period: 'today'
    };
    this.chart = null;
    this.data = {
      tickets: { new: 42, pending: 11, progress: 37, resolved: 64 },
      levels: {
        n1: { new: 15, progress: 12, pending: 4, resolved: 28 },
        n2: { new: 12, progress: 15, pending: 4, resolved: 18 },
        n3: { new: 8, progress: 6, pending: 2, resolved: 10 },
        n4: { new: 6, progress: 4, pending: 1, resolved: 6 }
      },
      ranking: [
        { name: 'Carlos Silva', level: 'N3', score: 98 },
        { name: 'Ana Santos', level: 'N2', score: 95 },
        { name: 'João Oliveira', level: 'N4', score: 92 },
        { name: 'Maria Costa', level: 'N2', score: 89 },
        { name: 'Pedro Lima', level: 'N1', score: 87 },
        { name: 'Julia Ferreira', level: 'N3', score: 84 },
        { name: 'Lucas Barbosa', level: 'N1', score: 82 },
        { name: 'Sofia Mendes', level: 'N2', score: 79 }
      ],
      alerts: [
        { type: 'warning', icon: 'exclamation-triangle', text: 'Sistema N2 com alta demanda', time: '2 min' },
        { type: 'info', icon: 'info-circle', text: 'Nova versão disponível', time: '5 min' },
        { type: 'success', icon: 'check-circle', text: 'Backup realizado com sucesso', time: '8 min' },
        { type: 'warning', icon: 'clock', text: 'Manutenção programada às 23h', time: '12 min' }
      ],
      performance: {
        resolution: 94.2,
        avgTime: 2.4,
        satisfaction: 4.7,
        efficiency: 89.1
      }
    };
    
    this.init();
  }

  init() {
    this.initMetrics();
    this.initCharts();
    this.initRanking();
    this.initAlerts();
    this.initPerformance();
    this.startAutoRefresh();
    this.updateTime();
    setInterval(() => this.updateTime(), 1000);
    
    // Initialize animations
    this.initAnimations();
  }

  initMetrics() {
    // Initialize sparkline charts
    this.initSparklines();
    this.simulateDataUpdates();
  }

  initSparklines() {
    const sparklineIds = ['newSparkline', 'pendingSparkline', 'progressSparkline', 'resolvedSparkline'];
    sparklineIds.forEach(id => {
      const canvas = document.getElementById(id);
      if (canvas) {
        const ctx = canvas.getContext('2d');
        this.drawSparkline(ctx, this.generateSparklineData());
      }
    });
  }

  drawSparkline(ctx, data) {
    const canvas = ctx.canvas;
    const width = canvas.width = 120;
    const height = canvas.height = 40;
    
    ctx.clearRect(0, 0, width, height);
    ctx.strokeStyle = '#3b82f6';
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    const max = Math.max(...data);
    const min = Math.min(...data);
    const range = max - min || 1;

    ctx.beginPath();
    data.forEach((value, index) => {
      const x = (index / (data.length - 1)) * width;
      const y = height - ((value - min) / range) * height;
      
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    ctx.stroke();
  }

  generateSparklineData() {
    return Array.from({ length: 10 }, () => Math.random() * 100);
  }

  initCharts() {
    const canvas = document.getElementById('trendsChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    
    const labels = [];
    const newData = [];
    const resolvedData = [];
    
    for (let i = 23; i >= 0; i--) {
      const hour = new Date();
      hour.setHours(hour.getHours() - i);
      labels.push(hour.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }));
      
      newData.push(Math.floor(Math.random() * 15) + 5);
      resolvedData.push(Math.floor(Math.random() * 20) + 10);
    }

    this.chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'Novos Chamados',
            data: newData,
            borderColor: '#1e40af',
            backgroundColor: 'rgba(30, 64, 175, 0.1)',
            tension: 0.4,
            fill: true
          },
          {
            label: 'Resolvidos',
            data: resolvedData,
            borderColor: '#059669',
            backgroundColor: 'rgba(5, 150, 105, 0.1)',
            tension: 0.4,
            fill: true
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          intersect: false,
          mode: 'index'
        },
        plugins: {
          legend: {
            position: 'top',
            labels: {
              usePointStyle: true,
              padding: 20,
              font: {
                family: 'Inter',
                size: 12
              }
            }
          }
        },
        scales: {
          x: {
            grid: {
              display: false
            },
            ticks: {
              font: {
                family: 'JetBrains Mono',
                size: 10
              },
              maxTicksLimit: 8
            }
          },
          y: {
            beginAtZero: true,
            grid: {
              color: 'rgba(0,0,0,0.05)'
            },
            ticks: {
              font: {
                family: 'JetBrains Mono',
                size: 10
              }
            }
          }
        }
      }
    });
  }

  initRanking() {
    const rankingList = document.getElementById('rankingList');
    if (!rankingList) return;

    const data = this.data.ranking.slice(0, 8);
    
    rankingList.innerHTML = data.map((tech, index) => `
      <div class="ranking-item" onclick="showTechnicianDetail('${tech.name}')">
        <div class="ranking-position ${index < 3 ? 'top3' : ''}">${index + 1}</div>
        <div class="ranking-info">
          <div class="ranking-name">${tech.name}</div>
          <div class="ranking-level">${tech.level}</div>
        </div>
        <div class="ranking-score">${tech.score}</div>
      </div>
    `).join('');
  }

  initAlerts() {
    const alertsList = document.getElementById('alertsList');
    if (!alertsList) return;

    const data = this.data.alerts;
    
    alertsList.innerHTML = data.map(alert => `
      <div class="alert-item ${alert.type}">
        <i class="fas fa-${alert.icon} alert-icon"></i>
        <span class="alert-text">${alert.text}</span>
        <span class="alert-time">${alert.time}</span>
      </div>
    `).join('');
  }

  initPerformance() {
    const perfElements = {
      resolutionRate: { value: this.data.performance.resolution, isPercentage: true, bar: 'resolutionBar' },
      avgTime: { value: this.data.performance.avgTime, isTime: true, bar: 'timeBar' },
      satisfaction: { value: this.data.performance.satisfaction, suffix: '/5', bar: 'satisfactionBar' },
      efficiency: { value: this.data.performance.efficiency, isPercentage: true, bar: 'efficiencyBar' }
    };

    Object.keys(perfElements).forEach(key => {
      const element = document.getElementById(key);
      const config = perfElements[key];
      
      if (element) {
        if (config.isPercentage) {
          element.textContent = `${config.value}%`;
        } else if (config.isTime) {
          element.textContent = `${config.value}h`;
        } else {
          element.textContent = `${config.value.toFixed(1)}${config.suffix}`;
        }
      }

      if (config.bar) {
        const bar = document.getElementById(config.bar);
        if (bar) {
          const percentage = config.isPercentage ? config.value : 
                           config.suffix === '/5' ? (config.value / 5) * 100 : 
                           Math.min(100, config.value * 20);
          bar.style.width = `${percentage}%`;
        }
      }
    });
  }

  simulateDataUpdates() {
    // Simulate real-time data changes
    setInterval(() => {
      // Update tickets with small random changes
      Object.keys(this.data.tickets).forEach(key => {
        const change = Math.floor(Math.random() * 3) - 1; // -1, 0, or 1
        this.data.tickets[key] = Math.max(0, this.data.tickets[key] + change);
        
        const element = document.getElementById(`${key}Tickets`);
        if (element) {
          this.animateValue(element, parseInt(element.textContent) || 0, this.data.tickets[key]);
        }
      });

      // Update level metrics
      Object.keys(this.data.levels).forEach(level => {
        Object.keys(this.data.levels[level]).forEach(status => {
          const change = Math.floor(Math.random() * 2);
          if (Math.random() > 0.7) { // 30% chance of change
            this.data.levels[level][status] = Math.max(0, this.data.levels[level][status] + change - 1);
            
            const element = document.getElementById(`${level}-${status}`);
            if (element) {
              this.animateValue(element, parseInt(element.textContent) || 0, this.data.levels[level][status], 800);
            }
          }
        });
      });

      this.updateMetricChanges();
    }, 15000); // Update every 15 seconds
  }

  animateValue(element, start, end, duration = 1000, isPercentage = false, isTime = false) {
    const startTime = performance.now();
    const difference = end - start;
    
    const update = (currentTime) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      const currentValue = start + (difference * progress);
      
      if (isPercentage) {
        element.textContent = `${currentValue.toFixed(1)}%`;
      } else if (isTime) {
        element.textContent = `${currentValue.toFixed(1)}h`;
      } else {
        element.textContent = Math.floor(currentValue);
      }
      
      if (progress < 1) {
        requestAnimationFrame(update);
      }
    }
    
    requestAnimationFrame(update);
  }

  updateMetricChanges() {
    const changes = {
      newChange: this.getRandomChange(-5, 20),
      pendingChange: this.getRandomChange(-15, 5),
      progressChange: this.getRandomChange(-10, 15),
      resolvedChange: this.getRandomChange(5, 25)
    };

    Object.keys(changes).forEach(key => {
      const element = document.getElementById(key);
      if (element) {
        const value = changes[key];
        const parent = element.closest('.metric-change');
        
        element.textContent = `${value > 0 ? '+' : ''}${value}%`;
        
        if (parent) {
          parent.className = `metric-change ${value >= 0 ? 'positive' : 'negative'}`;
          const icon = parent.querySelector('i');
          if (icon) {
            icon.className = `fas fa-arrow-${value >= 0 ? 'up' : 'down'}`;
          }
        }
      }
    });
  }

  getRandomChange(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }

  initAnimations() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
        }
      });
    }, { threshold: 0.1 });

    document.querySelectorAll('.fade-in').forEach(el => {
      el.style.opacity = '0';
      el.style.transform = 'translateY(20px)';
      el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
      observer.observe(el);
    });
  }

  updateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('pt-BR', { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit'
    });
    const dateString = now.toLocaleDateString('pt-BR');
    
    const timeElement = document.getElementById('currentTime');
    if (timeElement) {
      timeElement.textContent = timeString;
    }

    const lastUpdateElement = document.getElementById('lastUpdate');
    if (lastUpdateElement) {
      lastUpdateElement.textContent = `${dateString} ${timeString}`;
    }
  }

  startAutoRefresh() {
    this.autoRefreshInterval = setInterval(() => {
      this.refreshData();
    }, this.refreshDelay);
  }

  refreshData() {
    console.log('Refreshing dashboard data...');
    this.initSparklines();
    
    // Simulate new data for chart
    if (this.chart) {
      const newDataPoint = Math.floor(Math.random() * 15) + 5;
      const resolvedDataPoint = Math.floor(Math.random() * 20) + 10;

      const now = new Date();
      const timeLabel = now.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });

      this.chart.data.labels.push(timeLabel);
      this.chart.data.datasets[0].data.push(newDataPoint);
      this.chart.data.datasets[1].data.push(resolvedDataPoint);

      if (this.chart.data.labels.length > 24) {
        this.chart.data.labels.shift();
        this.chart.data.datasets[0].data.shift();
        this.chart.data.datasets[1].data.shift();
      }

      this.chart.update('none');
    }
  }

  stopAutoRefresh() {
    if (this.autoRefreshInterval) {
      clearInterval(this.autoRefreshInterval);
      this.autoRefreshInterval = null;
    }
  }
}

// Global Functions
function changeTheme(theme, button) {
  document.documentElement.setAttribute('data-theme', theme);
  
  // Update active button
  document.querySelectorAll('.theme-btn').forEach(btn => btn.classList.remove('active'));
  button.classList.add('active');
  
  // Save preference
  localStorage.setItem('dashboard-theme', theme);
  
  showNotification('Tema Alterado', `Tema ${theme} aplicado com sucesso`, 'success');
}

function toggleFilters() {
  const panel = document.getElementById('filterPanel');
  if (panel) {
    const isOpen = panel.classList.contains('open');
    if (isOpen) {
      panel.classList.remove('open');
    } else {
      panel.classList.add('open');
    }
    dashboard.isFilterPanelOpen = !isOpen;
  }
}

function toggleFilter(element, type, value) {
  const checkbox = element.querySelector('.filter-checkbox');
  const isChecked = checkbox.classList.contains('checked');
  
  if (isChecked) {
    checkbox.classList.remove('checked');
  } else {
    checkbox.classList.add('checked');
  }
  
  // Update filters
  dashboard.currentFilters[type] = isChecked ? null : value;
  console.log('Filter updated:', dashboard.currentFilters);
}

function handleSearch(query) {
  if (query.trim().length > 0) {
    showSearchResults();
    // Simulate search results
    const results = [
      { type: 'ticket', title: `Chamado #${Math.floor(Math.random() * 1000)}`, subtitle: 'Sistema em manutenção' },
      { type: 'technician', title: 'Carlos Silva', subtitle: 'N3 - Especialista' },
      { type: 'ticket', title: `Chamado #${Math.floor(Math.random() * 1000)}`, subtitle: 'Erro de conexão' }
    ];
    
    const searchResults = document.getElementById('searchResults');
    if (searchResults) {
      searchResults.innerHTML = results.map(result => `
        <div class="search-result-item">
          <div style="font-weight: 500;">${result.title}</div>
          <div style="font-size: 12px; color: var(--text-muted);">${result.subtitle}</div>
        </div>
      `).join('');
    }
  } else {
    hideSearchResults();
  }
}

function showSearchResults() {
  const results = document.getElementById('searchResults');
  if (results) {
    results.classList.add('show');
    dashboard.isSearchOpen = true;
  }
}

function hideSearchResults() {
  setTimeout(() => {
    const results = document.getElementById('searchResults');
    if (results) {
      results.classList.remove('show');
      dashboard.isSearchOpen = false;
    }
  }, 200);
}

function filterByStatus(status) {
  dashboard.currentFilters.status = status;
  showNotification('Filtro Aplicado', `Filtrando por status: ${status}`, 'info');
  console.log('Filtering by status:', status);
}

function showLevelDetail(level) {
  showNotification('Detalhes do Nível', `Visualizando detalhes do ${level}`, 'info');
  console.log('Showing level detail:', level);
}

function changePeriod(period, button) {
  // Update active button
  document.querySelectorAll('.period-btn').forEach(btn => btn.classList.remove('active'));
  button.classList.add('active');
  
  dashboard.currentFilters.period = period;
  showNotification('Período Alterado', `Visualizando dados: ${period}`, 'info');
  console.log('Period changed to:', period);
}

function forceRefresh() {
  const button = event.target.closest('.refresh-btn');
  const icon = button.querySelector('i');
  
  // Animate refresh icon
  icon.style.animation = 'spin 1s linear infinite';
  
  dashboard.refreshData();
  
  setTimeout(() => {
    icon.style.animation = '';
    showNotification('Dados Atualizados', 'Dashboard atualizado com sucesso', 'success');
  }, 1000);
}

function showTechnicianDetail(name) {
  showNotification('Técnico Selecionado', `Visualizando perfil de ${name}`, 'info');
  console.log('Showing technician detail:', name);
}

function showNotification(title, message, type = 'info') {
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  
  const icon = type === 'success' ? 'check-circle' : 
               type === 'warning' ? 'exclamation-triangle' : 
               type === 'error' ? 'times-circle' : 'info-circle';
  
  notification.innerHTML = `
    <i class="fas fa-${icon}"></i>
    <div>
      <div style="font-weight: 600;">${title}</div>
      <div style="font-size: 12px; opacity: 0.8;">${message}</div>
    </div>
    <button class="notification-close" onclick="this.parentElement.remove()">
      <i class="fas fa-times"></i>
    </button>
  `;
  
  document.body.appendChild(notification);
  
  // Auto remove after 5 seconds
  setTimeout(() => {
    if (notification.parentElement) {
      notification.remove();
    }
  }, 5000);
}

// CSS Animations
const style = document.createElement('style');
style.textContent = `
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  
  @keyframes slideInRight {
    from {
      opacity: 0;
      transform: translateX(100%);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }
  
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
  }
  
  .fade-in {
    animation: fadeIn 0.6s ease-out forwards;
    opacity: 0;
  }
`;
document.head.appendChild(style);

// Initialize Dashboard
let dashboard;
document.addEventListener('DOMContentLoaded', () => {
  dashboard = new DashboardManager();
  
  // Load saved theme
  const savedTheme = localStorage.getItem('dashboard-theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);
  
  // Update active theme button
  const themeButton = document.querySelector(`[onclick*="${savedTheme}"]`);
  if (themeButton) {
    document.querySelectorAll('.theme-btn').forEach(btn => btn.classList.remove('active'));
    themeButton.classList.add('active');
  }
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
  if (dashboard) {
    dashboard.stopAutoRefresh();
  }
});