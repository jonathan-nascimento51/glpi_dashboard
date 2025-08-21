import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import './index.css';

// Global error handler
window.addEventListener('error', event => {
  // Global error captured
});

// Handle connection status
window.addEventListener('online', () => {
  // Connection restored - could trigger UI notification here
});

window.addEventListener('offline', () => {
  // Connection lost - could trigger UI notification here
});

// Performance monitoring
if ('performance' in window) {
  window.addEventListener('load', () => {
    setTimeout(() => {
      const perfData = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      // Performance data available for monitoring tools
    }, 0);
  });
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
