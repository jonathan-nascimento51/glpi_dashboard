import { z } from 'zod';
export const Kpi = z.object({ level: z.enum(['N1','N2','N3','N4']), total: z.number().int().nonnegative(), open: z.number().int().nonnegative(), in_progress: z.number().int().nonnegative(), closed: z.number().int().nonnegative() });
export const Kpis = z.array(Kpi);
export type KpiVM = { level: 'N1'|'N2'|'N3'|'N4'; totals: { open: number; inProgress: number; closed: number; total: number } };
export function toKpiVM(raw: unknown): KpiVM[] {
  const parsed = Kpis.parse(raw);
  return parsed.map(k => ({ level: k.level, totals: { open: k.open, inProgress: k.in_progress, closed: k.closed, total: k.total } }));
}