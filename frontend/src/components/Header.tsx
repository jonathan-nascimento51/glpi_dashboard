import React, { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import { Search, RefreshCw, Filter, X, Monitor, Maximize, AlertTriangle, Clock, Wifi, WifiOff, Calendar, ChevronDown } from 'lucide-react';
import { Theme, SearchResult } from '../types';
import { SimpleTechIcon } from './SimpleTechIcon';

interface HeaderProps {
  currentTime: string;
  systemActive: boolean;
  theme: Theme;
  searchQuery: string;
  searchResults: SearchResult[];
  isSimplifiedMode: boolean;
  showMonitoringAlerts: boolean;
  alertsCount: number;
  dateRange: { startDate: string; endDate: string };
  onThemeChange: (theme: Theme) => void;
  onSearch: (query: string) => void;
  onRefresh: () => void;
  onToggleFilters: () => void;
  onToggleSimplifiedMode: () => void;
  onToggleMonitoringAlerts: () => void;
  onNotification: (title: string, message: string, type: 'success' | 'error' | 'warning' | 'info') => void;
  onDateRangeChange?: (dateRange: { startDate: string; endDate: string; label: string }) => void;
}

const themes: { value: Theme; label: string; icon: string }[] = [
  { value: 'light', label: 'Claro', icon: '☀️' },
  { value: 'dark', label: 'Escuro', icon: '🌙' },
  { value: 'corporate', label: 'Corporativo', icon: '🏢' },
  { value: 'tech', label: 'Tech', icon: '⚡' },
];

// Predefined date ranges
const dateRanges = [
  { label: 'Hoje', days: 0 },
  { label: 'Últimos 7 dias', days: 7 },
  { label: 'Últimos 15 dias', days: 15 },
  { label: 'Últimos 30 dias', days: 30 },
  { label: 'Últimos 90 dias', days: 90 },
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
  dateRange,
  onThemeChange,
  onSearch,
  onRefresh,
  onToggleFilters,
  onToggleSimplifiedMode,
  onToggleMonitoringAlerts,
  onNotification,
  onDateRangeChange,
}) => {
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [showThemeSelector, setShowThemeSelector] = useState(false);
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [customStartDate, setCustomStartDate] = useState('');
  const [customEndDate, setCustomEndDate] = useState('');
  
  const searchRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const themeRef = useRef<HTMLDivElement>(null);
  const dateRef = useRef<HTMLDivElement>(null);

  // Format date for display
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('pt-BR', { 
      day: '2-digit', 
      month: '2-digit', 
      year: '2-digit' 
    });
  };

  // Get date range label
  const getDateRangeLabel = () => {
    // ✅ Verificação de segurança
    if (!dateRange || !dateRange.startDate || !dateRange.endDate) {
      return 'Selecionar período';
    }
    
    const start = new Date(dateRange.startDate);
    const end = new Date(dateRange.endDate);
    const diffTime = Math.abs(end.getTime() - start.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    const predefined = dateRanges.find(range => range.days === diffDays);
    if (predefined) return predefined.label;
    
    return `${formatDate(dateRange.startDate)} - ${formatDate(dateRange.endDate)}`;
  };

  // Handle predefined date range selection
  const handleDateRangeSelect = useCallback((days: number) => {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);
    
    const startStr = startDate.toISOString().split('T')[0];
    const endStr = endDate.toISOString().split('T')[0];
    
    const range = dateRanges.find(r => r.days === days);
    onDateRangeChange?.({
      startDate: startStr,
      endDate: endStr,
      label: range?.label || 'Período personalizado'
    });
    setShowDatePicker(false);
    
    onNotification('Período Atualizado', `Filtro alterado para: ${range?.label}`, 'info');
  }, [onDateRangeChange, onNotification]);

  // Handle custom date range
  const handleCustomDateRange = useCallback(() => {
    if (customStartDate && customEndDate && onDateRangeChange) {
      onDateRangeChange({
        startDate: customStartDate,
        endDate: customEndDate,
        label: 'Período personalizado'
      });
      setShowDatePicker(false);
      onNotification('Período Personalizado', 'Período customizado aplicado', 'success');
    }
  }, [customStartDate, customEndDate, onDateRangeChange, onNotification]);

  // Search handlers
  const handleSearchChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    onSearch(e.target.value);
  }, [onSearch]);

  const handleSearchFocus = useCallback(() => {
    if (searchResults.length > 0) setShowSearchResults(true);
  }, [searchResults.length]);

  const handleSearchBlur = useCallback(() => {
    setTimeout(() => setShowSearchResults(false), 200);
  }, []);

  // Enhanced refresh with loading state
  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true);
    try {
      await onRefresh();
      onNotification('Sucesso', 'Dados atualizados', 'success');
    } catch {
      onNotification('Erro', 'Falha na atualização', 'error');
    } finally {
      setTimeout(() => setIsRefreshing(false), 1000);
    }
  }, [onRefresh, onNotification]);

  // Theme change handler
  const handleThemeChange = useCallback((newTheme: Theme) => {
    onThemeChange(newTheme);
    setShowThemeSelector(false);
    const themeName = themes.find(t => t.value === newTheme)?.label;
    onNotification('Tema', `Alterado para ${themeName}`, 'info');
  }, [onThemeChange, onNotification]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
      }
      if (e.key === 'Escape') {
        setShowSearchResults(false);
        setShowThemeSelector(false);
        setShowDatePicker(false);
      }
      if (e.key === 'F5') {
        e.preventDefault();
        handleRefresh();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleRefresh]);

  // Click outside handlers
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowSearchResults(false);
      }
      if (themeRef.current && !themeRef.current.contains(event.target as Node)) {
        setShowThemeSelector(false);
      }
      if (dateRef.current && !dateRef.current.contains(event.target as Node)) {
        setShowDatePicker(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const currentTheme = themes.find(t => t.value === theme) || themes[0];

  return (
    <header className="w-full bg-gradient-to-r from-blue-600 via-purple-600 to-blue-700 text-white shadow-xl border-b border-white/10 relative z-50">
      <div className="w-full px-6 py-4">
        <div className="flex items-center justify-between w-full">
          
          {/* ========== SEÇÃO ESQUERDA: LOGO + TÍTULO ========== */}
          <div className="flex items-center space-x-4 min-w-0 flex-shrink-0">
            <div className="w-11 h-11 bg-white/15 backdrop-blur-sm rounded-xl flex items-center justify-center border border-white/20 hover:bg-white/20 transition-all duration-200 group">
              <SimpleTechIcon size={24} className="group-hover:scale-110 transition-transform" />
            </div>
            <div className="min-w-0">
              <h1 className="text-xl font-bold text-white truncate">
                Dashboard GLPI
              </h1>
              <p className="text-blue-100 text-sm font-medium truncate">
                Departamento de Tecnologia do Estado
              </p>
            </div>
          </div>
          
          {/* ========== SEÇÃO CENTRO: BUSCA + FILTRO DE DATA ========== */}
          <div className="flex items-center space-x-6 flex-1 justify-center max-w-2xl mx-8">
            
            {/* Search Bar */}
            <div className="relative flex-1 max-w-md" ref={searchRef}>
              <div className="relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-4 h-4 text-white/60" />
                <input 
                  ref={inputRef}
                  type="text" 
                  value={searchQuery}
                  onChange={handleSearchChange}
                  onFocus={handleSearchFocus}
                  onBlur={handleSearchBlur}
                  placeholder="Buscar chamados... (Ctrl+K)"
                  className="w-full pl-12 pr-10 py-3 bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-white/30 focus:bg-white/20 transition-all text-sm font-medium"
                />
                {searchQuery && (
                  <button
                    onClick={() => onSearch('')}
                    className="absolute right-4 top-1/2 transform -translate-y-1/2 w-4 h-4 text-white/60 hover:text-white transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
              </div>
              
              {/* Search Results */}
              {showSearchResults && searchResults.length > 0 && (
                <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-xl shadow-2xl border border-gray-200 max-h-80 overflow-y-auto z-50">
                  {searchResults.map((result, index) => (
                    <button
                      key={index}
                      className="w-full px-4 py-3 text-left hover:bg-gray-50 border-b border-gray-100 last:border-b-0 transition-colors"
                    >
                      <div className="text-sm font-medium text-gray-900">{result.title}</div>
                      <div className="text-xs text-gray-500 mt-1">{result.description}</div>
                    </button>
                  ))}
                </div>
              )}
            </div>
            
            {/* Date Range Picker - FUNCIONAL */}
            <div className="relative" ref={dateRef}>
              <button
                onClick={() => setShowDatePicker(!showDatePicker)}
                className="flex items-center space-x-3 px-4 py-3 bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl text-white hover:bg-white/20 transition-all font-medium"
              >
                <Calendar className="w-4 h-4" />
                <span className="text-sm whitespace-nowrap">{getDateRangeLabel()}</span>
                <ChevronDown className="w-4 h-4" />
              </button>
              
              {/* Date Picker Dropdown */}
              {showDatePicker && (
                <div className="absolute top-full right-0 mt-2 bg-white rounded-xl shadow-2xl border border-gray-200 py-3 min-w-80 z-50">
                  <div className="px-4 pb-3 border-b border-gray-100">
                    <h3 className="text-sm font-semibold text-gray-900">Selecionar Período</h3>
                  </div>
                  
                  {/* Predefined Ranges */}
                  <div className="py-2">
                    {dateRanges.map((range) => (
                      <button
                        key={range.days}
                        onClick={() => handleDateRangeSelect(range.days)}
                        className="w-full px-4 py-2 text-left hover:bg-gray-50 transition-colors text-sm text-gray-700 hover:text-gray-900"
                      >
                        {range.label}
                      </button>
                    ))}
                  </div>
                  
                  {/* Custom Range */}
                  <div className="border-t border-gray-100 pt-3 px-4">
                    <div className="text-xs font-medium text-gray-500 mb-2">Período Personalizado</div>
                    <div className="grid grid-cols-2 gap-2 mb-3">
                      <input
                        type="date"
                        value={customStartDate}
                        onChange={(e) => setCustomStartDate(e.target.value)}
                        className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Data inicial"
                      />
                      <input
                        type="date"
                        value={customEndDate}
                        onChange={(e) => setCustomEndDate(e.target.value)}
                        className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Data final"
                      />
                    </div>
                    <button
                      onClick={handleCustomDateRange}
                      disabled={!customStartDate || !customEndDate}
                      className="w-full px-3 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      Aplicar Período
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
          
          {/* ========== SEÇÃO DIREITA: CONTROLES + STATUS ========== */}
          <div className="flex items-center space-x-3 flex-shrink-0">
            
            {/* System Status */}
            <div className={`flex items-center space-x-2 px-3 py-2 rounded-xl text-sm font-medium backdrop-blur-sm border ${
              systemActive
                ? 'bg-green-500/20 text-green-100 border-green-400/30'
                : 'bg-red-500/20 text-red-100 border-red-400/30'
            }`}>
              {systemActive ? <Wifi className="w-4 h-4" /> : <WifiOff className="w-4 h-4" />}
              <span>{systemActive ? 'Online' : 'Offline'}</span>
            </div>

            {/* Monitoring Alerts */}
            {alertsCount > 0 && (
              <button
                onClick={onToggleMonitoringAlerts}
                className="relative px-3 py-2 rounded-xl text-sm font-medium transition-all backdrop-blur-sm border bg-red-500/20 text-red-100 border-red-400/30 hover:bg-red-500/30"
              >
                <AlertTriangle className="w-4 h-4" />
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                  {alertsCount > 9 ? '9+' : alertsCount}
                </span>
              </button>
            )}

            {/* Filters */}
            <button 
              onClick={onToggleFilters}
              className="flex items-center space-x-2 px-3 py-2 bg-white/10 hover:bg-white/20 rounded-xl text-sm font-medium transition-all backdrop-blur-sm border border-white/20"
            >
              <Filter className="w-4 h-4" />
              <span>Filtros</span>
            </button>
            
            {/* Theme Selector */}
            <div className="relative" ref={themeRef}>
              <button
                onClick={() => setShowThemeSelector(!showThemeSelector)}
                className="flex items-center space-x-2 px-3 py-2 bg-white/10 hover:bg-white/20 rounded-xl text-sm font-medium transition-all backdrop-blur-sm border border-white/20"
              >
                <span>{currentTheme.icon}</span>
                <span>{currentTheme.label}</span>
              </button>
              
              {showThemeSelector && (
                <div className="absolute top-full right-0 mt-2 bg-white rounded-xl shadow-2xl border border-gray-200 py-2 min-w-40 z-50">
                  {themes.map((themeOption) => (
                    <button
                      key={themeOption.value}
                      onClick={() => handleThemeChange(themeOption.value)}
                      className={`w-full px-4 py-2 text-left hover:bg-gray-50 transition-colors flex items-center gap-3 ${
                        theme === themeOption.value ? 'bg-blue-50 text-blue-600' : 'text-gray-700'
                      }`}
                    >
                      <span>{themeOption.icon}</span>
                      <span className="text-sm">{themeOption.label}</span>
                      {theme === themeOption.value && (
                        <div className="ml-auto w-2 h-2 bg-blue-500 rounded-full" />
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>
            
            {/* Mode Toggle */}
            <button 
              onClick={onToggleSimplifiedMode}
              className={`flex items-center space-x-2 px-3 py-2 rounded-xl text-sm font-medium transition-all backdrop-blur-sm ${
                isSimplifiedMode 
                  ? 'bg-white/20 text-white border border-white/30' 
                  : 'bg-white/10 hover:bg-white/20 border border-white/20'
              }`}
            >
              {isSimplifiedMode ? <Maximize className="w-4 h-4" /> : <Monitor className="w-4 h-4" />}
              <span>{isSimplifiedMode ? 'Sair TV' : 'Modo TV'}</span>
            </button>
            
            {/* Refresh */}
            <button 
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="flex items-center space-x-2 px-3 py-2 bg-white/10 hover:bg-white/20 rounded-xl text-sm font-medium transition-all backdrop-blur-sm border border-white/20 disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
              <span>Atualizar</span>
            </button>
            
            {/* Current Time */}
            <div className="flex items-center space-x-2 text-sm text-blue-100 bg-white/10 px-3 py-2 rounded-xl backdrop-blur-sm border border-white/20 font-mono">
              <Clock className="w-4 h-4" />
              <span>{currentTime}</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};