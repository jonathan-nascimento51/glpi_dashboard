/**
 * Componente de Notificação de Alertas
 * 
 * Este componente exibe notificações flutuantes para alertas críticos
 * e fornece acesso rápido ao centro de alertas.
 */

import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import {
  Snackbar,
  Alert as MuiAlert,
  AlertTitle,
  IconButton,
  Box,
  Typography,
  Chip,
  Fab,
  Badge,
  Slide,
  Collapse,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Button
} from '@mui/material';
import {
  Close as CloseIcon,
  Notifications as NotificationsIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';
import { TransitionProps } from '@mui/material/transitions';
import {
  useAlerts,
  useCriticalAlerts,
  useAlertStats
} from '../hooks/useAlerts';
import { Alert } from '../services/alertService';

interface AlertNotificationProps {
  position?: {
    vertical: 'top' | 'bottom';
    horizontal: 'left' | 'center' | 'right';
  };
  autoHideDuration?: number;
  maxVisible?: number;
  onOpenAlertCenter?: () => void;
}

function SlideTransition(props: TransitionProps & {
  children: React.ReactElement<any, any>;
}) {
  return <Slide {...props} direction="up" />;
}

const AlertNotification: React.FC<AlertNotificationProps> = ({
  position = { vertical: 'top', horizontal: 'right' },
  autoHideDuration = 6000,
  maxVisible = 3,
  onOpenAlertCenter
}) => {
  const {
    alerts,
    activeAlerts,
    resolveAlert,
    isRunning
  } = useAlerts();
  
  const { hasUnresolved: hasCriticalUnresolved } = useCriticalAlerts();
  const stats = useAlertStats();

  const [visibleAlerts, setVisibleAlerts] = useState<Alert[]>([]);
  const [dismissedAlerts, setDismissedAlerts] = useState<Set<string>>(new Set());

  const [fabExpanded, setFabExpanded] = useState(false);
  const lastAlertCountRef = useRef(0);
  const fabTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Calcular alertas visíveis de forma otimizada
  const newAlerts = useMemo(() => {
    return activeAlerts
      .filter(alert => 
        (alert.type === 'critical' || alert.type === 'error') &&
        !dismissedAlerts.has(alert.id)
      )
      .slice(0, maxVisible);
  }, [activeAlerts, dismissedAlerts, maxVisible]);

  // Atualizar alertas visíveis quando novos alertas chegarem
  useEffect(() => {
    setVisibleAlerts(newAlerts);
    
    // Expandir FAB se houver novos alertas
    if (activeAlerts.length > lastAlertCountRef.current && activeAlerts.length > 0) {
      setFabExpanded(true);
      
      // Limpar timeout anterior se existir
      if (fabTimeoutRef.current) {
        clearTimeout(fabTimeoutRef.current);
      }
      
      // Definir novo timeout
      fabTimeoutRef.current = setTimeout(() => {
        setFabExpanded(false);
        fabTimeoutRef.current = null;
      }, 3000);
    }
    
    lastAlertCountRef.current = activeAlerts.length;
  }, [newAlerts, activeAlerts.length]);

  // Cleanup do timeout quando o componente for desmontado
  useEffect(() => {
    return () => {
      if (fabTimeoutRef.current) {
        clearTimeout(fabTimeoutRef.current);
      }
    };
  }, []);

  // Limpar alertas dispensados quando eles são resolvidos
  useEffect(() => {
    setDismissedAlerts(prev => {
      const resolvedIds = Array.from(prev).filter(id => 
        !activeAlerts.some(alert => alert.id === id)
      );
      
      if (resolvedIds.length > 0) {
        const newSet = new Set(prev);
        resolvedIds.forEach(id => newSet.delete(id));
        return newSet;
      }
      
      return prev;
    });
  }, [activeAlerts]);

  // Dispensar alerta
  const dismissAlert = useCallback((alertId: string) => {
    setDismissedAlerts(prev => new Set(prev).add(alertId));
    setVisibleAlerts(prev => prev.filter(alert => alert.id !== alertId));
  }, []);

  // Resolver e dispensar alerta
  const resolveAndDismiss = useCallback((alertId: string) => {
    resolveAlert(alertId);
    dismissAlert(alertId);
  }, [resolveAlert, dismissAlert]);

  // Obter ícone do alerta
  const getAlertIcon = (type: Alert['type']) => {
    switch (type) {
      case 'critical':
        return <ErrorIcon />;
      case 'error':
        return <ErrorIcon />;
      case 'warning':
        return <WarningIcon />;
      case 'info':
        return <InfoIcon />;
      default:
        return <NotificationsIcon />;
    }
  };

  // Obter severidade do MUI Alert
  const getAlertSeverity = (type: Alert['type']): 'error' | 'warning' | 'info' | 'success' => {
    switch (type) {
      case 'critical':
      case 'error':
        return 'error';
      case 'warning':
        return 'warning';
      case 'info':
        return 'info';
      default:
        return 'info';
    }
  };

  // Formatar timestamp relativo
  const getRelativeTime = (timestamp: Date): string => {
    const now = new Date();
    const diff = now.getTime() - timestamp.getTime();
    
    if (diff < 60000) {
      return 'agora';
    } else if (diff < 3600000) {
      return `${Math.floor(diff / 60000)}min`;
    } else {
      return `${Math.floor(diff / 3600000)}h`;
    }
  };

  return (
    <>
      {/* Notificações flutuantes */}
      {visibleAlerts.map((alert, index) => (
        <Snackbar
          key={alert.id}
          open={true}
          anchorOrigin={position}
          TransitionComponent={SlideTransition}
          sx={{
            position: 'fixed',
            top: position.vertical === 'top' 
              ? `${80 + index * 80}px` 
              : `${80 + (visibleAlerts.length - index - 1) * 80}px`,
            zIndex: 1400 + index
          }}
        >
          <MuiAlert
            severity={getAlertSeverity(alert.type)}
            variant="filled"
            sx={{ minWidth: 400, maxWidth: 500 }}
            action={
              <Box>
                <IconButton
                  size="small"
                  color="inherit"
                  onClick={() => resolveAndDismiss(alert.id)}
                  sx={{ mr: 1 }}
                >
                  <CloseIcon fontSize="small" />
                </IconButton>
              </Box>
            }
          >
            <AlertTitle>
              <Box display="flex" alignItems="center" gap={1}>
                {alert.title}
                <Chip
                  label={getRelativeTime(alert.timestamp)}
                  size="small"
                  variant="outlined"
                  sx={{ color: 'inherit', borderColor: 'currentColor' }}
                />
              </Box>
            </AlertTitle>
            <Typography variant="body2">
              {alert.message}
            </Typography>
            {alert.category && (
              <Chip
                label={alert.category}
                size="small"
                variant="outlined"
                sx={{ mt: 1, color: 'inherit', borderColor: 'currentColor' }}
              />
            )}
          </MuiAlert>
        </Snackbar>
      ))}

      {/* FAB de alertas */}
      <Box
        sx={{
          position: 'fixed',
          bottom: 24,
          right: 24,
          zIndex: 1300
        }}
      >
        <Collapse in={fabExpanded} timeout={300}>
          <Paper
            elevation={8}
            sx={{
              mb: 2,
              p: 2,
              maxWidth: 300,
              bgcolor: hasCriticalUnresolved ? 'error.main' : 'primary.main',
              color: 'white'
            }}
          >
            <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
              <Typography variant="subtitle2">
                Sistema de Alertas
              </Typography>
              <IconButton
                size="small"
                onClick={() => setFabExpanded(false)}
                sx={{ color: 'inherit' }}
              >
                <CloseIcon fontSize="small" />
              </IconButton>
            </Box>
            
            <List dense sx={{ py: 0 }}>
              <ListItem sx={{ px: 0 }}>
                <ListItemIcon sx={{ minWidth: 32 }}>
                  <ErrorIcon sx={{ color: 'inherit', fontSize: 20 }} />
                </ListItemIcon>
                <ListItemText
                  primary={`${stats.byType.critical || 0} Críticos`}
                  primaryTypographyProps={{ variant: 'body2' }}
                />
              </ListItem>
              <ListItem sx={{ px: 0 }}>
                <ListItemIcon sx={{ minWidth: 32 }}>
                  <WarningIcon sx={{ color: 'inherit', fontSize: 20 }} />
                </ListItemIcon>
                <ListItemText
                  primary={`${(stats.byType.error || 0) + (stats.byType.warning || 0)} Avisos`}
                  primaryTypographyProps={{ variant: 'body2' }}
                />
              </ListItem>
            </List>
            
            <Divider sx={{ my: 1, borderColor: 'rgba(255,255,255,0.3)' }} />
            
            <Button
              fullWidth
              variant="outlined"
              size="small"
              onClick={() => {
                onOpenAlertCenter?.();
                setFabExpanded(false);
              }}
              sx={{
                color: 'inherit',
                borderColor: 'rgba(255,255,255,0.5)',
                '&:hover': {
                  borderColor: 'white',
                  bgcolor: 'rgba(255,255,255,0.1)'
                }
              }}
            >
              Ver Todos
            </Button>
          </Paper>
        </Collapse>
        
        <Badge
          badgeContent={stats.active}
          color={hasCriticalUnresolved ? 'error' : 'warning'}
          max={99}
          invisible={stats.active === 0}
        >
          <Fab
            color={hasCriticalUnresolved ? 'error' : stats.active > 0 ? 'warning' : 'primary'}
            onClick={onOpenAlertCenter}
            sx={{
              animation: hasCriticalUnresolved ? 'pulse 2s infinite' : 'none',
              '@keyframes pulse': {
                '0%': {
                  transform: 'scale(1)',
                  boxShadow: '0 0 0 0 rgba(255, 0, 0, 0.7)'
                },
                '70%': {
                  transform: 'scale(1.05)',
                  boxShadow: '0 0 0 10px rgba(255, 0, 0, 0)'
                },
                '100%': {
                  transform: 'scale(1)',
                  boxShadow: '0 0 0 0 rgba(255, 0, 0, 0)'
                }
              }
            }}
          >
            <NotificationsIcon />
          </Fab>
        </Badge>
        
        {/* Indicador de status do monitoramento */}
        <Box
          sx={{
            position: 'absolute',
            top: -8,
            left: -8,
            width: 16,
            height: 16,
            borderRadius: '50%',
            bgcolor: isRunning ? 'success.main' : 'error.main',
            border: 2,
            borderColor: 'background.paper',
            animation: isRunning ? 'blink 2s infinite' : 'none',
            '@keyframes blink': {
              '0%, 50%': { opacity: 1 },
              '51%, 100%': { opacity: 0.3 }
            }
          }}
        />
      </Box>


    </>
  );
};

export default AlertNotification;