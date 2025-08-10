import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { KpiCard } from '../../components/KpiCard';

describe('KpiCard', () => {
  const defaultProps = {
    title: 'N1',
    total: 100,
    open: 25,
    inProgress: 30,
    closed: 45
  };

  it('deve renderizar corretamente no estado normal', () => {
    render(<KpiCard {...defaultProps} />);
    
    expect(screen.getByText('N1')).toBeInTheDocument();
    expect(screen.getByText('Total: 100')).toBeInTheDocument();
    expect(screen.getByText('Abertos: 25')).toBeInTheDocument();
    expect(screen.getByText('Em Andamento: 30')).toBeInTheDocument();
    expect(screen.getByText('Fechados: 45')).toBeInTheDocument();
  });

  it('deve renderizar estado de loading', () => {
    render(<KpiCard {...defaultProps} loading={true} />);
    
    expect(screen.getByText('Carregando...')).toBeInTheDocument();
    expect(screen.queryByText('N1')).not.toBeInTheDocument();
  });

  it('deve renderizar estado de erro', () => {
    const errorMessage = 'Erro ao carregar dados';
    render(<KpiCard {...defaultProps} error={errorMessage} />);
    
    expect(screen.getByText(`Erro: ${errorMessage}`)).toBeInTheDocument();
    expect(screen.queryByText('N1')).not.toBeInTheDocument();
  });

  it('deve priorizar loading sobre erro', () => {
    render(<KpiCard {...defaultProps} loading={true} error="Algum erro" />);
    
    expect(screen.getByText('Carregando...')).toBeInTheDocument();
    expect(screen.queryByText('Erro:')).not.toBeInTheDocument();
  });

  it('deve renderizar com valores zero', () => {
    const propsWithZeros = {
      title: 'N2',
      total: 0,
      open: 0,
      inProgress: 0,
      closed: 0
    };
    
    render(<KpiCard {...propsWithZeros} />);
    
    expect(screen.getByText('N2')).toBeInTheDocument();
    expect(screen.getByText('Total: 0')).toBeInTheDocument();
    expect(screen.getByText('Abertos: 0')).toBeInTheDocument();
    expect(screen.getByText('Em Andamento: 0')).toBeInTheDocument();
    expect(screen.getByText('Fechados: 0')).toBeInTheDocument();
  });

  it('deve renderizar com números grandes', () => {
    const propsWithLargeNumbers = {
      title: 'N3',
      total: 9999,
      open: 2500,
      inProgress: 3000,
      closed: 4499
    };
    
    render(<KpiCard {...propsWithLargeNumbers} />);
    
    expect(screen.getByText('Total: 9999')).toBeInTheDocument();
    expect(screen.getByText('Abertos: 2500')).toBeInTheDocument();
    expect(screen.getByText('Em Andamento: 3000')).toBeInTheDocument();
    expect(screen.getByText('Fechados: 4499')).toBeInTheDocument();
  });

  it('deve aplicar classes CSS corretas', () => {
    const { container } = render(<KpiCard {...defaultProps} />);
    const cardElement = container.firstChild as HTMLElement;
    
    expect(cardElement).toHaveClass('p-4', 'border', 'rounded');
  });

  it('deve aplicar classes CSS corretas no estado de loading', () => {
    const { container } = render(<KpiCard {...defaultProps} loading={true} />);
    const loadingElement = container.firstChild as HTMLElement;
    
    expect(loadingElement).toHaveClass('p-4', 'border', 'rounded');
  });

  it('deve aplicar classes CSS corretas no estado de erro', () => {
    const { container } = render(<KpiCard {...defaultProps} error="Erro teste" />);
    const errorElement = container.firstChild as HTMLElement;
    
    expect(errorElement).toHaveClass('p-4', 'border', 'rounded', 'text-red-600');
  });

  it('deve renderizar título personalizado', () => {
    const customProps = {
      ...defaultProps,
      title: 'Nível Personalizado'
    };
    
    render(<KpiCard {...customProps} />);
    
    expect(screen.getByText('Nível Personalizado')).toBeInTheDocument();
  });

  it('deve renderizar sem erro quando error é null', () => {
    render(<KpiCard {...defaultProps} error={null} />);
    
    expect(screen.getByText('N1')).toBeInTheDocument();
    expect(screen.queryByText('Erro:')).not.toBeInTheDocument();
  });

  it('deve renderizar sem loading quando loading é false', () => {
    render(<KpiCard {...defaultProps} loading={false} />);
    
    expect(screen.getByText('N1')).toBeInTheDocument();
    expect(screen.queryByText('Carregando...')).not.toBeInTheDocument();
  });
});
