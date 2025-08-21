/**
 * Centro de Alertas - Componente para exibir e gerenciar alertas de performance
 * 
 * Este componente fornece uma interface completa para visualizar, filtrar
 * e gerenciar alertas do sistema de monitoramento de performance.
 */

import React, { useState, useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Tabs,
  Tab,
  Badge,
  Tooltip,
  Switch,
  FormControlLabel,
  Grid,
  Paper,
  Divider,
  Alert as MuiAlert,
  Collapse,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  CheckCircle as CheckCircleIcon,
  Clear as ClearIcon,
  Settings as SettingsIcon,
  Refresh as RefreshIcon,
  FilterList as FilterIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon
} from '@mui/icons-material';
import {
  useAlerts,
  useAlertStats,
  useCriticalAlerts,
  useAlertConfig,
  useAlertNotifications
} from '../hooks/useAlerts';
import { Alert, AlertConfig } from '../services/alertService';

interface AlertCenterProps {
  open: boolean;
  onClose: () => void;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel({ children, value, index, ...other }: TabPanelProps) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`alert-tabpanel-${index}`}
      aria-labelledby={`alert-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const AlertCenter: React.FC<AlertCenterProps> = ({ open, onClose }) => {
  const {
    alerts,
    activeAlerts,
    resolveAlert,
    resolveAllAlerts,
    clearOldAlerts,
    createAlert,
    isRunning,
    startMonitoring,
    stopMonitoring
  } = useAlerts();
  
  const stats = useAlertStats();
  const { alerts: criticalAlerts, hasUnresolved: hasCriticalUnresolved } = useCriticalAlerts();
  const { config, updateConfig } = useAlertConfig();
  const {
    hasPermission,
    requestPermission,
    enableNotifications,
    disableNotifications,
    notificationsEnabled
  } = useAlertNotifications();

  const [currentTab, setCurrentTab] = useState(0);
  const [filterType, setFilterType] = useState<Alert['type'] | 'all'>('all');
  const [filterCategory, setFilterCategory] = useState<Alert['category'] | 'all'>('all');
  const [showResolved, setShowResolved] = useState(false);
  const [expandedAlert, setExpandedAlert] = useState<string | null>(null);
  const [settingsOpen, setSettingsOpen] = useState(false);

  // Filtrar alertas
  const filteredAlerts = useMemo(() => {
    let filtered = showResolved ? alerts : activeAlerts;
    
    if (filterType !== 'all') {
      filtered = filtered.filter(alert => alert.type === filterType);
    }
    
    if (filterCategory !== 'all') {
      filtered = filtered.filter(alert => alert.category === filterCategory);
    }
    
    return filtered.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
  }, [alerts, activeAlerts, showResolved, filterType, filterCategory]);

  // Obter ícone do alerta
  const getAlertIcon = (type: Alert['type']) => {
    switch (type) {
      case 'critical':
        return <ErrorIcon color="error" />;
      case 'error':
        return <ErrorIcon color="warning" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      case 'info':
        return <InfoIcon color="info" />;
      default:
        return <NotificationsIcon />;
    }
  };

  // Obter cor do alerta
  const getAlertColor = (type: Alert['type']) => {
    switch (type) {
      case 'critical':
        return 'error';
      case 'error':
        return 'warning';
      case 'warning':
        return 'warning';
      case 'info':
        return 'info';
      default:
        return 'default';
    }
  };

  // Formatar timestamp
  const formatTimestamp = (timestamp: Date) => {
    const now = new Date();
    const diff = now.getTime() - timestamp.getTime();
    
    if (diff < 60000) {
      return 'Agora mesmo';
    } else if (diff < 3600000) {
      return `${Math.floor(diff / 60000)} min atrás`;
    } else if (diff < 86400000) {
      return `${Math.floor(diff / 3600000)}h atrás`;
    } else {
      return timestamp.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    }
  };

  // Componente de configurações
  const SettingsDialog = () => (
    <Dialog open={settingsOpen} onClose={() => setSettingsOpen(false)} maxWidth="md" fullWidth>
      <DialogTitle>Configurações de Alertas</DialogTitle>
      <DialogContent>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Monitoramento
            </Typography>
            <FormControlLabel
              control={
                <Switch
                  checked={isRunning}
                  onChange={(e) => e.target.checked ? startMonitoring() : stopMonitoring()}
                />
              }
              label="Ativar monitoramento automático"
            />
          </Grid>
          
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Notificações
            </Typography>
            <FormControlLabel
              control={
                <Switch
                  checked={config.enableNotifications}
                  onChange={(e) => updateConfig({ enableNotifications: e.target.checked })}
                />
              }
              label="Ativar notificações"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={notificationsEnabled}
                  onChange={(e) => e.target.checked ? enableNotifications() : disableNotifications()}
                  disabled={!hasPermission}
                />
              }
              label="Notificações do navegador"
            />
            {!hasPermission && (
              <Button onClick={requestPermission} size="small">
                Solicitar Permissão
              </Button>
            )}
            <FormControlLabel
              control={
                <Switch
                  checked={config.enableSound}
                  onChange={(e) => updateConfig({ enableSound: e.target.checked })}
                />
              }
              label="Som para alertas críticos"
            />
          </Grid>
          
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Thresholds
            </Typography>
            {config.thresholds.map((threshold, index) => (
              <Paper key={threshold.metric} sx={{ p: 2, mb: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  {threshold.metric}
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={3}>
                    <TextField
                      label="Aviso"
                      type="number"
                      value={threshold.warningValue}
                      onChange={(e) => {
                        const newThresholds = [...config.thresholds];
                        newThresholds[index].warningValue = parseFloat(e.target.value);
                        updateConfig({ thresholds: newThresholds });
                      }}
                      size="small"
                      fullWidth
                    />
                  </Grid>
                  <Grid item xs={3}>
                    <TextField
                      label="Erro"
                      type="number"
                      value={threshold.errorValue}
                      onChange={(e) => {
                        const newThresholds = [...config.thresholds];
                        newThresholds[index].errorValue = parseFloat(e.target.value);
                        updateConfig({ thresholds: newThresholds });
                      }}
                      size="small"
                      fullWidth
                    />
                  </Grid>
                  <Grid item xs={3}>
                    <TextField
                      label="Crítico"
                      type="number"
                      value={threshold.criticalValue}
                      onChange={(e) => {
                        const newThresholds = [...config.thresholds];
                        newThresholds[index].criticalValue = parseFloat(e.target.value);
                        updateConfig({ thresholds: newThresholds });
                      }}
                      size="small"
                      fullWidth
                    />
                  </Grid>
                  <Grid item xs={3}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={threshold.enabled}
                          onChange={(e) => {
                            const newThresholds = [...config.thresholds];
                            newThresholds[index].enabled = e.target.checked;
                            updateConfig({ thresholds: newThresholds });
                          }}
                        />
                      }
                      label="Ativo"
                    />
                  </Grid>
                </Grid>
              </Paper>
            ))}
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setSettingsOpen(false)}>Fechar</Button>
      </DialogActions>
    </Dialog>
  );

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box display="flex" alignItems="center" gap={1}>
            <NotificationsIcon />
            <Typography variant="h6">Centro de Alertas</Typography>
            {hasCriticalUnresolved && (
              <Badge badgeContent={criticalAlerts.filter(a => !a.resolved).length} color="error">
                <ErrorIcon color="error" />
              </Badge>
            )}
          </Box>
          <Box>
            <Tooltip title="Configurações">
              <IconButton onClick={() => setSettingsOpen(true)}>
                <SettingsIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Atualizar">
              <IconButton onClick={() => window.location.reload()}>
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        {/* Estatísticas */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={3}>
            <Paper sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="h4" color="primary">
                {stats.total}
              </Typography>
              <Typography variant="body2">Total</Typography>
            </Paper>
          </Grid>
          <Grid item xs={3}>
            <Paper sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="h4" color="warning.main">
                {stats.active}
              </Typography>
              <Typography variant="body2">Ativos</Typography>
            </Paper>
          </Grid>
          <Grid item xs={3}>
            <Paper sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="h4" color="success.main">
                {stats.resolved}
              </Typography>
              <Typography variant="body2">Resolvidos</Typography>
            </Paper>
          </Grid>
          <Grid item xs={3}>
            <Paper sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="h4" color="info.main">
                {stats.recentCount}
              </Typography>
              <Typography variant="body2">Últimas 24h</Typography>
            </Paper>
          </Grid>
        </Grid>

        {/* Filtros */}
        <Box sx={{ mb: 2 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Tipo</InputLabel>
                <Select
                  value={filterType}
                  label="Tipo"
                  onChange={(e) => setFilterType(e.target.value as Alert['type'] | 'all')}
                >
                  <MenuItem value="all">Todos</MenuItem>
                  <MenuItem value="critical">Crítico</MenuItem>
                  <MenuItem value="error">Erro</MenuItem>
                  <MenuItem value="warning">Aviso</MenuItem>
                  <MenuItem value="info">Info</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Categoria</InputLabel>
                <Select
                  value={filterCategory}
                  label="Categoria"
                  onChange={(e) => setFilterCategory(e.target.value as Alert['category'] | 'all')}
                >
                  <MenuItem value="all">Todas</MenuItem>
                  <MenuItem value="performance">Performance</MenuItem>
                  <MenuItem value="cache">Cache</MenuItem>
                  <MenuItem value="api">API</MenuItem>
                  <MenuItem value="system">Sistema</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={3}>
              <FormControlLabel
                control={
                  <Switch
                    checked={showResolved}
                    onChange={(e) => setShowResolved(e.target.checked)}
                  />
                }
                label="Mostrar resolvidos"
              />
            </Grid>
            <Grid item xs={3}>
              <Button
                variant="outlined"
                onClick={resolveAllAlerts}
                disabled={activeAlerts.length === 0}
                fullWidth
              >
                Resolver Todos
              </Button>
            </Grid>
          </Grid>
        </Box>

        {/* Lista de Alertas */}
        <List>
          {filteredAlerts.length === 0 ? (
            <ListItem>
              <ListItemText
                primary="Nenhum alerta encontrado"
                secondary="Não há alertas que correspondam aos filtros selecionados"
              />
            </ListItem>
          ) : (
            filteredAlerts.map((alert) => (
              <React.Fragment key={alert.id}>
                <ListItem
                  sx={{
                    border: 1,
                    borderColor: 'divider',
                    borderRadius: 1,
                    mb: 1,
                    bgcolor: alert.resolved ? 'grey.50' : 'background.paper'
                  }}
                >
                  <Box sx={{ mr: 2 }}>
                    {getAlertIcon(alert.type)}
                  </Box>
                  <ListItemText
                    primary={
                      <Box display="flex" alignItems="center" gap={1}>
                        <Typography variant="subtitle1">
                          {alert.title}
                        </Typography>
                        <Chip
                          label={alert.type}
                          size="small"
                          color={getAlertColor(alert.type) as any}
                        />
                        <Chip
                          label={alert.category}
                          size="small"
                          variant="outlined"
                        />
                        {alert.resolved && (
                          <Chip
                            label="Resolvido"
                            size="small"
                            color="success"
                            icon={<CheckCircleIcon />}
                          />
                        )}
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          {alert.message}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {formatTimestamp(alert.timestamp)}
                        </Typography>
                      </Box>
                    }
                  />
                  <ListItemSecondaryAction>
                    <Box display="flex" alignItems="center" gap={1}>
                      {alert.metadata && (
                        <IconButton
                          onClick={() => setExpandedAlert(
                            expandedAlert === alert.id ? null : alert.id
                          )}
                          size="small"
                        >
                          {expandedAlert === alert.id ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                        </IconButton>
                      )}
                      {!alert.resolved && (
                        <Tooltip title="Resolver">
                          <IconButton
                            onClick={() => resolveAlert(alert.id)}
                            size="small"
                            color="success"
                          >
                            <CheckCircleIcon />
                          </IconButton>
                        </Tooltip>
                      )}
                    </Box>
                  </ListItemSecondaryAction>
                </ListItem>
                
                {/* Detalhes expandidos */}
                {alert.metadata && (
                  <Collapse in={expandedAlert === alert.id}>
                    <Box sx={{ ml: 6, mr: 2, mb: 2 }}>
                      <Paper sx={{ p: 2 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          Detalhes:
                        </Typography>
                        <pre style={{ fontSize: '0.8rem', overflow: 'auto' }}>
                          {JSON.stringify(alert.metadata, null, 2)}
                        </pre>
                      </Paper>
                    </Box>
                  </Collapse>
                )}
              </React.Fragment>
            ))
          )}
        </List>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={() => clearOldAlerts()} color="warning">
          Limpar Antigos
        </Button>
        <Button onClick={onClose}>Fechar</Button>
      </DialogActions>
      
      <SettingsDialog />
    </Dialog>
  );
};

export default AlertCenter;