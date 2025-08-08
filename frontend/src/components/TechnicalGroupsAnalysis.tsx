import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { TechnicalGroupsData } from '../hooks/useMaintenanceDashboard';

interface TechnicalGroupsAnalysisProps {
  data: TechnicalGroupsData;
}

export const TechnicalGroupsAnalysis: React.FC<TechnicalGroupsAnalysisProps> = ({ data }) => {
  const technicalGroups = data.groups;

  // Função para formatar nome do grupo
  const formatGroupName = (name: string) => {
    if (name === 'CC-MANUTENCAO') {
      return 'divisão de manutenção';
    }
    return name.replace('CC-', '').replace('DTI-', '');
  };

  // Dados para o gráfico de barras
  const barChartData = technicalGroups.map(group => ({
    name: formatGroupName(group.name),
    ativo: group.totalTickets - group.resolvedTickets,
    resolvido: group.resolvedTickets,
    eficiencia: group.efficiency
  }));

  // Dados para o gráfico de pizza por categoria
  const categoryData = technicalGroups.reduce((acc, group) => {
    const category = group.category;
    const existing = acc.find(item => item.name === category);
    if (existing) {
      existing.value += group.totalTickets;
    } else {
      acc.push({ name: category, value: group.totalTickets });
    }
    return acc;
  }, [] as { name: string; value: number }[]);

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 lg:p-6">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
          👥 Análise de Grupos Técnicos - Casa Civil
        </h2>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Performance e distribuição de chamados por equipe técnica
        </p>
      </div>

      {/* Groups Performance Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {technicalGroups.map((group) => (
          <div key={group.id} className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-gray-900 dark:text-white text-sm">
                {formatGroupName(group.name)}
              </h3>
              <span className="text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-2 py-1 rounded">
                {group.category || 'Geral'}
              </span>
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600 dark:text-gray-400">Em Andamento:</span>
                <span className="font-medium text-orange-600 dark:text-orange-400">{group.totalTickets - group.resolvedTickets}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600 dark:text-gray-400">Resolvidos:</span>
                <span className="font-medium text-green-600 dark:text-green-400">{group.resolvedTickets}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600 dark:text-gray-400">Total:</span>
                <span className="font-medium text-gray-900 dark:text-white">{group.totalTickets}</span>
              </div>
            </div>
            
            {/* Efficiency Bar */}
            <div className="mt-3">
              <div className="flex justify-between text-xs text-gray-600 dark:text-gray-400 mb-1">
                <span>Eficiência</span>
                <span>{group.efficiency}%</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full transition-all duration-500 ${
                    group.efficiency >= 80 ? 'bg-green-500' :
                     group.efficiency >= 70 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${group.efficiency}%` }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Bar Chart - Performance por Grupo */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 lg:p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            📊 Performance por Grupo
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={barChartData}>
              <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
              <XAxis 
                dataKey="name" 
                tick={{ fontSize: 12 }}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'rgba(255, 255, 255, 0.95)',
                  border: '1px solid #ccc',
                  borderRadius: '8px'
                }}
              />
              <Bar dataKey="ativo" fill="#f59e0b" name="Em Andamento" />
              <Bar dataKey="resolvido" fill="#10b981" name="Resolvidos" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Pie Chart - Distribuição por Categoria */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 lg:p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            🎯 Distribuição por Categoria
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={categoryData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${percent ? (percent * 100).toFixed(0) : 0}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {categoryData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Summary Statistics */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 lg:p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          📈 Estatísticas Gerais
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
              {technicalGroups.length}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Grupos Ativos</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
              {data.summary.totalActiveTickets}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Chamados Ativos</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">
              {data.summary.totalResolvedTickets}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Chamados Resolvidos</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
              {Math.round(data.summary.avgEfficiency)}%
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Eficiência Média</div>
          </div>
        </div>
      </div>
    </div>
  );
};