// ============================================================================
// COMPONENTES DO DASHBOARD GLPI
// Arquivo de exportação centralizada para todos os componentes
// ============================================================================

// ============================================================================
// COMPONENTES DE DASHBOARD
// ============================================================================
export { default as Dashboard } from './Dashboard/Dashboard';
export { default as DashboardHeader } from './Dashboard/DashboardHeader';
export { default as DashboardMetrics } from './Dashboard/DashboardMetrics';
export { default as DashboardFilters } from './Dashboard/DashboardFilters';
export { default as DashboardCharts } from './Dashboard/DashboardCharts';

// ============================================================================
// COMPONENTES DE UI BASE
// ============================================================================
export { default as Button } from './UI/Button';
export { default as Input } from './UI/Input';
export { default as Select } from './UI/Select';
export { default as Modal } from './UI/Modal';
export { default as Loading } from './UI/Loading';
export { default as ErrorBoundary } from './UI/ErrorBoundary';
export { default as Notification } from './UI/Notification';
export { default as Card } from './UI/Card';
export { default as Badge } from './UI/Badge';
export { default as Tooltip } from './UI/Tooltip';
export { default as Alert } from './UI/Alert';
export { default as Skeleton } from './UI/Skeleton';

// ============================================================================
// COMPONENTES DE GRÁFICOS
// ============================================================================
export { default as LineChart } from './Charts/LineChart';
export { default as BarChart } from './Charts/BarChart';
export { default as PieChart } from './Charts/PieChart';
export { default as DonutChart } from './Charts/DonutChart';

// ============================================================================
// COMPONENTES DE TABELA
// ============================================================================
export { default as DataTable } from './Table/DataTable';
export { default as TablePagination } from './Table/TablePagination';

// ============================================================================
// COMPONENTES DE FORMULÁRIO
// ============================================================================
export { default as Form } from './Form/Form';
export { default as FormField } from './Form/FormField';
export { default as Checkbox } from './Form/Checkbox';
export { default as TextArea } from './Form/TextArea';

// ============================================================================
// COMPONENTES DE LAYOUT
// ============================================================================
export { default as Layout } from './Layout/Layout';
export { default as Container } from './Layout/Container';
export { default as Grid } from './Layout/Grid';
export { default as Flex } from './Layout/Flex';

// ============================================================================
// COMPONENTES DE FEEDBACK
// ============================================================================
export { default as Toast } from './Feedback/Toast';
export { default as EmptyState } from './Feedback/EmptyState';

// ============================================================================
// COMPONENTES UTILITÁRIOS
// ============================================================================
export { default as ThemeProvider } from './Utility/ThemeProvider';

// ============================================================================
// COMPONENTES ESPECÍFICOS DO GLPI
// ============================================================================

// Componentes de Tickets
export { default as TicketCard } from './GLPI/TicketCard';
export { default as TicketList } from './GLPI/TicketList';
export { default as TicketStatus } from './GLPI/TicketStatus';
export { default as TicketPriority } from './GLPI/TicketPriority';

// Componentes de Métricas
export { default as TicketMetrics } from './GLPI/TicketMetrics';
export { default as TechnicianRanking } from './GLPI/TechnicianRanking';
export { default as LevelMetrics } from './GLPI/LevelMetrics';
export { default as StatusDistribution } from './GLPI/StatusDistribution';
export { default as PriorityDistribution } from './GLPI/PriorityDistribution';

// Componentes de Sistema
export { default as SystemHealth } from './GLPI/SystemHealth';
export { default as PerformanceMetrics } from './GLPI/PerformanceMetrics';
export { default as SearchFilters } from './GLPI/SearchFilters';

// Componentes de Usuário
export { default as UserProfile } from './GLPI/UserProfile';
export { default as NotificationCenter } from './GLPI/NotificationCenter';