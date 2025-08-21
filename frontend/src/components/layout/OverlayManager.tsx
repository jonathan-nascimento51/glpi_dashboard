import React, { Suspense } from 'react';
import CacheNotification from '../CacheNotification';
import { CacheStatsCard } from '../dashboard/CacheStatsCard';
import { PerformanceMonitor } from '../PerformanceMonitor';
import { AdvancedSettings } from '../AdvancedSettings';
import AlertCenter from '../AlertCenter';
import AlertNotification from '../AlertNotification';
import { LazyDataIntegrityMonitor, LazyPerformanceDashboard, DashboardSkeleton } from '../LazyComponents';
import type { DataIntegrityReport, CacheNotification as CacheNotificationType } from '../../types';

interface OverlayManagerProps {
  // Data Integrity Monitor
  dataIntegrityReport?: DataIntegrityReport;
  showIntegrityMonitor: boolean;
  onToggleIntegrityMonitor: () => void;
  
  // Performance Dashboard
  showPerformanceDashboard: boolean;
  onClosePerformanceDashboard: () => void;
  
  // Cache
  cacheNotifications: CacheNotificationType[];
  showCacheStats: boolean;
  onCloseCacheStats: () => void;
  onRemoveCacheNotification: (id: string) => void;
  clearFilterCache: () => void;
  getCacheStats: () => any;
  
  // Performance Monitor
  showPerformanceMonitor: boolean;
  onClosePerformanceMonitor: () => void;
  getPerformanceMetrics: () => any;
  isFilterInProgress: boolean;
  
  // Advanced Settings
  showAdvancedSettings: boolean;
  onCloseAdvancedSettings: () => void;
  
  // Alert Center
  showAlertCenter: boolean;
  onCloseAlertCenter: () => void;
  onOpenAlertCenter: () => void;
  
  // Development Controls
  isDevelopment?: boolean;
  onToggleCacheStats: () => void;
  onTogglePerformanceMonitor: () => void;
  onToggleAdvancedSettings: () => void;
  onToggleAlertCenter: () => void;
}

export const OverlayManager: React.FC<OverlayManagerProps> = ({
  dataIntegrityReport,
  showIntegrityMonitor,
  onToggleIntegrityMonitor,
  showPerformanceDashboard,
  onClosePerformanceDashboard,
  cacheNotifications,
  showCacheStats,
  onCloseCacheStats,
  onRemoveCacheNotification,
  clearFilterCache,
  getCacheStats,
  showPerformanceMonitor,
  onClosePerformanceMonitor,
  getPerformanceMetrics,
  isFilterInProgress,
  showAdvancedSettings,
  onCloseAdvancedSettings,
  showAlertCenter,
  onCloseAlertCenter,
  onOpenAlertCenter,
  isDevelopment = false,
  onToggleCacheStats,
  onTogglePerformanceMonitor,
  onToggleAdvancedSettings,
  onToggleAlertCenter,
}) => {
  return (
    <>
      {/* Data Integrity Monitor */}
      <Suspense fallback={<DashboardSkeleton />}>
        <LazyDataIntegrityMonitor
          report={dataIntegrityReport}
          isVisible={showIntegrityMonitor}
          onToggleVisibility={onToggleIntegrityMonitor}
        />
      </Suspense>

      {/* Performance Dashboard */}
      {showPerformanceDashboard && (
        <Suspense fallback={<DashboardSkeleton />}>
          <LazyPerformanceDashboard
            isVisible={showPerformanceDashboard}
            onClose={onClosePerformanceDashboard}
          />
        </Suspense>
      )}

      {/* Cache Notifications */}
      {cacheNotifications.map((notification, index) => (
        <div
          key={notification.id}
          style={{ top: `${4 + index * 80}px` }}
          className='fixed right-4 z-50'
        >
          <CacheNotification
            message={notification.message}
            isVisible={true}
            onClose={() => onRemoveCacheNotification(notification.id)}
          />
        </div>
      ))}

      {/* Cache Stats */}
      {showCacheStats && (
        <div className='fixed bottom-4 left-4 z-50'>
          <div className='bg-white rounded-lg shadow-lg p-4'>
            <div className='flex justify-between items-center mb-2'>
              <h3 className='text-sm font-semibold'>Cache Stats</h3>
              <button
                onClick={onCloseCacheStats}
                className='text-gray-400 hover:text-gray-600'
              >
                ×
              </button>
            </div>
            <CacheStatsCard />
            <button
              onClick={clearFilterCache}
              className='mt-2 px-3 py-1 bg-red-500 text-white text-xs rounded hover:bg-red-600'
            >
              Clear Cache
            </button>
          </div>
        </div>
      )}

      {/* Performance Monitor */}
      {showPerformanceMonitor && (
        <div className='fixed bottom-4 right-4 z-50'>
          <PerformanceMonitor
            getPerformanceMetrics={getPerformanceMetrics}
            isFilterInProgress={isFilterInProgress}
            onClose={onClosePerformanceMonitor}
          />
        </div>
      )}

      {/* Advanced Settings */}
      {showAdvancedSettings && (
        <div className='fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50'>
          <AdvancedSettings onClose={onCloseAdvancedSettings} />
        </div>
      )}

      {/* Alert Center */}
      <AlertCenter open={showAlertCenter} onClose={onCloseAlertCenter} />

      {/* Alert Notifications */}
      <AlertNotification onOpenAlertCenter={onOpenAlertCenter} />

      {/* Development Controls */}
      {isDevelopment && (
        <DevelopmentControls
          showCacheStats={showCacheStats}
          showPerformanceMonitor={showPerformanceMonitor}
          showAdvancedSettings={showAdvancedSettings}
          showAlertCenter={showAlertCenter}
          onToggleCacheStats={onToggleCacheStats}
          onTogglePerformanceMonitor={onTogglePerformanceMonitor}
          onToggleAdvancedSettings={onToggleAdvancedSettings}
          onToggleAlertCenter={onToggleAlertCenter}
        />
      )}
    </>
  );
};

