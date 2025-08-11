import { useEffect, useState } from 'react';
import { useFlag } from '../flags/unleash';
import { toKpiVM, KpiVM } from '../adapters/kpiAdapter';
export function useKpisRaw() {
  const useV2 = useFlag('use_v2_kpis');
  const [data, setData] = useState<KpiVM[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    const url = (import.meta.env.VITE_API_BASE_URL ?? '/api') + (useV2 ? '/v2/kpis' : '/v1/kpis');
    setLoading(true);
    fetch(url).then(async (r) => {
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const json = await r.json();
      setData(toKpiVM(json));
      setError(null);
    }).catch(e => setError(String(e))).finally(() => setLoading(false));
  }, [useV2]);
  return { data, loading, error, useV2 };
}
