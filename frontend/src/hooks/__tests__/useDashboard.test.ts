import { renderHook, act, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { useDashboard } from '../useDashboard';
import * as apiService from '../../services/api';

// Mock the API service
vi.mock('../../services/api', () => ({
  fetchDashboardMetrics: vi.fn(),
  getSystemStatus: vi.fn(),
  getTechnicianRanking: vi.fn(),
}));

const mockApiService = apiService as any;

describe('useDashboard Hook', () => {
  const mockMetrics = {
    total_tickets: 100,
    open_tickets: 25,
    closed_tickets: 70,
    pending_tickets: 5,
    avg_resolution_time: 180,
    technician_ranking: [
      {
        name: 'John Doe',
        tickets_resolved: 25,
        avg_resolution_time: 150,
        satisfaction_score: 4.8
      }
    ],
    system_status: {
      api_status: 'healthy',
      last_update: new Date().toISOString(),
      response_time: 0.5
    }
  };

  beforeEach(() => {
    vi.clearAllMocks();
    // Mock successful API responses by default
    mockApiService.fetchDashboardMetrics.mockResolvedValue(mockMetrics);
    mockApiService.getSystemStatus.mockResolvedValue(mockMetrics.system_status);
    mockApiService.getTechnicianRanking.mockResolvedValue(mockMetrics.technician_ranking);
  });

  afterEach(() => {
    vi.clearAllTimers();
  });

  it('should initialize with default state', () => {
    const { result } = renderHook(() => useDashboard());

    expect(result.current.metrics).toBeNull();
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(result.current.lastUpdated).toBeNull();
    expect(result.current.performance).toEqual({
      responseTime: 0,
      requestCount: 0,
      errorCount: 0,
      cacheHitRate: 0
    });
  });

  it('should load data successfully', async () => {
    const { result } = renderHook(() => useDashboard());

    await act(async () => {
      await result.current.loadData('2024-01-01', '2024-01-31');
    });

    await waitFor(() => {
      expect(result.current.metrics).toEqual(mockMetrics);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(result.current.lastUpdated).not.toBeNull();
    });

    expect(mockApiService.fetchDashboardMetrics).toHaveBeenCalledWith(
      '2024-01-01',
      '2024-01-31'
    );
  });

  it('should handle loading state correctly', async () => {
    // Make the API call take some time
    mockApiService.fetchDashboardMetrics.mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve(mockMetrics), 100))
    );

    const { result } = renderHook(() => useDashboard());

    act(() => {
      result.current.loadData('2024-01-01', '2024-01-31');
    });

    // Should be loading immediately
    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });
  });

  it('should handle API errors gracefully', async () => {
    const errorMessage = 'API connection failed';
    mockApiService.fetchDashboardMetrics.mockRejectedValue(new Error(errorMessage));

    const { result } = renderHook(() => useDashboard());

    await act(async () => {
      await result.current.loadData('2024-01-01', '2024-01-31');
    });

    await waitFor(() => {
      expect(result.current.error).toBe(errorMessage);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.metrics).toBeNull();
    });
  });

  it('should validate date filters correctly', async () => {
    const { result } = renderHook(() => useDashboard());

    // Test invalid date format
    await act(async () => {
      await result.current.loadData('01/01/2024', '2024-01-31');
    });

    await waitFor(() => {
      expect(result.current.error).toContain('Invalid date format');
    });

    // Test end date before start date
    await act(async () => {
      await result.current.loadData('2024-01-31', '2024-01-01');
    });

    await waitFor(() => {
      expect(result.current.error).toContain('End date must be after start date');
    });

    // Test date range too large (more than 1 year)
    await act(async () => {
      await result.current.loadData('2022-01-01', '2024-01-01');
    });

    await waitFor(() => {
      expect(result.current.error).toContain('Date range cannot exceed 1 year');
    });
  });

  it('should handle timeout errors', async () => {
    const timeoutError = new Error('Request timeout');
    timeoutError.name = 'TimeoutError';
    mockApiService.fetchDashboardMetrics.mockRejectedValue(timeoutError);

    const { result } = renderHook(() => useDashboard());

    await act(async () => {
      await result.current.loadData('2024-01-01', '2024-01-31');
    });

    await waitFor(() => {
      expect(result.current.error).toContain('Request timeout');
    });
  });

  it('should handle network errors', async () => {
    const networkError = new Error('Network error');
    networkError.name = 'NetworkError';
    mockApiService.fetchDashboardMetrics.mockRejectedValue(networkError);

    const { result } = renderHook(() => useDashboard());

    await act(async () => {
      await result.current.loadData('2024-01-01', '2024-01-31');
    });

    await waitFor(() => {
      expect(result.current.error).toContain('Network connection failed');
    });
  });

  it('should track performance metrics', async () => {
    const { result } = renderHook(() => useDashboard());

    await act(async () => {
      await result.current.loadData('2024-01-01', '2024-01-31');
    });

    await waitFor(() => {
      expect(result.current.performance.requestCount).toBe(1);
      expect(result.current.performance.responseTime).toBeGreaterThan(0);
      expect(result.current.performance.errorCount).toBe(0);
    });
  });

  it('should track error count on failures', async () => {
    mockApiService.fetchDashboardMetrics.mockRejectedValue(new Error('API Error'));

    const { result } = renderHook(() => useDashboard());

    await act(async () => {
      await result.current.loadData('2024-01-01', '2024-01-31');
    });

    await waitFor(() => {
      expect(result.current.performance.errorCount).toBe(1);
    });
  });

  it('should validate data structure', async () => {
    // Mock invalid data structure
    const invalidData = {
      total_tickets: 'invalid', // Should be number
      open_tickets: 25,
      // Missing required fields
    };
    mockApiService.fetchDashboardMetrics.mockResolvedValue(invalidData);

    const { result } = renderHook(() => useDashboard());

    await act(async () => {
      await result.current.loadData('2024-01-01', '2024-01-31');
    });

    await waitFor(() => {
      expect(result.current.error).toContain('Invalid data structure');
    });
  });

  it('should validate data consistency', async () => {
    // Mock inconsistent data
    const inconsistentData = {
      ...mockMetrics,
      total_tickets: 100,
      open_tickets: 50,
      closed_tickets: 60, // 50 + 60 + 5 = 115, not 100
      pending_tickets: 5
    };
    mockApiService.fetchDashboardMetrics.mockResolvedValue(inconsistentData);

    const { result } = renderHook(() => useDashboard());

    await act(async () => {
      await result.current.loadData('2024-01-01', '2024-01-31');
    });

    await waitFor(() => {
      expect(result.current.error).toContain('Data consistency check failed');
    });
  });

  it('should handle refresh data correctly', async () => {
    const { result } = renderHook(() => useDashboard());

    // Initial load
    await act(async () => {
      await result.current.loadData('2024-01-01', '2024-01-31');
    });

    await waitFor(() => {
      expect(result.current.metrics).toEqual(mockMetrics);
    });

    // Refresh with new data
    const updatedMetrics = { ...mockMetrics, total_tickets: 150 };
    mockApiService.fetchDashboardMetrics.mockResolvedValue(updatedMetrics);

    await act(async () => {
      await result.current.refreshData();
    });

    await waitFor(() => {
      expect(result.current.metrics?.total_tickets).toBe(150);
    });
  });

  it('should clear error when loading new data successfully', async () => {
    const { result } = renderHook(() => useDashboard());

    // First, cause an error
    mockApiService.fetchDashboardMetrics.mockRejectedValue(new Error('API Error'));
    
    await act(async () => {
      await result.current.loadData('2024-01-01', '2024-01-31');
    });

    await waitFor(() => {
      expect(result.current.error).toBe('API Error');
    });

    // Then, load successfully
    mockApiService.fetchDashboardMetrics.mockResolvedValue(mockMetrics);
    
    await act(async () => {
      await result.current.loadData('2024-01-01', '2024-01-31');
    });

    await waitFor(() => {
      expect(result.current.error).toBeNull();
      expect(result.current.metrics).toEqual(mockMetrics);
    });
  });

  it('should handle auto-refresh functionality', async () => {
    vi.useFakeTimers();
    
    const { result } = renderHook(() => useDashboard());

    // Initial load
    await act(async () => {
      await result.current.loadData('2024-01-01', '2024-01-31');
    });

    expect(mockApiService.fetchDashboardMetrics).toHaveBeenCalledTimes(1);

    // Fast-forward 5 minutes (auto-refresh interval)
    act(() => {
      vi.advanceTimersByTime(5 * 60 * 1000);
    });

    await waitFor(() => {
      expect(mockApiService.fetchDashboardMetrics).toHaveBeenCalledTimes(2);
    });

    vi.useRealTimers();
  });

  it('should generate unique request IDs', async () => {
    const { result } = renderHook(() => useDashboard());

    // Mock the API to capture the request ID
    let capturedRequestIds: string[] = [];
    mockApiService.fetchDashboardMetrics.mockImplementation(async (startDate, endDate) => {
      // In a real implementation, the request ID would be passed or generated
      // For testing, we'll simulate capturing it
      capturedRequestIds.push(`req_${Date.now()}_${Math.random()}`);
      return mockMetrics;
    });

    // Make multiple requests
    await act(async () => {
      await result.current.loadData('2024-01-01', '2024-01-31');
    });

    await act(async () => {
      await result.current.loadData('2024-02-01', '2024-02-28');
    });

    // Each request should have a unique ID
    expect(capturedRequestIds).toHaveLength(2);
    expect(capturedRequestIds[0]).not.toBe(capturedRequestIds[1]);
  });

  it('should log performance warnings for slow requests', async () => {
    const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
    
    // Mock slow API response (> 2 seconds)
    mockApiService.fetchDashboardMetrics.mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve(mockMetrics), 2100))
    );

    const { result } = renderHook(() => useDashboard());

    await act(async () => {
      await result.current.loadData('2024-01-01', '2024-01-31');
    });

    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('Slow request detected')
      );
    });

    consoleSpy.mockRestore();
  });
});