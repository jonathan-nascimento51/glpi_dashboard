import React from 'react';
import { Users, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { MetricsData, LevelMetrics } from '../types';

interface LevelsSectionProps {
  metrics: MetricsData;
}

interface LevelCardProps {
  level: string;
  data: LevelMetrics;
  resolucaoRate: number;
}

const LevelCard: React.FC<LevelCardProps> = ({ level, data, resolucaoRate }) => {
  return (
    <div className="card-base p-6 col-span-3 md:col-span-6 lg:col-span-3">
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-h3 text-primary">Nível {level}</h3>
        <span className="text-meta status-resolved">
          {resolucaoRate}% Resolução
        </span>
      </div>
      
      {/* Metrics Grid */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="text-center">
          <div className="text-numeric status-new">{data.novos}</div>
          <div className="text-body text-secondary">Novos</div>
        </div>
        <div className="text-center">
          <div className="text-numeric status-progress">{data.progresso}</div>
          <div className="text-body text-secondary">Progresso</div>
        </div>
        <div className="text-center">
          <div className="text-numeric status-pending">{data.pendentes}</div>
          <div className="text-body text-secondary">Pendentes</div>
        </div>
        <div className="text-center">
          <div className="text-numeric status-resolved">{data.resolvidos}</div>
          <div className="text-body text-secondary">Resolvidos</div>
        </div>
      </div>
      
      {/* Progress Bar */}
      <div className="w-full bg-gray-200 rounded-full h-1.5">
        <div 
          className="bg-status-resolved h-1.5 rounded-full transition-all duration-300"
          style={{ width: `${resolucaoRate}%` }}
        ></div>
      </div>
    </div>
  );
};

export const LevelsSection: React.FC<LevelsSectionProps> = ({ metrics }) => {
  // Verificação de segurança para evitar erros
  if (!metrics || !metrics.niveis) {
    return (
      <div className="space-y-6">
        <div className="text-center text-gray-500">Carregando métricas por nível...</div>
      </div>
    );
  }

  return (
    <section className="grid-container mb-8">
      <div className="col-span-12">
        <h2 className="text-h1 text-primary mb-6">Níveis de Atendimento</h2>
        <div className="grid grid-cols-12 gap-4">
          <LevelCard level="1" data={metrics.niveis.n1} resolucaoRate={85} />
          <LevelCard level="2" data={metrics.niveis.n2} resolucaoRate={78} />
          <LevelCard level="3" data={metrics.niveis.n3} resolucaoRate={92} />
          <LevelCard level="4" data={metrics.niveis.n4} resolucaoRate={95} />
        </div>
      </div>
    </section>
  );
};
