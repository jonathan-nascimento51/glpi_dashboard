import React, { useState, useEffect, useMemo } from 'react';
import { MetricsData, TechnicianRanking, NewTicket } from '../types';
import { DateRange } from '../types';
import { apiService } from '../services/api';
import { useThrottledCallback } from '../hooks/useDebounce';
import {
  BarChart3,
  Clock,
  Users,
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  Settings,
} from 'lucide-react';

interface ProfessionalDashboardProps {
  metrics: MetricsData | null;
  technicianRanking: TechnicianRanking[];
  isLoading: boolean;
  dateRange: DateRange;
  onDateRangeChange: (range: DateRange) => void;
  onRefresh: () => void;
}

interface StatusCardProps {
  title: string;
  value: number;
  icon: React.ComponentType<any>;
  color: string;
  bgColor: string;
  trend?: number;
}

const StatusCard = React.memo<StatusCardProps>(
  ({ title, value, icon: Icon, color, bgColor, trend }) => {
    const formattedValue = useMemo(() => value.toLocaleString(), [value]);
    const trendColor = useMemo(
      () => (trend !== undefined ? (trend >= 0 ? 'text-green-500' : 'text-red-500') : ''),
      [trend]
    );
    const trendTextColor = useMemo(
      () => (trend !== undefined ? (trend >= 0 ? 'text-green-600' : 'text-red-600') : ''),
      [trend]
    );

    return (
      <div className='bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-all duration-200'>
        <div className='flex items-center justify-between'>
          <div>
            <p className='text-sm font-medium text-gray-600 mb-1'>{title}</p>
            <p className={`text-3xl font-bold ${color}`}>{formattedValue}</p>
            {trend !== undefined && (
              <div className='flex items-center mt-2'>
                <TrendingUp className={`w-4 h-4 mr-1 ${trendColor}`} />
                <span className={`text-sm font-medium ${trendTextColor}`}>
                  {trend >= 0 ? '+' : ''}
                  {trend}%
                </span>
              </div>
            )}
          </div>
          <div className={`p-3 rounded-lg ${bgColor}`}>
            <Icon className={`w-6 h-6 ${color}`} />
          </div>
        </div>
      </div>
    );
  }
);

interface LevelSectionProps {
  level: string;
  data: {
    novos: number;
    progresso: number;
    pendentes: number;
    resolvidos: number;
  };
}

