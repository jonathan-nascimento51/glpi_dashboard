import React from 'react';
import { Users, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { MetricsData, LevelMetrics } from '../types';

interface LevelsSectionProps {
  metrics: MetricsData;
}

interface LevelCardProps {
  level: string;
  data: LevelMetrics;
  title: string;
  description: string;
}

const LevelCard: React.FC<LevelCardProps> = ({ level, data, title, description }) => {
  // Verificação de segurança para evitar erros
  if (!data) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="text-center text-gray-500">Carregando dados do {title}...</div>
      </div>
    );
  }

  const total = (data.novos || 0) + (data.progresso || 0) + (data.pendentes || 0) + (data.resolvidos || 0);
  const resolvedPercentage = total > 0 ? ((data.resolvidos || 0) / total) * 100 : 0;
  
  // Calculate trend (mock calculation based on resolved percentage)
  const getTrend = () => {
    if (resolvedPercentage > 70) return { icon: TrendingUp, color: 'text-green-500', text: 'Excelente' };
    if (resolvedPercentage > 50) return { icon: Minus, color: 'text-yellow-500', text: 'Bom' };
    return { icon: TrendingDown, color: 'text-red-500', text: 'Atenção' };
  };
  
  const trend = getTrend();
  const TrendIcon = trend.icon;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 hover:shadow-md transition-shadow duration-200">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center">
            <Users className="w-5 h-5 text-primary-600 dark:text-primary-400" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white">{title}</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">{description}</p>
          </div>
        </div>
        <div className="flex items-center space-x-1">
          <TrendIcon className={`w-4 h-4 ${trend.color}`} />
          <span className={`text-sm font-medium ${trend.color}`}>
            {trend.text}
          </span>
        </div>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-4 gap-4 mb-4">
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
            {data.novos || 0}
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400">Novos</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
            {data.progresso || 0}
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400">Progresso</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
            {data.pendentes || 0}
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400">Pendentes</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600 dark:text-green-400">
            {data.resolvidos || 0}
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400">Resolvidos</div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex justify-between text-xs text-gray-600 dark:text-gray-400">
          <span>Taxa de Resolução</span>
          <span>{resolvedPercentage.toFixed(1)}%</span>
        </div>
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
          <div 
            className="bg-green-500 h-2 rounded-full transition-all duration-500"
            style={{ width: `${resolvedPercentage}%` }}
          />
        </div>
      </div>

      {/* Total */}
      <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600 dark:text-gray-400">Total</span>
          <span className="text-lg font-semibold text-gray-900 dark:text-white">
            {total} chamados
          </span>
        </div>
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

  const levels = [
    {
      key: 'n1',
      title: 'N1 - Básico',
      description: 'Suporte básico e atendimento inicial',
      data: metrics.niveis?.n1,
    },
    {
      key: 'n2',
      title: 'N2 - Intermediário',
      description: 'Suporte técnico especializado',
      data: metrics.niveis?.n2,
    },
    {
      key: 'n3',
      title: 'N3 - Avançado',
      description: 'Problemas complexos e desenvolvimento',
      data: metrics.niveis?.n3,
    },
    {
      key: 'n4',
      title: 'N4 - Especialista',
      description: 'Arquitetura e soluções críticas',
      data: metrics.niveis?.n4,
    },
  ];

  // Calculate overall statistics
  const totalByLevel = levels.map(level => {
    const data = level.data || { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0 };
    const total = (data.novos || 0) + (data.progresso || 0) + (data.pendentes || 0) + (data.resolvidos || 0);
    return { ...level, total };
  });

  const overallTotal = totalByLevel.reduce((sum, level) => sum + level.total, 0);

  return (
    <div className="space-y-6">
      {/* Section Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Métricas por Nível
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Distribuição de chamados pelos níveis de suporte
          </p>
        </div>
        

      </div>

      {/* Levels Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {levels.map((level) => (
          <LevelCard
            key={level.key}
            level={level.key}
            data={level.data}
            title={level.title}
            description={level.description}
          />
        ))}
      </div>

      {/* Distribution Chart */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Distribuição por Nível
        </h3>
        
        <div className="space-y-4">
          {totalByLevel.map((level, index) => {
            const percentage = overallTotal > 0 ? (level.total / overallTotal) * 100 : 0;
            const colors = ['bg-blue-500', 'bg-green-500', 'bg-yellow-500', 'bg-purple-500'];
            
            return (
              <div key={level.key} className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="font-medium text-gray-900 dark:text-white">
                    {level.title}
                  </span>
                  <span className="text-gray-600 dark:text-gray-400">
                    {level.total} ({percentage.toFixed(1)}%)
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div 
                    className={`${colors[index]} h-2 rounded-full transition-all duration-500`}
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};