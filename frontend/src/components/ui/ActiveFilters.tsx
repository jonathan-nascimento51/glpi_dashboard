import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Trash2, Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';
import FilterBadge from './FilterBadge';
import { cn } from '@/lib/utils';

interface FilterItem {
  key: string;
  label: string;
  value: string | number;
  displayValue?: string;
}

interface ActiveFiltersProps {
  filters: Record<string, any>;
  onRemoveFilter: (key: string) => void;
  onClearAll: () => void;
  className?: string;
  filterLabels?: Record<string, string>;
}

const ActiveFilters: React.FC<ActiveFiltersProps> = ({
  filters,
  onRemoveFilter,
  onClearAll,
  className,
  filterLabels = {
    startDate: 'Data Início',
    endDate: 'Data Fim',
    filterType: 'Tipo de Filtro',
    status: 'Status',
    level: 'Nível',
    priority: 'Prioridade',
    technician: 'Técnico',
    category: 'Categoria',
    searchQuery: 'Busca'
  }
}) => {
  // Processar filtros ativos
  const activeFilters: FilterItem[] = React.useMemo(() => {
    const items: FilterItem[] = [];
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value && value !== '' && value !== null && value !== undefined) {
        // Tratamento especial para diferentes tipos de filtros
        let displayValue = value;
        let label = filterLabels[key] || key;
        
        // Formatação especial para datas
        if (key === 'startDate' || key === 'endDate') {
          if (typeof value === 'string' && value.includes('-')) {
            displayValue = new Date(value).toLocaleDateString('pt-BR');
          }
        }
        
        // Formatação especial para tipo de filtro
        if (key === 'filterType') {
          const typeLabels: Record<string, string> = {
            creation: 'Criação',
            modification: 'Modificação',
            current_status: 'Status Atual'
          };
          displayValue = typeLabels[value as string] || value;
        }
        
        // Formatação especial para arrays
        if (Array.isArray(value)) {
          displayValue = value.join(', ');
        }
        
        items.push({
          key,
          label,
          value,
          displayValue: displayValue.toString()
        });
      }
    });
    
    return items;
  }, [filters, filterLabels]);

  if (activeFilters.length === 0) {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.3 }}
      className={cn(
        'flex flex-wrap items-center gap-2 p-3 bg-gray-50/50 border border-gray-200 rounded-lg backdrop-blur-sm',
        className
      )}
    >
      <div className="flex items-center gap-2 text-sm text-gray-600 mr-2">
        <Filter className="w-4 h-4" />
        <span className="font-medium">Filtros ativos:</span>
      </div>
      
      <AnimatePresence mode="popLayout">
        {activeFilters.map((filter) => (
          <FilterBadge
            key={filter.key}
            label={filter.label}
            value={filter.displayValue || filter.value}
            onRemove={() => onRemoveFilter(filter.key)}
            variant="info"
          />
        ))}
      </AnimatePresence>
      
      {activeFilters.length > 1 && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
        >
          <Button
            variant="ghost"
            size="sm"
            onClick={onClearAll}
            className="text-red-600 hover:text-red-800 hover:bg-red-50 h-7 px-2 text-xs"
          >
            <Trash2 className="w-3 h-3 mr-1" />
            Limpar todos
          </Button>
        </motion.div>
      )}
    </motion.div>
  );
};

export default ActiveFilters;