// Componente separado para os controles de desenvolvimento
interface DevelopmentControlsProps {
  showCacheStats: boolean;
  showPerformanceMonitor: boolean;
  showAdvancedSettings: boolean;
  showAlertCenter: boolean;
  onToggleCacheStats: () => void;
  onTogglePerformanceMonitor: () => void;
  onToggleAdvancedSettings: () => void;
  onToggleAlertCenter: () => void;
}

const DevelopmentControls: React.FC<DevelopmentControlsProps> = ({
  showCacheStats,
  showPerformanceMonitor,
  showAdvancedSettings,
  showAlertCenter,
  onToggleCacheStats,
  onTogglePerformanceMonitor,
  onToggleAdvancedSettings,
  onToggleAlertCenter,
}) => (
  <div className='fixed bottom-4 left-1/2 transform -translate-x-1/2 z-40'>
    <div className='bg-white/90 backdrop-blur-sm rounded-lg shadow-lg p-2 flex space-x-2'>
      <ControlButton
        label='Cache'
        isActive={showCacheStats}
        onClick={onToggleCacheStats}
        activeColor='bg-blue-500'
      />
      <ControlButton
        label='Performance'
        isActive={showPerformanceMonitor}
        onClick={onTogglePerformanceMonitor}
        activeColor='bg-green-500'
      />
      <ControlButton
        label='Settings'
        isActive={showAdvancedSettings}
        onClick={onToggleAdvancedSettings}
        activeColor='bg-purple-500'
      />
      <ControlButton
        label='Alerts'
        isActive={showAlertCenter}
        onClick={onToggleAlertCenter}
        activeColor='bg-red-500'
      />
    </div>
  </div>
);

// Componente reutilizável para botões de controle
interface ControlButtonProps {
  label: string;
  isActive: boolean;
  onClick: () => void;
  activeColor: string;
}

const ControlButton: React.FC<ControlButtonProps> = ({
  label,
  isActive,
  onClick,
  activeColor,
}) => (
  <button
    onClick={onClick}
    className={`px-3 py-1 text-xs rounded transition-colors ${
      isActive
        ? `${activeColor} text-white`
        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
    }`}
  >
    {label}
  </button>
);