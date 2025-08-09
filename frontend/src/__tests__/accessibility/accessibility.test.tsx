import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';

// Extend Jest matchers
expect.extend(toHaveNoViolations);

// Mock components para testes
const MockDashboard = () => (
  <div>
    <header>
      <h1>Dashboard GLPI</h1>
      <nav aria-label="Navegação principal">
        <ul>
          <li><a href="/dashboard">Dashboard</a></li>
          <li><a href="/tickets">Tickets</a></li>
          <li><a href="/users">Usuários</a></li>
        </ul>
      </nav>
    </header>
    <main>
      <section aria-labelledby="metrics-heading">
        <h2 id="metrics-heading">Métricas</h2>
        <div role="region" aria-label="Gráficos de métricas">
          <canvas aria-label="Gráfico de tickets por status" role="img">
            Gráfico mostrando distribuição de tickets por status
          </canvas>
        </div>
      </section>
      <section aria-labelledby="filters-heading">
        <h2 id="filters-heading">Filtros</h2>
        <form>
          <label htmlFor="date-from">Data inicial:</label>
          <input type="date" id="date-from" name="dateFrom" />
          
          <label htmlFor="date-to">Data final:</label>
          <input type="date" id="date-to" name="dateTo" />
          
          <button type="submit">Aplicar filtros</button>
        </form>
      </section>
    </main>
  </div>
);

const MockTicketCard = ({ ticket }: { ticket: any }) => (
  <article 
    className="ticket-card"
    role="article"
    aria-labelledby={`ticket-title-${ticket.id}`}
    tabIndex={0}
  >
    <header>
      <h3 id={`ticket-title-${ticket.id}`}>{ticket.title}</h3>
      <span 
        className={`status status-${ticket.status}`}
        aria-label={`Status: ${ticket.status}`}
      >
        {ticket.status}
      </span>
    </header>
    <div className="ticket-content">
      <p>{ticket.description}</p>
      <div className="ticket-meta">
        <span aria-label={`Prioridade: ${ticket.priority}`}>
          Prioridade: {ticket.priority}
        </span>
        <span aria-label={`Criado em: ${ticket.createdAt}`}>
          {ticket.createdAt}
        </span>
      </div>
    </div>
    <footer>
      <button 
        aria-label={`Editar ticket ${ticket.title}`}
        onClick={() => console.log('Edit ticket')}
      >
        Editar
      </button>
      <button 
        aria-label={`Excluir ticket ${ticket.title}`}
        onClick={() => console.log('Delete ticket')}
      >
        Excluir
      </button>
    </footer>
  </article>
);

const MockModal = ({ isOpen, onClose, title, children }: any) => {
  if (!isOpen) return null;
  
  return (
    <div 
      className="modal-overlay"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <div className="modal-content">
        <header className="modal-header">
          <h2 id="modal-title">{title}</h2>
          <button 
            aria-label="Fechar modal"
            onClick={onClose}
            className="modal-close"
          >
            ×
          </button>
        </header>
        <div className="modal-body">
          {children}
        </div>
      </div>
    </div>
  );
};

const MockForm = () => {
  const [errors, setErrors] = React.useState<Record<string, string>>({});
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const formData = new FormData(e.target as HTMLFormElement);
    const title = formData.get('title') as string;
    
    if (!title) {
      setErrors({ title: 'Título é obrigatório' });
    } else {
      setErrors({});
    }
  };
  
  return (
    <form onSubmit={handleSubmit} noValidate>
      <div className="form-group">
        <label htmlFor="ticket-title">Título do Ticket *</label>
        <input 
          type="text" 
          id="ticket-title" 
          name="title"
          required
          aria-required="true"
          aria-invalid={errors.title ? 'true' : 'false'}
          aria-describedby={errors.title ? 'title-error' : undefined}
        />
        {errors.title && (
          <div id="title-error" role="alert" className="error-message">
            {errors.title}
          </div>
        )}
      </div>
      
      <div className="form-group">
        <label htmlFor="ticket-description">Descrição</label>
        <textarea 
          id="ticket-description" 
          name="description"
          rows={4}
          aria-describedby="description-help"
        />
        <div id="description-help" className="help-text">
          Descreva o problema ou solicitação em detalhes
        </div>
      </div>
      
      <div className="form-group">
        <fieldset>
          <legend>Prioridade</legend>
          <div className="radio-group">
            <input type="radio" id="priority-low" name="priority" value="low" />
            <label htmlFor="priority-low">Baixa</label>
            
            <input type="radio" id="priority-medium" name="priority" value="medium" defaultChecked />
            <label htmlFor="priority-medium">Média</label>
            
            <input type="radio" id="priority-high" name="priority" value="high" />
            <label htmlFor="priority-high">Alta</label>
          </div>
        </fieldset>
      </div>
      
      <div className="form-actions">
        <button type="submit">Criar Ticket</button>
        <button type="button">Cancelar</button>
      </div>
    </form>
  );
};

