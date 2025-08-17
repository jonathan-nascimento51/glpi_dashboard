import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import '@testing-library/jest-dom';

// Mock dos componentes que serão testados
const Button = ({
  children,
  onClick,
  disabled,
  variant = 'primary',
  size = 'medium',
  ...props
}: any) => (
  <button
    onClick={onClick}
    disabled={disabled}
    className={`btn btn-${variant} btn-${size}`}
    {...props}
  >
    {children}
  </button>
);

const Input = ({ label, error, value, onChange, type = 'text', placeholder, ...props }: any) => (
  <div className='input-group'>
    {label && <label>{label}</label>}
    <input
      type={type}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      className={error ? 'input-error' : 'input'}
      {...props}
    />
    {error && <span className='error-message'>{error}</span>}
  </div>
);

const Select = ({ label, options, value, onChange, error, placeholder, ...props }: any) => (
  <div className='select-group'>
    {label && <label>{label}</label>}
    <select
      value={value}
      onChange={onChange}
      className={error ? 'select-error' : 'select'}
      {...props}
    >
      {placeholder && <option value=''>{placeholder}</option>}
      {options?.map((option: any) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
    {error && <span className='error-message'>{error}</span>}
  </div>
);

const Card = ({ title, children, footer, className, ...props }: any) => (
  <div className={`card ${className || ''}`} {...props}>
    {title && <div className='card-header'>{title}</div>}
    <div className='card-body'>{children}</div>
    {footer && <div className='card-footer'>{footer}</div>}
  </div>
);

const Modal = ({ isOpen, onClose, title, children, footer }: any) => {
  if (!isOpen) return null;

  return (
    <div className='modal-overlay' onClick={onClose}>
      <div className='modal-content' onClick={e => e.stopPropagation()}>
        <div className='modal-header'>
          <h2>{title}</h2>
          <button className='modal-close' onClick={onClose}>
            ×
          </button>
        </div>
        <div className='modal-body'>{children}</div>
        {footer && <div className='modal-footer'>{footer}</div>}
      </div>
    </div>
  );
};

const Alert = ({ type = 'info', title, children, onClose }: any) => (
  <div className={`alert alert-${type}`}>
    {onClose && (
      <button className='alert-close' onClick={onClose}>
        ×
      </button>
    )}
    {title && <div className='alert-title'>{title}</div>}
    <div className='alert-content'>{children}</div>
  </div>
);

const Table = ({ columns, data, onRowClick, selectable, selectedRows, onSelectionChange }: any) => (
  <table className='table'>
    <thead>
      <tr>
        {selectable && (
          <th>
            <input
              type='checkbox'
              checked={selectedRows?.length === data?.length}
              onChange={e => {
                if (e.target.checked) {
                  onSelectionChange?.(data?.map((_: any, index: number) => index) || []);
                } else {
                  onSelectionChange?.([]);
                }
              }}
            />
          </th>
        )}
        {columns?.map((column: any) => (
          <th key={column.key}>{column.title}</th>
        ))}
      </tr>
    </thead>
    <tbody>
      {data?.map((row: any, index: number) => (
        <tr
          key={index}
          onClick={() => onRowClick?.(row, index)}
          className={selectedRows?.includes(index) ? 'selected' : ''}
        >
          {selectable && (
            <td>
              <input
                type='checkbox'
                checked={selectedRows?.includes(index)}
                onChange={e => {
                  if (e.target.checked) {
                    onSelectionChange?.([...selectedRows, index]);
                  } else {
                    onSelectionChange?.(selectedRows.filter((i: number) => i !== index));
                  }
                }}
              />
            </td>
          )}
          {columns?.map((column: any) => (
            <td key={column.key}>{row[column.key]}</td>
          ))}
        </tr>
      ))}
    </tbody>
  </table>
);

const Pagination = ({ currentPage, totalPages, onPageChange, pageSize, onPageSizeChange }: any) => (
  <div className='pagination'>
    <button disabled={currentPage <= 1} onClick={() => onPageChange(currentPage - 1)}>
      Anterior
    </button>
    <span>
      Página {currentPage} de {totalPages}
    </span>
    <button disabled={currentPage >= totalPages} onClick={() => onPageChange(currentPage + 1)}>
      Próxima
    </button>
    <select value={pageSize} onChange={e => onPageSizeChange(Number(e.target.value))}>
      <option value={10}>10 por página</option>
      <option value={25}>25 por página</option>
      <option value={50}>50 por página</option>
    </select>
  </div>
);

const Tabs = ({ tabs, activeTab, onTabChange }: any) => (
  <div className='tabs'>
    <div className='tab-list'>
      {tabs?.map((tab: any) => (
        <button
          key={tab.key}
          className={`tab ${activeTab === tab.key ? 'active' : ''}`}
          onClick={() => onTabChange(tab.key)}
        >
          {tab.title}
        </button>
      ))}
    </div>
    <div className='tab-content'>{tabs?.find((tab: any) => tab.key === activeTab)?.content}</div>
  </div>
);

const Badge = ({ children, variant = 'default', size = 'medium' }: any) => (
  <span className={`badge badge-${variant} badge-${size}`}>{children}</span>
);

const Tooltip = ({ children, content, position = 'top' }: any) => (
  <div className='tooltip-container'>
    {children}
    <div className={`tooltip tooltip-${position}`}>{content}</div>
  </div>
);

const ProgressBar = ({ value, max = 100, label, showPercentage = true }: any) => (
  <div className='progress-bar'>
    {label && <div className='progress-label'>{label}</div>}
    <div className='progress-track'>
      <div className='progress-fill' style={{ width: `${(value / max) * 100}%` }} />
    </div>
    {showPercentage && (
      <div className='progress-percentage'>{Math.round((value / max) * 100)}%</div>
    )}
  </div>
);

const Skeleton = ({ width, height, className }: any) => (
  <div className={`skeleton ${className || ''}`} style={{ width, height }} />
);

const EmptyState = ({ icon, title, description, action }: any) => (
  <div className='empty-state'>
    {icon && <div className='empty-icon'>{icon}</div>}
    <h3 className='empty-title'>{title}</h3>
    {description && <p className='empty-description'>{description}</p>}
    {action && <div className='empty-action'>{action}</div>}
  </div>
);

describe('Button Component', () => {
  test('renders button with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument();
  });

  test('handles click events', async () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    await userEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  test('disables button when disabled prop is true', () => {
    render(<Button disabled>Disabled</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });

  test('applies correct variant classes', () => {
    render(<Button variant='secondary'>Secondary</Button>);
    expect(screen.getByRole('button')).toHaveClass('btn-secondary');
  });

  test('applies correct size classes', () => {
    render(<Button size='large'>Large</Button>);
    expect(screen.getByRole('button')).toHaveClass('btn-large');
  });
});

describe('Input Component', () => {
  test('renders input with label', () => {
    render(<Input label='Username' />);
    expect(screen.getByLabelText('Username')).toBeInTheDocument();
  });

  test('handles value changes', async () => {
    const handleChange = vi.fn();
    render(<Input value='' onChange={handleChange} />);

    await userEvent.type(screen.getByRole('textbox'), 'test');
    expect(handleChange).toHaveBeenCalled();
  });

  test('displays error message', () => {
    render(<Input error='This field is required' />);
    expect(screen.getByText('This field is required')).toBeInTheDocument();
  });

  test('applies error class when error exists', () => {
    render(<Input error='Error' />);
    expect(screen.getByRole('textbox')).toHaveClass('input-error');
  });

  test('renders different input types', () => {
    render(<Input type='password' />);
    expect(screen.getByRole('textbox')).toHaveAttribute('type', 'password');
  });
});

describe('Select Component', () => {
  const options = [
    { value: 'option1', label: 'Option 1' },
    { value: 'option2', label: 'Option 2' },
  ];

  test('renders select with options', () => {
    render(<Select options={options} />);
    expect(screen.getByRole('combobox')).toBeInTheDocument();
    expect(screen.getByText('Option 1')).toBeInTheDocument();
    expect(screen.getByText('Option 2')).toBeInTheDocument();
  });

  test('handles selection changes', async () => {
    const handleChange = vi.fn();
    render(<Select options={options} onChange={handleChange} />);

    await userEvent.selectOptions(screen.getByRole('combobox'), 'option1');
    expect(handleChange).toHaveBeenCalled();
  });

  test('displays placeholder', () => {
    render(<Select options={options} placeholder='Select an option' />);
    expect(screen.getByText('Select an option')).toBeInTheDocument();
  });

  test('displays error message', () => {
    render(<Select options={options} error='Please select an option' />);
    expect(screen.getByText('Please select an option')).toBeInTheDocument();
  });
});

describe('Card Component', () => {
  test('renders card with title and content', () => {
    render(
      <Card title='Card Title'>
        <p>Card content</p>
      </Card>
    );

    expect(screen.getByText('Card Title')).toBeInTheDocument();
    expect(screen.getByText('Card content')).toBeInTheDocument();
  });

  test('renders card with footer', () => {
    render(<Card footer={<button>Action</button>}>Content</Card>);

    expect(screen.getByRole('button', { name: 'Action' })).toBeInTheDocument();
  });

  test('applies custom className', () => {
    render(<Card className='custom-card'>Content</Card>);
    expect(screen.getByText('Content').closest('.card')).toHaveClass('custom-card');
  });
});

describe('Modal Component', () => {
  test('renders modal when open', () => {
    render(
      <Modal isOpen={true} title='Modal Title'>
        Modal content
      </Modal>
    );

    expect(screen.getByText('Modal Title')).toBeInTheDocument();
    expect(screen.getByText('Modal content')).toBeInTheDocument();
  });

  test('does not render when closed', () => {
    render(
      <Modal isOpen={false} title='Modal Title'>
        Modal content
      </Modal>
    );

    expect(screen.queryByText('Modal Title')).not.toBeInTheDocument();
  });

  test('calls onClose when close button is clicked', async () => {
    const handleClose = vi.fn();
    render(
      <Modal isOpen={true} onClose={handleClose} title='Modal'>
        Content
      </Modal>
    );

    await userEvent.click(screen.getByText('×'));
    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  test('calls onClose when overlay is clicked', async () => {
    const handleClose = vi.fn();
    render(
      <Modal isOpen={true} onClose={handleClose} title='Modal'>
        Content
      </Modal>
    );

    await userEvent.click(document.querySelector('.modal-overlay')!);
    expect(handleClose).toHaveBeenCalledTimes(1);
  });
});

describe('Alert Component', () => {
  test('renders alert with different types', () => {
    const { rerender } = render(<Alert type='success'>Success message</Alert>);
    expect(screen.getByText('Success message').closest('.alert')).toHaveClass('alert-success');

    rerender(<Alert type='error'>Error message</Alert>);
    expect(screen.getByText('Error message').closest('.alert')).toHaveClass('alert-error');
  });

  test('renders alert with title', () => {
    render(<Alert title='Alert Title'>Alert content</Alert>);
    expect(screen.getByText('Alert Title')).toBeInTheDocument();
  });

  test('calls onClose when close button is clicked', async () => {
    const handleClose = vi.fn();
    render(<Alert onClose={handleClose}>Closable alert</Alert>);

    await userEvent.click(screen.getByText('×'));
    expect(handleClose).toHaveBeenCalledTimes(1);
  });
});

describe('Table Component', () => {
  const columns = [
    { key: 'name', title: 'Name' },
    { key: 'email', title: 'Email' },
  ];

  const data = [
    { name: 'John Doe', email: 'john@example.com' },
    { name: 'Jane Smith', email: 'jane@example.com' },
  ];

  test('renders table with data', () => {
    render(<Table columns={columns} data={data} />);

    expect(screen.getByText('Name')).toBeInTheDocument();
    expect(screen.getByText('Email')).toBeInTheDocument();
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('jane@example.com')).toBeInTheDocument();
  });

  test('handles row clicks', async () => {
    const handleRowClick = vi.fn();
    render(<Table columns={columns} data={data} onRowClick={handleRowClick} />);

    await userEvent.click(screen.getByText('John Doe'));
    expect(handleRowClick).toHaveBeenCalledWith(data[0], 0);
  });

  test('handles row selection', async () => {
    const handleSelectionChange = vi.fn();
    render(
      <Table
        columns={columns}
        data={data}
        selectable={true}
        selectedRows={[]}
        onSelectionChange={handleSelectionChange}
      />
    );

    const checkboxes = screen.getAllByRole('checkbox');
    await userEvent.click(checkboxes[1]); // First data row checkbox

    expect(handleSelectionChange).toHaveBeenCalledWith([0]);
  });
});

describe('Pagination Component', () => {
  test('renders pagination controls', () => {
    render(
      <Pagination
        currentPage={2}
        totalPages={5}
        onPageChange={vi.fn()}
        pageSize={10}
        onPageSizeChange={vi.fn()}
      />
    );

    expect(screen.getByText('Página 2 de 5')).toBeInTheDocument();
    expect(screen.getByText('Anterior')).toBeInTheDocument();
    expect(screen.getByText('Próxima')).toBeInTheDocument();
  });

  test('disables previous button on first page', () => {
    render(
      <Pagination
        currentPage={1}
        totalPages={5}
        onPageChange={vi.fn()}
        pageSize={10}
        onPageSizeChange={vi.fn()}
      />
    );

    expect(screen.getByText('Anterior')).toBeDisabled();
  });

  test('disables next button on last page', () => {
    render(
      <Pagination
        currentPage={5}
        totalPages={5}
        onPageChange={vi.fn()}
        pageSize={10}
        onPageSizeChange={vi.fn()}
      />
    );

    expect(screen.getByText('Próxima')).toBeDisabled();
  });

  test('handles page changes', async () => {
    const handlePageChange = vi.fn();
    render(
      <Pagination
        currentPage={2}
        totalPages={5}
        onPageChange={handlePageChange}
        pageSize={10}
        onPageSizeChange={vi.fn()}
      />
    );

    await userEvent.click(screen.getByText('Próxima'));
    expect(handlePageChange).toHaveBeenCalledWith(3);
  });
});

describe('Tabs Component', () => {
  const tabs = [
    { key: 'tab1', title: 'Tab 1', content: <div>Content 1</div> },
    { key: 'tab2', title: 'Tab 2', content: <div>Content 2</div> },
  ];

  test('renders tabs with content', () => {
    render(<Tabs tabs={tabs} activeTab='tab1' onTabChange={vi.fn()} />);

    expect(screen.getByText('Tab 1')).toBeInTheDocument();
    expect(screen.getByText('Tab 2')).toBeInTheDocument();
    expect(screen.getByText('Content 1')).toBeInTheDocument();
  });

  test('handles tab changes', async () => {
    const handleTabChange = vi.fn();
    render(<Tabs tabs={tabs} activeTab='tab1' onTabChange={handleTabChange} />);

    await userEvent.click(screen.getByText('Tab 2'));
    expect(handleTabChange).toHaveBeenCalledWith('tab2');
  });

  test('applies active class to current tab', () => {
    render(<Tabs tabs={tabs} activeTab='tab1' onTabChange={vi.fn()} />);

    expect(screen.getByText('Tab 1')).toHaveClass('active');
    expect(screen.getByText('Tab 2')).not.toHaveClass('active');
  });
});

describe('Badge Component', () => {
  test('renders badge with text', () => {
    render(<Badge>New</Badge>);
    expect(screen.getByText('New')).toBeInTheDocument();
  });

  test('applies variant classes', () => {
    render(<Badge variant='success'>Success</Badge>);
    expect(screen.getByText('Success')).toHaveClass('badge-success');
  });

  test('applies size classes', () => {
    render(<Badge size='large'>Large</Badge>);
    expect(screen.getByText('Large')).toHaveClass('badge-large');
  });
});

describe('Tooltip Component', () => {
  test('renders tooltip with content', () => {
    render(
      <Tooltip content='Tooltip text'>
        <button>Hover me</button>
      </Tooltip>
    );

    expect(screen.getByText('Hover me')).toBeInTheDocument();
    expect(screen.getByText('Tooltip text')).toBeInTheDocument();
  });

  test('applies position classes', () => {
    render(
      <Tooltip content='Tooltip' position='bottom'>
        <span>Target</span>
      </Tooltip>
    );

    expect(screen.getByText('Tooltip')).toHaveClass('tooltip-bottom');
  });
});

describe('ProgressBar Component', () => {
  test('renders progress bar with value', () => {
    render(<ProgressBar value={50} max={100} />);

    const progressFill = document.querySelector('.progress-fill');
    expect(progressFill).toHaveStyle('width: 50%');
  });

  test('displays percentage', () => {
    render(<ProgressBar value={75} max={100} showPercentage={true} />);
    expect(screen.getByText('75%')).toBeInTheDocument();
  });

  test('displays label', () => {
    render(<ProgressBar value={30} label='Loading...' />);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  test('hides percentage when showPercentage is false', () => {
    render(<ProgressBar value={50} showPercentage={false} />);
    expect(screen.queryByText('50%')).not.toBeInTheDocument();
  });
});

describe('Skeleton Component', () => {
  test('renders skeleton with dimensions', () => {
    render(<Skeleton width='200px' height='20px' />);

    const skeleton = document.querySelector('.skeleton');
    expect(skeleton).toHaveStyle('width: 200px');
    expect(skeleton).toHaveStyle('height: 20px');
  });

  test('applies custom className', () => {
    render(<Skeleton className='custom-skeleton' />);
    expect(document.querySelector('.skeleton')).toHaveClass('custom-skeleton');
  });
});

describe('EmptyState Component', () => {
  test('renders empty state with title', () => {
    render(<EmptyState title='No data found' />);
    expect(screen.getByText('No data found')).toBeInTheDocument();
  });

  test('renders with description', () => {
    render(<EmptyState title='No results' description='Try adjusting your search criteria' />);

    expect(screen.getByText('Try adjusting your search criteria')).toBeInTheDocument();
  });

  test('renders with action button', () => {
    render(<EmptyState title='No data' action={<button>Add new item</button>} />);

    expect(screen.getByRole('button', { name: 'Add new item' })).toBeInTheDocument();
  });

  test('renders with icon', () => {
    render(<EmptyState title='Empty' icon={<span data-testid='empty-icon'>📭</span>} />);

    expect(screen.getByTestId('empty-icon')).toBeInTheDocument();
  });
});
