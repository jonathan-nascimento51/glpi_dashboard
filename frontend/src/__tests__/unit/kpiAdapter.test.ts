import { describe, it, expect } from 'vitest';
import { toKpiVM, Kpi, Kpis } from '../../adapters/kpiAdapter';
import { z } from 'zod';

describe('kpiAdapter', () => {
  describe('Kpi schema validation', () => {
    it('deve validar um KPI válido', () => {
      const validKpi = {
        level: 'N1' as const,
        total: 100,
        open: 25,
        in_progress: 30,
        closed: 45
      };

      expect(() => Kpi.parse(validKpi)).not.toThrow();
      const result = Kpi.parse(validKpi);
      expect(result).toEqual(validKpi);
    });

    it('deve rejeitar KPI com level inválido', () => {
      const invalidKpi = {
        level: 'N5',
        total: 100,
        open: 25,
        in_progress: 30,
        closed: 45
      };

      expect(() => Kpi.parse(invalidKpi)).toThrow();
    });

    it('deve rejeitar KPI com números negativos', () => {
      const invalidKpi = {
        level: 'N1' as const,
        total: -1,
        open: 25,
        in_progress: 30,
        closed: 45
      };

      expect(() => Kpi.parse(invalidKpi)).toThrow();
    });

    it('deve rejeitar KPI com números decimais', () => {
      const invalidKpi = {
        level: 'N1' as const,
        total: 100.5,
        open: 25,
        in_progress: 30,
        closed: 45
      };

      expect(() => Kpi.parse(invalidKpi)).toThrow();
    });

    it('deve rejeitar KPI com campos obrigatórios ausentes', () => {
      const invalidKpi = {
        level: 'N1' as const,
        total: 100,
        // open ausente
        in_progress: 30,
        closed: 45
      };

      expect(() => Kpi.parse(invalidKpi)).toThrow();
    });
  });

  describe('Kpis array validation', () => {
    it('deve validar array de KPIs válidos', () => {
      const validKpis = [
        {
          level: 'N1' as const,
          total: 100,
          open: 25,
          in_progress: 30,
          closed: 45
        },
        {
          level: 'N2' as const,
          total: 80,
          open: 20,
          in_progress: 25,
          closed: 35
        }
      ];

      expect(() => Kpis.parse(validKpis)).not.toThrow();
      const result = Kpis.parse(validKpis);
      expect(result).toEqual(validKpis);
    });

    it('deve validar array vazio', () => {
      expect(() => Kpis.parse([])).not.toThrow();
      const result = Kpis.parse([]);
      expect(result).toEqual([]);
    });

    it('deve rejeitar array com KPI inválido', () => {
      const invalidKpis = [
        {
          level: 'N1' as const,
          total: 100,
          open: 25,
          in_progress: 30,
          closed: 45
        },
        {
          level: 'INVALID',
          total: 80,
          open: 20,
          in_progress: 25,
          closed: 35
        }
      ];

      expect(() => Kpis.parse(invalidKpis)).toThrow();
    });
  });

  describe('toKpiVM transformation', () => {
    it('deve transformar KPI único corretamente', () => {
      const rawData = [{
        level: 'N1' as const,
        total: 100,
        open: 25,
        in_progress: 30,
        closed: 45
      }];

      const result = toKpiVM(rawData);

      expect(result).toHaveLength(1);
      expect(result[0]).toEqual({
        level: 'N1',
        totals: {
          open: 25,
          inProgress: 30,
          closed: 45,
          total: 100
        }
      });
    });

    it('deve transformar múltiplos KPIs corretamente', () => {
      const rawData = [
        {
          level: 'N1' as const,
          total: 100,
          open: 25,
          in_progress: 30,
          closed: 45
        },
        {
          level: 'N2' as const,
          total: 80,
          open: 20,
          in_progress: 25,
          closed: 35
        },
        {
          level: 'N3' as const,
          total: 60,
          open: 15,
          in_progress: 20,
          closed: 25
        }
      ];

      const result = toKpiVM(rawData);

      expect(result).toHaveLength(3);
      expect(result[0].level).toBe('N1');
      expect(result[1].level).toBe('N2');
      expect(result[2].level).toBe('N3');
      
      expect(result[0].totals.inProgress).toBe(30);
      expect(result[1].totals.inProgress).toBe(25);
      expect(result[2].totals.inProgress).toBe(20);
    });

    it('deve transformar array vazio corretamente', () => {
      const rawData: any[] = [];
      const result = toKpiVM(rawData);
      expect(result).toEqual([]);
    });

    it('deve lan�ar erro para dados inválidos', () => {
      const invalidData = [{
        level: 'INVALID',
        total: 100,
        open: 25,
        in_progress: 30,
        closed: 45
      }];

      expect(() => toKpiVM(invalidData)).toThrow();
    });

    it('deve lan�ar erro para dados com tipos incorretos', () => {
      const invalidData = [{
        level: 'N1' as const,
        total: '100', // string ao invés de number
        open: 25,
        in_progress: 30,
        closed: 45
      }];

      expect(() => toKpiVM(invalidData)).toThrow();
    });

    it('deve lan�ar erro para null ou undefined', () => {
      expect(() => toKpiVM(null)).toThrow();
      expect(() => toKpiVM(undefined)).toThrow();
    });

    it('deve preservar todos os níveis de KPI', () => {
      const rawData = [
        { level: 'N1' as const, total: 100, open: 25, in_progress: 30, closed: 45 },
        { level: 'N2' as const, total: 80, open: 20, in_progress: 25, closed: 35 },
        { level: 'N3' as const, total: 60, open: 15, in_progress: 20, closed: 25 },
        { level: 'N4' as const, total: 40, open: 10, in_progress: 15, closed: 15 }
      ];

      const result = toKpiVM(rawData);

      expect(result).toHaveLength(4);
      expect(result.map(kpi => kpi.level)).toEqual(['N1', 'N2', 'N3', 'N4']);
    });

    it('deve manter a ordem dos KPIs', () => {
      const rawData = [
        { level: 'N3' as const, total: 60, open: 15, in_progress: 20, closed: 25 },
        { level: 'N1' as const, total: 100, open: 25, in_progress: 30, closed: 45 },
        { level: 'N2' as const, total: 80, open: 20, in_progress: 25, closed: 35 }
      ];

      const result = toKpiVM(rawData);

      expect(result[0].level).toBe('N3');
      expect(result[1].level).toBe('N1');
      expect(result[2].level).toBe('N2');
    });
  });
});

