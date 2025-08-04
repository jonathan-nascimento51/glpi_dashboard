/**
 * Main Application Entry Point
 * Initializes the dashboard and manages global application state
 */

// Global error handler
window.addEventListener('error', (event) => {
  console.error('Global error:', event.error);
  
  // Show user-friendly error message
  if (window.dashboard) {
    window.dashboard.showNotification(
      'Ocorreu um erro inesperado. Recarregando a página...', 
      'error'
    );
    
    // Auto-reload after 3 seconds on critical errors
    setTimeout(() => {
      window.location.reload();
    }, 3000);
  }
});

// Handle connection status
window.addEventListener('online', () => {
  if (window.dashboard) {
    window.dashboard.showNotification('Conexão restabelecida', 'success');
    window.dashboard.loadData();
  }
});

window.addEventListener('offline', () => {
  if (window.dashboard) {
    window.dashboard.showNotification('Conexão perdida. Trabalhando offline.', 'warning');
  }
});

// Performance monitoring
if ('performance' in window) {
  window.addEventListener('load', () => {
    setTimeout(() => {
      const perfData = performance.getEntriesByType('navigation')[0];
      console.log('Page load time:', perfData.loadEventEnd - perfData.loadEventStart, 'ms');
    }, 0);
  });
}

// Initialize service worker for offline capabilities (if needed)
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    // Service worker can be added here for offline functionality
    console.log('Service Worker support detected');
  });
}

// Global keyboard shortcuts
document.addEventListener('keydown', (e) => {
  // Ctrl/Cmd + K for search focus
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault();
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
      searchInput.focus();
    }
  }
  
  // F5 or Ctrl/Cmd + R for force refresh
  if (e.key === 'F5' || ((e.ctrlKey || e.metaKey) && e.key === 'r')) {
    e.preventDefault();
    if (window.dashboard) {
      window.dashboard.forceRefresh();
    }
  }
  
  // Escape to close panels
  if (e.key === 'Escape') {
    if (window.dashboard && window.dashboard.components.filterPanel) {
      window.dashboard.components.filterPanel.close();
    }
  }
});

// Auto-save theme preferences
window.addEventListener('beforeunload', () => {
  // Ensure theme is saved
  if (window.themeManager) {
    localStorage.setItem('dashboard-theme', window.themeManager.getTheme());
  }
});

// Application health check
setInterval(() => {
  if (window.dashboard && !window.dashboard.isLoading) {
    // Ping health check endpoint
    fetch('/api/health', { method: 'HEAD' })
      .catch(() => {
        console.warn('Health check failed');
      });
  }
}, 60000); // Every minute

console.log('Dashboard application initialized');
