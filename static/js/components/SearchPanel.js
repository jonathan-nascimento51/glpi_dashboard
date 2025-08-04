/**
 * Search Panel Component
 */
class SearchPanel {
  constructor() {
    this.searchTimeout = null;
    this.isSearching = false;
    this.init();
  }

  init() {
    this.setupSearchInput();
    this.setupEventListeners();
  }

  setupSearchInput() {
    const searchInput = document.querySelector('.search-input');
    if (!searchInput) return;

    searchInput.addEventListener('input', this.handleSearchInput.bind(this));
    searchInput.addEventListener('focus', this.handleSearchFocus.bind(this));
    searchInput.addEventListener('blur', this.handleSearchBlur.bind(this));
  }

  setupEventListeners() {
    // Close search results when clicking outside
    document.addEventListener('click', (e) => {
      const searchContainer = document.querySelector('.search-container');
      if (searchContainer && !searchContainer.contains(e.target)) {
        this.hideSearchResults();
      }
    });

    // Handle escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.hideSearchResults();
      }
    });
  }

  handleSearchInput(event) {
    const query = event.target.value.trim();

    // Clear previous timeout
    if (this.searchTimeout) {
      clearTimeout(this.searchTimeout);
    }

    if (query.length < 2) {
      this.hideSearchResults();
      return;
    }

    // Debounce search
    this.searchTimeout = setTimeout(() => {
      this.performSearch(query);
    }, 300);
  }

  handleSearchFocus() {
    const input = document.querySelector('.search-input');
    if (input && input.value.trim().length >= 2) {
      this.showSearchResults();
    }
  }

  handleSearchBlur() {
    // Delay hiding to allow clicking on results
    setTimeout(() => {
      this.hideSearchResults();
    }, 200);
  }

  async performSearch(query) {
    if (this.isSearching) return;

    this.isSearching = true;
    this.showSearchLoading();

    try {
      const response = await window.apiClient.search(query);
      
      if (response.data.error) {
        this.showSearchError(response.data.message);
        return;
      }

      this.displaySearchResults(response.data.results || []);
    } catch (error) {
      console.error('Search error:', error);
      this.showSearchError('Erro na pesquisa. Tente novamente.');
    } finally {
      this.isSearching = false;
    }
  }

  showSearchLoading() {
    const resultsContainer = this.getSearchResultsContainer();
    resultsContainer.innerHTML = `
      <div class="search-loading">
        <i class="fa fa-spinner fa-spin"></i>
        <span>Pesquisando...</span>
      </div>
    `;
    this.showSearchResults();
  }

  showSearchError(message) {
    const resultsContainer = this.getSearchResultsContainer();
    resultsContainer.innerHTML = `
      <div class="search-error">
        <i class="fa fa-exclamation-triangle"></i>
        <span>${message}</span>
      </div>
    `;
    this.showSearchResults();
  }

  displaySearchResults(results) {
    const resultsContainer = this.getSearchResultsContainer();

    if (results.length === 0) {
      resultsContainer.innerHTML = `
        <div class="search-no-results">
          <i class="fa fa-search"></i>
          <span>Nenhum resultado encontrado</span>
        </div>
      `;
    } else {
      resultsContainer.innerHTML = results.map(result => `
        <div class="search-result-item" onclick="this.handleResultClick('${result.id}')">
          <div class="search-result-icon">
            <i class="fa ${result.icon || 'fa-file'}"></i>
          </div>
          <div class="search-result-content">
            <div class="search-result-title">${result.title}</div>
            <div class="search-result-description">${result.description || ''}</div>
          </div>
          <div class="search-result-type">${result.type || ''}</div>
        </div>
      `).join('');
    }

    this.showSearchResults();
  }

  handleResultClick(resultId) {
    console.log('Result clicked:', resultId);
    // Implement navigation or action based on result
    this.hideSearchResults();
  }

  showSearchResults() {
    const resultsContainer = this.getSearchResultsContainer();
    resultsContainer.classList.add('show');
  }

  hideSearchResults() {
    const resultsContainer = this.getSearchResultsContainer();
    resultsContainer.classList.remove('show');
  }

  getSearchResultsContainer() {
    let container = document.querySelector('.search-results');
    
    if (!container) {
      container = document.createElement('div');
      container.className = 'search-results';
      
      const searchContainer = document.querySelector('.search-container');
      if (searchContainer) {
        searchContainer.appendChild(container);
      }
    }

    return container;
  }

  clearSearch() {
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
      searchInput.value = '';
      this.hideSearchResults();
    }
  }
}
