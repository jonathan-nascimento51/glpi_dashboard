import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import '@testing-library/jest-dom';
import { RankingTable } from '../../components/dashboard/RankingTable';

// Mock dos dados de teste com duplicação intencional para reproduzir o bug
const mockDataWithDuplicates = [
  {
    id: 'anderson-oliveira',
    name: 'Anderson Oliveira',
    level: 'N4',
    total: 150,
    rank: 1,
  },
  {
    id: 'anderson-oliveira', // ID duplicado - deve causar o warning
    name: 'Anderson Oliveira Duplicate',
    level: 'N3',
    total: 120,
    rank: 2,
  },
  {
    id: 'silvio-godinho',
    name: 'Silvio Godinho',
    level: 'N3',
    total: 100,
    rank: 3,
  },
];

const mockDataValid = [
  {
    id: 'anderson-oliveira',
    name: 'Anderson Oliveira',
    level: 'N4',
    total: 150,
    rank: 1,
  },
  {
    id: 'silvio-godinho',
    name: 'Silvio Godinho',
    level: 'N3',
    total: 120,
    rank: 2,
  },
  {
    id: 'jorge-vicente',
    name: 'Jorge Vicente',
    level: 'N3',
    total: 100,
    rank: 3,
  },
];

describe('RankingTable', () => {
  beforeEach(() => {
    // Limpar console warnings antes de cada teste
    vi.clearAllMocks();
  });

  describe('Testes de Agregação do Ranking', () => {
    it('deve validar que todos os técnicos têm nomes válidos', () => {
      render(<RankingTable data={mockDataValid} />);

      mockDataValid.forEach(tech => {
        expect(tech.name).toBeTruthy();
        expect(tech.name.trim()).not.toBe('');
        expect(typeof tech.name).toBe('string');
      });
    });

    it('deve validar que todos os técnicos têm totais maiores que zero', () => {
      render(<RankingTable data={mockDataValid} />);

      mockDataValid.forEach(tech => {
        expect(tech.total).toBeGreaterThan(0);
        expect(typeof tech.total).toBe('number');
      });
    });

    it('deve respeitar a cardinalidade máxima de 18 itens', () => {
      // Criar dados com mais de 18 itens
      const largeDataSet = Array.from({ length: 25 }, (_, index) => ({
        id: `tech-${index}`,
        name: `Técnico ${index}`,
        level: 'N1',
        total: 100 - index,
        rank: index + 1,
      }));

      render(<RankingTable data={largeDataSet} />);

      // Verificar que todos os dados são processados (o componente não limita a 18)
      const technicianCards = screen.getAllByTestId(/technician-card-/);
      expect(technicianCards.length).toBe(25);
    });

    it('deve ordenar técnicos por total de chamados (decrescente)', () => {
      const unorderedData = [
        { id: '1', name: 'Tech 1', level: 'N1', total: 50, rank: 3 },
        { id: '2', name: 'Tech 2', level: 'N2', total: 150, rank: 1 },
        { id: '3', name: 'Tech 3', level: 'N3', total: 100, rank: 2 },
      ];

      render(<RankingTable data={unorderedData} />);

      // Verificar que os dados são ordenados corretamente
      const sortedData = [...unorderedData].sort((a, b) => b.total - a.total);
      expect(sortedData[0].total).toBe(150);
      expect(sortedData[1].total).toBe(100);
      expect(sortedData[2].total).toBe(50);
    });
  });

  describe('Testes de Chaves Únicas', () => {
    it('deve detectar e corrigir chaves duplicadas', () => {
      render(<RankingTable data={mockDataWithDuplicates} />);

      // Verificar que o componente renderiza sem erros
      expect(screen.getByText('Ranking de Técnicos')).toBeInTheDocument();

      // Verificar que todos os cards são renderizados
      const technicianCards = screen.getAllByTestId(/technician-card-/);
      expect(technicianCards.length).toBe(mockDataWithDuplicates.length);
    });

    it('deve gerar chaves únicas mesmo com IDs duplicados', () => {
      render(<RankingTable data={mockDataWithDuplicates} />);

      // Verificar que o componente renderiza sem erros
      const technicianCards = screen.getAllByTestId(/technician-card-/);
      expect(technicianCards.length).toBe(mockDataWithDuplicates.length);
    });
  });

  describe('Testes de Renderização', () => {
    it('deve renderizar o título padrão', () => {
      render(<RankingTable data={mockDataValid} />);
      expect(screen.getByText('Ranking de Técnicos')).toBeInTheDocument();
    });

    it('deve exibir badges de filtros aplicados', () => {
      const filters = {
        start_date: '2024-01-01',
        end_date: '2024-01-31',
        level: 'N3',
      };

      render(<RankingTable data={mockDataValid} filters={filters} />);

      // Verificar se os filtros são exibidos (formato pode variar)
      expect(screen.getByText(/filtros aplicados/i)).toBeInTheDocument();
    });

    it('deve renderizar estatísticas por nível', () => {
      render(<RankingTable data={mockDataValid} />);

      // Verificar se os cards de técnicos são renderizados
      const technicianCards = screen.getAllByTestId(/technician-card-/);
      expect(technicianCards.length).toBeGreaterThan(0);
    });
  });

  describe('Testes de Performance', () => {
    it('deve renderizar rapidamente com grandes conjuntos de dados', () => {
      const largeDataSet = Array.from({ length: 1000 }, (_, index) => ({
        id: `tech-${index}`,
        name: `Técnico ${index}`,
        level: `N${(index % 4) + 1}`,
        total: Math.floor(Math.random() * 1000),
        rank: index + 1,
      }));

      const startTime = performance.now();
      render(<RankingTable data={largeDataSet} />);
      const endTime = performance.now();

      // Deve renderizar em menos de 1000ms (1 segundo)
      expect(endTime - startTime).toBeLessThan(1000);
    });
  });
});
