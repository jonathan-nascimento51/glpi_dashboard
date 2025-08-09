import React from 'react';
import { render } from '@testing-library/react';
import { vi } from 'vitest';
import { toMatchImageSnapshot } from 'jest-image-snapshot';

// Extend Jest matchers for visual testing
expect.extend({ toMatchImageSnapshot });

// Mock para Chart.js
vi.mock('react-chartjs-2', () => ({
  Chart: ({ type, data, options }: any) => (
    <div data-testid={`chart-${type}`} className={`chart chart-${type}`}>
      <div className="chart-title">{options?.plugins?.title?.text || 'Chart'}</div>
      <div className="chart-data">{JSON.stringify(data.labels)}</div>
    </div>
  ),
  Bar: ({ data, options }: any) => (
    <div data-testid="bar-chart" className="chart chart-bar">
      <div className="chart-title">{options?.plugins?.title?.text || 'Bar Chart'}</div>
      <div className="chart-data">{JSON.stringify(data.labels)}</div>
    </div>
  ),
  Line: ({ data, options }: any) => (
    <div data-testid="line-chart" className="chart chart-line">
      <div className="chart-title">{options?.plugins?.title?.text || 'Line Chart'}</div>
      <div className="chart-data">{JSON.stringify(data.labels)}</div>
    </div>
  ),
  Pie: ({ data, options }: any) => (
    <div data-testid="pie-chart" className="chart chart-pie">
      <div className="chart-title">{options?.plugins?.title?.text || 'Pie Chart'}</div>
      <div className="chart-data">{JSON.stringify(data.labels)}</div>
    </div>
  ),
  Doughnut: ({ data, options }: any) => (
    <div data-testid="doughnut-chart" className="chart chart-doughnut">
      <div className="chart-title">{options?.plugins?.title?.text || 'Doughnut Chart'}</div>
      <div className="chart-data">{JSON.stringify(data.labels)}</div>
    </div>
  )
}));

// Mock para ícones
vi.mock('lucide-react', () => ({
  Calendar: () => <div data-testid="calendar-icon" className="icon icon-calendar">📅</div>,
  Filter: () => <div data-testid="filter-icon" className="icon icon-filter">🔍</div>,
  Download: () => <div data-testid="download-icon" className="icon icon-download">⬇️</div>,
  RefreshCw: () => <div data-testid="refresh-icon" className="icon icon-refresh">🔄</div>,
  Settings: () => <div data-testid="settings-icon" className="icon icon-settings">⚙️</div>,
  User: () => <div data-testid="user-icon" className="icon icon-user">👤</div>,
  Bell: () => <div data-testid="bell-icon" className="icon icon-bell">🔔</div>,
  Search: () => <div data-testid="search-icon" className="icon icon-search">🔍</div>,
  Plus: () => <div data-testid="plus-icon" className="icon icon-plus">➕</div>,
  Edit: () => <div data-testid="edit-icon" className="icon icon-edit">✏️</div>,
  Trash: () => <div data-testid="trash-icon" className="icon icon-trash">🗑️</div>,
  Eye: () => <div data-testid="eye-icon" className="icon icon-eye">👁️</div>,
  ChevronDown: () => <div data-testid="chevron-down-icon" className="icon icon-chevron-down">⬇️</div>,
  ChevronUp: () => <div data-testid="chevron-up-icon" className="icon icon-chevron-up">⬆️</div>,
  X: () => <div data-testid="x-icon" className="icon icon-x">❌</div>
}));

