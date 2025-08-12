import type { Meta, StoryObj } from '@storybook/react';
import { TechnicianRankingComponent, CompactTechnicianRanking } from './TechnicianRanking';
import { TechnicianRankingData } from '../types/dashboardTypes';

const meta: Meta<typeof TechnicianRankingComponent> = {
  title: 'Dashboard/TechnicianRanking',
  component: TechnicianRankingComponent,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'Componente para exibir ranking de técnicos com estatísticas de performance.',
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
const mockRankingData: TechnicianRankingData = {
  technicians: [
    {
      id: '1',
      name: 'Ana Silva',
      level: 'N3',
      totalTickets: 145,
      resolvedTickets: 132,
      avgResponseTime: '2.3h',
      resolutionRate: 91.0,
      rank: 1,
      trend: 'up',
      avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face',
    },
    {
      id: '2',
      name: 'Carlos Santos',
      level: 'N2',
      totalTickets: 128,
      resolvedTickets: 115,
      avgResponseTime: '3.1h',
      resolutionRate: 89.8,
      rank: 2,
      trend: 'stable',
      avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face',
    },
    {
      id: '3',
      name: 'Maria Oliveira',
      level: 'N3',
      totalTickets: 134,
      resolvedTickets: 118,
      avgResponseTime: '2.8h',
      resolutionRate: 88.1,
      rank: 3,
      trend: 'up',
      avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face',
    },
    {
      id: '4',
      name: 'João Pereira',
      level: 'N2',
      totalTickets: 98,
      resolvedTickets: 84,
      avgResponseTime: '4.2h',
      resolutionRate: 85.7,
      rank: 4,
      trend: 'down',
      avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face',
    },
    {
      id: '5',
      name: 'Fernanda Costa',
      level: 'N1',
      totalTickets: 89,
      resolvedTickets: 76,
      avgResponseTime: '3.5h',
      resolutionRate: 85.4,
      rank: 5,
      trend: 'stable',
      avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&h=150&fit=crop&crop=face',
    },
    {
      id: '6',
      name: 'Roberto Lima',
      level: 'N4',
      totalTickets: 67,
      resolvedTickets: 56,
      avgResponseTime: '6.1h',
      resolutionRate: 83.6,
      rank: 6,
      trend: 'up',
      avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face',
    },
  ],
  summary: {
    totalTechnicians: 6,
    avgResolutionRate: 87.3,
    avgResponseTime: '3.7h',
    topPerformer: 'Ana Silva',
  },
};

const mockRankingDataSmall: TechnicianRankingData = {
  technicians: [
    {
      id: '1',
      name: 'Ana Silva',
      level: 'N3',
      totalTickets: 23,
      resolvedTickets: 21,
      avgResponseTime: '1.8h',
      resolutionRate: 91.3,
      rank: 1,
      trend: 'up',
      avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face',
    },
    {
      id: '2',
      name: 'Carlos Santos',
      level: 'N2',
      totalTickets: 18,
      resolvedTickets: 15,
      avgResponseTime: '2.3h',
      resolutionRate: 83.3,
      rank: 2,
      trend: 'stable',
      avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face',
    },
    {
      id: '3',
      name: 'Maria Oliveira',
      level: 'N1',
      totalTickets: 12,
      resolvedTickets: 9,
      avgResponseTime: '3.1h',
      resolutionRate: 75.0,
      rank: 3,
      trend: 'down',
      avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face',
    },
  ],
  summary: {
    totalTechnicians: 3,
    avgResolutionRate: 83.2,
    avgResponseTime: '2.4h',
    topPerformer: 'Ana Silva',
  },
};

const emptyRankingData: TechnicianRankingData = {
  technicians: [],
  summary: {
    totalTechnicians: 0,
    avgResolutionRate: 0,
    avgResponseTime: '0h',
    topPerformer: '',
  },
};

export const Default: Story = {
  args: {
    data: mockRankingData,
    isLoading: false,
    hasError: false,
    showCompact: false,
  },
};

export const Compact: Story = {
  args: {
    data: mockRankingData,
    isLoading: false,
    hasError: false,
    showCompact: true,
  },
  parameters: {
    docs: {
      storyDescription: 'Versão compacta do ranking, mostrando apenas os top 3 técnicos.',
    },
  },
};

export const SmallTeam: Story = {
  args: {
    data: mockRankingDataSmall,
    isLoading: false,
    hasError: false,
    showCompact: false,
  },
  parameters: {
    docs: {
      storyDescription: 'Ranking com equipe pequena (3 técnicos).',
    },
  },
};

export const Loading: Story = {
  args: {
    data: emptyRankingData,
    isLoading: true,
    hasError: false,
    showCompact: false,
  },
  parameters: {
    docs: {
      storyDescription: 'Estado de carregamento do ranking.',
    },
  },
};

export const Error: Story = {
  args: {
    data: emptyRankingData,
    isLoading: false,
    hasError: true,
    showCompact: false,
  },
  parameters: {
    docs: {
      storyDescription: 'Estado de erro do ranking.',
    },
  },
};

export const Empty: Story = {
  args: {
    data: emptyRankingData,
    isLoading: false,
    hasError: false,
    showCompact: false,
  },
  parameters: {
    docs: {
      storyDescription: 'Ranking sem dados para exibir.',
    },
  },
};

export const CompactLoading: Story = {
  args: {
    data: emptyRankingData,
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

// Stories específicas para CompactTechnicianRanking
const CompactMeta: Meta<typeof CompactTechnicianRanking> = {
  title: 'Dashboard/CompactTechnicianRanking',
  component: CompactTechnicianRanking,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
};

export const CompactDefault: StoryObj<typeof CompactTechnicianRanking> = {
  args: {
    data: mockRankingData,
    isLoading: false,
    hasError: false,
  },
  parameters: {
    docs: {
      storyDescription: 'Versão compacta independente do ranking de técnicos.',
    },
  },
};

export const CompactSmallTeam: StoryObj<typeof CompactTechnicianRanking> = {
  args: {
    data: mockRankingDataSmall,
    isLoading: false,
    hasError: false,
  },
};

export const CompactEmpty: StoryObj<typeof CompactTechnicianRanking> = {
  args: {
    data: emptyRankingData,
    isLoading: false,
    hasError: false,
  },
};

// Story para demonstrar diferentes estados lado a lado
export const AllStates: Story = {
  render: () => (
    <div className="space-y-8">
      <div>
        <h3 className="text-lg font-semibold mb-4">Ranking Completo</h3>
        <TechnicianRankingComponent data={mockRankingData} />
      </div>
      <div>
        <h3 className="text-lg font-semibold mb-4">Versão Compacta</h3>
        <CompactTechnicianRanking data={mockRankingData} />
      </div>
      <div>
        <h3 className="text-lg font-semibold mb-4">Equipe Pequena</h3>
        <TechnicianRankingComponent data={mockRankingDataSmall} />
      </div>
    </div>
  ),
  parameters: {
    docs: {
      storyDescription: 'Comparação entre diferentes estados e versões do ranking.',
    },
  },
};

// Story para demonstrar responsividade
export const Responsive: Story = {
  args: {
    data: mockRankingData,
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
      storyDescription: 'Ranking responsivo que se adapta a diferentes tamanhos de tela.',
    },
  },
};

// Story para demonstrar diferentes tendências
export const TrendVariations: Story = {
  render: () => {
    const trendData: TechnicianRankingData = {
      technicians: [
        {
          id: '1',
          name: 'Técnico Subindo',
          level: 'N2',
          totalTickets: 50,
          resolvedTickets: 45,
          avgResponseTime: '2.5h',
          resolutionRate: 90.0,
          rank: 1,
          trend: 'up',
        },
        {
          id: '2',
          name: 'Técnico Estável',
          level: 'N2',
          totalTickets: 48,
          resolvedTickets: 42,
          avgResponseTime: '2.8h',
          resolutionRate: 87.5,
          rank: 2,
          trend: 'stable',
        },
        {
          id: '3',
          name: 'Técnico Descendo',
          level: 'N1',
          totalTickets: 45,
          resolvedTickets: 36,
          avgResponseTime: '3.2h',
          resolutionRate: 80.0,
          rank: 3,
          trend: 'down',
        },
      ],
      summary: {
        totalTechnicians: 3,
        avgResolutionRate: 85.8,
        avgResponseTime: '2.8h',
        topPerformer: 'Técnico Subindo',
      },
    };

    return (
      <div className="max-w-2xl">
        <h3 className="text-lg font-semibold mb-4">Diferentes Tendências</h3>
        <TechnicianRankingComponent data={trendData} />
      </div>
    );
  },
  parameters: {
    docs: {
      storyDescription: 'Demonstração das diferentes tendências (subindo, estável, descendo).',
    },
  },
};

// Exportar stories do CompactTechnicianRanking
export {
  CompactDefault,
  CompactSmallTeam,
  CompactEmpty,
};