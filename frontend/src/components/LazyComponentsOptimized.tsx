import { lazy } from 'react'

// Dashboard components with code splitting
export const LazyPerformanceDashboard = lazy(() => import('./dashboard/PerformanceDashboard'))
export const LazyDataIntegrityMonitor = lazy(() => import('./dashboard/DataIntegrityMonitor'))
export const LazyTicketChart = lazy(() => import('./dashboard/TicketChart'))
export const LazyNewTicketsList = lazy(() => import('./dashboard/NewTicketsList'))
export const LazyRankingTable = lazy(() => import('./dashboard/RankingTable'))

// Optimized components
export const LazyModernDashboardOptimized = lazy(() => import('./dashboard/ModernDashboardOptimized'))
export const LazyVirtualizedList = lazy(() => import('./VirtualizedList'))

// Heavy components that benefit from code splitting
export const LazyMetricsGrid = lazy(() => import('./dashboard/MetricsGrid'))
export const LazySystemStatusComponent = lazy(() => import('./dashboard/SystemStatusComponent'))
export const LazyTechnicianRankingComponent = lazy(() => import('./dashboard/TechnicianRankingComponent'))

// Chart components
export const LazyChartComponents = {
  TicketChart: lazy(() => import('./dashboard/TicketChart')),
  PerformanceChart: lazy(() => import('./dashboard/PerformanceChart')),
  TrendChart: lazy(() => import('./dashboard/TrendChart'))
}

// UI components that might be heavy
export const LazyUIComponents = {
  DataTable: lazy(() => import('./ui/data-table')),
  Calendar: lazy(() => import('./ui/calendar')),
  DatePicker: lazy(() => import('./ui/date-picker'))
}

// Export all lazy components for easy importing
export const LazyComponents = {
  PerformanceDashboard: LazyPerformanceDashboard,
  DataIntegrityMonitor: LazyDataIntegrityMonitor,
  TicketChart: LazyTicketChart,
  NewTicketsList: LazyNewTicketsList,
  RankingTable: LazyRankingTable,
  ModernDashboardOptimized: LazyModernDashboardOptimized,
  VirtualizedList: LazyVirtualizedList,
  MetricsGrid: LazyMetricsGrid,
  SystemStatusComponent: LazySystemStatusComponent,
  TechnicianRankingComponent: LazyTechnicianRankingComponent,
  ...LazyChartComponents,
  ...LazyUIComponents
}
