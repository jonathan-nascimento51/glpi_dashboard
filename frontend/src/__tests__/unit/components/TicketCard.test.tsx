import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { TicketCard } from '../../../components/TicketCard';
import { Ticket } from '../../../types/api';

// Mock do framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    span: ({ children, ...props }: any) => <span {...props}>{children}</span>,
  },
  AnimatePresence: ({ children }: any) => children,
}));

// Mock dos ícones
vi.mock('lucide-react', () => ({
  Clock: () => <div data-testid="clock-icon" />,
  User: () => <div data-testid="user-icon" />,
  AlertCircle: () => <div data-testid="alert-icon" />,
  CheckCircle: () => <div data-testid="check-icon" />,
  XCircle: () => <div data-testid="x-icon" />,
  Calendar: () => <div data-testid="calendar-icon" />,
  Tag: () => <div data-testid="tag-icon" />,
}));

const mockTicket: Ticket = {
  id: 1,
  title: 'Problema no sistema',
  description: 'Descrição detalhada do problema',
  status: 'open',
  priority: 'high',
  category: 'Hardware',
  requester: 'João Silva',
  assignee: 'Maria Santos',
  created_at: '2024-01-15T10:30:00Z',
  updated_at: '2024-01-15T14:20:00Z',
  due_date: '2024-01-20T18:00:00Z',
  tags: ['urgente', 'hardware'],
  comments_count: 3,
  attachments_count: 2,
};

