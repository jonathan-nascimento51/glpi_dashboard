import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Search, X, Clock, Calendar, ChevronDown } from 'lucide-react';
import { Theme, SearchResult } from '../types';
import { SimpleTechIcon } from './SimpleTechIcon';

interface HeaderProps {
  currentTime: string;
  systemActive: boolean;
  theme: Theme;
  searchQuery: string;
  searchResults: SearchResult[];
  dateRange: { startDate: string; endDate: string };
  onThemeChange: (theme: Theme) => void;
  onSearch: (query: string) => void;
  onNotification: (title: string, message: string, type: 'success' | 'error' | 'warning' | 'info') => void;
  onDateRangeChange?: (dateRange: { startDate: string; endDate: string; label: string }) => void;
  onPerformanceDashboard?: () => void;
}

const themes: { value: Theme; label: string; icon: string }[] = [
  { value: 'light', label: 'Claro', icon: '☀️' },
  { value: 'dark', label: 'Escuro', icon: '🌙' },
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
  // systemActive, // Unused variable
  theme,
  searchQuery,
  searchResults,
  dateRange,
  onThemeChange,
  onSearch,
  onNotification,
  onDateRangeChange,
  onPerformanceDashboard,
}) => {
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [showThemeSelector, setShowThemeSelector] = useState(false);
  const [showDatePicker, setShowDatePicker] = useState(false);

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

    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

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
    <header className="figma-header w-full shadow-xl relative z-50">
      <div className="w-full px-6 py-4">
        <div className="flex items-center justify-between w-full">
          
          {/* ========== SEÇÃO ESQUERDA: LOGO + TÍTULO ========== */}
          <div className="flex items-center space-x-4 min-w-0 flex-shrink-0">
            <div className="w-11 h-11 figma-glass-card rounded-xl flex items-center justify-center hover:scale-105 transition-all duration-200 group">
              <SimpleTechIcon size={24} className="group-hover:scale-110 transition-transform" />
            </div>
            <div className="min-w-0">
              <h1 className="figma-heading-large text-xl font-bold truncate">
                Dashboard GLPI
              </h1>
              <p className="figma-subheading text-sm font-medium truncate">
                Departamento de Manutenção
              </p>
            </div>
          </div>
          
          {/* ========== SEÇÃO CENTRO: BUSCA + FILTRO DE DATA ========== */}
          <div className="flex items-center space-x-6 flex-1 justify-center max-w-2xl mx-8">
            
            {/* Search Bar */}
            <div className="relative flex-1 max-w-md" ref={searchRef}>
              <div className="relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-4 h-4 figma-body opacity-60" />
                <input 
                  ref={inputRef}
                  type="text" 
                  value={searchQuery}
                  onChange={handleSearchChange}
                  onFocus={handleSearchFocus}
                  onBlur={handleSearchBlur}
                  placeholder="Buscar chamados... (Ctrl+K)"
                  className="input-field w-full pl-12 pr-10 py-3 rounded-xl text-sm font-medium"
                />
                {searchQuery && (
                  <button
                    onClick={() => onSearch('')}
                    className="absolute right-4 top-1/2 transform -translate-y-1/2 w-4 h-4 figma-body opacity-60 hover:opacity-100 transition-opacity"
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
                className="btn-secondary flex items-center space-x-3 px-4 py-3 rounded-xl font-medium"
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
          <div className="flex items-center space-x-4 flex-shrink-0">
            


            {/* Theme Selector */}
            <div className="relative" ref={themeRef}>
              <button
                onClick={() => setShowThemeSelector(!showThemeSelector)}
                className="btn-secondary flex items-center space-x-2 px-3 py-2 rounded-xl text-sm font-medium"
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
            


            {/* Current Time */}
            <div className="figma-glass-card flex items-center space-x-3 text-sm px-4 py-2 rounded-xl font-mono min-w-0">
              <Clock className="w-4 h-4 flex-shrink-0" />
              <div className="flex flex-col leading-tight">
                <span className="figma-body text-xs font-medium whitespace-nowrap">{currentTime}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};