/**
 * Filter Panel Component
 */
class FilterPanel {
  constructor() {
    this.filters = {};
    this.isOpen = false;
    this.init();
  }

  init() {
    this.createFilterPanel();
    this.setupEventListeners();
  }

  createFilterPanel() {
    // Check if filter panel already exists
    if (document.querySelector('.filter-panel')) return;

    const panel = document.createElement('div');
    panel.className = 'filter-panel';
    panel.innerHTML = `
      <div class="filter-header">
        <h3 class="filter-title">Filtros</h3>
        <button class="filter-close" onclick="window.dashboard.components.filterPanel.close()">
          <i class="fa fa-times"></i>
        </button>
      </div>
      <div class="filter-content">
        ${this.createFilterGroups()}
      </div>
      <div class="filter-actions">
        <button class="btn btn-outline-secondary" onclick="window.dashboard.components.filterPanel.reset()">
          Limpar Filtros
        </button>
        <button class="btn btn-primary" onclick="window.dashboard.components.filterPanel.apply()">
          Aplicar Filtros
        </button>
      </div>
    `;

    document.body.appendChild(panel);
  }

  createFilterGroups() {
    const filterGroups = [
      {
        title: 'Status do Sistema',
        options: [
          { id: 'online', label: 'Online', checked: true },
          { id: 'offline', label: 'Offline', checked: false },
          { id: 'maintenance', label: 'Manutenção', checked: false }
        ]
      },
      {
        title: 'Período',
        options: [
          { id: 'last_hour', label: 'Última hora', checked: true },
          { id: 'last_24h', label: 'Últimas 24h', checked: false },
          { id: 'last_week', label: 'Última semana', checked: false },
          { id: 'last_month', label: 'Último mês', checked: false }
        ]
      },
      {
        title: 'Tipo de Métrica',
        options: [
          { id: 'cpu', label: 'CPU', checked: true },
          { id: 'memory', label: 'Memória', checked: true },
          { id: 'disk', label: 'Disco', checked: true },
          { id: 'network', label: 'Rede', checked: true }
        ]
      },
      {
        title: 'Severidade',
        options: [
          { id: 'info', label: 'Informação', checked: true },
          { id: 'warning', label: 'Aviso', checked: true },
          { id: 'critical', label: 'Crítico', checked: true }
        ]
      }
    ];

    return filterGroups.map(group => `
      <div class="filter-group">
        <div class="filter-group-title">${group.title}</div>
        <div class="filter-options">
          ${group.options.map(option => `
            <div class="filter-option" onclick="this.toggleFilter('${option.id}')">
              <div class="filter-checkbox ${option.checked ? 'checked' : ''}" data-filter="${option.id}">
                ${option.checked ? '<i class="fa fa-check"></i>' : ''}
              </div>
              <span class="filter-label">${option.label}</span>
            </div>
          `).join('')}
        </div>
      </div>
    `).join('');
  }

  setupEventListeners() {
    // Filter toggle button
    const filterBtn = document.querySelector('.filter-toggle');
    if (filterBtn) {
      filterBtn.addEventListener('click', this.toggle.bind(this));
    }

    // Create filter toggle button if it doesn't exist
    if (!filterBtn) {
      this.createFilterToggleButton();
    }
  }

  createFilterToggleButton() {
    const header = document.querySelector('.header-controls');
    if (!header) return;

    const button = document.createElement('button');
    button.className = 'btn btn-outline-secondary filter-toggle';
    button.innerHTML = '<i class="fa fa-filter"></i> Filtros';
    button.addEventListener('click', this.toggle.bind(this));

    header.appendChild(button);
  }

  toggleFilter(filterId) {
    const checkbox = document.querySelector(`[data-filter="${filterId}"]`);
    if (!checkbox) return;

    const isChecked = checkbox.classList.contains('checked');
    
    if (isChecked) {
      checkbox.classList.remove('checked');
      checkbox.innerHTML = '';
      this.filters[filterId] = false;
    } else {
      checkbox.classList.add('checked');
      checkbox.innerHTML = '<i class="fa fa-check"></i>';
      this.filters[filterId] = true;
    }
  }

  open() {
    const panel = document.querySelector('.filter-panel');
    if (panel) {
      panel.classList.add('open');
      this.isOpen = true;
    }
  }

  close() {
    const panel = document.querySelector('.filter-panel');
    if (panel) {
      panel.classList.remove('open');
      this.isOpen = false;
    }
  }

  toggle() {
    if (this.isOpen) {
      this.close();
    } else {
      this.open();
    }
  }

  apply() {
    // Collect active filters
    const activeFilters = {};
    
    document.querySelectorAll('.filter-checkbox.checked').forEach(checkbox => {
      const filterId = checkbox.getAttribute('data-filter');
      activeFilters[filterId] = true;
    });

    console.log('Applying filters:', activeFilters);
    
    // Trigger filter application event
    window.dispatchEvent(new CustomEvent('filtersApplied', {
      detail: { filters: activeFilters }
    }));

    this.close();
    
    // Show notification
    if (window.dashboard) {
      window.dashboard.showNotification('Filtros aplicados com sucesso', 'success');
    }
  }

  reset() {
    // Reset all checkboxes
    document.querySelectorAll('.filter-checkbox').forEach(checkbox => {
      const isDefault = this.isDefaultFilter(checkbox.getAttribute('data-filter'));
      
      if (isDefault) {
        checkbox.classList.add('checked');
        checkbox.innerHTML = '<i class="fa fa-check"></i>';
      } else {
        checkbox.classList.remove('checked');
        checkbox.innerHTML = '';
      }
    });

    this.filters = {};
    
    // Show notification
    if (window.dashboard) {
      window.dashboard.showNotification('Filtros resetados', 'info');
    }
  }

  isDefaultFilter(filterId) {
    // Define which filters are checked by default
    const defaults = ['online', 'last_hour', 'cpu', 'memory', 'disk', 'network', 'info', 'warning', 'critical'];
    return defaults.includes(filterId);
  }

  getActiveFilters() {
    return this.filters;
  }
}

// Make toggleFilter available globally for onclick handlers
window.toggleFilter = function(filterId) {
  if (window.dashboard && window.dashboard.components.filterPanel) {
    window.dashboard.components.filterPanel.toggleFilter(filterId);
  }
};
