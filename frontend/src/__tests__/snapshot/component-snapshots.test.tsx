import React from 'react';
import { render } from '@testing-library/react';
import { vi } from 'vitest';

// Mock para Chart.js
vi.mock('react-chartjs-2', () => ({
  Chart: ({ type, data, options }: any) => (
    <div data-testid={`chart-${type}`} className={`chart chart-${type}`}>
      <div className='chart-title'>{options?.plugins?.title?.text || 'Chart'}</div>
      <div className='chart-data'>{JSON.stringify(data.labels)}</div>
    </div>
  ),
  Bar: ({ data, options }: any) => (
    <div data-testid='bar-chart' className='chart chart-bar'>
      <div className='chart-title'>{options?.plugins?.title?.text || 'Bar Chart'}</div>
      <div className='chart-data'>{JSON.stringify(data.labels)}</div>
    </div>
  ),
  Line: ({ data, options }: any) => (
    <div data-testid='line-chart' className='chart chart-line'>
      <div className='chart-title'>{options?.plugins?.title?.text || 'Line Chart'}</div>
      <div className='chart-data'>{JSON.stringify(data.labels)}</div>
    </div>
  ),
  Pie: ({ data, options }: any) => (
    <div data-testid='pie-chart' className='chart chart-pie'>
      <div className='chart-title'>{options?.plugins?.title?.text || 'Pie Chart'}</div>
      <div className='chart-data'>{JSON.stringify(data.labels)}</div>
    </div>
  ),
  Doughnut: ({ data, options }: any) => (
    <div data-testid='doughnut-chart' className='chart chart-doughnut'>
      <div className='chart-title'>{options?.plugins?.title?.text || 'Doughnut Chart'}</div>
      <div className='chart-data'>{JSON.stringify(data.labels)}</div>
    </div>
  ),
}));

// Mock para ícones
vi.mock('lucide-react', () => ({
  Calendar: () => <span data-testid='calendar-icon'>📅</span>,
  Filter: () => <span data-testid='filter-icon'>🔍</span>,
  Download: () => <span data-testid='download-icon'>⬇️</span>,
  RefreshCw: () => <span data-testid='refresh-icon'>🔄</span>,
  Settings: () => <span data-testid='settings-icon'>⚙️</span>,
  User: () => <span data-testid='user-icon'>👤</span>,
  Bell: () => <span data-testid='bell-icon'>🔔</span>,
  Search: () => <span data-testid='search-icon'>🔍</span>,
  Plus: () => <span data-testid='plus-icon'>➕</span>,
  Edit: () => <span data-testid='edit-icon'>✏️</span>,
  Trash: () => <span data-testid='trash-icon'>🗑️</span>,
  Eye: () => <span data-testid='eye-icon'>👁️</span>,
  ChevronDown: () => <span data-testid='chevron-down-icon'>⬇️</span>,
  ChevronUp: () => <span data-testid='chevron-up-icon'>⬆️</span>,
  X: () => <span data-testid='x-icon'>❌</span>,
  AlertCircle: () => <span data-testid='alert-circle-icon'>⚠️</span>,
  CheckCircle: () => <span data-testid='check-circle-icon'>✅</span>,
  Info: () => <span data-testid='info-icon'>ℹ️</span>,
  ExternalLink: () => <span data-testid='external-link-icon'>🔗</span>,
  Menu: () => <span data-testid='menu-icon'>☰</span>,
  Home: () => <span data-testid='home-icon'>🏠</span>,
  BarChart: () => <span data-testid='bar-chart-icon'>📊</span>,
  PieChart: () => <span data-testid='pie-chart-icon'>🥧</span>,
  TrendingUp: () => <span data-testid='trending-up-icon'>📈</span>,
  TrendingDown: () => <span data-testid='trending-down-icon'>📉</span>,
}));

// Mock para framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    button: ({ children, ...props }: any) => <button {...props}>{children}</button>,
    span: ({ children, ...props }: any) => <span {...props}>{children}</span>,
  },
  AnimatePresence: ({ children }: any) => children,
}));

