import { useEffect, memo, useCallback } from 'react';

interface CacheNotificationProps {
  message: string;
  isVisible: boolean;
  onClose: () => void;
}

// SVG icons moved outside component to prevent recreation
const CheckIcon = () => (
  <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const CloseIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
  </svg>
);

const CacheNotification = memo<CacheNotificationProps>(({ message, isVisible, onClose }) => {
  // Memoize the close handler
  const handleClose = useCallback(() => {
    onClose();
  }, [onClose]);

  useEffect(() => {
    if (isVisible) {
      const timer = setTimeout(handleClose, 5000); // Auto-close apos 5 segundos
      
      return () => clearTimeout(timer);
    }
  }, [isVisible, handleClose]);

  if (!isVisible) return null;

  return (
    <div className="fixed top-4 right-4 z-50 animate-slide-in-right">
      <div className="bg-green-50 border border-green-200 rounded-lg p-4 shadow-lg max-w-sm">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <CheckIcon />
          </div>
          <div className="ml-3 flex-1">
            <h3 className="text-sm font-medium text-green-800">
              Cache Ativado Automaticamente
            </h3>
            <p className="mt-1 text-sm text-green-700">
              {message}
            </p>
          </div>
          <div className="ml-4 flex-shrink-0">
            <button
              onClick={handleClose}
              className="inline-flex text-green-400 hover:text-green-600 focus:outline-none focus:text-green-600"
            >
              <CloseIcon />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
});

CacheNotification.displayName = 'CacheNotification';

export default CacheNotification;