/**
 * Theme management utilities
 */
class ThemeManager {
  constructor() {
    this.currentTheme = localStorage.getItem('dashboard-theme') || 'light';
    this.applyTheme(this.currentTheme);
  }

  applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('dashboard-theme', theme);
    this.currentTheme = theme;
    
    // Dispatch theme change event
    window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme } }));
  }

  getTheme() {
    return this.currentTheme;
  }

  getAvailableThemes() {
    return [
      { value: 'light', label: 'Light', icon: 'fa-sun' },
      { value: 'dark', label: 'Dark', icon: 'fa-moon' },
      { value: 'corporate', label: 'Corp', icon: 'fa-building' },
      { value: 'tech', label: 'Tech', icon: 'fa-microchip' }
    ];
  }
}

// Global theme manager instance
window.themeManager = new ThemeManager();
