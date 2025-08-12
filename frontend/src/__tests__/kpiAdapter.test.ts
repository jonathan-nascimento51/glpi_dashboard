import { describe, it, expect, beforeAll, afterEach, afterAll } from 'vitest';
import { server } from '../mocks/server';
import { http, HttpResponse } from 'msw';
import { Kpi, Kpis, toKpiVM } from '../adapters/kpiAdapter';
import { z } from 'zod';

// Setup MSW
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('KPI Adapter', () => {
  describe('Zod validation', () => {
    it('should validate valid KPI data', () => {
      const validKpi = {
        level: 'N1',
        total: 20,
        open: 5,
        in_progress: 10,
        closed: 5
      };

      const result = Kpi.safeParse(validKpi);
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toEqual(validKpi);
      }
    });

    it('should reject invalid KPI data', () => {
      const invalidKpi = {
        level: 'INVALID',
        total: 'not a number',
        open: -1,
        in_progress: 10
        // missing closed field
      };

      const result = Kpi.safeParse(invalidKpi);
      expect(result.success).toBe(false);
    });

    it('should validate array of KPIs', () => {
      const validKpis = [
        { level: 'N1', total: 20, open: 5, in_progress: 10, closed: 5 },
        { level: 'N2', total: 12, open: 2, in_progress: 7, closed: 3 }
      ];

      const result = Kpis.safeParse(validKpis);
      expect(result.success).toBe(true);
    });
  });

  describe('toKpiVM transformation', () => {
    it('should transform valid KPI data to KpiVM', () => {
      const kpiData = [
        { level: 'N1', total: 20, open: 5, in_progress: 10, closed: 5 },
        { level: 'N2', total: 12, open: 2, in_progress: 7, closed: 3 }
      ];

      const result = toKpiVM(kpiData);
      
      expect(result).toHaveLength(2);
      expect(result[0]).toEqual({
        level: 'N1',
        totals: {
          total: 20,
          open: 5,
          inProgress: 10,
          closed: 5
        }
      });
      expect(result[1]).toEqual({
        level: 'N2',
        totals: {
          total: 12,
          open: 2,
          inProgress: 7,
          closed: 3
        }
      });
    });

    it('should throw error for invalid KPI data', () => {
      const invalidData = [
        { level: 'INVALID', total: 'not a number' }
      ];

      expect(() => toKpiVM(invalidData)).toThrow();
    });
  });

  describe('MSW integration', () => {
    it('should fetch and transform KPI data successfully', async () => {
      // Use the default handler from handlers.ts
      const response = await fetch('http://localhost:8000/api/v1/kpis');
      const data = await response.json();
      
      expect(response.ok).toBe(true);
      expect(data).toHaveLength(4);
      
      // Test transformation
      const transformed = toKpiVM(data);
      expect(transformed).toHaveLength(4);
      expect(transformed[0].level).toBe('N1');
      expect(transformed[0].totals.inProgress).toBe(10);
      expect(transformed[0].totals.total).toBe(20);
    });

    it('should handle API errors gracefully', async () => {
      // Override handler to return error
      server.use(
        http.get('http://localhost:8000/api/v1/kpis', () => {
          return HttpResponse.json(
            { error: 'Internal Server Error' },
            { status: 500 }
          );
        })
      );

      const response = await fetch('http://localhost:8000/api/v1/kpis');
      expect(response.status).toBe(500);
    });

    it('should handle malformed API response', async () => {
      // Override handler to return malformed data
      server.use(
        http.get('http://localhost:8000/api/v1/kpis', () => {
          return HttpResponse.json([
            { level: 'INVALID', total: 'not a number' }
          ]);
        })
      );

      const response = await fetch('http://localhost:8000/api/v1/kpis');
      const data = await response.json();
      
      expect(response.ok).toBe(true);
      expect(() => toKpiVM(data)).toThrow();
    });
  });
});