// Componentes mock para testes de snapshot
const MockButton = ({
  variant = 'primary',
  size = 'medium',
  disabled = false,
  loading = false,
  children,
  ...props
}: any) => (
  <button
    className={`btn btn-${variant} btn-${size} ${disabled ? 'disabled' : ''} ${loading ? 'loading' : ''}`}
    disabled={disabled}
    {...props}
  >
    {loading && <span className='spinner'>⏳</span>}
    {children}
  </button>
);

const MockInput = ({
  type = 'text',
  label,
  error,
  placeholder,
  value,
  disabled = false,
  required = false,
  ...props
}: any) => (
  <div className='form-group'>
    {label && (
      <label className={`form-label ${required ? 'required' : ''}`}>
        {label}
        {required && <span className='required-asterisk'>*</span>}
      </label>
    )}
    <input
      type={type}
      className={`form-input ${error ? 'error' : ''} ${disabled ? 'disabled' : ''}`}
      placeholder={placeholder}
      value={value}
      disabled={disabled}
      required={required}
      {...props}
    />
    {error && <span className='error-message'>{error}</span>}
  </div>
);

const MockSelect = ({
  label,
  options = [],
  error,
  placeholder = 'Selecione...',
  value,
  disabled = false,
  required = false,
  ...props
}: any) => (
  <div className='form-group'>
    {label && (
      <label className={`form-label ${required ? 'required' : ''}`}>
        {label}
        {required && <span className='required-asterisk'>*</span>}
      </label>
    )}
    <select
      className={`form-select ${error ? 'error' : ''} ${disabled ? 'disabled' : ''}`}
      value={value}
      disabled={disabled}
      required={required}
      {...props}
    >
      <option value=''>{placeholder}</option>
      {options.map((option: any, index: number) => (
        <option key={index} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
    {error && <span className='error-message'>{error}</span>}
  </div>
);

const MockCard = ({ title, subtitle, children, actions, variant = 'default', ...props }: any) => (
  <div className={`card card-${variant}`} {...props}>
    {(title || subtitle || actions) && (
      <div className='card-header'>
        <div className='card-title-section'>
          {title && <h3 className='card-title'>{title}</h3>}
          {subtitle && <p className='card-subtitle'>{subtitle}</p>}
        </div>
        {actions && <div className='card-actions'>{actions}</div>}
      </div>
    )}
    <div className='card-content'>{children}</div>
  </div>
);

const MockModal = ({ isOpen = true, title, children, onClose, size = 'medium', ...props }: any) => {
  if (!isOpen) return null;

  return (
    <div className='modal-overlay' {...props}>
      <div className={`modal modal-${size}`}>
        <div className='modal-header'>
          <h3 className='modal-title'>{title}</h3>
          <button className='modal-close' onClick={onClose}>
            <span data-testid='x-icon'>❌</span>
          </button>
        </div>
        <div className='modal-body'>{children}</div>
      </div>
    </div>
  );
};

const MockAlert = ({
  type = 'info',
  title,
  children,
  dismissible = false,
  onDismiss,
  ...props
}: any) => (
  <div className={`alert alert-${type}`} {...props}>
    <div className='alert-icon'>
      {type === 'success' && <span data-testid='check-circle-icon'>✅</span>}
      {type === 'error' && <span data-testid='alert-circle-icon'>⚠️</span>}
      {type === 'warning' && <span data-testid='alert-circle-icon'>⚠️</span>}
      {type === 'info' && <span data-testid='info-icon'>ℹ️</span>}
    </div>
    <div className='alert-content'>
      {title && <div className='alert-title'>{title}</div>}
      <div className='alert-message'>{children}</div>
    </div>
    {dismissible && (
      <button className='alert-dismiss' onClick={onDismiss}>
        <span data-testid='x-icon'>❌</span>
      </button>
    )}
  </div>
);

const MockTable = ({
  columns = [],
  data = [],
  loading = false,
  emptyMessage = 'Nenhum dado encontrado',
  ...props
}: any) => (
  <div className='table-container' {...props}>
    <table className='table'>
      <thead>
        <tr>
          {columns.map((column: any, index: number) => (
            <th key={index} className={column.sortable ? 'sortable' : ''}>
              {column.label}
              {column.sortable && <span className='sort-indicator'>↕️</span>}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {loading ? (
          <tr>
            <td colSpan={columns.length} className='loading-cell'>
              <span className='spinner'>⏳</span> Carregando...
            </td>
          </tr>
        ) : data.length === 0 ? (
          <tr>
            <td colSpan={columns.length} className='empty-cell'>
              {emptyMessage}
            </td>
          </tr>
        ) : (
          data.map((row: any, rowIndex: number) => (
            <tr key={rowIndex}>
              {columns.map((column: any, colIndex: number) => (
                <td key={colIndex}>
                  {column.render ? column.render(row[column.key], row) : row[column.key]}
                </td>
              ))}
            </tr>
          ))
        )}
      </tbody>
    </table>
  </div>
);

const MockPagination = ({
  currentPage = 1,
  totalPages = 5,
  onPageChange,
  showInfo = true,
  totalItems = 50,
  itemsPerPage = 10,
  ...props
}: any) => {
  const startItem = (currentPage - 1) * itemsPerPage + 1;
  const endItem = Math.min(currentPage * itemsPerPage, totalItems);

  return (
    <div className='pagination' {...props}>
      {showInfo && (
        <div className='pagination-info'>
          Mostrando {startItem}-{endItem} de {totalItems} registros
        </div>
      )}
      <div className='pagination-controls'>
        <button
          className='pagination-btn'
          disabled={currentPage === 1}
          onClick={() => onPageChange?.(currentPage - 1)}
        >
          Anterior
        </button>

        {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
          <button
            key={page}
            className={`pagination-btn ${page === currentPage ? 'active' : ''}`}
            onClick={() => onPageChange?.(page)}
          >
            {page}
          </button>
        ))}

        <button
          className='pagination-btn'
          disabled={currentPage === totalPages}
          onClick={() => onPageChange?.(currentPage + 1)}
        >
          Próximo
        </button>
      </div>
    </div>
  );
};

const MockBreadcrumb = ({ items = [], ...props }: any) => (
  <nav className='breadcrumb' {...props}>
    {items.map((item: any, index: number) => (
      <span key={index} className='breadcrumb-item'>
        {index > 0 && <span className='breadcrumb-separator'>/</span>}
        {item.href ? (
          <a href={item.href} className='breadcrumb-link'>
            {item.label}
          </a>
        ) : (
          <span className='breadcrumb-current'>{item.label}</span>
        )}
      </span>
    ))}
  </nav>
);

const MockTabs = ({ tabs = [], activeTab = 0, onTabChange, ...props }: any) => (
  <div className='tabs' {...props}>
    <div className='tab-list'>
      {tabs.map((tab: any, index: number) => (
        <button
          key={index}
          className={`tab ${index === activeTab ? 'active' : ''}`}
          onClick={() => onTabChange?.(index)}
        >
          {tab.label}
        </button>
      ))}
    </div>
    <div className='tab-content'>{tabs[activeTab]?.content}</div>
  </div>
);

const MockBadge = ({ variant = 'default', size = 'medium', children, ...props }: any) => (
  <span className={`badge badge-${variant} badge-${size}`} {...props}>
    {children}
  </span>
);

const MockTooltip = ({ content, position = 'top', children, ...props }: any) => (
  <div className='tooltip-container' {...props}>
    {children}
    <div className={`tooltip tooltip-${position}`}>{content}</div>
  </div>
);

const MockProgressBar = ({
  value = 0,
  max = 100,
  label,
  showPercentage = true,
  variant = 'default',
  ...props
}: any) => {
  const percentage = Math.round((value / max) * 100);

  return (
    <div className='progress-container' {...props}>
      {label && <div className='progress-label'>{label}</div>}
      <div className={`progress-bar progress-${variant}`}>
        <div className='progress-fill' style={{ width: `${percentage}%` }}></div>
      </div>
      {showPercentage && <div className='progress-percentage'>{percentage}%</div>}
    </div>
  );
};

const MockSkeleton = ({ width = '100%', height = '20px', variant = 'text', ...props }: any) => (
  <div className={`skeleton skeleton-${variant}`} style={{ width, height }} {...props}></div>
);

const MockEmptyState = ({ icon, title, description, action, ...props }: any) => (
  <div className='empty-state' {...props}>
    {icon && <div className='empty-state-icon'>{icon}</div>}
    {title && <h3 className='empty-state-title'>{title}</h3>}
    {description && <p className='empty-state-description'>{description}</p>}
    {action && <div className='empty-state-action'>{action}</div>}
  </div>
);

describe('Testes de Snapshot de Componentes', () => {
  describe('Botões', () => {
    it('deve capturar snapshot do botão primário', () => {
      const { container } = render(<MockButton variant='primary'>Botão Primário</MockButton>);
      expect(container.firstChild).toMatchSnapshot();
    });

    it('deve capturar snapshot do botão secundário', () => {
      const { container } = render(<MockButton variant='secondary'>Botão Secundário</MockButton>);
      expect(container.firstChild).toMatchSnapshot();
    });

    it('deve capturar snapshot do botão desabilitado', () => {
      const { container } = render(<MockButton disabled>Botão Desabilitado</MockButton>);
      expect(container.firstChild).toMatchSnapshot();
    });

    it('deve capturar snapshot do botão com loading', () => {
      const { container } = render(<MockButton loading>Carregando...</MockButton>);
      expect(container.firstChild).toMatchSnapshot();
    });

    it('deve capturar snapshot de botões de diferentes tamanhos', () => {
      const { container } = render(
        <div>
          <MockButton size='small'>Pequeno</MockButton>
          <MockButton size='medium'>Médio</MockButton>
          <MockButton size='large'>Grande</MockButton>
        </div>
      );
      expect(container.firstChild).toMatchSnapshot();
    });
  });

  describe('Formulários', () => {
    it('deve capturar snapshot de input de texto', () => {
      const { container } = render(
        <MockInput label='Nome' placeholder='Digite seu nome' required />
      );
      expect(container.firstChild).toMatchSnapshot();
    });

    it('deve capturar snapshot de input com erro', () => {
      const { container } = render(
        <MockInput label='Email' value='email-invalido' error='Email inválido' />
      );
      expect(container.firstChild).toMatchSnapshot();
    });

    it('deve capturar snapshot de select', () => {
      const options = [
        { value: 'low', label: 'Baixa' },
        { value: 'medium', label: 'Média' },
        { value: 'high', label: 'Alta' },
      ];

      const { container } = render(<MockSelect label='Prioridade' options={options} required />);
      expect(container.firstChild).toMatchSnapshot();
    });

    it('deve capturar snapshot de formulário completo', () => {
      const { container } = render(
        <form className='form'>
          <MockInput label='Título' placeholder='Digite o título' required />
          <MockInput type='textarea' label='Descrição' placeholder='Descreva o problema' />
          <MockSelect
            label='Prioridade'
            options={[
              { value: 'low', label: 'Baixa' },
              { value: 'medium', label: 'Média' },
              { value: 'high', label: 'Alta' },
            ]}
            required
          />
          <div className='form-actions'>
            <MockButton variant='primary'>Salvar</MockButton>
            <MockButton variant='secondary'>Cancelar</MockButton>
          </div>
        </form>
      );
      expect(container.firstChild).toMatchSnapshot();
    });
  });

  describe('Cards', () => {
    it('deve capturar snapshot de card básico', () => {
      const { container } = render(
        <MockCard title='Título do Card'>
          <p>Conteúdo do card</p>
        </MockCard>
      );
      expect(container.firstChild).toMatchSnapshot();
    });

    it('deve capturar snapshot de card com ações', () => {
      const actions = (
        <div>
          <MockButton size='small'>Editar</MockButton>
          <MockButton size='small' variant='secondary'>
            Excluir
          </MockButton>
        </div>
      );

      const { container } = render(
        <MockCard title='Card com Ações' subtitle='Subtítulo do card' actions={actions}>
          <p>Conteúdo do card com ações</p>
        </MockCard>
      );
      expect(container.firstChild).toMatchSnapshot();
    });

    it('deve capturar snapshot de cards de diferentes variantes', () => {
      const { container } = render(
        <div>
          <MockCard variant='default' title='Card Padrão'>
            <p>Conteúdo padrão</p>
          </MockCard>
          <MockCard variant='success' title='Card de Sucesso'>
            <p>Operação realizada com sucesso</p>
          </MockCard>
          <MockCard variant='warning' title='Card de Aviso'>
            <p>Atenção necessária</p>
          </MockCard>
          <MockCard variant='error' title='Card de Erro'>
            <p>Erro encontrado</p>
          </MockCard>
        </div>
      );
      expect(container.firstChild).toMatchSnapshot();
    });
  });

  describe('Modais', () => {
    it('deve capturar snapshot de modal básico', () => {
      const { container } = render(
        <MockModal title='Modal de Confirmação'>
          <p>Tem certeza que deseja realizar esta ação?</p>
          <div className='modal-actions'>
            <MockButton variant='primary'>Confirmar</MockButton>
            <MockButton variant='secondary'>Cancelar</MockButton>
          </div>
        </MockModal>
      );
      expect(container.firstChild).toMatchSnapshot();
    });

    it('deve capturar snapshot de modais de diferentes tamanhos', () => {
      const { container } = render(
        <div>
          <MockModal size='small' title='Modal Pequeno'>
            <p>Conteúdo pequeno</p>
          </MockModal>
          <MockModal size='large' title='Modal Grande'>
            <p>Conteúdo extenso com mais informações</p>
          </MockModal>
        </div>
      );
      expect(container.firstChild).toMatchSnapshot();
    });
  });

  describe('Alertas', () => {
    it('deve capturar snapshot de alertas de diferentes tipos', () => {
      const { container } = render(
        <div>
          <MockAlert type='success' title='Sucesso'>
            Operação realizada com sucesso!
          </MockAlert>
          <MockAlert type='error' title='Erro'>
            Ocorreu um erro ao processar a solicitação.
          </MockAlert>
          <MockAlert type='warning' title='Aviso'>
            Esta ação não pode ser desfeita.
          </MockAlert>
          <MockAlert type='info' title='Informação'>
            Informação importante para o usuário.
          </MockAlert>
        </div>
      );
      expect(container.firstChild).toMatchSnapshot();
    });

    it('deve capturar snapshot de alerta dismissível', () => {
      const { container } = render(
        <MockAlert type='info' dismissible>
          Este alerta pode ser fechado pelo usuário.
        </MockAlert>
      );
      expect(container.firstChild).toMatchSnapshot();
    });
  });

  describe('Tabelas', () => {
    it('deve capturar snapshot de tabela com dados', () => {
      const columns = [
        { key: 'id', label: 'ID', sortable: true },
        { key: 'name', label: 'Nome', sortable: true },
        { key: 'status', label: 'Status' },
        { key: 'actions', label: 'Ações' },
      ];

      const data = [
        { id: 1, name: 'Item 1', status: 'Ativo' },
        { id: 2, name: 'Item 2', status: 'Inativo' },
        { id: 3, name: 'Item 3', status: 'Pendente' },
      ];

      const { container } = render(<MockTable columns={columns} data={data} />);
      expect(container.firstChild).toMatchSnapshot();
    });

    it('deve capturar snapshot de tabela vazia', () => {
      const columns = [
        { key: 'id', label: 'ID' },
        { key: 'name', label: 'Nome' },
      ];

      const { container } = render(
        <MockTable columns={columns} data={[]} emptyMessage='Nenhum registro encontrado' />
      );
      expect(container.firstChild).toMatchSnapshot();
    });

    it('deve capturar snapshot de tabela carregando', () => {
      const columns = [
        { key: 'id', label: 'ID' },
        { key: 'name', label: 'Nome' },
      ];

      const { container } = render(<MockTable columns={columns} data={[]} loading />);
      expect(container.firstChild).toMatchSnapshot();
    });
  });

  describe('Paginação', () => {
    it('deve capturar snapshot de paginação', () => {
      const { container } = render(
        <MockPagination currentPage={3} totalPages={10} totalItems={100} itemsPerPage={10} />
      );
      expect(container.firstChild).toMatchSnapshot();
    });

    it('deve capturar snapshot de paginação na primeira página', () => {
      const { container } = render(
        <MockPagination currentPage={1} totalPages={5} totalItems={50} itemsPerPage={10} />
      );
      expect(container.firstChild).toMatchSnapshot();
    });

    it('deve capturar snapshot de paginação na última página', () => {
      const { container } = render(
        <MockPagination currentPage={5} totalPages={5} totalItems={50} itemsPerPage={10} />
      );
      expect(container.firstChild).toMatchSnapshot();
    });
  });

  describe('Navegação', () => {
    it('deve capturar snapshot de breadcrumb', () => {
      const items = [
        { label: 'Home', href: '/' },
        { label: 'Tickets', href: '/tickets' },
        { label: 'Detalhes' },
      ];

      const { container } = render(<MockBreadcrumb items={items} />);
      expect(container.firstChild).toMatchSnapshot();
    });

    it('deve capturar snapshot de tabs', () => {
      const tabs = [
        { label: 'Geral', content: <div>Conteúdo geral</div> },
        { label: 'Configurações', content: <div>Conteúdo de configurações</div> },
        { label: 'Avançado', content: <div>Conteúdo avançado</div> },
      ];

      const { container } = render(<MockTabs tabs={tabs} activeTab={1} />);
      expect(container.firstChild).toMatchSnapshot();
    });
  });

  describe('Componentes de Feedback', () => {
    it('deve capturar snapshot de badges', () => {
      const { container } = render(
        <div>
          <MockBadge variant='success'>Ativo</MockBadge>
          <MockBadge variant='warning'>Pendente</MockBadge>
          <MockBadge variant='error'>Erro</MockBadge>
          <MockBadge variant='info'>Info</MockBadge>
        </div>
      );
      expect(container.firstChild).toMatchSnapshot();
    });

    it('deve capturar snapshot de tooltip', () => {
      const { container } = render(
        <MockTooltip content='Informação adicional' position='top'>
          <span>Hover para ver tooltip</span>
        </MockTooltip>
      );
      expect(container.firstChild).toMatchSnapshot();
    });

    it('deve capturar snapshot de barra de progresso', () => {
      const { container } = render(
        <div>
          <MockProgressBar value={30} label='Progresso' variant='default' />
          <MockProgressBar value={75} label='Sucesso' variant='success' />
          <MockProgressBar value={90} label='Aviso' variant='warning' />
        </div>
      );
      expect(container.firstChild).toMatchSnapshot();
    });
  });

  describe('Estados de Loading', () => {
    it('deve capturar snapshot de skeletons', () => {
      const { container } = render(
        <div>
          <MockSkeleton variant='text' width='200px' height='20px' />
          <MockSkeleton variant='text' width='150px' height='16px' />
          <MockSkeleton variant='rectangle' width='100px' height='100px' />
          <MockSkeleton variant='circle' width='50px' height='50px' />
        </div>
      );
      expect(container.firstChild).toMatchSnapshot();
    });
  });

  describe('Estados Vazios', () => {
    it('deve capturar snapshot de estado vazio', () => {
      const { container } = render(
        <MockEmptyState
          icon={<span>📋</span>}
          title='Nenhum ticket encontrado'
          description='Não há tickets para exibir no momento.'
          action={<MockButton variant='primary'>Criar Ticket</MockButton>}
        />
      );
      expect(container.firstChild).toMatchSnapshot();
    });

    it('deve capturar snapshot de estado vazio de busca', () => {
      const { container } = render(
        <MockEmptyState
          icon={<span>🔍</span>}
          title='Nenhum resultado encontrado'
          description='Tente ajustar os filtros ou termos de busca.'
          action={<MockButton variant='secondary'>Limpar Filtros</MockButton>}
        />
      );
      expect(container.firstChild).toMatchSnapshot();
    });
  });

  describe('Layouts Complexos', () => {
    it('deve capturar snapshot de dashboard layout', () => {
      const { container } = render(
        <div className='dashboard-layout'>
          <header className='dashboard-header'>
            <h1>Dashboard GLPI</h1>
            <div className='header-actions'>
              <MockButton size='small'>Atualizar</MockButton>
              <MockButton size='small' variant='secondary'>
                Exportar
              </MockButton>
            </div>
          </header>

          <div className='dashboard-content'>
            <div className='metrics-grid'>
              <MockCard title='Total de Tickets'>
                <div className='metric-value'>1,234</div>
                <div className='metric-change positive'>+12%</div>
              </MockCard>

              <MockCard title='Tickets Abertos'>
                <div className='metric-value'>456</div>
                <div className='metric-change negative'>-5%</div>
              </MockCard>

              <MockCard title='Tempo Médio'>
                <div className='metric-value'>2.5h</div>
                <div className='metric-change neutral'>0%</div>
              </MockCard>
            </div>

            <div className='charts-grid'>
              <MockCard title='Tickets por Status'>
                <div data-testid='bar-chart' className='chart chart-bar'>
                  <div className='chart-title'>Tickets por Status</div>
                </div>
              </MockCard>

              <MockCard title='Tickets por Prioridade'>
                <div data-testid='pie-chart' className='chart chart-pie'>
                  <div className='chart-title'>Tickets por Prioridade</div>
                </div>
              </MockCard>
            </div>
          </div>
        </div>
      );
      expect(container.firstChild).toMatchSnapshot();
    });

    it('deve capturar snapshot de lista de tickets layout', () => {
      const { container } = render(
        <div className='tickets-layout'>
          <header className='page-header'>
            <MockBreadcrumb items={[{ label: 'Home', href: '/' }, { label: 'Tickets' }]} />
            <h1>Lista de Tickets</h1>
          </header>

          <div className='page-content'>
            <div className='filters-section'>
              <MockInput placeholder='Buscar tickets...' />
              <MockSelect
                placeholder='Status'
                options={[
                  { value: 'open', label: 'Aberto' },
                  { value: 'closed', label: 'Fechado' },
                ]}
              />
              <MockButton>Filtrar</MockButton>
            </div>

            <div className='tickets-grid'>
              <MockCard title='Ticket #001'>
                <p>Problema no sistema de login</p>
                <div className='ticket-meta'>
                  <MockBadge variant='error'>Alta</MockBadge>
                  <MockBadge variant='warning'>Aberto</MockBadge>
                </div>
              </MockCard>

              <MockCard title='Ticket #002'>
                <p>Solicitação de novo usuário</p>
                <div className='ticket-meta'>
                  <MockBadge variant='info'>Baixa</MockBadge>
                  <MockBadge variant='success'>Fechado</MockBadge>
                </div>
              </MockCard>
            </div>

            <MockPagination currentPage={1} totalPages={5} totalItems={50} />
          </div>
        </div>
      );
      expect(container.firstChild).toMatchSnapshot();
    });
  });
});
