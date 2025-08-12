import React, { useEffect } from 'react';
import { FlagsProvider } from '../flags/unleash';
import { initSentry } from '../observability/sentry';
import { useKpisRaw } from '../api/raw';
import { DashboardCard } from '../domains/dashboard';
function Inner() {
  const { data, loading, error, useV2 } = useKpisRaw();
  useEffect(() => { initSentry(); }, []);
  if (loading) return <div>Carregando...</div>;
  if (error) return <div>Erro: {error}</div>;
  return (<div><div style={{ marginBottom: 8 }}>Flag use_v2_kpis: {String(useV2)}</div><div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 12 }}>{data?.map(k => (<DashboardCard key={k.level} title={k.level} total={k.totals.total} open={k.totals.open} inProgress={k.totals.inProgress} closed={k.totals.closed} loading={false} error={null} />))}</div></div>);
}
export function KpiContainer() { return (<FlagsProvider><Inner/></FlagsProvider>); }
