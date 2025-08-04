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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800 text-white p-8">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-6xl font-bold mb-3 bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent drop-shadow-lg">Sistema de Monitoramento GLPI</h1>
        <p className="text-2xl text-blue-200 font-medium tracking-wide">Departamento de Tecnologia do Estado</p>
        <div className="w-40 h-1 bg-gradient-to-r from-blue-400 to-cyan-300 mx-auto mt-6 rounded-full shadow-lg"></div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-12 gap-6 h-full">
        {/* Left Column - N1 and N2 Levels */}
        <div className="col-span-6 space-y-8">
          {/* N1 Level */}
          <div className="bg-gradient-to-br from-slate-800/90 to-slate-700/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-slate-600/50 p-8">
            <h2 className="text-3xl font-bold mb-8 text-center text-white border-b border-blue-400/30 pb-4">Nível N1</h2>
            <div className="grid grid-cols-4 gap-6">
              <div className="bg-gradient-to-br from-emerald-500/20 to-emerald-600/30 border border-emerald-400/40 rounded-xl p-6 text-center hover:from-emerald-500/30 hover:to-emerald-600/40 transition-all duration-300 transform hover:scale-105 shadow-lg">
                <div className="text-4xl font-bold text-emerald-300 mb-2">{metrics.niveis.n1.novos}</div>
                <div className="text-sm text-emerald-200 font-semibold tracking-wide">Novos</div>
              </div>
              <div className="bg-gradient-to-br from-blue-500/20 to-blue-600/30 border border-blue-400/40 rounded-xl p-6 text-center hover:from-blue-500/30 hover:to-blue-600/40 transition-all duration-300 transform hover:scale-105 shadow-lg">
                <div className="text-4xl font-bold text-blue-300 mb-2">{metrics.niveis.n1.progresso}</div>
                <div className="text-sm text-blue-200 font-semibold tracking-wide">Em Progresso</div>
              </div>
              <div className="bg-gradient-to-br from-amber-500/20 to-amber-600/30 border border-amber-400/40 rounded-xl p-6 text-center hover:from-amber-500/30 hover:to-amber-600/40 transition-all duration-300 transform hover:scale-105 shadow-lg">
                <div className="text-4xl font-bold text-amber-300 mb-2">{metrics.niveis.n1.pendentes}</div>
                <div className="text-sm text-amber-200 font-semibold tracking-wide">Pendentes</div>
              </div>
              <div className="bg-gradient-to-br from-purple-500/20 to-purple-600/30 border border-purple-400/40 rounded-xl p-6 text-center hover:from-purple-500/30 hover:to-purple-600/40 transition-all duration-300 transform hover:scale-105 shadow-lg">
                <div className="text-4xl font-bold text-purple-300 mb-2">{metrics.niveis.n1.resolvidos}</div>
                <div className="text-sm text-purple-200 font-semibold tracking-wide">Resolvidos</div>
              </div>
            </div>
          </div>

          {/* N2 Level */}
          <div className="bg-gradient-to-br from-slate-800/90 to-slate-700/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-slate-600/50 p-8">
            <h2 className="text-3xl font-bold mb-8 text-center text-white border-b border-blue-400/30 pb-4">Nível N2</h2>
            <div className="grid grid-cols-4 gap-6">
              <div className="bg-gradient-to-br from-emerald-500/20 to-emerald-600/30 border border-emerald-400/40 rounded-xl p-6 text-center hover:from-emerald-500/30 hover:to-emerald-600/40 transition-all duration-300 transform hover:scale-105 shadow-lg">
                <div className="text-4xl font-bold text-emerald-300 mb-2">{metrics.niveis.n2.novos}</div>
                <div className="text-sm text-emerald-200 font-semibold tracking-wide">Novos</div>
              </div>
              <div className="bg-gradient-to-br from-blue-500/20 to-blue-600/30 border border-blue-400/40 rounded-xl p-6 text-center hover:from-blue-500/30 hover:to-blue-600/40 transition-all duration-300 transform hover:scale-105 shadow-lg">
                <div className="text-4xl font-bold text-blue-300 mb-2">{metrics.niveis.n2.progresso}</div>
                <div className="text-sm text-blue-200 font-semibold tracking-wide">Em Progresso</div>
              </div>
              <div className="bg-gradient-to-br from-amber-500/20 to-amber-600/30 border border-amber-400/40 rounded-xl p-6 text-center hover:from-amber-500/30 hover:to-amber-600/40 transition-all duration-300 transform hover:scale-105 shadow-lg">
                <div className="text-4xl font-bold text-amber-300 mb-2">{metrics.niveis.n2.pendentes}</div>
                <div className="text-sm text-amber-200 font-semibold tracking-wide">Pendentes</div>
              </div>
              <div className="bg-gradient-to-br from-purple-500/20 to-purple-600/30 border border-purple-400/40 rounded-xl p-6 text-center hover:from-purple-500/30 hover:to-purple-600/40 transition-all duration-300 transform hover:scale-105 shadow-lg">
                <div className="text-4xl font-bold text-purple-300 mb-2">{metrics.niveis.n2.resolvidos}</div>
                <div className="text-sm text-purple-200 font-semibold tracking-wide">Resolvidos</div>
              </div>
            </div>
          </div>
        </div>

        {/* Middle Column - N3 and N4 Levels */}
        <div className="col-span-3 space-y-8">
          {/* N3 Level */}
          <div className="bg-gradient-to-br from-slate-800/90 to-slate-700/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-slate-600/50 p-6">
            <h2 className="text-2xl font-bold mb-6 text-center text-white border-b border-blue-400/30 pb-3">Nível N3</h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gradient-to-br from-emerald-500/20 to-emerald-600/30 border border-emerald-400/40 rounded-xl p-4 text-center hover:from-emerald-500/30 hover:to-emerald-600/40 transition-all duration-300 transform hover:scale-105 shadow-lg">
                <div className="text-3xl font-bold text-emerald-300 mb-1">{metrics.niveis.n3.novos}</div>
                <div className="text-xs text-emerald-200 font-semibold tracking-wide">Novos</div>
              </div>
              <div className="bg-gradient-to-br from-blue-500/20 to-blue-600/30 border border-blue-400/40 rounded-xl p-4 text-center hover:from-blue-500/30 hover:to-blue-600/40 transition-all duration-300 transform hover:scale-105 shadow-lg">
                <div className="text-3xl font-bold text-blue-300 mb-1">{metrics.niveis.n3.progresso}</div>
                <div className="text-xs text-blue-200 font-semibold tracking-wide">Em Progresso</div>
              </div>
              <div className="bg-gradient-to-br from-amber-500/20 to-amber-600/30 border border-amber-400/40 rounded-xl p-4 text-center hover:from-amber-500/30 hover:to-amber-600/40 transition-all duration-300 transform hover:scale-105 shadow-lg">
                <div className="text-3xl font-bold text-amber-300 mb-1">{metrics.niveis.n3.pendentes}</div>
                <div className="text-xs text-amber-200 font-semibold tracking-wide">Pendentes</div>
              </div>
              <div className="bg-gradient-to-br from-purple-500/20 to-purple-600/30 border border-purple-400/40 rounded-xl p-4 text-center hover:from-purple-500/30 hover:to-purple-600/40 transition-all duration-300 transform hover:scale-105 shadow-lg">
                <div className="text-3xl font-bold text-purple-300 mb-1">{metrics.niveis.n3.resolvidos}</div>
                <div className="text-xs text-purple-200 font-semibold tracking-wide">Resolvidos</div>
              </div>
            </div>
          </div>

          {/* N4 Level */}
          <div className="bg-gradient-to-br from-slate-800/90 to-slate-700/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-slate-600/50 p-6">
            <h2 className="text-2xl font-bold mb-6 text-center text-white border-b border-blue-400/30 pb-3">Nível N4</h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gradient-to-br from-emerald-500/20 to-emerald-600/30 border border-emerald-400/40 rounded-xl p-4 text-center hover:from-emerald-500/30 hover:to-emerald-600/40 transition-all duration-300 transform hover:scale-105 shadow-lg">
                <div className="text-3xl font-bold text-emerald-300 mb-1">{metrics.niveis.n4.novos}</div>
                <div className="text-xs text-emerald-200 font-semibold tracking-wide">Novos</div>
              </div>
              <div className="bg-gradient-to-br from-blue-500/20 to-blue-600/30 border border-blue-400/40 rounded-xl p-4 text-center hover:from-blue-500/30 hover:to-blue-600/40 transition-all duration-300 transform hover:scale-105 shadow-lg">
                <div className="text-3xl font-bold text-blue-300 mb-1">{metrics.niveis.n4.progresso}</div>
                <div className="text-xs text-blue-200 font-semibold tracking-wide">Em Progresso</div>
              </div>
              <div className="bg-gradient-to-br from-amber-500/20 to-amber-600/30 border border-amber-400/40 rounded-xl p-4 text-center hover:from-amber-500/30 hover:to-amber-600/40 transition-all duration-300 transform hover:scale-105 shadow-lg">
                <div className="text-3xl font-bold text-amber-300 mb-1">{metrics.niveis.n4.pendentes}</div>
                <div className="text-xs text-amber-200 font-semibold tracking-wide">Pendentes</div>
              </div>
              <div className="bg-gradient-to-br from-purple-500/20 to-purple-600/30 border border-purple-400/40 rounded-xl p-4 text-center hover:from-purple-500/30 hover:to-purple-600/40 transition-all duration-300 transform hover:scale-105 shadow-lg">
                <div className="text-3xl font-bold text-purple-300 mb-1">{metrics.niveis.n4.resolvidos}</div>
                <div className="text-xs text-purple-200 font-semibold tracking-wide">Resolvidos</div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Ranking, Summary and New Tickets */}
        <div className="col-span-3 space-y-8">
          {/* Top Técnicos */}
          <div className="bg-gradient-to-br from-slate-800/90 to-slate-700/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-slate-600/50 p-6">
            <h2 className="text-2xl font-bold mb-6 text-center text-white border-b border-blue-400/30 pb-3">Top Técnicos</h2>
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {technicianRanking.map((tech, index) => (
                <div key={tech.id} className="flex items-center justify-between bg-gradient-to-r from-slate-700/50 to-slate-600/50 rounded-xl p-4 border border-slate-500/30 hover:from-slate-600/60 hover:to-slate-500/60 transition-all duration-300 transform hover:scale-105">
                  <div className="flex items-center space-x-4">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold shadow-lg ${
                      index === 0 ? 'bg-gradient-to-br from-yellow-400 to-yellow-600 text-yellow-900' :
                      index === 1 ? 'bg-gradient-to-br from-gray-300 to-gray-500 text-gray-800' :
                      index === 2 ? 'bg-gradient-to-br from-orange-400 to-orange-600 text-orange-900' :
                      'bg-gradient-to-br from-blue-400 to-blue-600 text-blue-900'
                    }`}>
                      {tech.rank || index + 1}
                    </div>
                    <div>
                      <div className="text-sm font-semibold text-white">{tech.nome || tech.name}</div>
                      <div className="text-xs text-blue-200">Técnico</div>
                    </div>
                  </div>
                  <div className="text-2xl font-bold text-cyan-300">{tech.total}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Resumo Geral */}
          <div className="bg-gradient-to-br from-slate-800/90 to-slate-700/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-slate-600/50 p-6">
            <h2 className="text-2xl font-bold mb-6 text-center text-white border-b border-blue-400/30 pb-3">Resumo Geral</h2>
            <div className="space-y-4">
              <div className="flex justify-between items-center p-4 bg-gradient-to-r from-blue-500/20 to-cyan-500/20 rounded-xl border border-blue-400/30">
                <span className="text-sm font-semibold text-blue-200">Total Geral:</span>
                <span className="text-2xl font-bold text-cyan-300">{metrics.total}</span>
              </div>
              <div className="flex justify-between items-center p-4 bg-gradient-to-r from-amber-500/20 to-orange-500/20 rounded-xl border border-amber-400/30">
                <span className="text-sm font-semibold text-amber-200">Ativos:</span>
                <span className="text-2xl font-bold text-amber-300">{metrics.novos + metrics.progresso + metrics.pendentes}</span>
              </div>
              <div className="flex justify-between items-center p-4 bg-gradient-to-r from-emerald-500/20 to-green-500/20 rounded-xl border border-emerald-400/30">
                <span className="text-sm font-semibold text-emerald-200">Resolvidos:</span>
                <span className="text-2xl font-bold text-emerald-300">{metrics.resolvidos}</span>
              </div>
            </div>
          </div>

          {/* Tickets Novos */}
          <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl shadow-lg border border-purple-200 p-6 hover:shadow-xl transition-all duration-300">
            <h2 className="text-2xl font-bold mb-6 text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600 border-b border-purple-200 pb-3">Tickets Recentes</h2>
            {ticketsLoading ? (
              <div className="text-center py-4">
                <div className="text-purple-600 font-medium">Carregando...</div>
              </div>
            ) : (
              <div className="space-y-3 max-h-48 overflow-y-auto">
                {newTickets.length > 0 ? (
                  newTickets.map((ticket) => (
                    <div key={ticket.id} className="bg-white/70 backdrop-blur-sm rounded-lg p-4 border border-purple-100 hover:bg-white/90 hover:border-purple-300 transition-all duration-200 hover:shadow-md">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="text-sm font-semibold text-gray-800 truncate">
                            #{ticket.id} - {ticket.title}
                          </div>
                          <div className="text-xs text-purple-600 mt-1 font-medium">
                            {ticket.requester} • {new Date(ticket.date).toLocaleString('pt-BR')}
                          </div>
                        </div>
                        <div className="ml-2">
                          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-sm">
                            {ticket.priority}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-4 text-purple-600 font-medium">
                    Nenhum ticket novo
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="mt-8 text-center border-t border-gradient-to-r from-blue-200 via-purple-200 to-pink-200 pt-6">
        <p className="text-lg font-semibold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600">
          Sistema atualizado automaticamente • {new Date().toLocaleString('pt-BR')}
        </p>
      </div>
    </div>
  );
};

export default SimplifiedDashboard;