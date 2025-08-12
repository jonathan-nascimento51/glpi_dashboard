import type { Meta, StoryObj } from '@storybook/react';
import { SystemStatusComponent, CompactSystemStatus } from './SystemStatus';
import { SystemStatusData } from '../types/dashboardTypes';

const meta: Meta<typeof SystemStatusComponent> = {
  title: 'Dashboard/SystemStatus',
  component: SystemStatusComponent,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'Componente para exibir o status do sistema, incluindo API e GLPI.',
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
const mockStatusDataHealthy: SystemStatusData = {
  overall: {
    status: 'healthy',
    uptime: '15d 8h 32m',
    lastCheck: new Date().toISOString(),
    responseTime: 145,
  },
  services: {
    api: {
      status: 'healthy',
      responseTime: 89,
      lastCheck: new Date().toISOString(),
      uptime: '15d 8h 32m',
      version: '2.1.4',
      endpoint: '/api/health',
    },
    glpi: {
      status: 'healthy',
      responseTime: 234,
      lastCheck: new Date().toISOString(),
      uptime: '15d 8h 32m',
      version: '10.0.7',
      endpoint: '/glpi/status',
    },
  },
  metrics: {
    totalRequests: 15847,
    errorRate: 0.2,
    avgResponseTime: 156,
    activeConnections: 23,
  },
  alerts: [],
};

const mockStatusDataWarning: SystemStatusData = {
  overall: {
    status: 'warning',
    uptime: '2d 14h 18m',
    lastCheck: new Date().toISOString(),
    responseTime: 892,
  },
  services: {
    api: {
      status: 'healthy',
      responseTime: 156,
      lastCheck: new Date().toISOString(),
      uptime: '2d 14h 18m',
      version: '2.1.4',
      endpoint: '/api/health',
    },
    glpi: {
      status: 'warning',
      responseTime: 1245,
      lastCheck: new Date().toISOString(),
      uptime: '2d 14h 18m',
      version: '10.0.7',
      endpoint: '/glpi/status',
    },
  },
  metrics: {
    totalRequests: 8934,
    errorRate: 2.8,
    avgResponseTime: 701,
    activeConnections: 67,
  },
  alerts: [
    {
      id: '1',
      type: 'warning',
      message: 'GLPI response time above threshold (1.2s)',
      timestamp: new Date().toISOString(),
    },
    {
      id: '2',
      type: 'warning',
      message: 'Error rate increased to 2.8%',
      timestamp: new Date(Date.now() - 300000).toISOString(), // 5 min ago
    },
  ],
};

const mockStatusDataCritical: SystemStatusData = {
  overall: {
    status: 'critical',
    uptime: '0d 2h 15m',
    lastCheck: new Date().toISOString(),
    responseTime: 0,
  },
  services: {
    api: {
      status: 'critical',
      responseTime: 0,
      lastCheck: new Date().toISOString(),
      uptime: '0d 2h 15m',
      version: '2.1.4',
      endpoint: '/api/health',
    },
    glpi: {
      status: 'critical',
      responseTime: 0,
      lastCheck: new Date().toISOString(),
      uptime: '0d 2h 15m',
      version: '10.0.7',
      endpoint: '/glpi/status',
    },
  },
  metrics: {
    totalRequests: 0,
    errorRate: 100,
    avgResponseTime: 0,
    activeConnections: 0,
  },
  alerts: [
    {
      id: '1',
      type: 'critical',
      message: 'API service is down',
      timestamp: new Date().toISOString(),
    },
    {
      id: '2',
      type: 'critical',
      message: 'GLPI service is unreachable',
      timestamp: new Date(Date.now() - 60000).toISOString(), // 1 min ago
    },
    {
      id: '3',
      type: 'critical',
      message: 'Database connection failed',
      timestamp: new Date(Date.now() - 120000).toISOString(), // 2 min ago
    },
  ],
};

const mockStatusDataMaintenance: SystemStatusData = {
  overall: {
    status: 'maintenance',
    uptime: '0d 0h 5m',
    lastCheck: new Date().toISOString(),
    responseTime: 0,
  },
  services: {
    api: {
      status: 'maintenance',
      responseTime: 0,
      lastCheck: new Date().toISOString(),
      uptime: '0d 0h 5m',
      version: '2.1.4',
      endpoint: '/api/health',
    },
    glpi: {
      status: 'maintenance',
      responseTime: 0,
      lastCheck: new Date().toISOString(),
      uptime: '0d 0h 5m',
      version: '10.0.7',
      endpoint: '/glpi/status',
    },
  },
  metrics: {
    totalRequests: 0,
    errorRate: 0,
    avgResponseTime: 0,
    activeConnections: 0,
  },
  alerts: [
    {
      id: '1',
      type: 'info',
      message: 'Sistema em manutenção programada',
      timestamp: new Date().toISOString(),
    },
    {
      id: '2',
      type: 'info',
      message: 'Previsão de retorno: 30 minutos',
      timestamp: new Date().toISOString(),
    },
  ],
};

const emptyStatusData: SystemStatusData = {
  overall: {
    status: 'unknown',
    uptime: '0d 0h 0m',
    lastCheck: '',
    responseTime: 0,
  },
  services: {
    api: {
      status: 'unknown',
      responseTime: 0,
      lastCheck: '',
      uptime: '0d 0h 0m',
      version: '',
      endpoint: '',
    },
    glpi: {
      status: 'unknown',
      responseTime: 0,
      lastCheck: '',
      uptime: '0d 0h 0m',
      version: '',
      endpoint: '',
    },
  },
  metrics: {
    totalRequests: 0,
    errorRate: 0,
    avgResponseTime: 0,
    activeConnections: 0,
  },
  alerts: [],
};

export const Healthy: Story = {
  args: {
    data: mockStatusDataHealthy,
    isLoading: false,
    hasError: false,
    showCompact: false,
  },
  parameters: {
    docs: {
      storyDescription: 'Sistema funcionando normalmente com todos os serviços saudáveis.',
    },
  },
};

export const Warning: Story = {
  args: {
    data: mockStatusDataWarning,
    isLoading: false,
    hasError: false,
    showCompact: false,
  },
  parameters: {
    docs: {
      storyDescription: 'Sistema com alertas de performance, mas ainda operacional.',
    },
  },
};

export const Critical: Story = {
  args: {
    data: mockStatusDataCritical,
    isLoading: false,
    hasError: false,
    showCompact: false,
  },
  parameters: {
    docs: {
      storyDescription: 'Sistema com falhas críticas nos serviços principais.',
    },
  },
};

export const Maintenance: Story = {
  args: {
    data: mockStatusDataMaintenance,
    isLoading: false,
    hasError: false,
    showCompact: false,
  },
  parameters: {
    docs: {
      storyDescription: 'Sistema em manutenção programada.',
    },
  },
};

export const Compact: Story = {
  args: {
    data: mockStatusDataHealthy,
    isLoading: false,
    hasError: false,
    showCompact: true,
  },
  parameters: {
    docs: {
      storyDescription: 'Versão compacta do status do sistema.',
    },
  },
};

export const CompactWarning: Story = {
  args: {
    data: mockStatusDataWarning,
    isLoading: false,
    hasError: false,
    showCompact: true,
  },
  parameters: {
    docs: {
      storyDescription: 'Versão compacta com alertas de warning.',
    },
  },
};

export const Loading: Story = {
  args: {
    data: emptyStatusData,
    isLoading: true,
    hasError: false,
    showCompact: false,
  },
  parameters: {
    docs: {
      storyDescription: 'Estado de carregamento do status do sistema.',
    },
  },
};

export const Error: Story = {
  args: {
    data: emptyStatusData,
    isLoading: false,
    hasError: true,
    showCompact: false,
  },
  parameters: {
    docs: {
      storyDescription: 'Estado de erro ao carregar o status do sistema.',
    },
  },
};

// Stories específicas para CompactSystemStatus
const CompactMeta: Meta<typeof CompactSystemStatus> = {
  title: 'Dashboard/CompactSystemStatus',
  component: CompactSystemStatus,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
};

export const CompactHealthy: StoryObj<typeof CompactSystemStatus> = {
  args: {
    data: mockStatusDataHealthy,
    isLoading: false,
    hasError: false,
  },
  parameters: {
    docs: {
      storyDescription: 'Versão compacta independente com sistema saudável.',
    },
  },
};

export const CompactCritical: StoryObj<typeof CompactSystemStatus> = {
  args: {
    data: mockStatusDataCritical,
    isLoading: false,
    hasError: false,
  },
};

export const CompactLoading: StoryObj<typeof CompactSystemStatus> = {
  args: {
    data: emptyStatusData,
    isLoading: true,
    hasError: false,
  },
};

// Story para demonstrar todos os estados lado a lado
export const AllStates: Story = {
  render: () => (
    <div className="space-y-8">
      <div>
        <h3 className="text-lg font-semibold mb-4 text-green-600">Sistema Saudável</h3>
        <SystemStatusComponent data={mockStatusDataHealthy} />
      </div>
      <div>
        <h3 className="text-lg font-semibold mb-4 text-yellow-600">Sistema com Alertas</h3>
        <SystemStatusComponent data={mockStatusDataWarning} />
      </div>
      <div>
        <h3 className="text-lg font-semibold mb-4 text-red-600">Sistema Crítico</h3>
        <SystemStatusComponent data={mockStatusDataCritical} />
      </div>
      <div>
        <h3 className="text-lg font-semibold mb-4 text-blue-600">Sistema em Manutenção</h3>
        <SystemStatusComponent data={mockStatusDataMaintenance} />
      </div>
    </div>
  ),
  parameters: {
    docs: {
      storyDescription: 'Comparação entre todos os estados possíveis do sistema.',
    },
  },
};

// Story para demonstrar versões compacta e completa
export const CompactVsFull: Story = {
  render: () => (
    <div className="space-y-8">
      <div>
        <h3 className="text-lg font-semibold mb-4">Versão Completa</h3>
        <SystemStatusComponent data={mockStatusDataWarning} showCompact={false} />
      </div>
      <div>
        <h3 className="text-lg font-semibold mb-4">Versão Compacta</h3>
        <CompactSystemStatus data={mockStatusDataWarning} />
      </div>
    </div>
  ),
  parameters: {
    docs: {
      storyDescription: 'Comparação entre as versões completa e compacta.',
    },
  },
};

// Story para demonstrar responsividade
export const Responsive: Story = {
  args: {
    data: mockStatusDataWarning,
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
      storyDescription: 'Status do sistema responsivo para diferentes tamanhos de tela.',
    },
  },
};

