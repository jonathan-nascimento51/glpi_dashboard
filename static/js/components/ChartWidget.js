/**
 * Chart Widget Component
 */
class ChartWidget {
  constructor() {
    this.charts = {};
    this.init();
  }

  init() {
    this.createCharts();
    this.setupEventListeners();
  }

  setupEventListeners() {
    window.addEventListener('themeChanged', this.updateTheme.bind(this));
  }

  createCharts() {
    this.createPerformanceChart();
    this.createResourceChart();
    this.createNetworkChart();
  }

  async createPerformanceChart() {
    const canvas = document.getElementById('performanceChart');
    if (!canvas) return;

    try {
      const data = await window.apiClient.getChartData('performance');
      
      this.charts.performance = new Chart(canvas, {
        type: 'line',
        data: data.data.error ? this.getEmptyChartData() : data.data,
        options: this.getChartOptions('performance')
      });
    } catch (error) {
      console.error('Error creating performance chart:', error);
      this.showChartError(canvas, 'Erro ao carregar gráfico de performance');
    }
  }

  async createResourceChart() {
    const canvas = document.getElementById('resourceChart');
    if (!canvas) return;

    try {
      const data = await window.apiClient.getChartData('resources');
      
      this.charts.resources = new Chart(canvas, {
        type: 'doughnut',
        data: data.data.error ? this.getEmptyDoughnutData() : data.data,
        options: this.getChartOptions('resources')
      });
    } catch (error) {
      console.error('Error creating resource chart:', error);
      this.showChartError(canvas, 'Erro ao carregar gráfico de recursos');
    }
  }

  async createNetworkChart() {
    const canvas = document.getElementById('networkChart');
    if (!canvas) return;

    try {
      const data = await window.apiClient.getChartData('network');
      
      this.charts.network = new Chart(canvas, {
        type: 'bar',
        data: data.data.error ? this.getEmptyChartData() : data.data,
        options: this.getChartOptions('network')
      });
    } catch (error) {
      console.error('Error creating network chart:', error);
      this.showChartError(canvas, 'Erro ao carregar gráfico de rede');
    }
  }

  getChartOptions(type) {
    const isDark = window.themeManager.getTheme() === 'dark';
    const textColor = isDark ? '#cbd5e1' : '#475569';
    const gridColor = isDark ? '#475569' : '#e2e8f0';

    const baseOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: {
            color: textColor,
            font: {
              family: 'Inter, sans-serif'
            }
          }
        }
      },
      scales: {
        x: {
          ticks: { color: textColor },
          grid: { color: gridColor }
        },
        y: {
          ticks: { color: textColor },
          grid: { color: gridColor }
        }
      }
    };

    switch (type) {
      case 'performance':
        return {
          ...baseOptions,
          elements: {
            line: {
              tension: 0.4
            }
          }
        };
      
      case 'resources':
        return {
          ...baseOptions,
          cutout: '60%',
          scales: {} // Remove scales for doughnut chart
        };
      
      case 'network':
        return {
          ...baseOptions,
          scales: {
            ...baseOptions.scales,
            y: {
              ...baseOptions.scales.y,
              beginAtZero: true
            }
          }
        };
    }
  }

  getEmptyChartData() {
    return {
      labels: [],
      datasets: [{
        label: 'Sem dados disponíveis',
        data: [],
        backgroundColor: 'rgba(148, 163, 184, 0.1)',
        borderColor: 'rgba(148, 163, 184, 0.3)',
        borderWidth: 1
      }]
    };
  }

  getEmptyDoughnutData() {
    return {
      labels: ['Sem dados'],
      datasets: [{
        data: [100],
        backgroundColor: ['rgba(148, 163, 184, 0.1)'],
        borderColor: ['rgba(148, 163, 184, 0.3)'],
        borderWidth: 1
      }]
    };
  }

  showChartError(canvas, message) {
    const container = canvas.parentElement;
    const errorDiv = document.createElement('div');
    errorDiv.className = 'chart-error';
    errorDiv.innerHTML = `
      <div class="error-content">
        <i class="fa fa-chart-line"></i>
        <p>${message}</p>
        <button onclick="window.dashboard.forceRefresh()" class="btn btn-sm btn-outline-primary">
          Recarregar
        </button>
      </div>
    `;
    
    canvas.style.display = 'none';
    container.appendChild(errorDiv);
  }

  updateTheme() {
    Object.entries(this.charts).forEach(([key, chart]) => {
      if (chart) {
        chart.options = this.getChartOptions(key);
        chart.update();
      }
    });
  }

  destroy() {
    Object.values(this.charts).forEach(chart => {
      if (chart) {
        chart.destroy();
      }
    });
    this.charts = {};
  }
}
