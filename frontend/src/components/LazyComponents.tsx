/**
 * Componentes com carregamento preguiçoso (React.lazy)
 * Centraliza todos os componentes que não são críticos para a primeira renderização
 */

import { lazy } from 'react';

// Componentes de dashboard secundários
export const LazyPerformanceDashboard = lazy(() =>
  import('./PerformanceDashboard').then(module => ({ default: module.default }))
);
export const LazyDataIntegrityMonitor = lazy(() =>
  import('./DataIntegrityMonitor').then(module => ({ default: module.default }))
);

// Componentes de dashboard que podem ser carregados sob demanda
export const LazyTicketChart = lazy(() =>
  import('./dashboard/TicketChart').then(module => ({ default: module.TicketChart }))
);

export const LazyNewTicketsList = lazy(() =>
  import('./dashboard/NewTicketsList').then(module => ({ default: module.NewTicketsList }))
);

export const LazyRankingTable = lazy(() =>
  import('./dashboard/RankingTable').then(module => ({ default: module.RankingTable }))
);

// Componentes de relatórios e análises
export const LazyProfessionalDashboard = lazy(() =>
  import('./ProfessionalDashboard').then(module => ({ default: module.ProfessionalDashboard }))
);

// Fallback components para Suspense
export const ChartSkeleton = () => (
  <div className='animate-pulse'>
    <div className='h-6 bg-gray-200 rounded w-1/3 mb-4' />
    <div className='h-64 bg-gray-200 rounded' />
  </div>
);

export const TableSkeleton = () => (
  <div className='animate-pulse space-y-4'>
    <div className='h-6 bg-gray-200 rounded w-1/4' />
    {Array.from({ length: 5 }).map((_, i) => (
      <div key={i} className='flex space-x-4'>
        <div className='h-10 w-10 bg-gray-200 rounded-full' />
        <div className='flex-1 space-y-2'>
          <div className='h-4 bg-gray-200 rounded w-3/4' />
          <div className='h-3 bg-gray-200 rounded w-1/2' />
        </div>
      </div>
    ))}
  </div>
);

export const DashboardSkeleton = () => (
  <div className='fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center'>
    <div className='bg-white rounded-lg shadow-xl p-8 max-w-md w-full mx-4'>
      <div className='animate-pulse'>
        <div className='h-6 bg-gray-200 rounded w-3/4 mb-4' />
        <div className='space-y-3'>
          <div className='h-4 bg-gray-200 rounded' />
          <div className='h-4 bg-gray-200 rounded w-5/6' />
          <div className='h-4 bg-gray-200 rounded w-4/6' />
        </div>
      </div>
    </div>
  </div>
);

export const ListSkeleton = () => (
  <div className='animate-pulse space-y-3'>
    <div className='h-5 bg-gray-200 rounded w-1/3 mb-4' />
    {Array.from({ length: 3 }).map((_, i) => (
      <div key={i} className='flex items-center space-x-3 p-3 border rounded'>
        <div className='h-4 bg-gray-200 rounded w-8' />
        <div className='h-4 bg-gray-200 rounded flex-1' />
        <div className='h-3 bg-gray-200 rounded w-16' />
      </div>
    ))}
  </div>
);
