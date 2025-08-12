import { render, screen } from '@testing-library/react';
import { RankingTable } from '../RankingTable';
import { TechnicianRanking } from '@/types';

// Mock data para testes
const mockRankingData: TechnicianRanking[] = [
  {
    id: '1',
    name: 'João Silva',
    level: 'Sênior',
    total: 25,
    rank: 1
  },
  {
    id: '2',
    name: 'Maria Santos',
    level: 'Pleno',
    total: 20,
    rank: 2
  },
  {
    id: '3',
    name: 'Pedro Costa',
    level: 'Júnior',
    total: 15,
    rank: 3
  }
];

const mockFilters = {
  start_date: '2025-01-01',
  end_date: '2025-12-31',
  level: 'Sênior',
  limit: 10
};

describe('RankingTable', () => {
  it('deve renderizar o título corretamente', () => {
    render(
      <RankingTable 
        data={mockRankingData} 
        title="Ranking de Técnicos" 
      />
    );
    
    expect(screen.getByText('Ranking de Técnicos')).toBeInTheDocument();
  });

  it('deve exibir os dados dos técnicos corretamente', () => {
    render(
      <RankingTable 
        data={mockRankingData} 
        title="Ranking de Técnicos" 
      />
    );
    
    // Verifica nomes formatados (primeiro nome + inicial do último)
    expect(screen.getByText('João S.')).toBeInTheDocument();
    expect(screen.getByText('Maria S.')).toBeInTheDocument();
    expect(screen.getByText('Pedro C.')).toBeInTheDocument();
    // Verifica totais de tickets
    expect(screen.getByText('25')).toBeInTheDocument();
    expect(screen.getByText('20')).toBeInTheDocument();
    expect(screen.getByText('15')).toBeInTheDocument();
  });

  it('deve exibir os filtros aplicados corretamente', () => {
    const filters = {
      start_date: '2024-01-01',
      end_date: '2024-01-31',
      level: 'N1'
    };

    render(
      <RankingTable 
        data={mockRankingData} 
        title="Ranking de Técnicos"
        filters={filters}
        className="test-class"
      />
    );

    expect(screen.getByText('Filtros aplicados:')).toBeInTheDocument();
    expect(screen.getByText(/De:/)).toBeInTheDocument();
    expect(screen.getByText(/Até:/)).toBeInTheDocument();
    expect(screen.getByText(/Nível:/)).toBeInTheDocument();
  });

  it('deve exibir filtros parciais quando alguns valores estão ausentes', () => {
    const filters = {
      start_date: '2024-01-01',
      level: 'N2'
      // end_date ausente
    };

    render(
      <RankingTable 
        data={mockRankingData} 
        title="Ranking de Técnicos"
        filters={filters}
        className="test-class"
      />
    );

    expect(screen.getByText('Filtros aplicados:')).toBeInTheDocument();
    expect(screen.getByText(/De:/)).toBeInTheDocument();
    expect(screen.getByText(/Nível:/)).toBeInTheDocument();
    expect(screen.queryByText(/Até:/)).not.toBeInTheDocument();
  });

  it('não deve exibir seção de filtros quando não há filtros', () => {
    render(
      <RankingTable 
        data={mockRankingData} 
        title="Ranking de Técnicos"
      />
    );
    
    expect(screen.queryByText(/Filtros aplicados:/)).not.toBeInTheDocument();
  });

  it('não deve exibir seção de filtros quando filtros estão vazios', () => {
    const emptyFilters = {};
    
    render(
      <RankingTable 
        data={mockRankingData} 
        title="Ranking de Técnicos"
        filters={emptyFilters}
      />
    );
    
    expect(screen.queryByText(/Filtros aplicados:/)).not.toBeInTheDocument();
  });

  it('deve renderizar sem dados', () => {
    render(
      <RankingTable 
        data={[]} 
        title="Ranking de Técnicos" 
      />
    );
    
    expect(screen.getByText(/Ranking de Técnicos/)).toBeInTheDocument();
  });

  it('deve aplicar classes CSS corretamente', () => {
    const { container } = render(
      <RankingTable 
        data={mockRankingData} 
        title="Ranking de Técnicos"
        className="custom-class"
      />
    );
    
    const tableContainer = container.querySelector('.custom-class');
    expect(tableContainer).toBeInTheDocument();
  });

  it('deve renderizar o componente sem erros', () => {
    render(
      <RankingTable 
        data={mockRankingData} 
        className="test-class"
      />
    );

    // Verifica se o componente renderiza sem erros
    expect(screen.getByText('Ranking de Técnicos')).toBeInTheDocument();
  });
});