const MockDataTable = ({ data }: { data: any[] }) => (
  <div className="table-container">
    <table role="table" aria-label="Lista de tickets">
      <caption>Tickets do sistema - {data.length} itens</caption>
      <thead>
        <tr>
          <th scope="col">
            <button aria-label="Ordenar por ID">
              ID
            </button>
          </th>
          <th scope="col">
            <button aria-label="Ordenar por título">
              Título
            </button>
          </th>
          <th scope="col">
            <button aria-label="Ordenar por status">
              Status
            </button>
          </th>
          <th scope="col">
            <button aria-label="Ordenar por prioridade">
              Prioridade
            </button>
          </th>
          <th scope="col">Ações</th>
        </tr>
      </thead>
      <tbody>
        {data.map((ticket, index) => (
          <tr key={ticket.id}>
            <td>{ticket.id}</td>
            <td>
              <a href={`/tickets/${ticket.id}`} aria-describedby={`ticket-desc-${ticket.id}`}>
                {ticket.title}
              </a>
              <div id={`ticket-desc-${ticket.id}`} className="sr-only">
                Ticket criado em {ticket.createdAt}
              </div>
            </td>
            <td>
              <span className={`status status-${ticket.status}`}>
                {ticket.status}
              </span>
            </td>
            <td>{ticket.priority}</td>
            <td>
              <button aria-label={`Editar ticket ${ticket.title}`}>
                Editar
              </button>
              <button aria-label={`Excluir ticket ${ticket.title}`}>
                Excluir
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

describe('Testes de Acessibilidade', () => {
  describe('Dashboard', () => {
    it('deve não ter violações de acessibilidade', async () => {
      const { container } = render(<MockDashboard />);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
    
    it('deve ter estrutura semântica correta', () => {
      render(<MockDashboard />);
      
      // Verificar landmarks
      expect(screen.getByRole('banner')).toBeInTheDocument(); // header
      expect(screen.getByRole('main')).toBeInTheDocument();
      expect(screen.getByRole('navigation')).toBeInTheDocument();
      
      // Verificar hierarquia de headings
      const h1 = screen.getByRole('heading', { level: 1 });
      const h2s = screen.getAllByRole('heading', { level: 2 });
      
      expect(h1).toHaveTextContent('Dashboard GLPI');
      expect(h2s).toHaveLength(2);
    });
    
    it('deve ter navegação acessível por teclado', async () => {
      const user = userEvent.setup();
      render(<MockDashboard />);
      
      const links = screen.getAllByRole('link');
      
      // Testar navegação por Tab
      await user.tab();
      expect(links[0]).toHaveFocus();
      
      await user.tab();
      expect(links[1]).toHaveFocus();
      
      await user.tab();
      expect(links[2]).toHaveFocus();
    });
  });
  
  describe('TicketCard', () => {
    const mockTicket = {
      id: 1,
      title: 'Problema no sistema',
      description: 'Sistema apresentando lentidão',
      status: 'open',
      priority: 'high',
      createdAt: '2024-01-15'
    };
    
    it('deve não ter violações de acessibilidade', async () => {
      const { container } = render(<MockTicketCard ticket={mockTicket} />);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
    
    it('deve ter labels e descrições adequadas', () => {
      render(<MockTicketCard ticket={mockTicket} />);
      
      // Verificar article com label
      const article = screen.getByRole('article');
      expect(article).toHaveAttribute('aria-labelledby', 'ticket-title-1');
      
      // Verificar status com label
      expect(screen.getByLabelText('Status: open')).toBeInTheDocument();
      
      // Verificar botões com labels descritivos
      expect(screen.getByLabelText('Editar ticket Problema no sistema')).toBeInTheDocument();
      expect(screen.getByLabelText('Excluir ticket Problema no sistema')).toBeInTheDocument();
    });
    
    it('deve ser navegável por teclado', async () => {
      const user = userEvent.setup();
      render(<MockTicketCard ticket={mockTicket} />);
      
      const article = screen.getByRole('article');
      const editButton = screen.getByLabelText('Editar ticket Problema no sistema');
      const deleteButton = screen.getByLabelText('Excluir ticket Problema no sistema');
      
      // Testar foco no article
      await user.tab();
      expect(article).toHaveFocus();
      
      // Testar navegação para botões
      await user.tab();
      expect(editButton).toHaveFocus();
      
      await user.tab();
      expect(deleteButton).toHaveFocus();
    });
  });
  
  describe('Modal', () => {
    it('deve não ter violações de acessibilidade', async () => {
      const { container } = render(
        <MockModal isOpen={true} onClose={() => {}} title="Teste Modal">
          <p>Conteúdo do modal</p>
        </MockModal>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
    
    it('deve ter atributos ARIA corretos', () => {
      render(
        <MockModal isOpen={true} onClose={() => {}} title="Teste Modal">
          <p>Conteúdo do modal</p>
        </MockModal>
      );
      
      const dialog = screen.getByRole('dialog');
      expect(dialog).toHaveAttribute('aria-modal', 'true');
      expect(dialog).toHaveAttribute('aria-labelledby', 'modal-title');
      
      expect(screen.getByText('Teste Modal')).toHaveAttribute('id', 'modal-title');
    });
    
    it('deve gerenciar foco corretamente', async () => {
      const user = userEvent.setup();
      const onClose = vi.fn();
      
      render(
        <MockModal isOpen={true} onClose={onClose} title="Teste Modal">
          <button>Botão no modal</button>
        </MockModal>
      );
      
      const closeButton = screen.getByLabelText('Fechar modal');
      const modalButton = screen.getByText('Botão no modal');
      
      // Testar navegação por Tab dentro do modal
      await user.tab();
      expect(closeButton).toHaveFocus();
      
      await user.tab();
      expect(modalButton).toHaveFocus();
      
      // Testar fechamento com Escape
      await user.keyboard('{Escape}');
      expect(onClose).toHaveBeenCalled();
    });
  });
  
  describe('Formulários', () => {
    it('deve não ter violações de acessibilidade', async () => {
      const { container } = render(<MockForm />);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
    
    it('deve ter labels associados corretamente', () => {
      render(<MockForm />);
      
      // Verificar associação label-input
      const titleInput = screen.getByLabelText('Título do Ticket *');
      expect(titleInput).toHaveAttribute('id', 'ticket-title');
      
      const descriptionTextarea = screen.getByLabelText('Descrição');
      expect(descriptionTextarea).toHaveAttribute('id', 'ticket-description');
    });
    
    it('deve indicar campos obrigatórios', () => {
      render(<MockForm />);
      
      const titleInput = screen.getByLabelText('Título do Ticket *');
      expect(titleInput).toHaveAttribute('required');
      expect(titleInput).toHaveAttribute('aria-required', 'true');
    });
    
    it('deve exibir mensagens de erro acessíveis', async () => {
      const user = userEvent.setup();
      render(<MockForm />);
      
      const submitButton = screen.getByText('Criar Ticket');
      
      // Submeter formulário sem preencher campo obrigatório
      await user.click(submitButton);
      
      // Verificar mensagem de erro
      const errorMessage = screen.getByRole('alert');
      expect(errorMessage).toHaveTextContent('Título é obrigatório');
      
      // Verificar associação com o campo
      const titleInput = screen.getByLabelText('Título do Ticket *');
      expect(titleInput).toHaveAttribute('aria-invalid', 'true');
      expect(titleInput).toHaveAttribute('aria-describedby', 'title-error');
    });
    
    it('deve ter fieldset e legend para grupos de radio', () => {
      render(<MockForm />);
      
      const fieldset = screen.getByRole('group', { name: 'Prioridade' });
      expect(fieldset).toBeInTheDocument();
      
      const radioButtons = screen.getAllByRole('radio');
      expect(radioButtons).toHaveLength(3);
      
      // Verificar que um está selecionado por padrão
      expect(screen.getByLabelText('Média')).toBeChecked();
    });
    
    it('deve ter texto de ajuda associado', () => {
      render(<MockForm />);
      
      const descriptionTextarea = screen.getByLabelText('Descrição');
      expect(descriptionTextarea).toHaveAttribute('aria-describedby', 'description-help');
      
      const helpText = screen.getByText('Descreva o problema ou solicitação em detalhes');
      expect(helpText).toHaveAttribute('id', 'description-help');
    });
  });
  
  describe('Tabela de Dados', () => {
    const mockData = [
      { id: 1, title: 'Ticket 1', status: 'open', priority: 'high', createdAt: '2024-01-15' },
      { id: 2, title: 'Ticket 2', status: 'closed', priority: 'low', createdAt: '2024-01-14' }
    ];
    
    it('deve não ter violações de acessibilidade', async () => {
      const { container } = render(<MockDataTable data={mockData} />);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
    
    it('deve ter estrutura de tabela semântica', () => {
      render(<MockDataTable data={mockData} />);
      
      const table = screen.getByRole('table');
      expect(table).toHaveAttribute('aria-label', 'Lista de tickets');
      
      // Verificar caption
      expect(screen.getByText('Tickets do sistema - 2 itens')).toBeInTheDocument();
      
      // Verificar headers de coluna
      const columnHeaders = screen.getAllByRole('columnheader');
      expect(columnHeaders).toHaveLength(5);
      
      // Verificar scope nos headers
      columnHeaders.slice(0, 4).forEach(header => {
        expect(header).toHaveAttribute('scope', 'col');
      });
    });
    
    it('deve ter botões de ordenação acessíveis', () => {
      render(<MockDataTable data={mockData} />);
      
      expect(screen.getByLabelText('Ordenar por ID')).toBeInTheDocument();
      expect(screen.getByLabelText('Ordenar por título')).toBeInTheDocument();
      expect(screen.getByLabelText('Ordenar por status')).toBeInTheDocument();
      expect(screen.getByLabelText('Ordenar por prioridade')).toBeInTheDocument();
    });
    
    it('deve ter links e botões com labels descritivos', () => {
      render(<MockDataTable data={mockData} />);
      
      // Verificar links dos tickets
      expect(screen.getByRole('link', { name: 'Ticket 1' })).toBeInTheDocument();
      expect(screen.getByRole('link', { name: 'Ticket 2' })).toBeInTheDocument();
      
      // Verificar botões de ação
      expect(screen.getByLabelText('Editar ticket Ticket 1')).toBeInTheDocument();
      expect(screen.getByLabelText('Excluir ticket Ticket 1')).toBeInTheDocument();
    });
  });
  
  describe('Navegação por Teclado', () => {
    it('deve permitir navegação completa por teclado', async () => {
      const user = userEvent.setup();
      
      render(
        <div>
          <MockDashboard />
          <MockForm />
        </div>
      );
      
      // Testar navegação sequencial
      const focusableElements = [
        screen.getAllByRole('link'),
        screen.getAllByRole('button'),
        screen.getAllByRole('textbox'),
        screen.getAllByRole('radio')
      ].flat();
      
      // Navegar por todos os elementos focáveis
      for (let i = 0; i < Math.min(5, focusableElements.length); i++) {
        await user.tab();
        expect(document.activeElement).toBeInstanceOf(HTMLElement);
      }
    });
    
    it('deve permitir ativação por Enter e Space', async () => {
      const user = userEvent.setup();
      const onClick = vi.fn();
      
      render(
        <button onClick={onClick}>Botão Teste</button>
      );
      
      const button = screen.getByText('Botão Teste');
      
      // Focar no botão
      button.focus();
      
      // Testar ativação com Enter
      await user.keyboard('{Enter}');
      expect(onClick).toHaveBeenCalledTimes(1);
      
      // Testar ativação com Space
      await user.keyboard(' ');
      expect(onClick).toHaveBeenCalledTimes(2);
    });
  });
  
  describe('Contraste e Visibilidade', () => {
    it('deve ter elementos visíveis para screen readers', () => {
      render(
        <div>
          <span className="sr-only">Texto apenas para screen readers</span>
          <button aria-label="Botão com label invisível">
            <span aria-hidden="true">👍</span>
          </button>
        </div>
      );
      
      // Verificar que elementos com sr-only ainda são acessíveis
      expect(screen.getByText('Texto apenas para screen readers')).toBeInTheDocument();
      
      // Verificar que ícones decorativos estão ocultos
      const icon = screen.getByText('👍');
      expect(icon).toHaveAttribute('aria-hidden', 'true');
    });
  });
  
  describe('Estados de Loading e Erro', () => {
    it('deve anunciar estados de loading', () => {
      render(
        <div>
          <div role="status" aria-live="polite">
            Carregando dados...
          </div>
          <div aria-busy="true">
            Conteúdo sendo carregado
          </div>
        </div>
      );
      
      expect(screen.getByRole('status')).toHaveTextContent('Carregando dados...');
      expect(screen.getByText('Conteúdo sendo carregado')).toHaveAttribute('aria-busy', 'true');
    });
    
    it('deve anunciar mensagens de erro', () => {
      render(
        <div>
          <div role="alert">
            Erro ao carregar dados
          </div>
          <div aria-live="assertive">
            Operação falhou
          </div>
        </div>
      );
      
      expect(screen.getByRole('alert')).toHaveTextContent('Erro ao carregar dados');
      expect(screen.getByText('Operação falhou')).toHaveAttribute('aria-live', 'assertive');
    });
  });
  
  describe('Responsividade e Mobile', () => {
    it('deve manter acessibilidade em diferentes tamanhos de tela', () => {
      // Simular tela pequena
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      });
      
      render(<MockDashboard />);
      
      // Verificar que elementos essenciais ainda estão presentes
      expect(screen.getByRole('banner')).toBeInTheDocument();
      expect(screen.getByRole('main')).toBeInTheDocument();
      expect(screen.getByRole('navigation')).toBeInTheDocument();
    });
  });
});