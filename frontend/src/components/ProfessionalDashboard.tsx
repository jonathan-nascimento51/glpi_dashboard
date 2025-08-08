import React, { useState, useEffect, useTransition } from 'react';
import { TechnicianRanking, NewTicket } from '../types';
import { MaintenanceMetrics } from '../hooks/useMaintenanceDashboard';
import { DateRange } from '../types';
import { apiService } from '../services/api';
import CategoryRankingTable from './dashboard/CategoryRankingTable';
import { 
  Wrench, 
  Clock, 
  Users, 
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  Settings,
  Calendar,
  HardHat,
  Cog,
  Shield,
  Building,
  Hammer,
  Zap
} from 'lucide-react';

interface ProfessionalDashboardProps {
  metrics: MaintenanceMetrics | null;
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

const StatusCard: React.FC<StatusCardProps> = ({ title, value, icon: Icon, color, bgColor, trend }) => (
  <div className={`rounded-xl shadow-lg border-2 p-6 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 ${bgColor}`}>
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wide">{title}</p>
        <p className={`text-4xl font-bold ${color} mb-1`}>{value.toLocaleString()}</p>
        {trend !== undefined && (
          <div className="flex items-center mt-2">
            <TrendingUp className={`w-4 h-4 mr-1 ${trend >= 0 ? 'text-green-600' : 'text-red-600'}`} />
            <span className={`text-sm font-bold ${trend >= 0 ? 'text-green-700' : 'text-red-700'}`}>
              {trend >= 0 ? '+' : ''}{trend}% este mês
            </span>
          </div>
        )}
      </div>
      <div className={`p-4 rounded-xl shadow-md ${color.replace('text-', 'bg-').replace('-700', '-100')} border-2 ${color.replace('text-', 'border-').replace('-700', '-300')}`}>
        <Icon className={`w-8 h-8 ${color}`} />
      </div>
    </div>
  </div>
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

const LevelSection: React.FC<LevelSectionProps> = ({ level, data }) => {
  const total = data.novos + data.progresso + data.pendentes + data.resolvidos;
  const resolvedPercentage = total > 0 ? ((data.resolvidos / total) * 100).toFixed(1) : '0';
  
  const getLevelIcon = (level: string) => {
    switch(level) {
      case 'N1': return { icon: Hammer, color: 'text-blue-600', bg: 'bg-blue-100' };
      case 'N2': return { icon: Cog, color: 'text-green-600', bg: 'bg-green-100' };
      case 'N3': return { icon: Shield, color: 'text-purple-600', bg: 'bg-purple-100' };
      case 'N4': return { icon: Zap, color: 'text-red-600', bg: 'bg-red-100' };
      default: return { icon: Settings, color: 'text-gray-600', bg: 'bg-gray-100' };
    }
  };
  
  const levelConfig = getLevelIcon(level);
  const LevelIcon = levelConfig.icon;
  
  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg border-2 border-gray-200 p-6 hover:shadow-xl transition-all duration-300">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-lg ${levelConfig.bg}`}>
            <LevelIcon className={`w-6 h-6 ${levelConfig.color}`} />
          </div>
          <h3 className="text-xl font-bold text-gray-900">Nível {level}</h3>
        </div>
        <div className="flex items-center space-x-2 bg-green-50 px-3 py-1 rounded-full">
          <span className="text-sm font-medium text-gray-700">Eficiência:</span>
          <span className="text-sm font-bold text-green-700">{resolvedPercentage}%</span>
        </div>
      </div>
      
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="text-center p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg border-2 border-blue-200 hover:shadow-md transition-all">
          <div className="text-3xl font-bold text-blue-700 mb-1">{data.novos}</div>
          <div className="text-sm font-semibold text-blue-800 uppercase tracking-wide">Novos</div>
        </div>
        <div className="text-center p-4 bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-lg border-2 border-yellow-200 hover:shadow-md transition-all">
          <div className="text-3xl font-bold text-yellow-700 mb-1">{data.progresso}</div>
          <div className="text-sm font-semibold text-yellow-800 uppercase tracking-wide">Em Execução</div>
        </div>
        <div className="text-center p-4 bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg border-2 border-orange-200 hover:shadow-md transition-all">
          <div className="text-3xl font-bold text-orange-700 mb-1">{data.pendentes}</div>
          <div className="text-sm font-semibold text-orange-800 uppercase tracking-wide">Aguardando</div>
        </div>
        <div className="text-center p-4 bg-gradient-to-br from-green-50 to-green-100 rounded-lg border-2 border-green-200 hover:shadow-md transition-all">
          <div className="text-3xl font-bold text-green-700 mb-1">{data.resolvidos}</div>
          <div className="text-sm font-semibold text-green-800 uppercase tracking-wide">Concluídos</div>
        </div>
      </div>
      
      {/* Progress Bar */}
      <div className="mt-6">
        <div className="flex justify-between text-sm font-medium text-gray-700 mb-2">
          <span>Progresso de Conclusão</span>
          <span className="font-bold">{resolvedPercentage}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3 shadow-inner">
          <div 
            className="bg-gradient-to-r from-green-500 to-green-600 h-3 rounded-full transition-all duration-500 shadow-sm" 
            style={{ width: `${resolvedPercentage}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
};

export const ProfessionalDashboard: React.FC<ProfessionalDashboardProps> = ({
  metrics,
  technicianRanking,
  isLoading,
  dateRange,
  onDateRangeChange: _,
  onRefresh
}) => {
  // Debug logs
  console.log('🔍 ProfessionalDashboard - Props recebidos:', {
    metrics,
    technicianRanking,
    isLoading,
    dateRange
  });
  const [newTickets, setNewTickets] = useState<NewTicket[]>([]);
  const [ticketsLoading, setTicketsLoading] = useState(false);
  const [, startTransition] = useTransition();
  const [currentTime, setCurrentTime] = useState('');

  // Update current time
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setCurrentTime(now.toLocaleString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      }));
    };

    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  // Fetch recent tickets - OTIMIZADO para reduzir recarregamentos
  useEffect(() => {
    const fetchNewTickets = async () => {
      setTicketsLoading(true);
      try {
        startTransition(() => {
          apiService.getNewTickets(8).then(tickets => {
            setNewTickets(tickets);
            setTicketsLoading(false);
          }).catch(error => {
            console.error('Erro ao buscar tickets:', error);
            setTicketsLoading(false);
          });
        });
      } catch (error) {
        console.error('Erro ao buscar tickets novos:', error);
        setTicketsLoading(false);
      }
    };

    fetchNewTickets();
    
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
        fetchNewTickets();
      } else {
        console.log('⏸️ Atualização de tickets pausada no Professional Dashboard');
      }
    }, 300000); // 5 minutos
    
    return () => clearInterval(interval);
  }, []);

  if (isLoading && !metrics) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <div className="text-gray-600 text-lg font-medium">Carregando Dashboard...</div>
        </div>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <div className="text-gray-900 text-xl font-semibold mb-2">Erro ao Carregar Dados</div>
          <div className="text-gray-600 mb-4">Não foi possível conectar ao sistema GLPI</div>
          <button 
            onClick={onRefresh}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Tentar Novamente
          </button>
        </div>
      </div>
    );
  }

  const totalActive = metrics.novos + metrics.progresso + metrics.pendentes;
  const totalTickets = totalActive + metrics.resolvidos;
  const resolutionRate = totalTickets > 0 ? ((metrics.resolvidos / totalTickets) * 100).toFixed(1) : '0';

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-green-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-slate-800 via-slate-700 to-slate-800 shadow-lg border-b-4 border-orange-500">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="bg-orange-500 p-3 rounded-xl shadow-lg">
                <HardHat className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-white flex items-center gap-2">
                  Dashboard de Conservação & Manutenção
                  <Wrench className="w-6 h-6 text-orange-400" />
                </h1>
                <p className="text-slate-300 mt-1 flex items-center gap-2">
                  <Building className="w-4 h-4" />
                  Sistema Integrado de Gestão Patrimonial - GLPI
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-6">
              <div className="text-right bg-slate-700/50 px-4 py-2 rounded-lg backdrop-blur-sm">
                <div className="text-sm font-medium text-white flex items-center gap-2">
                  <Clock className="w-4 h-4 text-orange-400" />
                  {currentTime}
                </div>
                <div className="text-xs text-slate-300">Monitoramento em Tempo Real</div>
              </div>
              <button
                onClick={onRefresh}
                disabled={isLoading}
                className="bg-orange-600 hover:bg-orange-700 text-white px-6 py-3 rounded-lg disabled:opacity-50 transition-all duration-200 flex items-center space-x-2 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
              >
                <Settings className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
                <span className="font-medium">Atualizar Sistema</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatusCard
            title="Serviços em Andamento"
            value={totalActive}
            icon={Wrench}
            color="text-orange-700"
            bgColor="bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200"
            trend={5}
          />
          <StatusCard
            title="Serviços Concluídos"
            value={metrics.resolvidos}
            icon={CheckCircle}
            color="text-green-700"
            bgColor="bg-gradient-to-br from-green-50 to-green-100 border-green-200"
            trend={12}
          />
          <StatusCard
            title="Eficiência Operacional"
            value={parseFloat(resolutionRate)}
            icon={Zap}
            color="text-blue-700"
            bgColor="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200"
          />
          <StatusCard
            title="Equipe Técnica"
            value={technicianRanking.length}
            icon={HardHat}
            color="text-slate-700"
            bgColor="bg-gradient-to-br from-slate-50 to-slate-100 border-slate-200"
          />
        </div>

        {/* Levels Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <LevelSection level="N1" data={metrics.niveis.n1} />
          <LevelSection level="N2" data={metrics.niveis.n2} />
          <LevelSection level="N3" data={metrics.niveis.n3} />
          <LevelSection level="N4" data={metrics.niveis.n4} />
        </div>

        {/* Bottom Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Top Categories */}
          <div className="lg:col-span-2">
            <CategoryRankingTable 
              title="Ranking Completo de Categorias de Serviços"
              dateRange={dateRange ? { start: dateRange.startDate || '', end: dateRange.endDate || '' } : undefined}
              limit={100}
              autoRefresh={true}
            />
          </div>

          {/* Recent Tickets */}
          <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg border-2 border-gray-200 p-6 hover:shadow-xl transition-all duration-300">
            <div className="flex items-center gap-3 mb-6">
              <div className="bg-slate-100 p-2 rounded-lg">
                <Clock className="w-6 h-6 text-slate-700" />
              </div>
              <h3 className="text-xl font-bold text-gray-900">Solicitações Recentes</h3>
            </div>
            {ticketsLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600 mx-auto mb-2"></div>
                <div className="text-sm text-gray-600 font-medium">Carregando solicitações...</div>
              </div>
            ) : (
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {newTickets.length > 0 ? (
                  newTickets.map((ticket) => (
                    <div key={ticket.id} className="p-4 bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg border-l-4 border-orange-500 hover:shadow-md transition-all duration-200 hover:from-orange-50 hover:to-orange-100">
                      <div className="flex justify-between items-start mb-2">
                        <div className="text-sm font-bold text-gray-900 truncate flex-1 mr-2 flex items-center gap-2">
                          <Wrench className="w-4 h-4 text-orange-600" />
                          #{ticket.id}
                        </div>
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-orange-100 text-orange-800 border border-orange-200">
                          {ticket.priority}
                        </span>
                      </div>
                      <div className="text-sm text-gray-700 mb-3 line-clamp-2 font-medium">
                        {ticket.title}
                      </div>
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-gray-600 font-medium flex items-center gap-1">
                          <Users className="w-3 h-3" />
                          {ticket.requester}
                        </span>
                        <span className="text-gray-500 font-medium flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {new Date(ticket.date).toLocaleDateString('pt-BR')}
                        </span>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <div className="bg-gray-100 p-4 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                      <Clock className="w-8 h-8 text-gray-400" />
                    </div>
                    <div className="text-sm font-medium">Nenhuma solicitação recente</div>
                    <div className="text-xs text-gray-400 mt-1">Aguardando novas demandas</div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-8">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <div>© 2024 Departamento de Tecnologia do Estado</div>
            <div className="flex items-center space-x-4">
              <span>Última atualização: {currentTime}</span>
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-slate-500 rounded-full animate-pulse"></div>
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