const LevelSection = React.memo<LevelSectionProps>(({ level, data }) => {
  const total = useMemo(
    () => data.novos + data.progresso + data.pendentes + data.resolvidos,
    [data]
  );
  const resolvedPercentage = useMemo(
    () => (total > 0 ? ((data.resolvidos / total) * 100).toFixed(1) : '0'),
    [total, data.resolvidos]
  );

  return (
    <div className='bg-white rounded-xl shadow-sm border border-gray-200 p-6'>
      <div className='flex items-center justify-between mb-6'>
        <h3 className='text-lg font-semibold text-gray-900'>Nível {level}</h3>
        <div className='flex items-center space-x-2'>
          <span className='text-sm text-gray-500'>Taxa de Resolução:</span>
          <span className='text-sm font-semibold text-green-600'>{resolvedPercentage}%</span>
        </div>
      </div>

      <div className='grid grid-cols-2 lg:grid-cols-4 gap-4'>
        <div className='text-center p-4 bg-blue-50 rounded-lg border border-blue-100'>
          <div className='text-2xl font-bold text-blue-600 mb-1'>{data.novos}</div>
          <div className='text-sm font-medium text-blue-700'>Novos</div>
        </div>
        <div className='text-center p-4 bg-yellow-50 rounded-lg border border-yellow-100'>
          <div className='text-2xl font-bold text-yellow-600 mb-1'>{data.progresso}</div>
          <div className='text-sm font-medium text-yellow-700'>Em Progresso</div>
        </div>
        <div className='text-center p-4 bg-orange-50 rounded-lg border border-orange-100'>
          <div className='text-2xl font-bold text-orange-600 mb-1'>{data.pendentes}</div>
          <div className='text-sm font-medium text-orange-700'>Pendentes</div>
        </div>
        <div className='text-center p-4 bg-green-50 rounded-lg border border-green-100'>
          <div className='text-2xl font-bold text-green-600 mb-1'>{data.resolvidos}</div>
          <div className='text-sm font-medium text-green-700'>Resolvidos</div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className='mt-4'>
        <div className='flex justify-between text-xs text-gray-500 mb-1'>
          <span>Progresso de Resolução</span>
          <span>{resolvedPercentage}%</span>
        </div>
        <div className='w-full bg-gray-200 rounded-full h-2'>
          <div
            className='bg-green-500 h-2 rounded-full transition-all duration-300'
            style={{ width: `${resolvedPercentage}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
});

export const ProfessionalDashboard: React.FC<ProfessionalDashboardProps> = ({
  metrics,
  technicianRanking,
  isLoading,
  dateRange,
  onRefresh,
}) => {
  // Debug logs
  console.log('🔍 ProfessionalDashboard - Props recebidos:', {
    metrics,
    technicianRanking,
    isLoading,
    dateRange,
  });
  const [newTickets, setNewTickets] = useState<NewTicket[]>([]);
  const [ticketsLoading, setTicketsLoading] = useState(false);
  const [currentTime, setCurrentTime] = useState('');

  // Update current time
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setCurrentTime(
        now.toLocaleString('pt-BR', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
        })
      );
    };

    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  // Throttled function to prevent excessive API calls
  const throttledFetchNewTickets = useThrottledCallback(async () => {
    setTicketsLoading(true);
    try {
      const tickets = await apiService.getNewTickets(8);
      setNewTickets(tickets);
      setTicketsLoading(false);
    } catch (error) {
      console.error('Erro ao buscar tickets novos:', error);
      setTicketsLoading(false);
    }
  }, 2000); // 2 second throttle

  // Fetch recent tickets - OTIMIZADO para reduzir recarregamentos
  useEffect(() => {
    throttledFetchNewTickets();

    // CORREÇÃO: Aumentado para 5 minutos e adicionado controle de interação
    const interval = setInterval(() => {
      // Verificar se auto-refresh está habilitado
      const autoRefreshEnabled = localStorage.getItem('autoRefreshEnabled');
      if (autoRefreshEnabled === 'false') {
        console.log('⏸️ Auto-refresh de tickets desabilitado pelo usuário');
        return;
      }

      const lastInteraction = localStorage.getItem('lastUserInteraction');
      const now = Date.now();
      const timeSinceInteraction = lastInteraction ? now - parseInt(lastInteraction) : Infinity;

      // Só atualiza se não houver interação recente (últimos 2 minutos)
      if (timeSinceInteraction > 120000) {
        console.log('🎫 Atualizando tickets novos no Professional Dashboard');
        throttledFetchNewTickets();
      } else {
        console.log('⏸️ Atualização de tickets pausada no Professional Dashboard');
      }
    }, 300000); // 5 minutos

    return () => clearInterval(interval);
  }, []);

  if (isLoading && !metrics) {
    return (
      <div className='min-h-screen bg-gray-50 flex items-center justify-center'>
        <div className='text-center'>
          <div className='animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4'></div>
          <div className='text-gray-600 text-lg font-medium'>Carregando Dashboard...</div>
        </div>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className='min-h-screen bg-gray-50 flex items-center justify-center'>
        <div className='text-center'>
          <AlertTriangle className='w-16 h-16 text-red-500 mx-auto mb-4' />
          <div className='text-gray-900 text-xl font-semibold mb-2'>Erro ao Carregar Dados</div>
          <div className='text-gray-600 mb-4'>Não foi possível conectar ao sistema GLPI</div>
          <button
            onClick={() => onRefresh()}
            className='bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors'
          >
            Tentar Novamente
          </button>
        </div>
      </div>
    );
  }

  const totalActive = useMemo(
    () => metrics.novos + metrics.progresso + metrics.pendentes,
    [metrics.novos, metrics.progresso, metrics.pendentes]
  );
  const totalTickets = useMemo(
    () => totalActive + metrics.resolvidos,
    [totalActive, metrics.resolvidos]
  );
  const resolutionRate = useMemo(
    () => (totalTickets > 0 ? ((metrics.resolvidos / totalTickets) * 100).toFixed(1) : '0'),
    [metrics.resolvidos, totalTickets]
  );

  return (
    <div className='min-h-screen bg-gray-50'>
      {/* Header */}
      <header className='bg-white shadow-sm border-b border-gray-200'>
        <div className='max-w-7xl mx-auto px-6 py-4'>
          <div className='flex items-center justify-between'>
            <div>
              <h1 className='text-2xl font-bold text-gray-900'>Dashboard GLPI</h1>
              <p className='text-sm text-gray-600 mt-1'>Sistema de Monitoramento de Chamados</p>
            </div>
            <div className='flex items-center space-x-6'>
              <div className='text-right'>
                <div className='text-sm font-medium text-gray-900'>{currentTime}</div>
                <div className='text-xs text-gray-500'>Atualização Automática</div>
              </div>
              <button
                onClick={onRefresh}
                disabled={isLoading}
                className='bg-slate-700 text-white px-4 py-2 rounded-lg hover:bg-slate-800 disabled:opacity-50 transition-colors flex items-center space-x-2'
              >
                <Settings className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                <span>Atualizar</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className='max-w-7xl mx-auto px-6 py-8'>
        {/* Summary Cards */}
        <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8'>
          <StatusCard
            title='Chamados Ativos'
            value={totalActive}
            icon={AlertTriangle}
            color='text-slate-700 dark:text-slate-300'
            bgColor='figma-level-badge'
            trend={5}
          />
          <StatusCard
            title='Resolvidos'
            value={metrics.resolvidos}
            icon={CheckCircle}
            color='text-slate-700 dark:text-slate-300'
            bgColor='figma-level-badge'
            trend={12}
          />
          <StatusCard
            title='Taxa de Resolução'
            value={parseFloat(resolutionRate)}
            icon={BarChart3}
            color='text-slate-700 dark:text-slate-300'
            bgColor='figma-level-badge'
          />
          <StatusCard
            title='Técnicos Ativos'
            value={technicianRanking.length}
            icon={Users}
            color='text-slate-700 dark:text-slate-300'
            bgColor='figma-level-badge'
          />
        </div>

        {/* Levels Grid */}
        <div className='grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8'>
          <LevelSection level='N1' data={metrics.niveis.n1} />
          <LevelSection level='N2' data={metrics.niveis.n2} />
          <LevelSection level='N3' data={metrics.niveis.n3} />
          <LevelSection level='N4' data={metrics.niveis.n4} />
        </div>

        {/* Bottom Section */}
        <div className='grid grid-cols-1 lg:grid-cols-3 gap-6'>
          {/* Technician Ranking */}
          <div className='lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200 p-6'>
            <h3 className='text-lg font-semibold text-gray-900 mb-6'>Ranking de Técnicos</h3>
            <div className='space-y-4 max-h-96 overflow-y-auto'>
              {technicianRanking.map((tech, index) => {
                const rankBadgeColor = useMemo(() => {
                  switch (index) {
                    case 0:
                      return 'bg-slate-600';
                    case 1:
                      return 'bg-slate-500';
                    case 2:
                      return 'bg-slate-700';
                    default:
                      return 'bg-slate-800';
                  }
                }, [index]);

                return (
                  <div
                    key={tech.id}
                    className='flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors'
                  >
                    <div className='flex items-center space-x-4'>
                      <div
                        className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold text-white ${rankBadgeColor}`}
                      >
                        {index + 1}
                      </div>
                      <div>
                        <div className='font-medium text-gray-900'>{tech.nome || tech.name}</div>
                        <div className='text-sm text-gray-500'>Técnico de Suporte</div>
                      </div>
                    </div>
                    <div className='text-right'>
                      <div className='text-lg font-semibold text-gray-900'>{tech.total}</div>
                      <div className='text-sm text-gray-500'>chamados</div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Recent Tickets */}
          <div className='bg-white rounded-xl shadow-sm border border-gray-200 p-6'>
            <h3 className='text-lg font-semibold text-gray-900 mb-6'>Chamados Recentes</h3>
            {ticketsLoading ? (
              <div className='text-center py-8'>
                <div className='animate-spin rounded-full h-8 w-8 border-b-2 border-slate-600 mx-auto mb-2'></div>
                <div className='text-sm text-gray-500'>Carregando...</div>
              </div>
            ) : (
              <div className='space-y-3 max-h-96 overflow-y-auto'>
                {newTickets.length > 0 ? (
                  newTickets.map(ticket => {
                    const formattedDate = useMemo(
                      () => new Date(ticket.date).toLocaleDateString('pt-BR'),
                      [ticket.date]
                    );

                    return (
                      <div
                        key={ticket.id}
                        className='p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors'
                      >
                        <div className='flex justify-between items-start mb-2'>
                          <div className='text-sm font-medium text-gray-900 truncate flex-1 mr-2'>
                            #{ticket.id}
                          </div>
                          <span className='inline-flex items-center px-2 py-1 rounded text-xs font-medium figma-badge-subtle'>
                            {ticket.priority}
                          </span>
                        </div>
                        <div className='text-sm text-gray-600 mb-2 line-clamp-2'>
                          {ticket.title}
                        </div>
                        <div className='flex items-center justify-between text-xs text-gray-500'>
                          <span>{ticket.requester}</span>
                          <span>{formattedDate}</span>
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <div className='text-center py-8 text-gray-500'>
                    <Clock className='w-8 h-8 mx-auto mb-2 text-gray-400' />
                    <div className='text-sm'>Nenhum chamado recente</div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className='bg-white border-t border-gray-200 mt-8'>
        <div className='max-w-7xl mx-auto px-6 py-4'>
          <div className='flex items-center justify-between text-sm text-gray-500'>
            <div>© 2024 Departamento de Tecnologia do Estado</div>
            <div className='flex items-center space-x-4'>
              <span>Última atualização: {currentTime}</span>
              <div className='flex items-center space-x-1'>
                <div className='w-2 h-2 bg-slate-500 rounded-full animate-pulse'></div>
                <span>Sistema Online</span>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default ProfessionalDashboard;
