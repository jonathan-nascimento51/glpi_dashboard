/**
 * Header Component
 */
class Header {
  constructor() {
    this.init();
  }

  init() {
    this.setupBrandAnimation();
    this.setupMobileToggle();
  }

  setupBrandAnimation() {
    const brandLogo = document.querySelector('.brand-logo');
    if (brandLogo) {
      brandLogo.addEventListener('mouseenter', () => {
        brandLogo.style.transform = 'scale(1.1) rotate(5deg)';
      });
      
      brandLogo.addEventListener('mouseleave', () => {
        brandLogo.style.transform = 'scale(1) rotate(0deg)';
      });
    }
  }

  setupMobileToggle() {
    // Setup mobile sidebar toggle if needed
    const toggle = document.querySelector('.sidebar-toggle');
    if (toggle) {
      toggle.addEventListener('click', this.toggleSidebar.bind(this));
    }
  }

  toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
      sidebar.classList.toggle('open');
    }
  }

  updateConnectionStatus(isOnline) {
    const statusIndicator = document.querySelector('.connection-status');
    if (statusIndicator) {
      statusIndicator.className = `connection-status ${isOnline ? 'online' : 'offline'}`;
      statusIndicator.title = isOnline ? 'Conectado' : 'Desconectado';
    }
  }
}
