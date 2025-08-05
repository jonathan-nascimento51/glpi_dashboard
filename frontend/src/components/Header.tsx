import React, { useState, useRef, useEffect } from 'react';
import { Search, RefreshCw, Filter, Cpu, X, Monitor, Maximize, AlertTriangle } from 'lucide-react';
import { Theme, SearchResult } from '../types';

interface HeaderProps {
  currentTime: string;
  systemActive: boolean;
  theme: Theme;
  searchQuery: string;
  searchResults: SearchResult[];
  isSimplifiedMode: boolean;
  showMonitoringAlerts: boolean;
  alertsCount: number;
  onThemeChange: (theme: Theme) => void;
  onSearch: (query: string) => void;
  onRefresh: () => void;
  onToggleFilters: () => void;
  onToggleSimplifiedMode: () => void;
  onToggleMonitoringAlerts: () => void;
  onNotification: (title: string, message: string, type: 'success' | 'error' | 'warning' | 'info') => void;
}

const themes: { value: Theme; label: string }[] = [
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' },
  { value: 'corporate', label: 'Corp' },
  { value: 'tech', label: 'Tech' },
];

export const Header: React.FC<HeaderProps> = ({
  currentTime,
  systemActive,
  theme,
  searchQuery,
  searchResults,
  isSimplifiedMode,
  showMonitoringAlerts,
  alertsCount,
  onThemeChange,
  onSearch,
  onRefresh,
  onToggleFilters,
  onToggleSimplifiedMode,
  onToggleMonitoringAlerts,
  onNotification,
}) => {
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [searchInputFocused, setSearchInputFocused] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Handle search input changes with debouncing
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    onSearch(value);
  };

  // Handle search focus
  const handleSearchFocus = () => {
    setSearchInputFocused(true);
    setShowSearchResults(true);
  };

  // Handle search blur
  const handleSearchBlur = () => {
    setSearchInputFocused(false);
    // Delay hiding results to allow clicking on them
    setTimeout(() => {
      setShowSearchResults(false);
    }, 200);
  };

  // Handle search result selection
  const handleSearchResultClick = (result: SearchResult) => {
    onNotification(
      `${result.type === 'ticket' ? 'Chamado' : 'Item'} selecionado`,
      result.title,
      'info'
    );
    setShowSearchResults(false);
    if (inputRef.current) {
      inputRef.current.blur();
    }
  };

  // Handle system status click
  const handleSystemStatusClick = () => {
    onNotification(
      'Sistema Online',
      'Todos os serviços estão funcionando normalmente',
      'success'
    );
  };

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl/Cmd + K for search focus
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <header className="glass-effect border-b border-gray-200/50 dark:border-gray-700/50 px-6 py-4 sticky top-0 z-50">
      <div className="flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
              <Cpu className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gradient">
                Centro de Comando
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Departamento de Tecnologia
              </p>
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="flex items-center space-x-4">
          {/* Theme Switcher - Dark/Light only */}
          <div className="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
            <button
              onClick={() => onThemeChange('light')}
              className={`px-3 py-1 text-sm font-medium rounded-md transition-colors duration-200 ${
                theme === 'light'
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              Light
            </button>
            <button
              onClick={() => onThemeChange('dark')}
              className={`px-3 py-1 text-sm font-medium rounded-md transition-colors duration-200 ${
                theme === 'dark'
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              Dark
            </button>
          </div>

          {/* Search */}
          <div className="relative" ref={searchRef}>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                ref={inputRef}
                type="text"
                placeholder="Buscar chamados, técnicos..."
                value={searchQuery}
                onChange={handleSearchChange}
                onFocus={handleSearchFocus}
                onBlur={handleSearchBlur}
                className="input-field pl-10 pr-4 w-64 text-sm"
              />
            </div>
            
            {/* Search Results */}
            {showSearchResults && (searchResults.length > 0 || searchQuery) && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-50 max-h-64 overflow-y-auto">
                {searchResults.length > 0 ? (
                  searchResults.map((result) => (
                    <button
                      key={result.id}
                      onClick={() => handleSearchResultClick(result)}
                      className="w-full px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-gray-700 border-b border-gray-100 dark:border-gray-600 last:border-b-0"
                    >
                      <div className="font-medium text-gray-900 dark:text-white text-sm">
                        {result.title}
                      </div>
                      {result.description && (
                        <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                          {result.description}
                        </div>
                      )}
                      <div className="flex items-center mt-2">
                        <span className={`status-indicator status-${result.status || 'new'}`}>
                          {result.type === 'ticket' ? 'Chamado' : 'Técnico'}
                        </span>
                      </div>
                    </button>
                  ))
                ) : searchQuery ? (
                  <div className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                    Nenhum resultado encontrado para "{searchQuery}"
                  </div>
                ) : null}
              </div>
            )}
          </div>



          {/* TV Mode Button */}
          <button
            onClick={onToggleSimplifiedMode}
            className={`btn-secondary flex items-center space-x-2 ${
              isSimplifiedMode ? 'bg-primary-600 text-white' : ''
            }`}
            title={isSimplifiedMode ? 'Sair do Modo TV' : 'Ativar Modo TV'}
          >
            <Monitor className="w-4 h-4" />
            <span className="text-sm">{isSimplifiedMode ? 'Sair TV' : 'Modo TV'}</span>
          </button>

          {/* Refresh Button */}
          <button
            onClick={onRefresh}
            className="btn-secondary flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span className="text-sm">Atualizar</span>
          </button>





          {/* Current Time */}
          <div className="text-sm font-mono text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-800 px-3 py-2 rounded-lg">
            {currentTime}
          </div>
        </div>
      </div>
    </header>
  );
};