// Componentes mock para testes visuais
const MockDashboard = () => (
  <div className="dashboard">
    <header className="dashboard-header">
      <h1>Dashboard GLPI</h1>
      <div className="header-actions">
        <button className="btn btn-primary">Atualizar</button>
        <button className="btn btn-secondary">Exportar</button>
      </div>
    </header>
    
    <div className="dashboard-filters">
      <div className="filter-group">
        <label>Data Inicial:</label>
        <input type="date" defaultValue="2024-01-01" />
      </div>
      <div className="filter-group">
        <label>Data Final:</label>
        <input type="date" defaultValue="2024-01-31" />
      </div>
      <button className="btn btn-primary">Aplicar</button>
    </div>
    
    <div className="dashboard-metrics">
      <div className="metric-card">
        <h3>Total de Tickets</h3>
        <div className="metric-value">1,234</div>
        <div className="metric-change positive">+12%</div>
      </div>
      <div className="metric-card">
        <h3>Tickets Abertos</h3>
        <div className="metric-value">456</div>
        <div className="metric-change negative">-5%</div>
      </div>
      <div className="metric-card">
        <h3>Tickets Fechados</h3>
        <div className="metric-value">778</div>
        <div className="metric-change positive">+8%</div>
      </div>
      <div className="metric-card">
        <h3>Tempo Médio</h3>
        <div className="metric-value">2.5h</div>
        <div className="metric-change neutral">0%</div>
      </div>
    </div>
    
    <div className="dashboard-charts">
      <div className="chart-container">
        <div data-testid="bar-chart" className="chart chart-bar">
          <div className="chart-title">Tickets por Status</div>
          <div className="chart-data">["Aberto", "Em Andamento", "Fechado"]</div>
        </div>
      </div>
      <div className="chart-container">
        <div data-testid="pie-chart" className="chart chart-pie">
          <div className="chart-title">Tickets por Prioridade</div>
          <div className="chart-data">["Alta", "Média", "Baixa"]</div>
        </div>
      </div>
    </div>
  </div>
);

const MockTicketList = () => (
  <div className="ticket-list">
    <header className="list-header">
      <h2>Lista de Tickets</h2>
      <div className="list-actions">
        <button className="btn btn-primary">Novo Ticket</button>
        <button className="btn btn-secondary">Filtros</button>
      </div>
    </header>
    
    <div className="list-filters">
      <input type="text" placeholder="Buscar tickets..." className="search-input" />
      <select className="filter-select">
        <option>Todos os Status</option>
        <option>Aberto</option>
        <option>Em Andamento</option>
        <option>Fechado</option>
      </select>
      <select className="filter-select">
        <option>Todas as Prioridades</option>
        <option>Alta</option>
        <option>Média</option>
        <option>Baixa</option>
      </select>
    </div>
    
    <div className="ticket-cards">
      {[1, 2, 3].map(id => (
        <div key={id} className="ticket-card">
          <div className="ticket-header">
            <h3>Ticket #{id}</h3>
            <span className={`status status-${id === 1 ? 'open' : id === 2 ? 'progress' : 'closed'}`}>
              {id === 1 ? 'Aberto' : id === 2 ? 'Em Andamento' : 'Fechado'}
            </span>
          </div>
          <div className="ticket-content">
            <p>Descrição do ticket {id}</p>
            <div className="ticket-meta">
              <span className="priority priority-high">Alta</span>
              <span className="date">15/01/2024</span>
              <span className="assignee">João Silva</span>
            </div>
          </div>
          <div className="ticket-actions">
            <button className="btn btn-sm btn-primary">Editar</button>
            <button className="btn btn-sm btn-secondary">Ver</button>
          </div>
        </div>
      ))}
    </div>
  </div>
);

const MockTicketForm = () => (
  <div className="ticket-form">
    <header className="form-header">
      <h2>Novo Ticket</h2>
    </header>
    
    <form className="form">
      <div className="form-group">
        <label htmlFor="title">Título *</label>
        <input type="text" id="title" className="form-input" placeholder="Digite o título do ticket" />
      </div>
      
      <div className="form-group">
        <label htmlFor="description">Descrição</label>
        <textarea id="description" className="form-textarea" rows={4} placeholder="Descreva o problema..." />
      </div>
      
      <div className="form-row">
        <div className="form-group">
          <label htmlFor="priority">Prioridade</label>
          <select id="priority" className="form-select">
            <option>Baixa</option>
            <option>Média</option>
            <option>Alta</option>
          </select>
        </div>
        
        <div className="form-group">
          <label htmlFor="category">Categoria</label>
          <select id="category" className="form-select">
            <option>Hardware</option>
            <option>Software</option>
            <option>Rede</option>
          </select>
        </div>
      </div>
      
      <div className="form-group">
        <label htmlFor="assignee">Responsável</label>
        <select id="assignee" className="form-select">
          <option>Selecionar...</option>
          <option>João Silva</option>
          <option>Maria Santos</option>
          <option>Pedro Costa</option>
        </select>
      </div>
      
      <div className="form-actions">
        <button type="submit" className="btn btn-primary">Criar Ticket</button>
        <button type="button" className="btn btn-secondary">Cancelar</button>
      </div>
    </form>
  </div>
);

