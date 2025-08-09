import React from 'react';
type Props = { title: string; total: number; open: number; inProgress: number; closed: number; loading?: boolean; error?: string | null; };
export const KpiCard: React.FC<Props> = ({ title, total, open, inProgress, closed, loading, error }) => {
  if (loading) return <div className="p-4 border rounded">Carregando...</div>;
  if (error) return <div className="p-4 border rounded text-red-600">Erro: {error}</div>;
  return (<div className="p-4 border rounded"><h3 className="font-semibold">{title}</h3><div>Total: {total}</div><div>Abertos: {open}</div><div>Em Andamento: {inProgress}</div><div>Fechados: {closed}</div></div>);
};