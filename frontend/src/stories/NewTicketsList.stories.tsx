import type { Meta, StoryObj } from '@storybook/react';
import { NewTicketsList } from '../components/dashboard/NewTicketsList';
import React from 'react';

// Mock data para diferentes estados
const mockTickets = [
  {
    id: '1',
    title: 'Sistema de email não funciona',
    priority: 'Crítica',
    status: 'Novo',
    requester: 'João Silva',
    created_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(), // 30 min atrás
    category: 'Email'
  },
  {
    id: '2', 
    title: 'Impressora não imprime',
    priority: 'Alta',
    status: 'Em Andamento',
    requester: 'Maria Santos',
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(), // 2h atrás
    category: 'Hardware'
  },
  {
    id: '3',
    title: 'Acesso negado ao sistema',
    priority: 'Média',
    status: 'Novo',
    requester: 'Pedro Costa',
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 4).toISOString(), // 4h atrás
    category: 'Acesso'
  },
  {
    id: '4',
    title: 'Computador lento',
    priority: 'Baixa',
    status: 'Aguardando',
    requester: 'Ana Oliveira',
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 8).toISOString(), // 8h atrás
    category: 'Performance'
  }
];

const meta: Meta<typeof NewTicketsList> = {
  title: 'Dashboard/NewTicketsList',
  component: NewTicketsList,
  decorators: [
    (Story) => (
      <div style={{ padding: '20px', backgroundColor: '#f5f5f5', minHeight: '500px' }}>
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof NewTicketsList>;

export const Ok: Story = {
  args: {
    limit: 10,
  },
  parameters: {
    mockData: [
      {
        url: '/api/tickets/new',
        method: 'GET',
        status: 200,
        response: { tickets: mockTickets, total: mockTickets.length },
      },
    ],
  },
};

export const Loading: Story = {
  args: {
    limit: 10,
  },
  parameters: {
    mockData: [
      {
        url: '/api/tickets/new',
        method: 'GET',
        delay: 2000,
        status: 200,
        response: { tickets: mockTickets, total: mockTickets.length },
      },
    ],
  },
};

export const Empty: Story = {
  args: {
    limit: 10,
  },
  parameters: {
    mockData: [
      {
        url: '/api/tickets/new',
        method: 'GET',
        status: 200,
        response: { tickets: [], total: 0 },
      },
    ],
  },
};

export const Error: Story = {
  args: {
    limit: 10,
  },
  parameters: {
    mockData: [
      {
        url: '/api/tickets/new',
        method: 'GET',
        status: 500,
        response: { error: 'Falha ao carregar tickets' },
      },
    ],
  },
};
