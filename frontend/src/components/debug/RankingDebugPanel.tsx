import React, { useState, useEffect } from 'react';
import { RankingDebugger } from '../../debug/rankingDebug';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { RefreshCw, Download, Trash2, Eye, EyeOff } from 'lucide-react';

interface RankingDebugPanelProps {
  isVisible?: boolean;
  onToggle?: () => void;
}

export const RankingDebugPanel: React.FC<RankingDebugPanelProps> = ({ 
  isVisible = false, 
  onToggle 
}) => {
  const [logs, setLogs] = useState<any[]>([]);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [filter, setFilter] = useState<string>('all');

  const refreshLogs = () => {
    setLogs(RankingDebugger.getLogs());
  };

  useEffect(() => {
    if (isVisible) {
      refreshLogs();
      
      if (autoRefresh) {
        const interval = setInterval(refreshLogs, 1000);
        return () => clearInterval(interval);
      }
    }
  }, [isVisible, autoRefresh]);

  const filteredLogs = logs.filter(log => {
    if (filter === 'all') return true;
    if (filter === 'ranking') return log.event.toLowerCase().includes('ranking') || log.event.toLowerCase().includes('technician');
    if (filter === 'cache') return log.event.toLowerCase().includes('cache');
    if (filter === 'api') return log.source === 'api';
    return log.source === filter;
  });

  const getEventColor = (event: string) => {
    if (event.includes('error')) return 'bg-red-100 text-red-800';
    if (event.includes('cache')) return 'bg-blue-100 text-blue-800';
    if (event.includes('api')) return 'bg-green-100 text-green-800';
    if (event.includes('ranking')) return 'bg-purple-100 text-purple-800';
    return 'bg-gray-100 text-gray-800';
  };

  if (!isVisible) {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        <Button
          onClick={onToggle}
          variant="outline"
          size="sm"
          className="bg-white shadow-lg"
        >
          <Eye className="w-4 h-4 mr-2" />
          Debug Ranking
        </Button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 w-96 max-h-96">
      <Card className="shadow-xl">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-medium">
              🔍 Ranking Debug Panel
            </CardTitle>
            <div className="flex items-center gap-2">
              <Button
                onClick={() => setAutoRefresh(!autoRefresh)}
                variant="ghost"
                size="sm"
                className={autoRefresh ? 'text-green-600' : 'text-gray-400'}
              >
                <RefreshCw className={`w-3 h-3 ${autoRefresh ? 'animate-spin' : ''}`} />
              </Button>
              <Button
                onClick={RankingDebugger.exportLogs}
                variant="ghost"
                size="sm"
              >
                <Download className="w-3 h-3" />
              </Button>
              <Button
                onClick={() => {
                  RankingDebugger.clearLogs();
                  refreshLogs();
                }}
                variant="ghost"
                size="sm"
              >
                <Trash2 className="w-3 h-3" />
              </Button>
              <Button
                onClick={onToggle}
                variant="ghost"
                size="sm"
              >
                <EyeOff className="w-3 h-3" />
              </Button>
            </div>
          </div>
          
          <div className="flex gap-1 mt-2">
            {['all', 'ranking', 'cache', 'api', 'useDashboard', 'RankingTable'].map(f => (
              <Button
                key={f}
                onClick={() => setFilter(f)}
                variant={filter === f ? 'default' : 'outline'}
                size="sm"
                className="text-xs px-2 py-1 h-6"
              >
                {f}
              </Button>
            ))}
          </div>
        </CardHeader>
        
        <CardContent className="p-2">
          <div className="max-h-64 overflow-y-auto space-y-1 text-xs">
            {filteredLogs.slice(-20).reverse().map((log, index) => (
              <div key={index} className="border rounded p-2 bg-gray-50">
                <div className="flex items-center justify-between mb-1">
                  <Badge className={getEventColor(log.event)}>
                    {log.event}
                  </Badge>
                  <span className="text-gray-500 text-xs">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <div className="text-gray-600 mb-1">
                  <strong>Source:</strong> {log.source}
                </div>
                <div className="bg-white p-1 rounded text-xs font-mono overflow-x-auto">
                  {JSON.stringify(log.data, null, 2)}
                </div>
              </div>
            ))}
            
            {filteredLogs.length === 0 && (
              <div className="text-center text-gray-500 py-4">
                Nenhum log encontrado
              </div>
            )}
          </div>
          
          <div className="mt-2 pt-2 border-t text-xs text-gray-500">
            Total: {logs.length} logs | Filtrados: {filteredLogs.length}
          </div>
          
          <div className="mt-2">
            <Button
              onClick={RankingDebugger.analyzeRankingFlow}
              variant="outline"
              size="sm"
              className="w-full text-xs"
            >
              Analisar Fluxo do Ranking
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};