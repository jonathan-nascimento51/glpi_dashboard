import type { Meta, StoryObj } from '@storybook/react';
import { MetricsGrid } from './MetricsGrid';
import { MetricsData } from '../types/dashboardTypes';

const meta: Meta<typeof MetricsGrid> = {
  title: 'Dashboard/MetricsGrid',
  component: MetricsGrid,
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: 'Grid de métricas do dashboard que exibe resumo geral, métricas por nível e distribuição por status.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    isLoading: {
      control: { type: 'boolean' },
    },
    hasError: {
      control: { type: 'boolean' },
    },
    showCompact: {
      control: { type: 'boolean' },
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

// Mock data para as stories
const mockMetricsData: MetricsData = {
  summary: {
    total: 1234,
    resolved: 856,
    pending: 378,
    responseTime: '4.2h',
    resolutionRate: 69.4,
  },
  byLevel: {
    N1: {
      total: 145,
      resolved: 98,
      pending: 47,
      responseTime: '2.3h',
    },
    N2: {
      total: 289,
      resolved: 201,
      pending: 88,
      responseTime: '4.1h',
    },
    N3: {
      total: 534,
      resolved: 378,
      pending: 156,
      responseTime: '6.8h',
    },
    N4: {
      total: 266,
      resolved: 179,
      pending: 87,
      responseTime: '12.5h',
    },
  },
  byStatus: {
    new: 45,
    assigned: 123,
    planned: 67,
    waiting: 89,
    solved: 734,
    closed: 122,
    cancelled: 54,
  },
  trends: {
    total: { direction: 'up', value: '+8.5%' },
    resolved: { direction: 'up', value: '+12.3%' },
    pending: { direction: 'down', value: '-5.2%' },
    responseTime: { direction: 'stable', value: '0%' },
  },
};

const mockMetricsDataLow: MetricsData = {
  summary: {
    total: 23,
    resolved: 15,
    pending: 8,
    responseTime: '1.8h',
    resolutionRate: 65.2,
  },
  byLevel: {
    N1: {
      total: 8,
      resolved: 6,
      pending: 2,
      responseTime: '1.2h',
    },
    N2: {
      total: 9,
      resolved: 6,
      pending: 3,
      responseTime: '1.8h',
    },
    N3: {
      total: 4,
      resolved: 2,
      pending: 2,
      responseTime: '2.5h',
    },
    N4: {
      total: 2,
      resolved: 1,
      pending: 1,
      responseTime: '4.2h',
    },
  },
  byStatus: {
    new: 2,
    assigned: 3,
    planned: 1,
    waiting: 2,
    solved: 12,
    closed: 3,
    cancelled: 0,
  },
  trends: {
    total: { direction: 'down', value: '-15.2%' },
    resolved: { direction: 'up', value: '+5.1%' },
    pending: { direction: 'down', value: '-8.7%' },
    responseTime: { direction: 'up', value: '+12%' },
  },
};

const emptyMetricsData: MetricsData = {
  summary: {
    total: 0,
    resolved: 0,
    pending: 0,
    responseTime: '0h',
    resolutionRate: 0,
  },
  byLevel: {
    N1: { total: 0, resolved: 0, pending: 0, responseTime: '0h' },
    N2: { total: 0, resolved: 0, pending: 0, responseTime: '0h' },
    N3: { total: 0, resolved: 0, pending: 0, responseTime: '0h' },
    N4: { total: 0, resolved: 0, pending: 0, responseTime: '0h' },
  },
  byStatus: {
    new: 0,
    assigned: 0,
    planned: 0,
    waiting: 0,
    solved: 0,
    closed: 0,
    cancelled: 0,
  },
  trends: {
    total: { direction: 'stable', value: '0%' },
    resolved: { direction: 'stable', value: '0%' },
    pending: { direction: 'stable', value: '0%' },
    responseTime: { direction: 'stable', value: '0%' },
  },
};

export const Default: Story = {
  args: {
    data: mockMetricsData,
    isLoading: false,
    hasError: false,
    showCompact: false,
  },
};

export const Compact: Story = {
  args: {
    data: mockMetricsData,
    isLoading: false,
    hasError: false,
    showCompact: true,
  },
  parameters: {
    docs: {
      storyDescription: 'Versão compacta do grid de métricas, ideal para espaços menores.',
    },
  },
};

export const LowVolume: Story = {
  args: {
    data: mockMetricsDataLow,
    isLoading: false,
    hasError: false,
    showCompact: false,
  },
  parameters: {
    docs: {
      storyDescription: 'Grid com baixo volume de tickets para testar diferentes cenários.',
    },
  },
};

export const Loading: Story = {
  args: {
    data: emptyMetricsData,
    isLoading: true,
    hasError: false,
    showCompact: false,
  },
  parameters: {
    docs: {
      storyDescription: 'Estado de carregamento do grid de métricas.',
    },
  },
};

export const Error: Story = {
  args: {
    data: emptyMetricsData,
    isLoading: false,
    hasError: true,
    showCompact: false,
  },
  parameters: {
    docs: {
      storyDescription: 'Estado de erro do grid de métricas.',
    },
  },
};

export const Empty: Story = {
  args: {
    data: emptyMetricsData,
    isLoading: false,
    hasError: false,
    showCompact: false,
  },
  parameters: {
    docs: {
      storyDescription: 'Grid sem dados para exibir.',
    },
  },
};

export const CompactLoading: Story = {
  args: {
    data: emptyMetricsData,
    isLoading: true,
    hasError: false,
    showCompact: true,
  },
  parameters: {
    docs: {
      storyDescription: 'Versão compacta em estado de carregamento.',
    },
  },
};

export const CompactError: Story = {
  args: {
    data: emptyMetricsData,
    isLoading: false,
    hasError: true,
    showCompact: true,
  },
  parameters: {
    docs: {
      storyDescription: 'Versão compacta em estado de erro.',
    },
  },
};

// Story para demonstrar responsividade
export const Responsive: Story = {
  args: {
    data: mockMetricsData,
    isLoading: false,
    hasError: false,
    showCompact: false,
  },
  parameters: {
    viewport: {
      viewports: {
        mobile: {
          name: 'Mobile',
          styles: {
            width: '375px',
            height: '667px',
          },
        },
        tablet: {
          name: 'Tablet',
          styles: {
            width: '768px',
            height: '1024px',
          },
        },
        desktop: {
          name: 'Desktop',
          styles: {
            width: '1200px',
            height: '800px',
          },
        },
      },
    },
    docs: {
      storyDescription: 'Grid responsivo que se adapta a diferentes tamanhos de tela.',
    },
  },
};

// Story para demonstrar diferentes estados de dados
export const DataStates: Story = {
  render: () => (
    <div className="space-y-8">
      <div>
        <h3 className="text-lg font-semibold mb-4">Alto Volume</h3>
        <MetricsGrid data={mockMetricsData} />
      </div>
      <div>
        <h3 className="text-lg font-semibold mb-4">Baixo Volume</h3>
        <MetricsGrid data={mockMetricsDataLow} />
      </div>
      <div>
        <h3 className="text-lg font-semibold mb-4">Sem Dados</h3>
        <MetricsGrid data={emptyMetricsData} />
      </div>
    </div>
  ),
  parameters: {
    docs: {
      storyDescription: 'Comparação entre diferentes estados de dados no grid.',
    },
  },
};

// Story para demonstrar versões compacta e completa lado a lado
export const CompactVsFull: Story = {
  render: () => (
    <div className="space-y-8">
      <div>
        <h3 className="text-lg font-semibold mb-4">Versão Completa</h3>
        <MetricsGrid data={mockMetricsData} showCompact={false} />
      </div>
      <div>
        <h3 className="text-lg font-semibold mb-4">Versão Compacta</h3>
        <MetricsGrid data={mockMetricsData} showCompact={true} />
      </div>
    </div>
  ),
  parameters: {
    docs: {
      storyDescription: 'Comparação entre as versões completa e compacta do grid.',
    },
  },
};