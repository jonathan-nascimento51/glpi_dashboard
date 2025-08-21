import { useState, useCallback } from 'react';

export interface OverlayStates {
  showIntegrityMonitor: boolean;
  showPerformanceDashboard: boolean;
  showChartExample: boolean;
  showCacheStats: boolean;
  showPerformanceMonitor: boolean;
  showAdvancedSettings: boolean;
  showAlertCenter: boolean;
}

export interface OverlayActions {
  toggleIntegrityMonitor: () => void;
  openPerformanceDashboard: () => void;
  closePerformanceDashboard: () => void;
  toggleChartExample: () => void;
  toggleCacheStats: () => void;
  togglePerformanceMonitor: () => void;
  toggleAdvancedSettings: () => void;
  toggleAlertCenter: () => void;
  openAlertCenter: () => void;
  closeAlertCenter: () => void;
  resetAllOverlays: () => void;
}

const initialStates: OverlayStates = {
  showIntegrityMonitor: true,
  showPerformanceDashboard: false,
  showChartExample: false,
  showCacheStats: false,
  showPerformanceMonitor: false,
  showAdvancedSettings: false,
  showAlertCenter: false,
};

export const useOverlayManager = () => {
  const [overlayStates, setOverlayStates] = useState<OverlayStates>(initialStates);

  const toggleIntegrityMonitor = useCallback(() => {
    setOverlayStates(prev => ({
      ...prev,
      showIntegrityMonitor: !prev.showIntegrityMonitor,
    }));
  }, []);

  const openPerformanceDashboard = useCallback(() => {
    setOverlayStates(prev => ({
      ...prev,
      showPerformanceDashboard: true,
    }));
  }, []);

  const closePerformanceDashboard = useCallback(() => {
    setOverlayStates(prev => ({
      ...prev,
      showPerformanceDashboard: false,
    }));
  }, []);

  const toggleChartExample = useCallback(() => {
    setOverlayStates(prev => ({
      ...prev,
      showChartExample: !prev.showChartExample,
    }));
  }, []);

  const toggleCacheStats = useCallback(() => {
    setOverlayStates(prev => ({
      ...prev,
      showCacheStats: !prev.showCacheStats,
    }));
  }, []);

  const togglePerformanceMonitor = useCallback(() => {
    setOverlayStates(prev => ({
      ...prev,
      showPerformanceMonitor: !prev.showPerformanceMonitor,
    }));
  }, []);

  const toggleAdvancedSettings = useCallback(() => {
    setOverlayStates(prev => ({
      ...prev,
      showAdvancedSettings: !prev.showAdvancedSettings,
    }));
  }, []);

  const toggleAlertCenter = useCallback(() => {
    setOverlayStates(prev => ({
      ...prev,
      showAlertCenter: !prev.showAlertCenter,
    }));
  }, []);

  const openAlertCenter = useCallback(() => {
    setOverlayStates(prev => ({
      ...prev,
      showAlertCenter: true,
    }));
  }, []);

  const closeAlertCenter = useCallback(() => {
    setOverlayStates(prev => ({
      ...prev,
      showAlertCenter: false,
    }));
  }, []);

  const resetAllOverlays = useCallback(() => {
    setOverlayStates(initialStates);
  }, []);

  const actions: OverlayActions = {
    toggleIntegrityMonitor,
    openPerformanceDashboard,
    closePerformanceDashboard,
    toggleChartExample,
    toggleCacheStats,
    togglePerformanceMonitor,
    toggleAdvancedSettings,
    toggleAlertCenter,
    openAlertCenter,
    closeAlertCenter,
    resetAllOverlays,
  };

  return {
    overlayStates,
    ...actions,
  };
};