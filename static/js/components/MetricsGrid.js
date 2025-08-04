/**
 * Metrics Grid Component
 */
class MetricsGrid {
  constructor() {
    this.metrics = {};
    this.init();
  }

  init() {
    this.createMetricCards();
  }

  createMetricCards() {
    const metricsContainer = document.querySelector('.metrics-grid');
    if (!metricsContainer) return;

    const metricConfigs = [
      {
        id: 'cpu_usage',
        title: 'CPU',
        icon: 'fa-microchip',
        format: 'percentage',
        thresholds: { warning: 70, critical: 90 }
      },
      {
        id: 'memory_usage',
        title: 'Memória',
        icon: 'fa-memory',
        format: 'percentage',
        thresholds: { warning: 75, critical: 90 }
      },
      {
        id: 'disk_usage',
        title: 'Armazenamento',
        icon: 'fa-hard-drive',
        format: 'percentage',
        thresholds: { warning: 80, critical: 95 }
      },
      {
        id: 'network_status',
        title: 'Rede',
        icon: 'fa-network-wired',
        format: 'status'
      },
      {
        id: 'active_users',
        title: 'Usuários Ativos',
        icon: 'fa-users',
        format: 'number'
      },
      {
        id: 'system_uptime',
        title: 'Tempo Ativo',
        icon: 'fa-clock',
        format: 'uptime'
      }
    ];

    metricConfigs.forEach(config => {
      this.createMetricCard(config);
    });
  }

  createMetricCard(config) {
    const card = document.createElement('div');
    card.className = 'metric-card';
    card.id = `metric-${config.id}`;
    
    card.innerHTML = `
      <div class="metric-header">
        <div class="metric-icon">
          <i class="fa ${config.icon}"></i>
        </div>
        <h3 class="metric-title">${config.title}</h3>
      </div>
      <div class="metric-content">
        <div class="metric-value" id="value-${config.id}">--</div>
        <div class="metric-status" id="status-${config.id}">
          <span class="status-indicator"></span>
          <span class="status-text">Carregando...</span>
        </div>
      </div>
      <div class="metric-trend" id="trend-${config.id}">
        <i class="fa fa-minus"></i>
        <span>Sem dados</span>
      </div>
    `;

    const container = document.querySelector('.metrics-grid');
    if (container) {
      container.appendChild(card);
    }
  }

  updateData(metricsData) {
    if (metricsData.error) {
      this.showErrorState(metricsData.message);
      return;
    }

    Object.entries(metricsData.data || {}).forEach(([key, data]) => {
      this.updateMetric(key, data);
    });
  }

  updateMetric(metricId, data) {
    const valueElement = document.getElementById(`value-${metricId}`);
    const statusElement = document.getElementById(`status-${metricId}`);
    const trendElement = document.getElementById(`trend-${metricId}`);

    if (!valueElement) return;

    if (data.status === 'error') {
      valueElement.textContent = 'N/A';
      this.setStatus(statusElement, 'error', 'Erro');
      return;
    }

    // Update value based on format
    switch (metricId) {
      case 'cpu_usage':
      case 'memory_usage':
      case 'disk_usage':
        valueElement.textContent = `${data.value || 0}%`;
        this.setStatusByThreshold(statusElement, data.value, { warning: 70, critical: 90 });
        break;
      
      case 'network_status':
        valueElement.textContent = data.status === 'online' ? 'Online' : 'Offline';
        this.setStatus(statusElement, data.status === 'online' ? 'success' : 'error', 
                     data.status === 'online' ? 'Conectado' : 'Desconectado');
        break;
      
      case 'active_users':
        valueElement.textContent = data.count || 0;
        this.setStatus(statusElement, 'success', 'Normal');
        break;
      
      case 'system_uptime':
        valueElement.textContent = this.formatUptime(data.value);
        this.setStatus(statusElement, 'success', 'Estável');
        break;
    }

    // Update trend if available
    if (data.trend && trendElement) {
      this.updateTrend(trendElement, data.trend);
    }
  }

  setStatusByThreshold(statusElement, value, thresholds) {
    if (value >= thresholds.critical) {
      this.setStatus(statusElement, 'error', 'Crítico');
    } else if (value >= thresholds.warning) {
      this.setStatus(statusElement, 'warning', 'Atenção');
    } else {
      this.setStatus(statusElement, 'success', 'Normal');
    }
  }

  setStatus(statusElement, type, text) {
    if (!statusElement) return;

    const indicator = statusElement.querySelector('.status-indicator');
    const textSpan = statusElement.querySelector('.status-text');

    if (indicator) {
      indicator.className = `status-indicator status-${type}`;
    }
    
    if (textSpan) {
      textSpan.textContent = text;
    }
  }

  updateTrend(trendElement, trend) {
    const icon = trendElement.querySelector('i');
    const text = trendElement.querySelector('span');

    if (trend.direction === 'up') {
      icon.className = 'fa fa-arrow-up';
      trendElement.className = 'metric-trend trend-up';
    } else if (trend.direction === 'down') {
      icon.className = 'fa fa-arrow-down';
      trendElement.className = 'metric-trend trend-down';
    } else {
      icon.className = 'fa fa-minus';
      trendElement.className = 'metric-trend trend-stable';
    }

    if (text) {
      text.textContent = trend.text || 'Estável';
    }
  }

  formatUptime(seconds) {
    if (!seconds) return '0d 0h';
    
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);

    if (days > 0) {
      return `${days}d ${hours}h`;
    } else if (hours > 0) {
      return `${hours}h ${minutes}m`;
    } else {
      return `${minutes}m`;
    }
  }

  showErrorState(message) {
    const metricsGrid = document.querySelector('.metrics-grid');
    if (metricsGrid) {
      const errorElement = document.querySelector('.metrics-error') || document.createElement('div');
      errorElement.className = 'metrics-error';
      errorElement.innerHTML = `
        <div class="error-content">
          <i class="fa fa-exclamation-triangle"></i>
          <h3>Erro ao carregar métricas</h3>
          <p>${message}</p>
          <button onclick="window.dashboard.forceRefresh()" class="btn btn-primary">
            <i class="fa fa-refresh"></i> Tentar novamente
          </button>
        </div>
      `;
      
      if (!document.querySelector('.metrics-error')) {
        metricsGrid.appendChild(errorElement);
      }
    }
  }
}
