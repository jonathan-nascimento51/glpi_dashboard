import type { Meta, StoryObj } from '@storybook/react';
import { DashboardCard, LevelCard } from './DashboardCard';
import { TrendDirection } from '../types/dashboardTypes';

const meta: Meta<typeof DashboardCard> = {
  title: 'Dashboard/DashboardCard',
  component: DashboardCard,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: { type: 'select' },
      options: ['default', 'primary', 'success', 'warning', 'danger'],
    },
    trend: {
      control: { type: 'select' },
      options: ['up', 'down', 'stable'],
    },
    isLoading: {
      control: { type: 'boolean' },
    },
    hasError: {
      control: { type: 'boolean' },
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

// DashboardCard Stories
export const Default: Story = {
  args: {
    title: 'Total de Tickets',
    value: '1,234',
    subtitle: 'Últimas 24 horas',
    icon: 'Ticket',
    variant: 'default',
  },
};

export const WithTrendUp: Story = {
  args: {
    title: 'Tickets Resolvidos',
    value: '856',
    subtitle: '+12% em relação ao mês anterior',
    icon: 'CheckCircle',
    variant: 'success',
    trend: 'up' as TrendDirection,
    trendValue: '+12%',
  },
};

export const WithTrendDown: Story = {
  args: {
    title: 'Tickets Pendentes',
    value: '378',
    subtitle: '-8% em relação ao mês anterior',
    icon: 'Clock',
    variant: 'warning',
    trend: 'down' as TrendDirection,
    trendValue: '-8%',
  },
};

export const WithTrendStable: Story = {
  args: {
    title: 'Tempo Médio de Resolução',
    value: '4.2h',
    subtitle: 'Sem alteração significativa',
    icon: 'Timer',
    variant: 'primary',
    trend: 'stable' as TrendDirection,
    trendValue: '0%',
  },
};

export const Loading: Story = {
  args: {
    title: 'Carregando...',
    value: '---',
    subtitle: 'Aguardando dados',
    icon: 'Loader',
    variant: 'default',
    isLoading: true,
  },
};

export const Error: Story = {
  args: {
    title: 'Erro ao Carregar',
    value: 'N/A',
    subtitle: 'Falha na conexão',
    icon: 'AlertTriangle',
    variant: 'danger',
    hasError: true,
  },
};

export const DangerVariant: Story = {
  args: {
    title: 'Tickets Críticos',
    value: '23',
    subtitle: 'Requer atenção imediata',
    icon: 'AlertTriangle',
    variant: 'danger',
    trend: 'up' as TrendDirection,
    trendValue: '+15%',
  },
};

// LevelCard Stories
const LevelCardMeta: Meta<typeof LevelCard> = {
  title: 'Dashboard/LevelCard',
  component: LevelCard,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    level: {
      control: { type: 'select' },
      options: ['N1', 'N2', 'N3', 'N4'],
    },
    isLoading: {
      control: { type: 'boolean' },
    },
    hasError: {
      control: { type: 'boolean' },
    },
  },
};

export const LevelCardDefault: StoryObj<typeof LevelCard> = {
  args: {
    level: 'N1',
    total: 145,
    resolved: 98,
    pending: 47,
    responseTime: '2.3h',
  },
  parameters: {
    docs: {
      storyDescription: 'Card padrão para exibir métricas por nível de suporte.',
    },
  },
};

export const LevelCardN2: StoryObj<typeof LevelCard> = {
  args: {
    level: 'N2',
    total: 89,
    resolved: 67,
    pending: 22,
    responseTime: '4.1h',
  },
};

export const LevelCardN3: StoryObj<typeof LevelCard> = {
  args: {
    level: 'N3',
    total: 34,
    resolved: 28,
    pending: 6,
    responseTime: '6.8h',
  },
};

export const LevelCardN4: StoryObj<typeof LevelCard> = {
  args: {
    level: 'N4',
    total: 12,
    resolved: 10,
    pending: 2,
    responseTime: '12.5h',
  },
};

export const LevelCardLoading: StoryObj<typeof LevelCard> = {
  args: {
    level: 'N1',
    total: 0,
    resolved: 0,
    pending: 0,
    responseTime: '0h',
    isLoading: true,
  },
};

export const LevelCardError: StoryObj<typeof LevelCard> = {
  args: {
    level: 'N1',
    total: 0,
    resolved: 0,
    pending: 0,
    responseTime: '0h',
    hasError: true,
  },
};

// Grid de exemplos
export const LevelCardsGrid: StoryObj = {
  render: () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 p-4">
      <LevelCard
        level="N1"
        total={145}
        resolved={98}
        pending={47}
        responseTime="2.3h"
      />
      <LevelCard
        level="N2"
        total={89}
        resolved={67}
        pending={22}
        responseTime="4.1h"
      />
      <LevelCard
        level="N3"
        total={34}
        resolved={28}
        pending={6}
        responseTime="6.8h"
      />
      <LevelCard
        level="N4"
        total={12}
        resolved={10}
        pending={2}
        responseTime="12.5h"
      />
    </div>
  ),
  parameters: {
    docs: {
      storyDescription: 'Exemplo de grid com todos os níveis de suporte.',
    },
  },
};

// Exportar também as stories do LevelCard
export {
  LevelCardDefault,
  LevelCardN2,
  LevelCardN3,
  LevelCardN4,
  LevelCardLoading,
  LevelCardError,
  LevelCardsGrid,
};