describe('TicketCard Component', () => {
  const defaultProps = {
    ticket: mockTicket,
    onClick: vi.fn(),
    onStatusChange: vi.fn(),
    onPriorityChange: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('deve renderizar informações básicas do ticket', () => {
    render(<TicketCard {...defaultProps} />);

    expect(screen.getByText('Problema no sistema')).toBeInTheDocument();
    expect(screen.getByText('Descrição detalhada do problema')).toBeInTheDocument();
    expect(screen.getByText('João Silva')).toBeInTheDocument();
    expect(screen.getByText('Maria Santos')).toBeInTheDocument();
    expect(screen.getByText('Hardware')).toBeInTheDocument();
  });

  it('deve exibir status correto com cores apropriadas', () => {
    const { rerender } = render(<TicketCard {...defaultProps} />);

    // Status aberto
    expect(screen.getByText('Aberto')).toBeInTheDocument();
    expect(screen.getByTestId('alert-icon')).toBeInTheDocument();

    // Status fechado
    const closedTicket = { ...mockTicket, status: 'closed' as const };
    rerender(<TicketCard {...defaultProps} ticket={closedTicket} />);
    expect(screen.getByText('Fechado')).toBeInTheDocument();
    expect(screen.getByTestId('check-icon')).toBeInTheDocument();

    // Status em progresso
    const inProgressTicket = { ...mockTicket, status: 'in_progress' as const };
    rerender(<TicketCard {...defaultProps} ticket={inProgressTicket} />);
    expect(screen.getByText('Em Progresso')).toBeInTheDocument();
    expect(screen.getByTestId('clock-icon')).toBeInTheDocument();
  });

  it('deve exibir prioridade com cores corretas', () => {
    const { rerender } = render(<TicketCard {...defaultProps} />);

    // Prioridade alta
    expect(screen.getByText('Alta')).toBeInTheDocument();

    // Prioridade média
    const mediumTicket = { ...mockTicket, priority: 'medium' as const };
    rerender(<TicketCard {...defaultProps} ticket={mediumTicket} />);
    expect(screen.getByText('Média')).toBeInTheDocument();

    // Prioridade baixa
    const lowTicket = { ...mockTicket, priority: 'low' as const };
    rerender(<TicketCard {...defaultProps} ticket={lowTicket} />);
    expect(screen.getByText('Baixa')).toBeInTheDocument();
  });

  it('deve formatar datas corretamente', () => {
    render(<TicketCard {...defaultProps} />);

    // Verifica se as datas estão formatadas
    expect(screen.getByText(/15\/01\/2024/)).toBeInTheDocument();
    expect(screen.getByText(/20\/01\/2024/)).toBeInTheDocument();
  });

  it('deve exibir tags quando fornecidas', () => {
    render(<TicketCard {...defaultProps} />);

    expect(screen.getByText('urgente')).toBeInTheDocument();
    expect(screen.getByText('hardware')).toBeInTheDocument();
  });

  it('deve exibir contadores de comentários e anexos', () => {
    render(<TicketCard {...defaultProps} />);

    expect(screen.getByText('3 comentários')).toBeInTheDocument();
    expect(screen.getByText('2 anexos')).toBeInTheDocument();
  });

  it('deve chamar onClick quando clicado', () => {
    const onClickMock = vi.fn();
    render(<TicketCard {...defaultProps} onClick={onClickMock} />);

    fireEvent.click(screen.getByRole('article'));
    expect(onClickMock).toHaveBeenCalledWith(mockTicket);
  });

  it('deve permitir mudança de status', async () => {
    const onStatusChangeMock = vi.fn();
    render(<TicketCard {...defaultProps} onStatusChange={onStatusChangeMock} />);

    const statusButton = screen.getByText('Aberto');
    fireEvent.click(statusButton);

    // Verifica se o menu de status aparece
    await waitFor(() => {
      expect(screen.getByText('Em Progresso')).toBeInTheDocument();
      expect(screen.getByText('Fechado')).toBeInTheDocument();
    });

    // Clica em uma nova opção
    fireEvent.click(screen.getByText('Em Progresso'));
    expect(onStatusChangeMock).toHaveBeenCalledWith(mockTicket.id, 'in_progress');
  });

  it('deve permitir mudança de prioridade', async () => {
    const onPriorityChangeMock = vi.fn();
    render(<TicketCard {...defaultProps} onPriorityChange={onPriorityChangeMock} />);

    const priorityButton = screen.getByText('Alta');
    fireEvent.click(priorityButton);

    // Verifica se o menu de prioridade aparece
    await waitFor(() => {
      expect(screen.getByText('Média')).toBeInTheDocument();
      expect(screen.getByText('Baixa')).toBeInTheDocument();
    });

    // Clica em uma nova opção
    fireEvent.click(screen.getByText('Baixa'));
    expect(onPriorityChangeMock).toHaveBeenCalledWith(mockTicket.id, 'low');
  });

  it('deve exibir indicador de ticket vencido', () => {
    const overdueTicket = {
      ...mockTicket,
      due_date: '2024-01-10T18:00:00Z', // Data no passado
    };
    
    render(<TicketCard {...defaultProps} ticket={overdueTicket} />);
    
    expect(screen.getByText(/Vencido/)).toBeInTheDocument();
  });

  it('deve exibir indicador de ticket próximo ao vencimento', () => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    const dueSoonTicket = {
      ...mockTicket,
      due_date: tomorrow.toISOString(),
    };
    
    render(<TicketCard {...defaultProps} ticket={dueSoonTicket} />);
    
    expect(screen.getByText(/Vence em/)).toBeInTheDocument();
  });

  it('deve lidar com ticket sem assignee', () => {
    const unassignedTicket = {
      ...mockTicket,
      assignee: null,
    };
    
    render(<TicketCard {...defaultProps} ticket={unassignedTicket} />);
    
    expect(screen.getByText('Não atribuído')).toBeInTheDocument();
  });

  it('deve lidar com ticket sem tags', () => {
    const noTagsTicket = {
      ...mockTicket,
      tags: [],
    };
    
    render(<TicketCard {...defaultProps} ticket={noTagsTicket} />);
    
    expect(screen.queryByTestId('tag-icon')).not.toBeInTheDocument();
  });

  it('deve lidar com ticket sem due_date', () => {
    const noDueDateTicket = {
      ...mockTicket,
      due_date: null,
    };
    
    render(<TicketCard {...defaultProps} ticket={noDueDateTicket} />);
    
    expect(screen.queryByText(/Vence/)).not.toBeInTheDocument();
  });

  it('deve aplicar classe CSS para modo compacto', () => {
    render(<TicketCard {...defaultProps} compact />);
    
    const card = screen.getByRole('article');
    expect(card).toHaveClass('compact');
  });

  it('deve aplicar classe CSS para ticket selecionado', () => {
    render(<TicketCard {...defaultProps} selected />);
    
    const card = screen.getByRole('article');
    expect(card).toHaveClass('selected');
  });

  it('deve exibir loading state quando especificado', () => {
    render(<TicketCard {...defaultProps} loading />);
    
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  it('deve truncar descrição longa', () => {
    const longDescriptionTicket = {
      ...mockTicket,
      description: 'Esta é uma descrição muito longa que deveria ser truncada para não ocupar muito espaço no card e manter a interface limpa e organizada.',
    };
    
    render(<TicketCard {...defaultProps} ticket={longDescriptionTicket} />);
    
    const description = screen.getByText(/Esta é uma descrição muito longa/);
    expect(description).toHaveClass('truncated');
  });

  it('deve permitir expandir descrição truncada', async () => {
    const longDescriptionTicket = {
      ...mockTicket,
      description: 'Esta é uma descrição muito longa que deveria ser truncada para não ocupar muito espaço no card e manter a interface limpa e organizada.',
    };
    
    render(<TicketCard {...defaultProps} ticket={longDescriptionTicket} />);
    
    const expandButton = screen.getByText('Ver mais');
    fireEvent.click(expandButton);
    
    await waitFor(() => {
      expect(screen.getByText('Ver menos')).toBeInTheDocument();
    });
  });

  it('deve exibir avatar do usuário quando disponível', () => {
    const ticketWithAvatar = {
      ...mockTicket,
      requester_avatar: 'https://example.com/avatar.jpg',
    };
    
    render(<TicketCard {...defaultProps} ticket={ticketWithAvatar} />);
    
    const avatar = screen.getByRole('img', { name: /João Silva/ });
    expect(avatar).toHaveAttribute('src', 'https://example.com/avatar.jpg');
  });

  it('deve exibir iniciais quando avatar não está disponível', () => {
    render(<TicketCard {...defaultProps} />);
    
    expect(screen.getByText('JS')).toBeInTheDocument(); // Iniciais de João Silva
  });

  it('deve aplicar animações de hover', () => {
    render(<TicketCard {...defaultProps} />);
    
    const card = screen.getByRole('article');
    
    fireEvent.mouseEnter(card);
    expect(card).toHaveClass('hovered');
    
    fireEvent.mouseLeave(card);
    expect(card).not.toHaveClass('hovered');
  });

  it('deve ser acessível via teclado', () => {
    const onClickMock = vi.fn();
    render(<TicketCard {...defaultProps} onClick={onClickMock} />);

    const card = screen.getByRole('article');
    
    // Deve ser focável
    card.focus();
    expect(card).toHaveFocus();
    
    // Deve responder ao Enter
    fireEvent.keyDown(card, { key: 'Enter' });
    expect(onClickMock).toHaveBeenCalledWith(mockTicket);
    
    // Deve responder ao Space
    fireEvent.keyDown(card, { key: ' ' });
    expect(onClickMock).toHaveBeenCalledTimes(2);
  });

  it('deve exibir tooltip com informações adicionais', async () => {
    render(<TicketCard {...defaultProps} showTooltip />);
    
    const card = screen.getByRole('article');
    fireEvent.mouseEnter(card);
    
    await waitFor(() => {
      expect(screen.getByRole('tooltip')).toBeInTheDocument();
      expect(screen.getByText(/Criado em:/)).toBeInTheDocument();
      expect(screen.getByText(/Atualizado em:/)).toBeInTheDocument();
    });
  });

  it('deve permitir ações em lote quando selecionado', () => {
    const onBatchActionMock = vi.fn();
    render(
      <TicketCard 
        {...defaultProps} 
        selectable 
        onBatchAction={onBatchActionMock}
      />
    );
    
    const checkbox = screen.getByRole('checkbox');
    fireEvent.click(checkbox);
    
    expect(onBatchActionMock).toHaveBeenCalledWith(mockTicket.id, true);
  });
});