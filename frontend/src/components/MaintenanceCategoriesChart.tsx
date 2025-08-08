import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Progress } from './ui/progress';
import { Badge } from './ui/badge';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import { Wrench } from 'lucide-react';
import { MaintenanceCategoriesData } from '../hooks/useMaintenanceDashboard';

interface MaintenanceCategoriesChartProps {
  data: MaintenanceCategoriesData;
}

export const MaintenanceCategoriesChart: React.FC<MaintenanceCategoriesChartProps> = ({ 
  data 
}) => {
  // Cores para os gráficos
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  // Dados para gráfico de barras (volume de tickets)
  const volumeData = data.categories.map(category => ({
    name: category.name,
    tickets: category.ticketCount,
    tempo: category.avgResolutionTime
  }));

  // Dados para gráfico de pizza (distribuição por prioridade)
  const priorityData = data.categories.reduce((acc, category) => {
    const priorityName = category.priority;
    const existing = acc.find(item => item.name === priorityName);
    if (existing) {
      existing.value += category.ticketCount;
    } else {
      acc.push({ name: priorityName, value: category.ticketCount });
    }
    return acc;
  }, [] as { name: string; value: number }[]);

  // Dados para gráfico de linha (eficiência)
  const efficiencyData = data.categories.map(category => ({
    name: category.name,
    eficiencia: 100 - (category.avgResolutionTime / 48) * 100,
    conclusao: (category.ticketCount / data.summary.totalTickets) * 100
  }));

  // Estatísticas gerais
  const { summary } = data;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 lg:p-6">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
          🔧 Análise de Categorias de Manutenção
        </h2>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Distribuição e performance das categorias de serviços de manutenção
        </p>
      </div>

      {/* Summary Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-3xl font-bold text-blue-600">
              {summary.totalTickets}
            </div>
            <div className="text-sm text-gray-600">Total de Tickets</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-3xl font-bold text-orange-600">
              {summary.avgResolutionTime.toFixed(1)}h
            </div>
            <div className="text-sm text-gray-600">Tempo Médio</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-3xl font-bold text-green-600">
              {((summary.totalTickets / summary.totalTickets) * 100).toFixed(1)}%
            </div>
            <div className="text-sm text-gray-600">Taxa de Conclusão</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-3xl font-bold text-red-600">
              {summary.criticalCategories}
            </div>
            <div className="text-sm text-gray-600">Categorias Críticas</div>
          </CardContent>
        </Card>
      </div>

      {/* Cards de Categorias */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {data.categories.map((category) => (
          <Card key={category.id} className="hover:shadow-lg transition-shadow">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <Wrench className="h-4 w-4" />
                  {category.name}
                </span>
                <div className="flex gap-1">
                  <Badge 
                    variant={category.priority === 'Alta' ? 'destructive' : 
                            category.priority === 'Média' ? 'default' : 'secondary'}
                    className="text-xs"
                  >
                    {category.priority}
                  </Badge>
                  <Badge 
                    variant={category.status === 'Crítico' ? 'destructive' : 'outline'}
                    className="text-xs"
                  >
                    {category.status}
                  </Badge>
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Tickets</span>
                  <span className="font-semibold">{category.ticketCount}</span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Tempo Médio</span>
                  <span className="font-semibold">{category.avgResolutionTime}h</span>
                </div>
                
                <div className="space-y-1">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Taxa de Conclusão</span>
                    <span className="font-semibold">{((category.ticketCount / data.summary.totalTickets) * 100).toFixed(1)}%</span>
                  </div>
                  <Progress value={(category.ticketCount / data.summary.totalTickets) * 100} className="h-2" />
                </div>
                
                <div className="space-y-1">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Eficiência</span>
                    <span className="font-semibold">{(100 - (category.avgResolutionTime / 48) * 100).toFixed(1)}%</span>
                  </div>
                  <Progress value={100 - (category.avgResolutionTime / 48) * 100} className="h-2" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Volume Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Volume de Tickets por Categoria</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={volumeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="tickets" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Priority Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Distribuição por Prioridade</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={priorityData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${percent ? (percent * 100).toFixed(0) : 0}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {priorityData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Efficiency Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Eficiência por Categoria</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={efficiencyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="eficiencia" 
                  stroke="#8884d8" 
                  strokeWidth={2}
                  name="Eficiência (%)"
                />
                <Line 
                  type="monotone" 
                  dataKey="conclusao" 
                  stroke="#82ca9d" 
                  strokeWidth={2}
                  name="Taxa de Conclusão (%)"
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};