import { describe, it, expect } from 'vitest';
import {
  validateMetricsData,
  validateTechnicianRanking,
  validateSystemStatus,
  isValidMetricsData,
  isValidTechnicianRanking,
  isValidSystemStatus,
  MetricsDataSchema,
  TechnicianRankingSchema,
  SystemStatusSchema,
} from '../types/validation';

describe('Data Validation', () => {
  describe('MetricsData Validation', () => {
    it('should validate correct metrics data', () => {
      const validData = {
        success: true,
        message: 'KPIs obtidos do GLPI',
        timestamp: '2025-01-11T03:25:00Z',
        tempo_execucao: 0.5,
        niveis: {
          N1: {
            novos: 5,
            progresso: 3,
            pendentes: 2,
            resolvidos: 10,
            tendencia_novos: 1.2,
            tendencia_progresso: -0.5,
            tendencia_pendentes: 0.8,
            tendencia_resolvidos: 2.1,
          },
          N2: {
            novos: 3,
            progresso: 2,
            pendentes: 1,
            resolvidos: 8,
            tendencia_novos: 0.8,
            tendencia_progresso: -0.2,
            tendencia_pendentes: 0.3,
            tendencia_resolvidos: 1.5,
          },
          N3: {
            novos: 2,
            progresso: 1,
            pendentes: 0,
            resolvidos: 5,
            tendencia_novos: 0.5,
            tendencia_progresso: 0.1,
            tendencia_pendentes: -0.1,
            tendencia_resolvidos: 1.0,
          },
          N4: {
            novos: 1,
            progresso: 0,
            pendentes: 0,
            resolvidos: 3,
            tendencia_novos: 0.2,
            tendencia_progresso: 0.0,
            tendencia_pendentes: 0.0,
            tendencia_resolvidos: 0.8,
          },
        },
      };

      const result = validateMetricsData(validData);
      expect(result).toEqual(validData);
      expect(isValidMetricsData(validData)).toBe(true);
    });

    it('should return fallback for invalid metrics data', () => {
      const invalidData = {
        success: 'not a boolean',
        message: 123,
        timestamp: null,
      };

      const result = validateMetricsData(invalidData);
      expect(result.success).toBe(false);
      expect(result.message).toBe('Invalid data received');
      expect(result.niveis).toBeDefined();
      expect(isValidMetricsData(invalidData)).toBe(false);
    });

    it('should handle missing niveis data', () => {
      const dataWithoutNiveis = {
        success: true,
        message: 'Test',
        timestamp: '2025-01-11T03:25:00Z',
        tempo_execucao: 0.5,
      };

      const result = validateMetricsData(dataWithoutNiveis);
      expect(result.success).toBe(false);
      expect(result.niveis).toBeDefined();
    });

    it('should validate negative numbers correctly', () => {
      const dataWithNegatives = {
        success: true,
        message: 'Test',
        timestamp: '2025-01-11T03:25:00Z',
        tempo_execucao: 0.5,
        niveis: {
          N1: {
            novos: -1, // Invalid: negative number
            progresso: 3,
            pendentes: 2,
            resolvidos: 10,
            tendencia_novos: 1.2,
            tendencia_progresso: -0.5,
            tendencia_pendentes: 0.8,
            tendencia_resolvidos: 2.1,
          },
          N2: { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, tendencia_novos: 0, tendencia_progresso: 0, tendencia_pendentes: 0, tendencia_resolvidos: 0 },
          N3: { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, tendencia_novos: 0, tendencia_progresso: 0, tendencia_pendentes: 0, tendencia_resolvidos: 0 },
          N4: { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0, tendencia_novos: 0, tendencia_progresso: 0, tendencia_pendentes: 0, tendencia_resolvidos: 0 },
        },
      };

      const result = validateMetricsData(dataWithNegatives);
      expect(result.success).toBe(false); // Should fallback due to validation error
    });
  });

  describe('TechnicianRanking Validation', () => {
    it('should validate correct ranking data', () => {
      const validRanking = [
        {
          id: '1',
          name: 'João Silva',
          level: 'N1',
          rank: 1,
          total: 25,
          score: 95.5,
        },
        {
          id: '2',
          nome: 'Maria Santos', // Using 'nome' instead of 'name'
          level: 'N2',
          rank: 2,
          total: 20,
        },
      ];

      const result = validateTechnicianRanking(validRanking);
      expect(result).toEqual(validRanking);
      expect(isValidTechnicianRanking(validRanking)).toBe(true);
    });

    it('should return empty array for invalid ranking data', () => {
      const invalidRanking = [
        {
          id: '1',
          // Missing name/nome
          level: 'N1',
          rank: 0, // Invalid: rank must be >= 1
          total: -5, // Invalid: total must be >= 0
        },
      ];

      const result = validateTechnicianRanking(invalidRanking);
      expect(result).toEqual([]);
      expect(isValidTechnicianRanking(invalidRanking)).toBe(false);
    });

    it('should require either name or nome', () => {
      const rankingWithoutName = [
        {
          id: '1',
          level: 'N1',
          rank: 1,
          total: 25,
        },
      ];

      const result = validateTechnicianRanking(rankingWithoutName);
      expect(result).toEqual([]);
    });
  });

  describe('SystemStatus Validation', () => {
    it('should validate correct status data', () => {
      const validStatus = {
        api_status: 'online',
        database_status: 'connected',
        glpi_connection: true,
        ultima_atualizacao: '2025-01-11T03:25:00Z',
      };

      const result = validateSystemStatus(validStatus);
      expect(result).toEqual(validStatus);
      expect(isValidSystemStatus(validStatus)).toBe(true);
    });

    it('should return fallback for invalid status data', () => {
      const invalidStatus = {
        api_status: 123, // Invalid: should be string
        database_status: null,
        glpi_connection: 'yes', // Invalid: should be boolean
      };

      const result = validateSystemStatus(invalidStatus);
      expect(result.api_status).toBe('unknown');
      expect(result.database_status).toBe('unknown');
      expect(result.glpi_connection).toBe(false);
      expect(isValidSystemStatus(invalidStatus)).toBe(false);
    });

    it('should handle missing optional fields', () => {
      const minimalStatus = {
        api_status: 'online',
        database_status: 'connected',
        glpi_connection: true,
      };

      const result = validateSystemStatus(minimalStatus);
      expect(result).toEqual(minimalStatus);
      expect(isValidSystemStatus(minimalStatus)).toBe(true);
    });
  });

  describe('Edge Cases', () => {
    it('should handle null and undefined inputs', () => {
      expect(() => validateMetricsData(null)).not.toThrow();
      expect(() => validateMetricsData(undefined)).not.toThrow();
      expect(() => validateTechnicianRanking(null)).not.toThrow();
      expect(() => validateSystemStatus(undefined)).not.toThrow();
    });

    it('should handle empty objects and arrays', () => {
      const emptyMetrics = validateMetricsData({});
      expect(emptyMetrics.success).toBe(false);

      const emptyRanking = validateTechnicianRanking([]);
      expect(emptyRanking).toEqual([]);

      const emptyStatus = validateSystemStatus({});
      expect(emptyStatus.glpi_connection).toBe(false);
    });

    it('should handle malformed JSON-like strings', () => {
      const malformedData = '{"success": true, "message": "test"';
      const result = validateMetricsData(malformedData);
      expect(result.success).toBe(false);
    });
  });
});
