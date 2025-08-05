import React, { useState } from 'react';
import { Calendar, Clock, Filter } from 'lucide-react';

export interface DateRange {
  startDate: string;
  endDate: string;
  label: string;
}

interface DateRangeFilterProps {
  selectedRange: DateRange;
  onRangeChange: (range: DateRange) => void;
  isLoading?: boolean;
}

const DateRangeFilter: React.FC<DateRangeFilterProps> = ({
  selectedRange,
  onRangeChange,
  isLoading = false
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [customStartDate, setCustomStartDate] = useState('');
  const [customEndDate, setCustomEndDate] = useState('');

  // Predefined date ranges
  const predefinedRanges: DateRange[] = [
    {
      startDate: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      endDate: new Date().toISOString().split('T')[0],
      label: 'Últimas 24 horas'
    },
    {
      startDate: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      endDate: new Date().toISOString().split('T')[0],
      label: 'Últimos 7 dias'
    },
    {
      startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      endDate: new Date().toISOString().split('T')[0],
      label: 'Últimos 30 dias'
    },
    {
      startDate: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      endDate: new Date().toISOString().split('T')[0],
      label: 'Últimos 90 dias'
    }
  ];

  const handlePredefinedRangeSelect = (range: DateRange) => {
    onRangeChange(range);
    setIsOpen(false);
  };

  const handleCustomRangeApply = () => {
    if (customStartDate && customEndDate) {
      const customRange: DateRange = {
        startDate: customStartDate,
        endDate: customEndDate,
        label: `${new Date(customStartDate).toLocaleDateString('pt-BR')} - ${new Date(customEndDate).toLocaleDateString('pt-BR')}`
      };
      onRangeChange(customRange);
      setIsOpen(false);
    }
  };

  const formatDateForDisplay = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('pt-BR');
  };

  return (
    <div className="relative">
      {/* Filter Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={isLoading}
        className="flex items-center space-x-2 bg-slate-800/80 hover:bg-slate-700/80 border border-slate-600/50 rounded-lg px-4 py-2 text-slate-200 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <Calendar className="w-4 h-4" />
        <span className="text-sm font-medium">
          {selectedRange.label}
        </span>
        <Filter className="w-4 h-4" />
        {isLoading && (
          <div className="w-4 h-4 border-2 border-slate-400 border-t-transparent rounded-full animate-spin" />
        )}
      </button>

      {/* Dropdown Panel */}
      {isOpen && (
        <div className="absolute top-full left-0 mt-2 w-80 bg-slate-800/95 backdrop-blur-sm border border-slate-600/50 rounded-lg shadow-xl z-50">
          <div className="p-4">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-slate-200 flex items-center space-x-2">
                <Clock className="w-4 h-4" />
                <span>Filtro por Período</span>
              </h3>
              <button
                onClick={() => setIsOpen(false)}
                className="text-slate-400 hover:text-slate-200 transition-colors"
              >
                ✕
              </button>
            </div>

            {/* Predefined Ranges */}
            <div className="space-y-2 mb-4">
              <h4 className="text-xs font-medium text-slate-300 uppercase tracking-wide">Períodos Rápidos</h4>
              {predefinedRanges.map((range, index) => (
                <button
                  key={index}
                  onClick={() => handlePredefinedRangeSelect(range)}
                  className={`w-full text-left px-3 py-2 rounded-md text-sm transition-all duration-200 ${
                    selectedRange.label === range.label
                      ? 'bg-blue-600/80 text-white'
                      : 'text-slate-300 hover:bg-slate-700/60 hover:text-slate-200'
                  }`}
                >
                  {range.label}
                  <div className="text-xs text-slate-400 mt-1">
                    {formatDateForDisplay(range.startDate)} - {formatDateForDisplay(range.endDate)}
                  </div>
                </button>
              ))}
            </div>

            {/* Custom Range */}
            <div className="border-t border-slate-600/50 pt-4">
              <h4 className="text-xs font-medium text-slate-300 uppercase tracking-wide mb-3">Período Personalizado</h4>
              <div className="space-y-3">
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Data Inicial</label>
                  <input
                    type="date"
                    value={customStartDate}
                    onChange={(e) => setCustomStartDate(e.target.value)}
                    className="w-full bg-slate-700/60 border border-slate-600/50 rounded-md px-3 py-2 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Data Final</label>
                  <input
                    type="date"
                    value={customEndDate}
                    onChange={(e) => setCustomEndDate(e.target.value)}
                    className="w-full bg-slate-700/60 border border-slate-600/50 rounded-md px-3 py-2 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50"
                  />
                </div>
                <button
                  onClick={handleCustomRangeApply}
                  disabled={!customStartDate || !customEndDate}
                  className="w-full bg-blue-600/80 hover:bg-blue-600 disabled:bg-slate-600/50 disabled:cursor-not-allowed text-white text-sm font-medium py-2 rounded-md transition-all duration-200"
                >
                  Aplicar Período
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DateRangeFilter;