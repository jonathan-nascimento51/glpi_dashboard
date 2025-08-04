/**
 * API utility functions for making requests to Flask backend
 */
class ApiClient {
  constructor(baseUrl = '') {
    this.baseUrl = baseUrl;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `HTTP error! status: ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error(`API request failed for ${url}:`, error);
      throw error;
    }
  }

  async get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  }

  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Dashboard specific API calls
  async getMetrics() {
    return this.get('/api/metrics');
  }

  async getSystemStatus() {
    return this.get('/api/system-status');
  }

  async search(query) {
    return this.get(`/api/search?q=${encodeURIComponent(query)}`);
  }

  async getChartData(chartType) {
    return this.get(`/api/chart-data/${chartType}`);
  }

  async getAlerts() {
    return this.get('/api/alerts');
  }
}

// Global API client instance
window.apiClient = new ApiClient();
