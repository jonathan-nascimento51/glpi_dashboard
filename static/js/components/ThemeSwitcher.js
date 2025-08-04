/**
 * Theme Switcher Component
 */
class ThemeSwitcher {
  constructor() {
    this.init();
  }

  init() {
    this.createThemeSwitcher();
    this.setupEventListeners();
  }

  createThemeSwitcher() {
    const headerControls = document.querySelector('.header-controls');
    if (!headerControls) return;

    // Check if theme switcher already exists
    if (document.querySelector('.theme-switcher')) return;

    const themeSwitcher = document.createElement('div');
    themeSwitcher.className = 'theme-switcher';

    const themes = window.themeManager.getAvailableThemes();
    const currentTheme = window.themeManager.getTheme();

    themeSwitcher.innerHTML = themes.map(theme => `
      <button 
        class="theme-btn ${theme.value === currentTheme ? 'active' : ''}" 
        data-theme="${theme.value}"
        title="Tema ${theme.label}"
      >
        <i class="fa ${theme.icon}"></i>
        <span>${theme.label}</span>
      </button>
    `).join('');

    // Insert before the last child (usually the user menu or status)
    headerControls.insertBefore(themeSwitcher, headerControls.lastElementChild);
  }

  setupEventListeners() {
    document.addEventListener('click', (e) => {
      if (e.target.closest('.theme-btn')) {
        const button = e.target.closest('.theme-btn');
        const theme = button.getAttribute('data-theme');
        this.changeTheme(theme);
      }
    });

    // Listen for theme changes from other sources
    window.addEventListener('themeChanged', (e) => {
      this.updateActiveButton(e.detail.theme);
    });
  }

  changeTheme(theme) {
    window.themeManager.applyTheme(theme);
    this.updateActiveButton(theme);
    
    // Add visual feedback
    this.addThemeChangeEffect();
  }

  updateActiveButton(theme) {
    document.querySelectorAll('.theme-btn').forEach(btn => {
      if (btn.getAttribute('data-theme') === theme) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });
  }

  addThemeChangeEffect() {
    // Add a subtle flash effect when theme changes
    const body = document.body;
    body.style.transition = 'background-color 0.3s ease';
    
    // Trigger a small opacity change for visual feedback
    body.style.opacity = '0.95';
    setTimeout(() => {
      body.style.opacity = '1';
    }, 150);
  }

  // Auto theme detection based on system preference
  detectSystemTheme() {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'light';
  }

  // Enable auto theme switching based on time
  enableAutoTheme() {
    const hour = new Date().getHours();
    const isNightTime = hour < 7 || hour > 19;
    
    if (isNightTime) {
      this.changeTheme('dark');
    } else {
      this.changeTheme('light');
    }
  }
}
