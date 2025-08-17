import { render, screen } from '@testing-library/react';
import { ModernDashboard } from '../ModernDashboard';
import { MetricsData, TechnicianRanking } from '@/types';

// Mock do RankingTable para verificar se os props são passados corretamente
jest.mock('../RankingTable', () => ({
  RankingTable: ({ data, title, filters }: any) => (
    <div data-testid='ranking-table'>
      <h2>{title}</h2>
      <div data-testid='ranking-data'>{JSON.stringify(data)}</div>
      {filters && <div data-testid='ranking-filters'>{JSON.stringify(filters)}</div>}
    </div>
  ),
}));

// Mock data para testes
const mockMetrics: MetricsData = {
  total_tickets: 100,
  open_tickets: 25,
  closed_tickets: 75,
  pending_tickets: 10,
  in_progress_tickets: 15,
  tendencias: {
    total_tickets: { valor: 5, tipo: 'aumento' },
    open_tickets: { valor: 2, tipo: 'aumento' },
    closed_tickets: { valor: 3, tipo: 'aumento' },
  },
};

const mockTechnicianRanking: TechnicianRanking[] = [
  {
    id: 1,
    name: 'João Silva',
    level: 'Sênior',
    tickets_count: 25,
    rank: 1,
  },
  {
    id: 2,
    name: 'Maria Santos',
    level: 'Pleno',
    tickets_count: 20,
    rank: 2,
  },
];

const mockFilters = {
  start_date: '2025-01-01',
  end_date: '2025-12-31',
  level: 'Sênior',
  limit: 10,
};

describe('ModernDashboard', () => {
  it('deve renderizar sem erros', () => {
    render(<ModernDashboard metrics={mockMetrics} technicianRanking={mockTechnicianRanking} />);

    expect(screen.getByTestId('ranking-table')).toBeInTheDocument();
  });

  it('deve passar filtros para o RankingTable quando fornecidos', () => {
    render(
      <ModernDashboard
        metrics={mockMetrics}
        technicianRanking={mockTechnicianRanking}
        filters={mockFilters}
      />
    );

    const filtersElement = screen.getByTestId('ranking-filters');
    expect(filtersElement).toBeInTheDocument();
    expect(filtersElement).toHaveTextContent(JSON.stringify(mockFilters));
  });

  it('não deve passar filtros quando não fornecidos', () => {
    render(<ModernDashboard metrics={mockMetrics} technicianRanking={mockTechnicianRanking} />);

    expect(screen.queryByTestId('ranking-filters')).not.toBeInTheDocument();
  });

  it('deve passar dados de ranking corretamente', () => {
    render(<ModernDashboard metrics={mockMetrics} technicianRanking={mockTechnicianRanking} />);

    const dataElement = screen.getByTestId('ranking-data');
    expect(dataElement).toBeInTheDocument();
    // Verifica se os dados foram processados e passados
    expect(dataElement.textContent).toContain('João Silva');
    expect(dataElement.textContent).toContain('Maria Santos');
  });

  it('deve lidar com dados vazios de ranking', () => {
    render(<ModernDashboard metrics={mockMetrics} technicianRanking={[]} />);

    const dataElement = screen.getByTestId('ranking-data');
    expect(dataElement).toBeInTheDocument();
    expect(dataElement.textContent).toBe('[]');
  });

  it('deve aplicar className personalizada', () => {
    const { container } = render(
      <ModernDashboard
        metrics={mockMetrics}
        technicianRanking={mockTechnicianRanking}
        className='custom-dashboard-class'
      />
    );

    expect(container.firstChild).toHaveClass('custom-dashboard-class');
  });

  it('deve mostrar estado de loading quando isLoading é true', () => {
    render(
      <ModernDashboard
        metrics={mockMetrics}
        technicianRanking={mockTechnicianRanking}
        isLoading={true}
      />
    );

    // Verifica se há indicadores de loading
    expect(document.querySelector('.animate-pulse')).toBeInTheDocument();
  });

  it('deve processar dados de ranking com níveis corretos', () => {
    const rankingWithLevels: TechnicianRanking[] = [
      {
        id: 1,
        name: 'João Silva',
        level: 'Sênior',
        tickets_count: 25,
        rank: 1,
      },
      {
        id: 2,
        name: 'Maria Santos',
        level: 'Pleno',
        tickets_count: 20,
        rank: 2,
      },
      {
        id: 3,
        name: 'Pedro Costa',
        level: 'Júnior',
        tickets_count: 15,
        rank: 3,
      },
    ];

    render(<ModernDashboard metrics={mockMetrics} technicianRanking={rankingWithLevels} />);

    const dataElement = screen.getByTestId('ranking-data');
    expect(dataElement.textContent).toContain('Sênior');
    expect(dataElement.textContent).toContain('Pleno');
    expect(dataElement.textContent).toContain('Júnior');
  });
});
