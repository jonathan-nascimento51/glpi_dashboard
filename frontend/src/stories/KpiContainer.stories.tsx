import type { Meta, StoryObj } from '@storybook/react';
import { KpiContainer } from '../components/KpiContainer';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';

// Mock do hook useKpisRaw
const mockUseKpisRaw = {
  ok: {
    data: [
      {
        level: 'N1',
        totals: { total: 45, open: 12, inProgress: 18, closed: 15 }
      },
      {
        level: 'N2', 
        totals: { total: 32, open: 8, inProgress: 14, closed: 10 }
      },
      {
        level: 'N3',
        totals: { total: 28, open: 5, inProgress: 12, closed: 11 }
      },
      {
        level: 'N4',
        totals: { total: 15, open: 2, inProgress: 6, closed: 7 }
      }
    ],
    loading: false,
    error: null,
    useV2: true
  },
  loading: {
    data: null,
    loading: true,
    error: null,
    useV2: false
  },
  empty: {
    data: [],
    loading: false,
    error: null,
    useV2: true
  },
  error: {
    data: null,
    loading: false,
    error: 'Falha ao carregar dados dos KPIs',
    useV2: false
  }
};

// Wrapper para prover QueryClient
const QueryWrapper = ({ children }: { children: React.ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        refetchOnWindowFocus: false,
      },
    },
  });
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

const meta: Meta<typeof KpiContainer> = {
  title: 'Dashboard/KpiContainer',
  component: KpiContainer,
  decorators: [
    (Story) => (
      <QueryWrapper>
        <div style={{ padding: '20px', backgroundColor: '#f5f5f5' }}>
          <Story />
        </div>
      </QueryWrapper>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof KpiContainer>;

export const Ok: Story = {
  parameters: {
    mockData: [
      {
        url: '/api/kpis/raw',
        method: 'GET',
        status: 200,
        response: mockUseKpisRaw.ok.data,
      },
    ],
  },
};

export const Loading: Story = {
  parameters: {
    mockData: [
      {
        url: '/api/kpis/raw',
        method: 'GET',
        delay: 2000,
        status: 200,
        response: mockUseKpisRaw.ok.data,
      },
    ],
  },
};

export const Empty: Story = {
  parameters: {
    mockData: [
      {
        url: '/api/kpis/raw',
        method: 'GET',
        status: 200,
        response: [],
      },
    ],
  },
};

export const Error: Story = {
  parameters: {
    mockData: [
      {
        url: '/api/kpis/raw',
        method: 'GET',
        status: 500,
        response: { error: 'Falha ao carregar dados dos KPIs' },
      },
    ],
  },
};
