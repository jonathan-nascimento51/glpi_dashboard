/**
 * Main Dashboard Component
 */
class Dashboard {
  constructor() {
    this.components = {};
    this.isLoading = false;
    this.refreshInterval = null;
    this.init();
  }

  init() {
    this.initializeComponents();
    this.setupEventListeners();
    this.startAutoRefresh();
  }

  initializeComponents() {
    // Initialize all dashboard components
    this.components.header = new Header();
    this.components.metricsGrid = new MetricsGrid();
    this.components.chartWidget = new ChartWidget();
    this.components.searchPanel = new SearchPanel();
    this.components.filterPanel = new FilterPanel();
    this.components.themeSwitcher = new ThemeSwitcher();
  }

  setupEventListeners() {
    // Global event listeners
    window.addEventListener('resize', this.handleResize.bind(this));
    window.addEventListener('themeChanged', this.handleThemeChange.bind(this));
    
    // Status live button
    const statusLive = document.querySelector('.status-live');
    if (statusLive) {
      statusLive.addEventListener('click', this.forceRefresh.bind(this));
    }
  }

  async loadData() {
    if (this.isLoading) return;
    
    this.isLoading = true;
    this.showLoadingState();

    try {
      // Load all dashboard data
      const [metrics, systemStatus, alerts] = await Promise.all([
        window.apiClient.getMetrics(),
        window.apiClient.getSystemStatus(),
        window.apiClient.getAlerts()
      ]);

      // Update components with new data
      this.components.metricsGrid.updateData(metrics.data);
      this.updateSystemStatus(systemStatus.data);
      this.updateAlerts(alerts.data);

      this.hideLoadingState();
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      this.showErrorState(error.message);
    } finally {
      this.isLoading = false;
    }
  }

  updateSystemStatus(status) {
    const statusElement = document.querySelector('.status-live');
    if (!statusElement) return;

    if (status.error) {
      statusElement.style.background = 'rgba(220, 38, 38, 0.1)';
      statusElement.style.borderColor = 'rgba(220, 38, 38, 0.2)';
      statusElement.style.color = 'var(--accent-red)';
      statusElement.innerHTML = '<i class="fa fa-circle-exclamation"></i> Sistema Offline';
      return;
    }

    // Update live status based on API response
    const pulse = statusElement.querySelector('.status-pulse');
    if (pulse) {
      pulse.style.animationPlayState = status.status === 'online' ? 'running' : 'paused';
    }
  }

  updateAlerts(alerts) {
    if (alerts.error) {
      console.warn('Could not load alerts:', alerts.message);
      return;
    }

    // Update alerts display if component exists
    const alertsContainer = document.querySelector('.alerts-container');
    if (alertsContainer && alerts.length > 0) {
      this.displayAlerts(alerts);
    }
  }

  displayAlerts(alerts) {
    // Implementation for alert display
    console.log('Displaying alerts:', alerts);
  }

  showLoadingState() {
    // Add loading states to components
    document.querySelectorAll('.metric-card').forEach(card => {
      card.classList.add('loading');
    });
  }

  hideLoadingState() {
    document.querySelectorAll('.metric-card').forEach(card => {
      card.classList.remove('loading');
    });
  }

  showErrorState(message) {
    // Show error notification
    this.showNotification(`Erro: ${message}`, 'error');
  }

  showNotification(message, type = 'info') {
    // Create and show notification
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
      <i class="fa fa-${type === 'error' ? 'exclamation-triangle' : 'info-circle'}"></i>
      <span>${message}</span>
      <button class="notification-close" onclick="this.parentElement.remove()">
        <i class="fa fa-times"></i>
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

  async forceRefresh() {
    await this.loadData();
    this.showNotification('Dados atualizados com sucesso', 'success');
  }

  startAutoRefresh() {
    // Refresh every 30 seconds
    this.refreshInterval = setInterval(() => {
      this.loadData();
    }, 30000);
  }

  stopAutoRefresh() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
      this.refreshInterval = null;
    }
  }

  handleResize() {
    // Handle responsive behavior
    Object.values(this.components).forEach(component => {
      if (component.handleResize) {
        component.handleResize();
      }
    });
  }

  handleThemeChange(event) {
    // Update charts when theme changes
    if (this.components.chartWidget) {
      this.components.chartWidget.updateTheme();
    }
  }

  destroy() {
    this.stopAutoRefresh();
    
    // Cleanup components
    Object.values(this.components).forEach(component => {
      if (component.destroy) {
        component.destroy();
      }
    });
  }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.dashboard = new Dashboard();
  window.dashboard.loadData();
});