// Story para demonstrar diferentes tempos de resposta
export const ResponseTimeVariations: Story = {
  render: () => {
    const fastResponse: SystemStatusData = {
      ...mockStatusDataHealthy,
      overall: { ...mockStatusDataHealthy.overall, responseTime: 45 },
      services: {
        api: { ...mockStatusDataHealthy.services.api, responseTime: 32 },
        glpi: { ...mockStatusDataHealthy.services.glpi, responseTime: 58 },
      },
    };

    const slowResponse: SystemStatusData = {
      ...mockStatusDataWarning,
      overall: { ...mockStatusDataWarning.overall, responseTime: 2340 },
      services: {
        api: { ...mockStatusDataWarning.services.api, responseTime: 1890 },
        glpi: { ...mockStatusDataWarning.services.glpi, responseTime: 2790 },
      },
    };

    return (
      <div className="space-y-8">
        <div>
          <h3 className="text-lg font-semibold mb-4 text-green-600">Resposta Rápida (&lt;100ms)</h3>
          <CompactSystemStatus data={fastResponse} />
        </div>
        <div>
          <h3 className="text-lg font-semibold mb-4 text-yellow-600">Resposta Normal (100-1000ms)</h3>
          <CompactSystemStatus data={mockStatusDataHealthy} />
        </div>
        <div>
          <h3 className="text-lg font-semibold mb-4 text-red-600">Resposta Lenta (&gt;2000ms)</h3>
          <CompactSystemStatus data={slowResponse} />
        </div>
      </div>
    );
  },
  parameters: {
    docs: {
      storyDescription: 'Demonstração de diferentes tempos de resposta e seus indicadores visuais.',
    },
  },
};

// Exportar stories do CompactSystemStatus
export {
  CompactHealthy,
  CompactCritical,
  CompactLoading,
};