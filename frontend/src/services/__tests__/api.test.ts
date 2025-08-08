import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import axios, { AxiosError } from 'axios';
import { fetchDashboardMetrics, apiService } from '../api';
import type { DashboardMetrics } from '../../types/dashboard';

// Mock axios
vi.mock('axios');
const mockedAxios = axios as any;

describe('API Service', () => {
  const mockMetrics: DashboardMetrics = {
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
    // Reset axios mock
    mockedAxios.create.mockReturnValue({
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() }
      }
    });
  });

  afterEach(() => {
    vi.clearAllTimers();
  });

  describe('fetchDashboardMetrics', () => {
    it('should fetch dashboard metrics successfully', async () => {
      const mockResponse = {
        data: {
          success: true,
          data: mockMetrics
        },
        status: 200,
        statusText: 'OK'
      };

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse.data)
      });

      const result = await fetchDashboardMetrics('2024-01-01', '2024-01-31');

      expect(result).toEqual(mockMetrics);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/dashboard/metrics'),
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          }),
          signal: expect.any(AbortSignal)
        })
      );
    });

    it('should validate date parameters', async () => {
      // Test invalid date format
      await expect(
        fetchDashboardMetrics('01/01/2024', '2024-01-31')
      ).rejects.toThrow('Invalid date format');

      // Test end date before start date
      await expect(
        fetchDashboardMetrics('2024-01-31', '2024-01-01')
      ).rejects.toThrow('End date must be after start date');

      // Test date range too large
      await expect(
        fetchDashboardMetrics('2022-01-01', '2024-12-31')
      ).rejects.toThrow('Date range cannot exceed 2 years');
    });

    it('should sanitize date parameters', async () => {
      const mockResponse = {
        data: {
          success: true,
          data: mockMetrics
        }
      };

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockResponse.data)
      });

      // Test with dates that need sanitization
      await fetchDashboardMetrics('  2024-01-01  ', '2024-01-31\n');

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('start_date=2024-01-01&end_date=2024-01-31'),
        expect.any(Object)
      );
    });

    it('should handle timeout errors', async () => {
      global.fetch = vi.fn().mockImplementation(() => 
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Request timeout')), 100)
        )
      );

      await expect(
        fetchDashboardMetrics('2024-01-01', '2024-01-31')
      ).rejects.toThrow('Request timeout');
    });

    it('should handle network errors', async () => {
      global.fetch = vi.fn().mockRejectedValue(new Error('Network error'));

      await expect(
        fetchDashboardMetrics('2024-01-01', '2024-01-31')
      ).rejects.toThrow('Network error');
    });

    it('should handle HTTP error responses', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: () => Promise.resolve({
          success: false,
          error: 'Server error'
        })
      });

      await expect(
        fetchDashboardMetrics('2024-01-01', '2024-01-31')
      ).rejects.toThrow('Server error');
    });

    it('should validate API response structure', async () => {
      const invalidResponse = {
        data: {
          success: true,
          data: {
            // Missing required fields
            total_tickets: 'invalid' // Should be number
          }
        }
      };

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: () => Promise.resolve(invalidResponse.data)
      });

      await expect(
        fetchDashboardMetrics('2024-01-01', '2024-01-31')
      ).rejects.toThrow('Invalid API response structure');
    });

    it('should validate data consistency', async () => {
      const inconsistentData = {
        ...mockMetrics,
        total_tickets: 100,
        open_tickets: 50,
        closed_tickets: 60, // 50 + 60 + 5 = 115, not 100
        pending_tickets: 5
      };

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: () => Promise.resolve({
          success: true,
          data: inconsistentData
        })
      });

      await expect(
        fetchDashboardMetrics('2024-01-01', '2024-01-31')
      ).rejects.toThrow('Data consistency validation failed');
    });

    it('should implement retry logic for network errors', async () => {
      let callCount = 0;
      global.fetch = vi.fn().mockImplementation(() => {
        callCount++;
        if (callCount < 3) {
          return Promise.reject(new Error('Network error'));
        }
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve({
            success: true,
            data: mockMetrics
          })
        });
      });

      const result = await fetchDashboardMetrics('2024-01-01', '2024-01-31');

      expect(result).toEqual(mockMetrics);
      expect(global.fetch).toHaveBeenCalledTimes(3);
    });

    it('should log performance metrics', async () => {
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
      
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: () => Promise.resolve({
          success: true,
          data: mockMetrics
        })
      });

      await fetchDashboardMetrics('2024-01-01', '2024-01-31');

      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('Dashboard metrics request completed')
      );

      consoleSpy.mockRestore();
    });

    it('should warn about slow requests', async () => {
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
      
      // Mock slow response (> 2 seconds)
      global.fetch = vi.fn().mockImplementation(() => 
        new Promise(resolve => 
          setTimeout(() => resolve({
            ok: true,
            status: 200,
            json: () => Promise.resolve({
              success: true,
              data: mockMetrics
            })
          }), 2100)
        )
      );

      await fetchDashboardMetrics('2024-01-01', '2024-01-31');

      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('Slow request detected')
      );

      consoleSpy.mockRestore();
    });
  });

  describe('apiService.getMetrics', () => {
    it('should get metrics with caching', async () => {
      const mockAxiosInstance = {
        get: vi.fn().mockResolvedValue({
          data: {
            success: true,
            data: mockMetrics
          }
        })
      };
      
      mockedAxios.create.mockReturnValue(mockAxiosInstance);

      const result1 = await apiService.getMetrics('2024-01-01', '2024-01-31');
      const result2 = await apiService.getMetrics('2024-01-01', '2024-01-31');

      expect(result1).toEqual(mockMetrics);
      expect(result2).toEqual(mockMetrics);
      
      // Should only make one API call due to caching
      expect(mockAxiosInstance.get).toHaveBeenCalledTimes(1);
    });

    it('should validate date parameters', async () => {
      await expect(
        apiService.getMetrics('invalid-date', '2024-01-31')
      ).rejects.toThrow('Invalid date format');
    });

    it('should handle API errors gracefully', async () => {
      const mockAxiosInstance = {
        get: vi.fn().mockRejectedValue(new AxiosError('API Error', '500'))
      };
      
      mockedAxios.create.mockReturnValue(mockAxiosInstance);

      // Should return fallback data instead of throwing
      const result = await apiService.getMetrics('2024-01-01', '2024-01-31');
      
      expect(result).toBeDefined();
      expect(result.total_tickets).toBe(0); // Fallback data
    });
  });

  describe('apiService.getSystemStatus', () => {
    it('should get system status', async () => {
      const mockStatus = {
        api_status: 'healthy',
        database_status: 'connected',
        last_update: new Date().toISOString()
      };

      const mockAxiosInstance = {
        get: vi.fn().mockResolvedValue({
          data: {
            success: true,
            data: mockStatus
          }
        })
      };
      
      mockedAxios.create.mockReturnValue(mockAxiosInstance);

      const result = await apiService.getSystemStatus();

      expect(result).toEqual(mockStatus);
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/system/status');
    });

    it('should handle system status errors', async () => {
      const mockAxiosInstance = {
        get: vi.fn().mockRejectedValue(new Error('System error'))
      };
      
      mockedAxios.create.mockReturnValue(mockAxiosInstance);

      const result = await apiService.getSystemStatus();
      
      // Should return fallback status
      expect(result.api_status).toBe('unknown');
    });
  });

  describe('apiService.getTechnicianRanking', () => {
    it('should get technician ranking', async () => {
      const mockRanking = [
        {
          name: 'John Doe',
          tickets_resolved: 25,
          avg_resolution_time: 150
        }
      ];

      const mockAxiosInstance = {
        get: vi.fn().mockResolvedValue({
          data: {
            success: true,
            data: mockRanking
          }
        })
      };
      
      mockedAxios.create.mockReturnValue(mockAxiosInstance);

      const result = await apiService.getTechnicianRanking('2024-01-01', '2024-01-31');

      expect(result).toEqual(mockRanking);
      expect(mockAxiosInstance.get).toHaveBeenCalledWith(
        '/technicians/ranking',
        expect.objectContaining({
          params: {
            start_date: '2024-01-01',
            end_date: '2024-01-31'
          }
        })
      );
    });
  });

  describe('Cache Management', () => {
    it('should clear all caches', () => {
      // This would test the clearAllCaches function
      expect(() => apiService.clearAllCaches()).not.toThrow();
    });

    it('should respect cache TTL', async () => {
      vi.useFakeTimers();
      
      const mockAxiosInstance = {
        get: vi.fn().mockResolvedValue({
          data: {
            success: true,
            data: mockMetrics
          }
        })
      };
      
      mockedAxios.create.mockReturnValue(mockAxiosInstance);

      // First call
      await apiService.getMetrics('2024-01-01', '2024-01-31');
      
      // Advance time beyond cache TTL (5 minutes)
      vi.advanceTimersByTime(6 * 60 * 1000);
      
      // Second call should make new API request
      await apiService.getMetrics('2024-01-01', '2024-01-31');

      expect(mockAxiosInstance.get).toHaveBeenCalledTimes(2);
      
      vi.useRealTimers();
    });
  });

  describe('Error Categorization', () => {
    it('should categorize timeout errors', async () => {
      const timeoutError = new Error('Request timeout');
      timeoutError.name = 'TimeoutError';
      
      global.fetch = vi.fn().mockRejectedValue(timeoutError);

      await expect(
        fetchDashboardMetrics('2024-01-01', '2024-01-31')
      ).rejects.toThrow('Request timeout');
    });

    it('should categorize network errors', async () => {
      const networkError = new Error('Network error');
      networkError.name = 'NetworkError';
      
      global.fetch = vi.fn().mockRejectedValue(networkError);

      await expect(
        fetchDashboardMetrics('2024-01-01', '2024-01-31')
      ).rejects.toThrow('Network connection failed');
    });

    it('should categorize authentication errors', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 401,
        statusText: 'Unauthorized',
        json: () => Promise.resolve({
          success: false,
          error: 'Authentication failed'
        })
      });

      await expect(
        fetchDashboardMetrics('2024-01-01', '2024-01-31')
      ).rejects.toThrow('Authentication failed');
    });

    it('should categorize server errors', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: () => Promise.resolve({
          success: false,
          error: 'Internal server error'
        })
      });

      await expect(
        fetchDashboardMetrics('2024-01-01', '2024-01-31')
      ).rejects.toThrow('Server error occurred');
    });
  });
});