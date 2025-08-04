import React from 'react';
import { X, Check } from 'lucide-react';
import { FilterState, TicketStatus } from '../types';

interface FilterPanelProps {
  isOpen: boolean;
  filters: FilterState;
  onClose: () => void;
  onFiltersChange: (filters: Partial<FilterState>) => void;
}

interface FilterOptionProps {
  checked: boolean;
  label: string;
  onClick: () => void;
}

const FilterOption: React.FC<FilterOptionProps> = ({ checked, label, onClick }) => {
  return (
    <button
      onClick={onClick}
      className="flex items-center space-x-3 w-full p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200"
    >
      <div className={`
        w-5 h-5 rounded border-2 flex items-center justify-center transition-colors duration-200
        ${checked 
          ? 'bg-primary-600 border-primary-600 text-white' 
          : 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800'
        }
      `}>
        {checked && <Check className="w-3 h-3" />}
      </div>
      <span className="text-sm font-medium text-gray-900 dark:text-white">
        {label}
      </span>
    </button>
  );
};

export const FilterPanel: React.FC<FilterPanelProps> = ({
  isOpen,
  filters,
  onClose,
  onFiltersChange,
}) => {
  if (!isOpen) return null;

  const handlePeriodChange = (period: FilterState['period']) => {
    onFiltersChange({ period });
  };

  const handleLevelToggle = (level: string) => {
    const newLevels = filters.levels.includes(level)
      ? filters.levels.filter(l => l !== level)
      : [...filters.levels, level];
    onFiltersChange({ levels: newLevels });
  };

  const handleStatusToggle = (status: TicketStatus) => {
    const newStatus = filters.status.includes(status)
      ? filters.status.filter(s => s !== status)
      : [...filters.status, status];
    onFiltersChange({ status: newStatus });
  };

  const handlePriorityToggle = (priority: 'high' | 'medium' | 'low') => {
    const newPriority = filters.priority.includes(priority)
      ? filters.priority.filter(p => p !== priority)
      : [...filters.priority, priority];
    onFiltersChange({ priority: newPriority });
  };

  const resetFilters = () => {
    onFiltersChange({
      period: 'today',
      levels: ['n1', 'n2', 'n3', 'n4'],
      status: ['new', 'progress', 'pending', 'resolved'],
      priority: ['high', 'medium', 'low'],
    });
  };

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 z-40 transition-opacity duration-300"
        onClick={onClose}
      />
      
      {/* Panel */}
      <div className="fixed top-0 right-0 h-full w-80 bg-white dark:bg-gray-900 shadow-xl z-50 transform transition-transform duration-300 slide-in">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Filtros Avançados
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors duration-200"
          >
            <X className="w-5 h-5 text-gray-500 dark:text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6 overflow-y-auto h-full pb-20">
          {/* Period Filter */}
          <div className="space-y-3">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wide">
              Período
            </h3>
            <div className="space-y-2">
              {[
                { value: 'today', label: 'Hoje' },
                { value: 'week', label: 'Esta Semana' },
                { value: 'month', label: 'Este Mês' },
              ].map((period) => (
                <FilterOption
                  key={period.value}
                  checked={filters.period === period.value}
                  label={period.label}
                  onClick={() => handlePeriodChange(period.value as FilterState['period'])}
                />
              ))}
            </div>
          </div>

          {/* Levels Filter */}
          <div className="space-y-3">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wide">
              Níveis
            </h3>
            <div className="space-y-2">
              {[
                { value: 'n1', label: 'N1 - Básico' },
                { value: 'n2', label: 'N2 - Intermediário' },
                { value: 'n3', label: 'N3 - Avançado' },
                { value: 'n4', label: 'N4 - Especialista' },
              ].map((level) => (
                <FilterOption
                  key={level.value}
                  checked={filters.levels.includes(level.value)}
                  label={level.label}
                  onClick={() => handleLevelToggle(level.value)}
                />
              ))}
            </div>
          </div>

          {/* Status Filter */}
          <div className="space-y-3">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wide">
              Status
            </h3>
            <div className="space-y-2">
              {[
                { value: 'new', label: 'Novos' },
                { value: 'progress', label: 'Em Progresso' },
                { value: 'pending', label: 'Pendente' },
                { value: 'resolved', label: 'Resolvido' },
              ].map((status) => (
                <FilterOption
                  key={status.value}
                  checked={filters.status.includes(status.value as TicketStatus)}
                  label={status.label}
                  onClick={() => handleStatusToggle(status.value as TicketStatus)}
                />
              ))}
            </div>
          </div>

          {/* Priority Filter */}
          <div className="space-y-3">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wide">
              Prioridade
            </h3>
            <div className="space-y-2">
              {[
                { value: 'high', label: 'Alta' },
                { value: 'medium', label: 'Média' },
                { value: 'low', label: 'Baixa' },
              ].map((priority) => (
                <FilterOption
                  key={priority.value}
                  checked={filters.priority.includes(priority.value as 'high' | 'medium' | 'low')}
                  label={priority.label}
                  onClick={() => handlePriorityToggle(priority.value as 'high' | 'medium' | 'low')}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="absolute bottom-0 left-0 right-0 p-6 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700">
          <div className="flex space-x-3">
            <button
              onClick={resetFilters}
              className="flex-1 btn-secondary"
            >
              Limpar Filtros
            </button>
            <button
              onClick={onClose}
              className="flex-1 btn-primary"
            >
              Aplicar
            </button>
          </div>
        </div>
      </div>
    </>
  );
};