import type { Meta, StoryObj } from '@storybook/react';
import { RankingTable } from '../components/dashboard/RankingTable';
import React from 'react';

// Mock data para diferentes estados
const mockTechnicians = [
  { id: '1', name: 'João Silva', level: 'N4', total: 45, rank: 1 },
  { id: '2', name: 'Maria Santos', level: 'N3', total: 38, rank: 2 },
  { id: '3', name: 'Pedro Costa', level: 'N3', total: 32, rank: 3 },
  { id: '4', name: 'Ana Oliveira', level: 'N2', total: 28, rank: 4 },
  { id: '5', name: 'Carlos Ferreira', level: 'N2', total: 25, rank: 5 },
  { id: '6', name: 'Lucia Rodrigues', level: 'N1', total: 22, rank: 6 },
  { id: '7', name: 'Roberto Lima', level: 'N1', total: 18, rank: 7 },
  { id: '8', name: 'Fernanda Alves', level: 'N1', total: 15, rank: 8 }
];

const meta: Meta<typeof RankingTable> = {
  title: 'Dashboard/RankingTable',
  component: RankingTable,
  decorators: [
    (Story) => (
      <div style={{ padding: '20px', backgroundColor: '#f5f5f5', minHeight: '400px' }}>
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof RankingTable>;

export const Ok: Story = {
  args: {
    data: mockTechnicians,
    title: 'Ranking de Técnicos',
  },
};

export const Loading: Story = {
  args: {
    data: [],
    title: 'Ranking de Técnicos',
  },
  decorators: [
    (Story) => (
      <div style={{ padding: '20px', backgroundColor: '#f5f5f5', minHeight: '400px' }}>
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '200px' }}>
          <div>Carregando ranking...</div>
        </div>
      </div>
    ),
  ],
};

export const Empty: Story = {
  args: {
    data: [],
    title: 'Ranking de Técnicos',
  },
  decorators: [
    (Story) => (
      <div style={{ padding: '20px', backgroundColor: '#f5f5f5', minHeight: '400px' }}>
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '200px' }}>
          <div>Nenhum técnico encontrado</div>
        </div>
      </div>
    ),
  ],
};

export const Error: Story = {
  args: {
    data: [],
    title: 'Ranking de Técnicos',
  },
  decorators: [
    (Story) => (
      <div style={{ padding: '20px', backgroundColor: '#f5f5f5', minHeight: '400px' }}>
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '200px', color: 'red' }}>
          <div>Erro ao carregar ranking dos técnicos</div>
        </div>
      </div>
    ),
  ],
};
