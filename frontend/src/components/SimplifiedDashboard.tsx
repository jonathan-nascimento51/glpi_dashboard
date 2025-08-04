import React from 'react';
import { MetricsData, TechnicianRanking } from '../types';

interface SimplifiedDashboardProps {
  metrics: MetricsData;
  technicianRanking: TechnicianRanking[];
  currentTime: string;
  lastUpdated: Date | null;
}

export const SimplifiedDashboard: React.FC<SimplifiedDashboardProps> = ({
  metrics,
  technicianRanking,
  currentTime,
  lastUpdated,
}) => {
  return (
    <div className="h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900 text-white p-4 overflow-hidden flex flex-col">
      {/* Header - Compacto */}
      <div className="flex justify-between items-center mb-4">
        <div>
          <h1 className="text-3xl font-bold mb-1">Dashboard de Suporte - Níveis</h1>
          <p className="text-base text-blue-200">Monitoramento por Níveis de Atendimento</p>
        </div>
        <div className="text-right">
          <div className="text-2xl font-mono font-bold">{currentTime}</div>
          <div className="text-sm text-blue-200">
            {new Date().toLocaleDateString('pt-BR', {
              weekday: 'short',
              day: 'numeric',
              month: 'short',
            })}
          </div>
        </div>
      </div>

      {/* Layout Principal - 3 colunas */}
      <div className="flex-1 grid grid-cols-3 gap-4">
        {/* Coluna 1 - N1 e N2 */}
        <div className="space-y-4">
          {/* N1 Level */}
          <div className="bg-gradient-to-br from-green-500/20 to-green-600/30 backdrop-blur-sm rounded-xl p-4 border border-green-400/40 h-[calc(50%-8px)]">
            <div className="flex justify-between items-center mb-3">
              <h2 className="text-xl font-bold text-green-300">N1 - BÁSICO</h2>
              <div className="text-2xl font-bold text-green-200">
                {metrics.niveis.n1.novos + metrics.niveis.n1.progresso + metrics.niveis.n1.pendentes + metrics.niveis.n1.resolvidos}
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2 h-[calc(100%-60px)]">
              <div className="bg-blue-500/20 rounded-lg p-2 flex flex-col justify-center items-center border border-blue-400/30">
                <div className="text-xl font-bold text-blue-300">{metrics.niveis.n1.novos}</div>
                <div className="text-xs text-blue-200 font-semibold">NOVOS</div>
              </div>
              <div className="bg-green-500/20 rounded-lg p-2 flex flex-col justify-center items-center border border-green-400/30">
                <div className="text-xl font-bold text-green-300">{metrics.niveis.n1.progresso}</div>
                <div className="text-xs text-green-200 font-semibold">PROGRESSO</div>
              </div>
              <div className="bg-orange-500/20 rounded-lg p-2 flex flex-col justify-center items-center border border-orange-400/30">
                <div className="text-xl font-bold text-orange-300">{metrics.niveis.n1.pendentes}</div>
                <div className="text-xs text-orange-200 font-semibold">PENDENTES</div>
              </div>
              <div className="bg-emerald-500/20 rounded-lg p-2 flex flex-col justify-center items-center border border-emerald-400/30">
                <div className="text-xl font-bold text-emerald-300">{metrics.niveis.n1.resolvidos}</div>
                <div className="text-xs text-emerald-200 font-semibold">RESOLVIDOS</div>
              </div>
            </div>
          </div>

          {/* N2 Level */}
          <div className="bg-gradient-to-br from-blue-500/20 to-blue-600/30 backdrop-blur-sm rounded-xl p-4 border border-blue-400/40 h-[calc(50%-8px)]">
            <div className="flex justify-between items-center mb-3">
              <h2 className="text-xl font-bold text-blue-300">N2 - INTERMEDIÁRIO</h2>
              <div className="text-2xl font-bold text-blue-200">
                {metrics.niveis.n2.novos + metrics.niveis.n2.progresso + metrics.niveis.n2.pendentes + metrics.niveis.n2.resolvidos}
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2 h-[calc(100%-60px)]">
              <div className="bg-blue-500/20 rounded-lg p-2 flex flex-col justify-center items-center border border-blue-400/30">
                <div className="text-xl font-bold text-blue-300">{metrics.niveis.n2.novos}</div>
                <div className="text-xs text-blue-200 font-semibold">NOVOS</div>
              </div>
              <div className="bg-green-500/20 rounded-lg p-2 flex flex-col justify-center items-center border border-green-400/30">
                <div className="text-xl font-bold text-green-300">{metrics.niveis.n2.progresso}</div>
                <div className="text-xs text-green-200 font-semibold">PROGRESSO</div>
              </div>
              <div className="bg-orange-500/20 rounded-lg p-2 flex flex-col justify-center items-center border border-orange-400/30">
                <div className="text-xl font-bold text-orange-300">{metrics.niveis.n2.pendentes}</div>
                <div className="text-xs text-orange-200 font-semibold">PENDENTES</div>
              </div>
              <div className="bg-emerald-500/20 rounded-lg p-2 flex flex-col justify-center items-center border border-emerald-400/30">
                <div className="text-xl font-bold text-emerald-300">{metrics.niveis.n2.resolvidos}</div>
                <div className="text-xs text-emerald-200 font-semibold">RESOLVIDOS</div>
              </div>
            </div>
          </div>
        </div>

        {/* Coluna 2 - N3 e N4 */}
        <div className="space-y-4">
          {/* N3 Level */}
          <div className="bg-gradient-to-br from-purple-500/20 to-purple-600/30 backdrop-blur-sm rounded-xl p-4 border border-purple-400/40 h-[calc(50%-8px)]">
            <div className="flex justify-between items-center mb-3">
              <h2 className="text-xl font-bold text-purple-300">N3 - AVANÇADO</h2>
              <div className="text-2xl font-bold text-purple-200">
                {metrics.niveis.n3.novos + metrics.niveis.n3.progresso + metrics.niveis.n3.pendentes + metrics.niveis.n3.resolvidos}
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2 h-[calc(100%-60px)]">
              <div className="bg-blue-500/20 rounded-lg p-2 flex flex-col justify-center items-center border border-blue-400/30">
                <div className="text-xl font-bold text-blue-300">{metrics.niveis.n3.novos}</div>
                <div className="text-xs text-blue-200 font-semibold">NOVOS</div>
              </div>
              <div className="bg-green-500/20 rounded-lg p-2 flex flex-col justify-center items-center border border-green-400/30">
                <div className="text-xl font-bold text-green-300">{metrics.niveis.n3.progresso}</div>
                <div className="text-xs text-green-200 font-semibold">PROGRESSO</div>
              </div>
              <div className="bg-orange-500/20 rounded-lg p-2 flex flex-col justify-center items-center border border-orange-400/30">
                <div className="text-xl font-bold text-orange-300">{metrics.niveis.n3.pendentes}</div>
                <div className="text-xs text-orange-200 font-semibold">PENDENTES</div>
              </div>
              <div className="bg-emerald-500/20 rounded-lg p-2 flex flex-col justify-center items-center border border-emerald-400/30">
                <div className="text-xl font-bold text-emerald-300">{metrics.niveis.n3.resolvidos}</div>
                <div className="text-xs text-emerald-200 font-semibold">RESOLVIDOS</div>
              </div>
            </div>
          </div>

          {/* N4 Level */}
          <div className="bg-gradient-to-br from-red-500/20 to-red-600/30 backdrop-blur-sm rounded-xl p-4 border border-red-400/40 h-[calc(50%-8px)]">
            <div className="flex justify-between items-center mb-3">
              <h2 className="text-xl font-bold text-red-300">N4 - ESPECIALISTA</h2>
              <div className="text-2xl font-bold text-red-200">
                {metrics.niveis.n4.novos + metrics.niveis.n4.progresso + metrics.niveis.n4.pendentes + metrics.niveis.n4.resolvidos}
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2 h-[calc(100%-60px)]">
              <div className="bg-blue-500/20 rounded-lg p-2 flex flex-col justify-center items-center border border-blue-400/30">
                <div className="text-xl font-bold text-blue-300">{metrics.niveis.n4.novos}</div>
                <div className="text-xs text-blue-200 font-semibold">NOVOS</div>
              </div>
              <div className="bg-green-500/20 rounded-lg p-2 flex flex-col justify-center items-center border border-green-400/30">
                <div className="text-xl font-bold text-green-300">{metrics.niveis.n4.progresso}</div>
                <div className="text-xs text-green-200 font-semibold">PROGRESSO</div>
              </div>
              <div className="bg-orange-500/20 rounded-lg p-2 flex flex-col justify-center items-center border border-orange-400/30">
                <div className="text-xl font-bold text-orange-300">{metrics.niveis.n4.pendentes}</div>
                <div className="text-xs text-orange-200 font-semibold">PENDENTES</div>
              </div>
              <div className="bg-emerald-500/20 rounded-lg p-2 flex flex-col justify-center items-center border border-emerald-400/30">
                <div className="text-xl font-bold text-emerald-300">{metrics.niveis.n4.resolvidos}</div>
                <div className="text-xs text-emerald-200 font-semibold">RESOLVIDOS</div>
              </div>
            </div>
          </div>
        </div>

        {/* Coluna 3 - Ranking e Resumo */}
        <div className="space-y-4">
          {/* Top Técnicos */}
          <div className="bg-gradient-to-br from-indigo-500/20 to-indigo-600/30 backdrop-blur-sm rounded-xl p-4 border border-indigo-400/40 h-[calc(70%-8px)]">
            <h2 className="text-xl font-bold text-indigo-300 mb-3">Top Técnicos</h2>
            <div className="space-y-2">
              {technicianRanking.slice(0, 5).map((tech, index) => (
                <div key={tech.id} className="flex items-center justify-between bg-white/10 rounded-lg p-2 border border-white/20">
                  <div className="flex items-center space-x-2">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                      index === 0 ? 'bg-yellow-500 text-black' :
                      index === 1 ? 'bg-gray-400 text-black' :
                      index === 2 ? 'bg-orange-600 text-white' :
                      'bg-blue-600 text-white'
                    }`}>
                      {index + 1}
                    </div>
                    <div>
                      <div className="text-sm font-semibold text-white">{tech.name}</div>
                      <div className="text-xs text-gray-300">{tech.level}</div>
                    </div>
                  </div>
                  <div className="text-lg font-bold text-green-300">{tech.total || tech.score}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Resumo Geral */}
          <div className="bg-gradient-to-br from-gray-500/20 to-gray-600/30 backdrop-blur-sm rounded-xl p-4 border border-gray-400/40 h-[calc(30%-8px)]">
            <h2 className="text-lg font-bold text-gray-300 mb-2">Resumo Geral</h2>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-300">Total Geral:</span>
                <span className="text-lg font-bold text-yellow-300">{metrics.total}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-300">Ativos:</span>
                <span className="text-lg font-bold text-green-300">{metrics.novos + metrics.progresso + metrics.pendentes}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-300">Resolvidos:</span>
                <span className="text-lg font-bold text-emerald-300">{metrics.resolvidos}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer - Compacto */}
      <div className="mt-4 text-center text-blue-200">
        <p className="text-sm">
          Última atualização: {lastUpdated ? lastUpdated.toLocaleString('pt-BR') : 'Nunca'}
        </p>
      </div>
    </div>
  );
};