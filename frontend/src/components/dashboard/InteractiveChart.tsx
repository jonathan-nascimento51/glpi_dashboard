import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import { TicketChart } from './TicketChart';
import { Badge } from '@/components/ui/badge';
import { MousePointer, BarChart3 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { createDrillDownData } from '@/hooks/useChartNavigation';

interface ChartData {
  name: string;
  novos: number;
  progresso: number;
  pendentes: number;
  resolvidos: number;
}

interface InteractiveChartProps {
  data: ChartData[];
  type?: 'area' | 'bar' | 'pie';
  title?: string;
  className?: string;
  enableDrillDown?: boolean;
  drillDownType?: 'status' | 'category' | 'technician' | 'priority';
  showInteractiveIndicator?: boolean;
}

/**
 * Componente de gráfico interativo com funcionalidades de drill-down
 * Encapsula o TicketChart com indicadores visuais de interatividade
 */
export const InteractiveChart = React.memo<InteractiveChartProps>(function InteractiveChart({
  data,
  type = 'area',
  title = 'Evolução dos Tickets',
  className,
  enableDrillDown = true,
  drillDownType = 'status',
  showInteractiveIndicator = true,
}) {
  // Preparar dados para drill-down
  const drillDownData = useMemo(() => {
    if (!enableDrillDown) return data;
    
    return createDrillDownData(data, {
      type: drillDownType,
      chartType: type,
      enableNavigation: true,
    });
  }, [data, enableDrillDown, drillDownType, type]);

  return (
    <div className={cn('relative group', className)}>
      <TicketChart
        data={drillDownData}
        type={type}
        title={title}
        enableDrillDown={enableDrillDown}
        className={cn(
          'transition-all duration-200',
          enableDrillDown && 'hover:shadow-lg hover:scale-[1.02]'
        )}
      />
      
      {/* Indicador de interatividade */}
      {enableDrillDown && showInteractiveIndicator && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
        >
          <Badge 
            variant="secondary" 
            className="text-xs bg-blue-50 text-blue-700 border-blue-200 shadow-sm"
          >
            <MousePointer className="h-3 w-3 mr-1" />
            Clique para detalhes
          </Badge>
        </motion.div>
      )}
      
      {/* Indicador de tipo de drill-down */}
      {enableDrillDown && (
        <div className="absolute bottom-3 left-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          <Badge 
            variant="outline" 
            className="text-xs bg-white/90 backdrop-blur-sm"
          >
            <BarChart3 className="h-3 w-3 mr-1" />
            {drillDownType === 'status' && 'Por Status'}
            {drillDownType === 'category' && 'Por Categoria'}
            {drillDownType === 'technician' && 'Por Técnico'}
            {drillDownType === 'priority' && 'Por Prioridade'}
          </Badge>
        </div>
      )}
    </div>
  );
});

export default InteractiveChart;