const MockModal = ({ variant = 'default' }: { variant?: 'default' | 'warning' | 'error' }) => (
  <div className="modal-overlay">
    <div className={`modal modal-${variant}`}>
      <div className="modal-header">
        <h3>Confirmar Ação</h3>
        <button className="modal-close">×</button>
      </div>
      <div className="modal-body">
        <p>Tem certeza que deseja realizar esta ação?</p>
        {variant === 'warning' && (
          <div className="warning-message">
            ⚠️ Esta ação não pode ser desfeita.
          </div>
        )}
        {variant === 'error' && (
          <div className="error-message">
            ❌ Ocorreu um erro ao processar a solicitação.
          </div>
        )}
      </div>
      <div className="modal-footer">
        <button className="btn btn-primary">Confirmar</button>
        <button className="btn btn-secondary">Cancelar</button>
      </div>
    </div>
  </div>
);

const MockDataTable = () => (
  <div className="data-table">
    <div className="table-header">
      <h3>Relatório de Tickets</h3>
      <div className="table-actions">
        <button className="btn btn-sm btn-secondary">Exportar CSV</button>
        <button className="btn btn-sm btn-secondary">Imprimir</button>
      </div>
    </div>
    
    <div className="table-container">
      <table className="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Título</th>
            <th>Status</th>
            <th>Prioridade</th>
            <th>Responsável</th>
            <th>Data</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {[1, 2, 3, 4, 5].map(id => (
            <tr key={id}>
              <td>#{id.toString().padStart(4, '0')}</td>
              <td>Problema no sistema {id}</td>
              <td>
                <span className={`status status-${id % 3 === 0 ? 'closed' : id % 2 === 0 ? 'progress' : 'open'}`}>
                  {id % 3 === 0 ? 'Fechado' : id % 2 === 0 ? 'Em Andamento' : 'Aberto'}
                </span>
              </td>
              <td>
                <span className={`priority priority-${id % 3 === 0 ? 'low' : id % 2 === 0 ? 'medium' : 'high'}`}>
                  {id % 3 === 0 ? 'Baixa' : id % 2 === 0 ? 'Média' : 'Alta'}
                </span>
              </td>
              <td>Usuário {id}</td>
              <td>15/01/2024</td>
              <td>
                <button className="btn btn-xs btn-primary">Ver</button>
                <button className="btn btn-xs btn-secondary">Editar</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
    
    <div className="table-pagination">
      <div className="pagination-info">
        Mostrando 1-5 de 50 registros
      </div>
      <div className="pagination-controls">
        <button className="btn btn-sm btn-secondary" disabled>Anterior</button>
        <button className="btn btn-sm btn-primary">1</button>
        <button className="btn btn-sm btn-secondary">2</button>
        <button className="btn btn-sm btn-secondary">3</button>
        <button className="btn btn-sm btn-secondary">Próximo</button>
      </div>
    </div>
  </div>
);

// Função para adicionar estilos CSS para os testes visuais
const addTestStyles = () => {
  const style = document.createElement('style');
  style.textContent = `
    /* Reset básico */
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
    
    /* Dashboard */
    .dashboard { padding: 20px; background: #f5f5f5; min-height: 100vh; }
    .dashboard-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
    .dashboard-header h1 { color: #333; font-size: 24px; }
    .header-actions { display: flex; gap: 10px; }
    
    .dashboard-filters { display: flex; gap: 15px; align-items: end; margin-bottom: 20px; padding: 15px; background: white; border-radius: 8px; }
    .filter-group { display: flex; flex-direction: column; gap: 5px; }
    .filter-group label { font-size: 12px; color: #666; }
    
    .dashboard-metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }
    .metric-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .metric-card h3 { font-size: 14px; color: #666; margin-bottom: 10px; }
    .metric-value { font-size: 32px; font-weight: bold; color: #333; margin-bottom: 5px; }
    .metric-change { font-size: 12px; }
    .metric-change.positive { color: #10b981; }
    .metric-change.negative { color: #ef4444; }
    .metric-change.neutral { color: #6b7280; }
    
    .dashboard-charts { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    .chart-container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .chart { height: 300px; display: flex; flex-direction: column; align-items: center; justify-content: center; }
    .chart-title { font-weight: bold; margin-bottom: 10px; }
    .chart-data { font-size: 12px; color: #666; }
    
    /* Buttons */
    .btn { padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 500; }
    .btn-primary { background: #3b82f6; color: white; }
    .btn-secondary { background: #6b7280; color: white; }
    .btn-sm { padding: 6px 12px; font-size: 12px; }
    .btn-xs { padding: 4px 8px; font-size: 11px; }
    .btn:disabled { opacity: 0.5; cursor: not-allowed; }
    
    /* Forms */
    .form-input, .form-textarea, .form-select { padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px; }
    .form-input:focus, .form-textarea:focus, .form-select:focus { outline: none; border-color: #3b82f6; }
    
    /* Ticket List */
    .ticket-list { padding: 20px; }
    .list-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
    .list-actions { display: flex; gap: 10px; }
    .list-filters { display: flex; gap: 15px; margin-bottom: 20px; }
    .search-input { flex: 1; padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 6px; }
    .filter-select { padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 6px; }
    
    .ticket-cards { display: grid; gap: 15px; }
    .ticket-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .ticket-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
    .ticket-header h3 { color: #333; }
    .ticket-content p { color: #666; margin-bottom: 10px; }
    .ticket-meta { display: flex; gap: 15px; font-size: 12px; }
    .ticket-actions { display: flex; gap: 10px; margin-top: 15px; }
    
    /* Status and Priority */
    .status { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 500; }
    .status-open { background: #dbeafe; color: #1e40af; }
    .status-progress { background: #fef3c7; color: #92400e; }
    .status-closed { background: #d1fae5; color: #065f46; }
    
    .priority { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 500; }
    .priority-high { background: #fee2e2; color: #991b1b; }
    .priority-medium { background: #fef3c7; color: #92400e; }
    .priority-low { background: #d1fae5; color: #065f46; }
    
    /* Forms */
    .ticket-form { padding: 20px; max-width: 600px; margin: 0 auto; }
    .form-header { margin-bottom: 20px; }
    .form { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .form-group { margin-bottom: 15px; }
    .form-group label { display: block; margin-bottom: 5px; font-weight: 500; color: #333; }
    .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
    .form-actions { display: flex; gap: 10px; margin-top: 20px; }
    
    /* Modal */
    .modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; }
    .modal { background: white; border-radius: 8px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); max-width: 400px; width: 100%; }
    .modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 20px 0; }
    .modal-close { background: none; border: none; font-size: 20px; cursor: pointer; }
    .modal-body { padding: 20px; }
    .modal-footer { display: flex; gap: 10px; justify-content: end; padding: 0 20px 20px; }
    .warning-message, .error-message { padding: 10px; border-radius: 6px; margin-top: 10px; }
    .warning-message { background: #fef3c7; color: #92400e; }
    .error-message { background: #fee2e2; color: #991b1b; }
    
    /* Table */
    .data-table { padding: 20px; }
    .table-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
    .table-actions { display: flex; gap: 10px; }
    .table-container { background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .table { width: 100%; border-collapse: collapse; }
    .table th, .table td { padding: 12px; text-align: left; border-bottom: 1px solid #e5e7eb; }
    .table th { background: #f9fafb; font-weight: 600; color: #374151; }
    .table tbody tr:hover { background: #f9fafb; }
    
    .table-pagination { display: flex; justify-content: between; align-items: center; margin-top: 15px; }
    .pagination-info { color: #6b7280; font-size: 14px; }
    .pagination-controls { display: flex; gap: 5px; }
    
    /* Icons */
    .icon { display: inline-block; width: 16px; height: 16px; text-align: center; }
  `;
  document.head.appendChild(style);
};

describe('Testes de Regressão Visual', () => {
  beforeAll(() => {
    addTestStyles();
  });
  
  describe('Dashboard', () => {
    it('deve renderizar o dashboard corretamente', () => {
      const { container } = render(<MockDashboard />);
      expect(container.firstChild).toMatchImageSnapshot({
        customSnapshotIdentifier: 'dashboard-default',
        failureThreshold: 0.01,
        failureThresholdType: 'percent'
      });
    });
    
    it('deve renderizar métricas com diferentes estados', () => {
      const { container } = render(
        <div className="dashboard-metrics">
          <div className="metric-card">
            <h3>Tickets Críticos</h3>
            <div className="metric-value">15</div>
            <div className="metric-change negative">+25%</div>
          </div>
          <div className="metric-card">
            <h3>Tickets Resolvidos</h3>
            <div className="metric-value">89</div>
            <div className="metric-change positive">+12%</div>
          </div>
          <div className="metric-card">
            <h3>Tempo Médio</h3>
            <div className="metric-value">4.2h</div>
            <div className="metric-change neutral">0%</div>
          </div>
        </div>
      );
      expect(container.firstChild).toMatchImageSnapshot({
        customSnapshotIdentifier: 'dashboard-metrics-states'
      });
    });
  });
  
  describe('Lista de Tickets', () => {
    it('deve renderizar a lista de tickets corretamente', () => {
      const { container } = render(<MockTicketList />);
      expect(container.firstChild).toMatchImageSnapshot({
        customSnapshotIdentifier: 'ticket-list-default'
      });
    });
    
    it('deve renderizar cards de ticket com diferentes status', () => {
      const { container } = render(
        <div className="ticket-cards">
          <div className="ticket-card">
            <div className="ticket-header">
              <h3>Ticket Aberto</h3>
              <span className="status status-open">Aberto</span>
            </div>
            <div className="ticket-content">
              <p>Problema urgente no servidor</p>
              <div className="ticket-meta">
                <span className="priority priority-high">Alta</span>
                <span className="date">15/01/2024</span>
              </div>
            </div>
          </div>
          <div className="ticket-card">
            <div className="ticket-header">
              <h3>Ticket em Andamento</h3>
              <span className="status status-progress">Em Andamento</span>
            </div>
            <div className="ticket-content">
              <p>Manutenção programada</p>
              <div className="ticket-meta">
                <span className="priority priority-medium">Média</span>
                <span className="date">14/01/2024</span>
              </div>
            </div>
          </div>
          <div className="ticket-card">
            <div className="ticket-header">
              <h3>Ticket Fechado</h3>
              <span className="status status-closed">Fechado</span>
            </div>
            <div className="ticket-content">
              <p>Problema resolvido</p>
              <div className="ticket-meta">
                <span className="priority priority-low">Baixa</span>
                <span className="date">13/01/2024</span>
              </div>
            </div>
          </div>
        </div>
      );
      expect(container.firstChild).toMatchImageSnapshot({
        customSnapshotIdentifier: 'ticket-cards-different-status'
      });
    });
  });
  
  describe('Formulários', () => {
    it('deve renderizar o formulário de ticket corretamente', () => {
      const { container } = render(<MockTicketForm />);
      expect(container.firstChild).toMatchImageSnapshot({
        customSnapshotIdentifier: 'ticket-form-default'
      });
    });
    
    it('deve renderizar formulário com estados de erro', () => {
      const { container } = render(
        <div className="form">
          <div className="form-group">
            <label htmlFor="title">Título *</label>
            <input 
              type="text" 
              id="title" 
              className="form-input" 
              style={{ borderColor: '#ef4444' }}
              defaultValue=""
            />
            <div style={{ color: '#ef4444', fontSize: '12px', marginTop: '5px' }}>
              Este campo é obrigatório
            </div>
          </div>
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input 
              type="email" 
              id="email" 
              className="form-input" 
              style={{ borderColor: '#ef4444' }}
              defaultValue="email-invalido"
            />
            <div style={{ color: '#ef4444', fontSize: '12px', marginTop: '5px' }}>
              Email inválido
            </div>
          </div>
        </div>
      );
      expect(container.firstChild).toMatchImageSnapshot({
        customSnapshotIdentifier: 'form-with-errors'
      });
    });
  });
  
  describe('Modais', () => {
    it('deve renderizar modal padrão corretamente', () => {
      const { container } = render(<MockModal />);
      expect(container.firstChild).toMatchImageSnapshot({
        customSnapshotIdentifier: 'modal-default'
      });
    });
    
    it('deve renderizar modal de aviso', () => {
      const { container } = render(<MockModal variant="warning" />);
      expect(container.firstChild).toMatchImageSnapshot({
        customSnapshotIdentifier: 'modal-warning'
      });
    });
    
    it('deve renderizar modal de erro', () => {
      const { container } = render(<MockModal variant="error" />);
      expect(container.firstChild).toMatchImageSnapshot({
        customSnapshotIdentifier: 'modal-error'
      });
    });
  });
  
  describe('Tabelas', () => {
    it('deve renderizar tabela de dados corretamente', () => {
      const { container } = render(<MockDataTable />);
      expect(container.firstChild).toMatchImageSnapshot({
        customSnapshotIdentifier: 'data-table-default'
      });
    });
    
    it('deve renderizar tabela com linha selecionada', () => {
      const { container } = render(
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Nome</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>#001</td>
                <td>Item 1</td>
                <td><span className="status status-open">Ativo</span></td>
              </tr>
              <tr style={{ backgroundColor: '#e0f2fe' }}>
                <td>#002</td>
                <td>Item 2 (Selecionado)</td>
                <td><span className="status status-progress">Pendente</span></td>
              </tr>
              <tr>
                <td>#003</td>
                <td>Item 3</td>
                <td><span className="status status-closed">Inativo</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      );
      expect(container.firstChild).toMatchImageSnapshot({
        customSnapshotIdentifier: 'table-with-selection'
      });
    });
  });
  
  describe('Estados de Loading', () => {
    it('deve renderizar skeleton loading corretamente', () => {
      const { container } = render(
        <div className="loading-container">
          <div className="skeleton-card">
            <div className="skeleton-header">
              <div className="skeleton-line" style={{ width: '60%', height: '20px', backgroundColor: '#e5e7eb', borderRadius: '4px' }}></div>
              <div className="skeleton-line" style={{ width: '80px', height: '16px', backgroundColor: '#e5e7eb', borderRadius: '4px' }}></div>
            </div>
            <div className="skeleton-content">
              <div className="skeleton-line" style={{ width: '100%', height: '16px', backgroundColor: '#e5e7eb', borderRadius: '4px', marginBottom: '8px' }}></div>
              <div className="skeleton-line" style={{ width: '80%', height: '16px', backgroundColor: '#e5e7eb', borderRadius: '4px', marginBottom: '8px' }}></div>
              <div className="skeleton-line" style={{ width: '60%', height: '16px', backgroundColor: '#e5e7eb', borderRadius: '4px' }}></div>
            </div>
          </div>
        </div>
      );
      expect(container.firstChild).toMatchImageSnapshot({
        customSnapshotIdentifier: 'skeleton-loading'
      });
    });
    
    it('deve renderizar spinner loading', () => {
      const { container } = render(
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '40px' }}>
          <div 
            style={{
              width: '32px',
              height: '32px',
              border: '3px solid #e5e7eb',
              borderTop: '3px solid #3b82f6',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite'
            }}
          ></div>
          <span style={{ marginLeft: '10px', color: '#6b7280' }}>Carregando...</span>
        </div>
      );
      expect(container.firstChild).toMatchImageSnapshot({
        customSnapshotIdentifier: 'spinner-loading'
      });
    });
  });
  
  describe('Estados de Erro', () => {
    it('deve renderizar página de erro 404', () => {
      const { container } = render(
        <div style={{ textAlign: 'center', padding: '60px 20px' }}>
          <div style={{ fontSize: '72px', marginBottom: '20px' }}>404</div>
          <h2 style={{ marginBottom: '10px', color: '#374151' }}>Página não encontrada</h2>
          <p style={{ color: '#6b7280', marginBottom: '30px' }}>A página que você está procurando não existe.</p>
          <button className="btn btn-primary">Voltar ao Dashboard</button>
        </div>
      );
      expect(container.firstChild).toMatchImageSnapshot({
        customSnapshotIdentifier: 'error-404'
      });
    });
    
    it('deve renderizar estado de erro genérico', () => {
      const { container } = render(
        <div style={{ textAlign: 'center', padding: '40px 20px' }}>
          <div style={{ fontSize: '48px', marginBottom: '20px' }}>⚠️</div>
          <h3 style={{ marginBottom: '10px', color: '#374151' }}>Algo deu errado</h3>
          <p style={{ color: '#6b7280', marginBottom: '20px' }}>Ocorreu um erro inesperado. Tente novamente.</p>
          <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
            <button className="btn btn-primary">Tentar Novamente</button>
            <button className="btn btn-secondary">Reportar Problema</button>
          </div>
        </div>
      );
      expect(container.firstChild).toMatchImageSnapshot({
        customSnapshotIdentifier: 'error-generic'
      });
    });
  });
  
  describe('Estados Vazios', () => {
    it('deve renderizar estado vazio para lista de tickets', () => {
      const { container } = render(
        <div style={{ textAlign: 'center', padding: '60px 20px' }}>
          <div style={{ fontSize: '48px', marginBottom: '20px' }}>📋</div>
          <h3 style={{ marginBottom: '10px', color: '#374151' }}>Nenhum ticket encontrado</h3>
          <p style={{ color: '#6b7280', marginBottom: '30px' }}>Não há tickets para exibir no momento.</p>
          <button className="btn btn-primary">Criar Primeiro Ticket</button>
        </div>
      );
      expect(container.firstChild).toMatchImageSnapshot({
        customSnapshotIdentifier: 'empty-state-tickets'
      });
    });
    
    it('deve renderizar estado vazio para busca', () => {
      const { container } = render(
        <div style={{ textAlign: 'center', padding: '40px 20px' }}>
          <div style={{ fontSize: '48px', marginBottom: '20px' }}>🔍</div>
          <h3 style={{ marginBottom: '10px', color: '#374151' }}>Nenhum resultado encontrado</h3>
          <p style={{ color: '#6b7280', marginBottom: '20px' }}>Tente ajustar os filtros ou termos de busca.</p>
          <button className="btn btn-secondary">Limpar Filtros</button>
        </div>
      );
      expect(container.firstChild).toMatchImageSnapshot({
        customSnapshotIdentifier: 'empty-state-search'
      });
    });
  });
  
  describe('Responsividade', () => {
    it('deve renderizar dashboard em tela pequena', () => {
      // Simular viewport mobile
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      });
      
      const { container } = render(
        <div style={{ width: '375px' }}>
          <div className="dashboard" style={{ padding: '10px' }}>
            <div className="dashboard-metrics" style={{ gridTemplateColumns: '1fr', gap: '10px' }}>
              <div className="metric-card">
                <h3>Total</h3>
                <div className="metric-value">1,234</div>
              </div>
              <div className="metric-card">
                <h3>Abertos</h3>
                <div className="metric-value">456</div>
              </div>
            </div>
          </div>
        </div>
      );
      expect(container.firstChild).toMatchImageSnapshot({
        customSnapshotIdentifier: 'dashboard-mobile'
      });
    });
  });
});