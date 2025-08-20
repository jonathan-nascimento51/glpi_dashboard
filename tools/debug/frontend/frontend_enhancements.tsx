// Adições para o frontend - Suporte a Tipos de Filtro

// Adicionar ao DateRangeFilter.tsx
interface FilterTypeOption {
  value: string;
  label: string;
  description: string;
}

const FilterTypeSelector: React.FC<{
  value: string;
  onChange: (value: string) => void;
  options: FilterTypeOption[];
}> = ({ value, onChange, options }) => {
  return (
    <div className="filter-type-selector">
      <label htmlFor="filter-type">Tipo de Filtro:</label>
      <select
        id="filter-type"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="form-select"
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      <small className="form-text text-muted">
        {options.find(opt => opt.value === value)?.description}
      </small>
    </div>
  );
};

// Adicionar ao hook useDashboard.ts
const fetchFilterTypes = async (): Promise<FilterTypeOption[]> => {
  try {
    const response = await fetch('/api/filter-types');
    const data = await response.json();
    return data.filter_types;
  } catch (error) {
    console.error('Erro ao buscar tipos de filtro:', error);
    return [
      {
        value: 'creation',
        label: 'Data de Criação',
        description: 'Tickets criados no período'
      }
    ];
  }
};

// Modificar a função fetchMetrics para incluir filter_type
const fetchMetrics = async (filters: DashboardFilters) => {
  const params = new URLSearchParams();
  
  if (filters.startDate) params.append('start_date', filters.startDate);
  if (filters.endDate) params.append('end_date', filters.endDate);
  if (filters.filterType) params.append('filter_type', filters.filterType);
  
  // ... outros parâmetros
  
  const response = await fetch(`/api/metrics?${params}`);
  return response.json();
};
