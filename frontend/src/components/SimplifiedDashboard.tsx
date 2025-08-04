import React, { useEffect, useState } from 'react';
import { MetricsData, TechnicianRanking, NewTicket } from '../types';
import { apiService } from '../services/api';

interface SimplifiedDashboardProps {
  metrics: MetricsData | null;
  technicianRanking: TechnicianRanking[];
  isLoading: boolean;
}

const SimplifiedDashboard: React.FC<SimplifiedDashboardProps> = ({
  metrics,
  technicianRanking,
  isLoading
}) => {
  const [newTickets, setNewTickets] = useState<NewTicket[]>([]);
  const [ticketsLoading, setTicketsLoading] = useState(false);

  // Buscar tickets novos
  useEffect(() => {
    const fetchNewTickets = async () => {
      setTicketsLoading(true);
      try {
        const tickets = await apiService.getNewTickets(5);
        setNewTickets(tickets);
      } catch (error) {
        console.error('Erro ao buscar tickets novos:', error);
      } finally {
        setTicketsLoading(false);
      }
    };

    fetchNewTickets();
    // Atualizar a cada 30 segundos
    const interval = setInterval(fetchNewTickets, 30000);
    return () => clearInterval(interval);
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center">
        <div className="text-slate-700 text-2xl font-medium">Carregando dados...</div>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center">
        <div className="text-slate-700 text-2xl font-medium">Erro ao carregar dados</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-purple-900 p-6">
      {/* Header */}
      <div className="text-center mb-6">
        <h1 className="text-3xl font-semibold mb-2 text-white tracking-wide">
          Sistema de Monitoramento GLPI
        </h1>
        <p className="text-sm text-slate-300 font-medium uppercase tracking-wider">
          Departamento de Tecnologia do Estado
        </p>
      </div>

      {/* Main Grid Layout - Reorganized for better TV display */}
      <div className="grid grid-cols-12 gap-6 max-w-[1920px] mx-auto">
        
        {/* Top Row - N1 and N2 Levels (Full Width) */}
        <div className="col-span-6">
          <div className="bg-slate-800/80 backdrop-blur-sm rounded-lg shadow-lg border border-slate-700/60 p-4 h-full">
            <h2 className="text-lg font-medium mb-4 text-center text-slate-200 border-b border-slate-600/40 pb-2">Nível N1</h2>
            <div className="grid grid-cols-4 gap-3">
              <div className="bg-slate-700/40 border border-slate-600/50 rounded-lg p-4 text-center hover:bg-slate-700/60 transition-all duration-200">
                <div className="text-2xl font-semibold text-emerald-400 mb-1">{metrics.niveis.n1.novos}</div>
                <div className="text-xs text-slate-300 font-medium uppercase tracking-wide">Novos</div>
              </div>
              <div className="bg-slate-700/40 border border-slate-600/50 rounded-lg p-4 text-center hover:bg-slate-700/60 transition-all duration-200">
                <div className="text-2xl font-semibold text-blue-400 mb-1">{metrics.niveis.n1.progresso}</div>
                <div className="text-xs text-slate-300 font-medium uppercase tracking-wide">Em Progresso</div>
              </div>
              <div className="bg-slate-700/40 border border-slate-600/50 rounded-lg p-4 text-center hover:bg-slate-700/60 transition-all duration-200">
                <div className="text-2xl font-semibold text-amber-400 mb-1">{metrics.niveis.n1.pendentes}</div>
                <div className="text-xs text-slate-300 font-medium uppercase tracking-wide">Pendentes</div>
              </div>
              <div className="bg-slate-700/40 border border-slate-600/50 rounded-lg p-4 text-center hover:bg-slate-700/60 transition-all duration-200">
                <div className="text-2xl font-semibold text-purple-400 mb-1">{metrics.niveis.n1.resolvidos}</div>
                <div className="text-xs text-slate-300 font-medium uppercase tracking-wide">Resolvidos</div>
              </div>
            </div>
          </div>
        </div>

        <div className="col-span-6">
          <div className="bg-slate-800/80 backdrop-blur-sm rounded-lg shadow-lg border border-slate-700/60 p-4 h-full">
            <h2 className="text-lg font-medium mb-4 text-center text-slate-200 border-b border-slate-600/40 pb-2">Nível N2</h2>
            <div className="grid grid-cols-4 gap-3">
              <div className="bg-slate-700/40 border border-slate-600/50 rounded-lg p-4 text-center hover:bg-slate-700/60 transition-all duration-200">
                <div className="text-2xl font-semibold text-emerald-400 mb-1">{metrics.niveis.n2.novos}</div>
                <div className="text-xs text-slate-300 font-medium uppercase tracking-wide">Novos</div>
              </div>
              <div className="bg-slate-700/40 border border-slate-600/50 rounded-lg p-4 text-center hover:bg-slate-700/60 transition-all duration-200">
                <div className="text-2xl font-semibold text-blue-400 mb-1">{metrics.niveis.n2.progresso}</div>
                <div className="text-xs text-slate-300 font-medium uppercase tracking-wide">Em Progresso</div>
              </div>
              <div className="bg-slate-700/40 border border-slate-600/50 rounded-lg p-4 text-center hover:bg-slate-700/60 transition-all duration-200">
                <div className="text-2xl font-semibold text-amber-400 mb-1">{metrics.niveis.n2.pendentes}</div>
                <div className="text-xs text-slate-300 font-medium uppercase tracking-wide">Pendentes</div>
              </div>
              <div className="bg-slate-700/40 border border-slate-600/50 rounded-lg p-4 text-center hover:bg-slate-700/60 transition-all duration-200">
                <div className="text-2xl font-semibold text-purple-400 mb-1">{metrics.niveis.n2.resolvidos}</div>
                <div className="text-xs text-slate-300 font-medium uppercase tracking-wide">Resolvidos</div>
              </div>
            </div>
          </div>
        </div>

        {/* Second Row - N3 and N4 Levels */}
        <div className="col-span-6">
          <div className="bg-slate-800/80 backdrop-blur-sm rounded-lg shadow-lg border border-slate-700/60 p-4 h-full">
            <h2 className="text-lg font-medium mb-4 text-center text-slate-200 border-b border-slate-600/40 pb-2">Nível N3</h2>
            <div className="grid grid-cols-4 gap-3">
              <div className="bg-slate-700/40 border border-slate-600/50 rounded-lg p-4 text-center hover:bg-slate-700/60 transition-all duration-200">
                <div className="text-2xl font-semibold text-emerald-400 mb-1">{metrics.niveis.n3.novos}</div>
                <div className="text-xs text-slate-300 font-medium uppercase tracking-wide">Novos</div>
              </div>
              <div className="bg-slate-700/40 border border-slate-600/50 rounded-lg p-4 text-center hover:bg-slate-700/60 transition-all duration-200">
                <div className="text-2xl font-semibold text-blue-400 mb-1">{metrics.niveis.n3.progresso}</div>
                <div className="text-xs text-slate-300 font-medium uppercase tracking-wide">Em Progresso</div>
              </div>
              <div className="bg-slate-700/40 border border-slate-600/50 rounded-lg p-4 text-center hover:bg-slate-700/60 transition-all duration-200">
                <div className="text-2xl font-semibold text-amber-400 mb-1">{metrics.niveis.n3.pendentes}</div>
                <div className="text-xs text-slate-300 font-medium uppercase tracking-wide">Pendentes</div>
              </div>
              <div className="bg-slate-700/40 border border-slate-600/50 rounded-lg p-4 text-center hover:bg-slate-700/60 transition-all duration-200">
                <div className="text-2xl font-semibold text-purple-400 mb-1">{metrics.niveis.n3.resolvidos}</div>
                <div className="text-xs text-slate-300 font-medium uppercase tracking-wide">Resolvidos</div>
              </div>
            </div>
          </div>
        </div>

        <div className="col-span-6">
          <div className="bg-slate-800/80 backdrop-blur-sm rounded-lg shadow-lg border border-slate-700/60 p-4 h-full">
            <h2 className="text-lg font-medium mb-4 text-center text-slate-200 border-b border-slate-600/40 pb-2">Nível N4</h2>
            <div className="grid grid-cols-4 gap-3">
              <div className="bg-slate-700/40 border border-slate-600/50 rounded-lg p-4 text-center hover:bg-slate-700/60 transition-all duration-200">
                <div className="text-2xl font-semibold text-emerald-400 mb-1">{metrics.niveis.n4.novos}</div>
                <div className="text-xs text-slate-300 font-medium uppercase tracking-wide">Novos</div>
              </div>
              <div className="bg-slate-700/40 border border-slate-600/50 rounded-lg p-4 text-center hover:bg-slate-700/60 transition-all duration-200">
                <div className="text-2xl font-semibold text-blue-400 mb-1">{metrics.niveis.n4.progresso}</div>
                <div className="text-xs text-slate-300 font-medium uppercase tracking-wide">Em Progresso</div>
              </div>
              <div className="bg-slate-700/40 border border-slate-600/50 rounded-lg p-4 text-center hover:bg-slate-700/60 transition-all duration-200">
                <div className="text-2xl font-semibold text-amber-400 mb-1">{metrics.niveis.n4.pendentes}</div>
                <div className="text-xs text-slate-300 font-medium uppercase tracking-wide">Pendentes</div>
              </div>
              <div className="bg-slate-700/40 border border-slate-600/50 rounded-lg p-4 text-center hover:bg-slate-700/60 transition-all duration-200">
                <div className="text-2xl font-semibold text-purple-400 mb-1">{metrics.niveis.n4.resolvidos}</div>
                <div className="text-xs text-slate-300 font-medium uppercase tracking-wide">Resolvidos</div>
              </div>
            </div>
          </div>
        </div>

        {/* Third Row - Top Técnicos, Resumo Geral and Tickets Recentes */}
        <div className="col-span-4">
          <div className="bg-slate-800/80 backdrop-blur-sm rounded-lg shadow-lg border border-slate-700/60 p-4 h-full">
            <h2 className="text-lg font-medium mb-4 text-center text-slate-200 border-b border-slate-600/40 pb-2">Top Técnicos</h2>
            <div className="space-y-3 max-h-80 overflow-y-auto">
              {technicianRanking.map((tech, index) => (
                <div key={tech.id} className="flex items-center justify-between bg-slate-700/40 rounded-lg p-3 border border-slate-600/50 hover:bg-slate-700/60 transition-all duration-200">
                  <div className="flex items-center space-x-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                      index === 0 ? 'bg-yellow-500/80 text-yellow-100' :
                      index === 1 ? 'bg-gray-500/80 text-gray-100' :
                      index === 2 ? 'bg-orange-500/80 text-orange-100' :
                      'bg-blue-500/80 text-blue-100'
                    }`}>
                      {tech.rank || index + 1}
                    </div>
                    <div>
                      <div className="text-sm font-medium text-slate-300">{tech.nome || tech.name}</div>
                      <div className="text-xs text-slate-400">Técnico</div>
                    </div>
                  </div>
                  <div className="text-lg font-semibold text-slate-200">{tech.total}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="col-span-4">
          <div className="bg-slate-800/80 backdrop-blur-sm rounded-lg shadow-lg border border-slate-700/60 p-4 h-full">
            <h2 className="text-lg font-medium mb-4 text-center text-slate-200 border-b border-slate-600/40 pb-2">Resumo Geral</h2>
            <div className="space-y-2">
               <div className="flex justify-between items-center p-3 bg-slate-700/40 rounded-lg border border-slate-600/50">
                 <span className="text-sm font-medium text-slate-300">Total Geral:</span>
                 <span className="text-xl font-bold text-slate-200">{metrics.total}</span>
               </div>
               <div className="flex justify-between items-center p-3 bg-slate-700/40 rounded-lg border border-slate-600/50">
                 <span className="text-sm font-medium text-slate-300">Ativos:</span>
                 <span className="text-xl font-bold text-amber-400">{metrics.novos + metrics.progresso + metrics.pendentes}</span>
               </div>
               <div className="flex justify-between items-center p-3 bg-slate-700/40 rounded-lg border border-slate-600/50">
                 <span className="text-sm font-medium text-slate-300">Resolvidos:</span>
                 <span className="text-xl font-bold text-emerald-400">{metrics.resolvidos}</span>
               </div>
               <div className="flex justify-between items-center p-3 bg-slate-700/40 rounded-lg border border-slate-600/50">
                 <span className="text-sm font-medium text-slate-300">Tempo Médio:</span>
                 <span className="text-sm font-semibold text-blue-400">2.5h</span>
               </div>
               <div className="flex justify-between items-center p-3 bg-slate-700/40 rounded-lg border border-slate-600/50">
                 <span className="text-sm font-medium text-slate-300">SLA Cumprido:</span>
                 <span className="text-sm font-semibold text-green-400">94%</span>
               </div>
             </div>
          </div>
        </div>

        <div className="col-span-4">
          <div className="bg-slate-800/80 backdrop-blur-sm rounded-lg shadow-lg border border-slate-700/60 p-4 h-full">
            <h2 className="text-lg font-medium mb-4 text-center text-slate-200 border-b border-slate-600/40 pb-2">Tickets Recentes</h2>
            {ticketsLoading ? (
              <div className="text-center py-8">
                <div className="text-slate-300 font-medium">Carregando...</div>
              </div>
            ) : (
              <div className="space-y-3 max-h-80 overflow-y-auto">
                {newTickets.length > 0 ? (
                  newTickets.map((ticket) => (
                    <div key={ticket.id} className="bg-slate-700/40 rounded-lg p-3 border border-slate-600/50 hover:bg-slate-700/60 transition-all duration-200">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="text-xs font-medium text-slate-300 truncate">
                            #{ticket.id} - {ticket.title}
                          </div>
                          <div className="text-xs text-slate-400 mt-1">
                            {ticket.requester} • {new Date(ticket.date).toLocaleString('pt-BR')}
                          </div>
                        </div>
                        <div className="ml-2">
                          <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-slate-600/60 text-slate-200">
                            {ticket.priority}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-slate-300 font-medium">
                    Nenhum ticket novo
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="mt-6 text-center">
        <p className="text-sm text-slate-400 font-medium">
          Atualização automática a cada 30 segundos
        </p>
      </div>
    </div>
  );
};

export default SimplifiedDashboard;