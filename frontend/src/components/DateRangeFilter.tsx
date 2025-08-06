import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Calendar, Clock, Filter, ChevronDown } from 'lucide-react';
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

// Interface unificada que suporta ambos os formatos
export interface DateRange {
  startDate?: string;  // Para compatibilidade com versão antiga
  endDate?: string;    // Para compatibilidade com versão antiga
  start?: Date;        // Para compatibilidade com versão nova
  end?: Date;          // Para compatibilidade com versão nova
  label: string;
}

interface DateRangeFilterProps {
  // Props da versão antiga
  selectedRange?: DateRange;
  onRangeChange?: (range: DateRange) => void;
  isLoading?: boolean;
  
  // Props da versão nova
  value?: DateRange;
  onChange?: (range: DateRange) => void;
  className?: string;
  
  // Configuração de tema
  variant?: 'modern' | 'classic';
}

const DateRangeFilter: React.FC<DateRangeFilterProps> = ({
  selectedRange,
  onRangeChange,
  isLoading = false,
  value,
  onChange,
  className,
  variant = 'classic'
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [customStartDate, setCustomStartDate] = useState('');
  const [customEndDate, setCustomEndDate] = useState('');

  // Normalizar props para compatibilidade
  const currentRange = value || selectedRange;
  const handleRangeChange = onChange || onRangeChange;

  // Intervalos predefinidos unificados
  const predefinedRanges = [
    {
      startDate: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      endDate: new Date().toISOString().split('T')[0],
      start: new Date(Date.now() - 24 * 60 * 60 * 1000),
      end: new Date(),
      label: 'Hoje'
    },
    {
      startDate: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      endDate: new Date().toISOString().split('T')[0],
      start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
      end: new Date(),
      label: 'Últimos 7 dias'
    },
    {
      startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      endDate: new Date().toISOString().split('T')[0],
      start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
      end: new Date(),
      label: 'Últimos 30 dias'
    },
    {
      startDate: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      endDate: new Date().toISOString().split('T')[0],
      start: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000),
      end: new Date(),
      label: 'Últimos 90 dias'
    }
  ];

  const handlePredefinedRangeSelect = (range: DateRange) => {
    if (handleRangeChange) {
      handleRangeChange(range);
    }
    setIsOpen(false);
  };

  const handleCustomRangeApply = () => {
    if (customStartDate && customEndDate && handleRangeChange) {
      const customRange: DateRange = {
        startDate: customStartDate,
        endDate: customEndDate,
        start: new Date(customStartDate),
        end: new Date(customEndDate),
        label: `${new Date(customStartDate).toLocaleDateString('pt-BR')} - ${new Date(customEndDate).toLocaleDateString('pt-BR')}`
      };
      handleRangeChange(customRange);
      setIsOpen(false);
    }
  };

  const formatDateForDisplay = (range: DateRange) => {
    if (!range) return 'Selecionar período';
    
    if (range.label !== "Personalizado") {
      return range.label;
    }

    const formatDate = (date: Date | string) => {
      const d = typeof date === 'string' ? new Date(date) : date;
      return new Intl.DateTimeFormat('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      }).format(d);
    };

    const startDate = range.start || (range.startDate ? new Date(range.startDate) : null);
    const endDate = range.end || (range.endDate ? new Date(range.endDate) : null);

    if (startDate && endDate) {
      return `${formatDate(startDate)} - ${formatDate(endDate)}`;
    }

    return range.label;
  };

  // Renderização moderna (para ModernDashboard)
  if (variant === 'modern') {
    const filterVariants = {
      hidden: { opacity: 0, y: -10 },
      visible: {
        opacity: 1,
        y: 0,
        transition: {
          duration: 0.3,
          ease: "easeOut"
        }
      }
    };

    return (
      <motion.div
        variants={filterVariants}
        initial="hidden"
        animate="visible"
        className={cn("flex items-center gap-3", className)}
      >
        <Card className="border-0 shadow-sm bg-white/50 backdrop-blur-sm">
          <CardContent className="p-3">
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Calendar className="h-4 w-4" />
                <span className="font-medium">Período:</span>
              </div>
              
              <Select 
                value={currentRange?.label || ''}
                onValueChange={(value) => {
                  const preset = predefinedRanges.find(p => p.label === value);
                  if (preset && handleRangeChange) {
                    handleRangeChange(preset);
                  }
                }}
              >
                <SelectTrigger className="w-48 border-gray-200 bg-white/80 hover:bg-white transition-colors">
                  <SelectValue placeholder={formatDateForDisplay(currentRange || { label: 'Selecionar período' })} />
                </SelectTrigger>
                <SelectContent>
                  {predefinedRanges.map((preset) => (
                    <SelectItem key={preset.label} value={preset.label}>
                      <div className="flex items-center justify-between w-full">
                        <span>{preset.label}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              <Badge 
                variant="outline" 
                className="text-xs bg-blue-50 text-blue-700 border-blue-200"
              >
                {formatDateForDisplay(currentRange || { label: 'Selecionar período' })}
              </Badge>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    );
  }

  // Renderização clássica
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
          {currentRange?.label || 'Selecionar período'}
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
                    currentRange?.label === range.label
                      ? 'bg-blue-600/80 text-white'
                      : 'text-slate-300 hover:bg-slate-700/60 hover:text-slate-200'
                  }`}
                >
                  {range.label}
                  <div className="text-xs text-slate-400 mt-1">
                    {new Date(range.startDate).toLocaleDateString('pt-BR')} - {new Date(range.endDate).toLocaleDateString('pt-BR')}
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

// Corrigir a exportação para named export
export { DateRangeFilter };
export default DateRangeFilter;