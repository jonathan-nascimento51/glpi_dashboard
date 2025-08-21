import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import AlertCenter from '../components/AlertCenter';
import AlertNotification from '../components/AlertNotification';

// Mock dos hooks e serviços
vi.mock('../hooks/useAlerts', () => ({
  useAlerts: () => ({
    alerts: [],
    isLoading: false,
    error: null,
    refreshAlerts: vi.fn(),
    resolveAlert: vi.fn(),
    clearAllAlerts: vi.fn()
  })
}));

vi.mock('../services/alertService', () => ({
  alertService: {
    getAlerts: vi.fn(() => []),
    getActiveAlerts: vi.fn(() => []),
    resolveAlert: vi.fn(),
    clearOldAlerts: vi.fn(),
    start: vi.fn(),
    stop: vi.fn()
  }
}));

describe('Alert Components', () => {
  describe('AlertCenter', () => {
    it('should render without crashing when closed', () => {
      const mockOnClose = vi.fn();
      render(<AlertCenter open={false} onClose={mockOnClose} />);
      // Quando fechado, o componente não deve estar visível
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });

    it('should render when open', () => {
      const mockOnClose = vi.fn();
      render(<AlertCenter open={true} onClose={mockOnClose} />);
      // Quando aberto, deve mostrar o dialog
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    it('should call onClose when close button is clicked', () => {
      const mockOnClose = vi.fn();
      render(<AlertCenter open={true} onClose={mockOnClose} />);
      
      const closeButton = screen.getByLabelText(/fechar/i);
      fireEvent.click(closeButton);
      
      expect(mockOnClose).toHaveBeenCalled();
    });
  });

  describe('AlertNotification', () => {
    it('should render without crashing', () => {
      const mockOnOpenAlertCenter = vi.fn();
      render(<AlertNotification onOpenAlertCenter={mockOnOpenAlertCenter} />);
      
      // Deve renderizar o FAB (Floating Action Button)
      expect(screen.getByRole('button')).toBeInTheDocument();
    });

    it('should call onOpenAlertCenter when FAB is clicked', () => {
      const mockOnOpenAlertCenter = vi.fn();
      render(<AlertNotification onOpenAlertCenter={mockOnOpenAlertCenter} />);
      
      const fab = screen.getByRole('button');
      fireEvent.click(fab);
      
      expect(mockOnOpenAlertCenter).toHaveBeenCalled();
    });
  });
});