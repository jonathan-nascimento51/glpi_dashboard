import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface TooltipProps {
  children: React.ReactNode;
  content: React.ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right';
  className?: string;
  delay?: number;
}

export const Tooltip: React.FC<TooltipProps> = ({
  children,
  content,
  position = 'top',
  className = '',
  delay = 300,
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [actualPosition, setActualPosition] = useState(position);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLDivElement>(null);

  const showTooltip = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    timeoutRef.current = setTimeout(() => {
      setIsVisible(true);
    }, delay);
  };

  const hideTooltip = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    setIsVisible(false);
  };

  const [tooltipStyle, setTooltipStyle] = useState<React.CSSProperties>({});

  useEffect(() => {
    const updatePosition = () => {
      if (!triggerRef.current) return;

      const triggerRect = triggerRef.current.getBoundingClientRect();
      const viewport = {
        width: window.innerWidth,
        height: window.innerHeight,
      };

      let newPosition = position;
      let style: React.CSSProperties = {};

      // Verificar se o tooltip sai da tela e ajustar posição
      if (position === 'top' && triggerRect.top - 100 < 0) {
        newPosition = 'bottom';
      } else if (position === 'bottom' && triggerRect.bottom + 100 > viewport.height) {
        newPosition = 'top';
      } else if (position === 'left' && triggerRect.left - 200 < 0) {
        newPosition = 'right';
      } else if (position === 'right' && triggerRect.right + 200 > viewport.width) {
        newPosition = 'left';
      }

      // Calcular posição baseada no elemento trigger
      switch (newPosition) {
        case 'top':
          style = {
            top: triggerRect.top - 10,
            left: triggerRect.left + triggerRect.width / 2,
            transform: 'translate(-50%, -100%)',
          };
          break;
        case 'bottom':
          style = {
            top: triggerRect.bottom + 10,
            left: triggerRect.left + triggerRect.width / 2,
            transform: 'translate(-50%, 0)',
          };
          break;
        case 'left':
          style = {
            top: triggerRect.top + triggerRect.height / 2,
            left: triggerRect.left - 10,
            transform: 'translate(-100%, -50%)',
          };
          break;
        case 'right':
          style = {
            top: triggerRect.top + triggerRect.height / 2,
            left: triggerRect.right + 10,
            transform: 'translate(0, -50%)',
          };
          break;
      }

      setActualPosition(newPosition);
      setTooltipStyle(style);
    };

    if (isVisible) {
      updatePosition();
      // Atualizar posição quando a janela for redimensionada
      window.addEventListener('resize', updatePosition);
      window.addEventListener('scroll', updatePosition);

      return () => {
        window.removeEventListener('resize', updatePosition);
        window.removeEventListener('scroll', updatePosition);
      };
    }
  }, [isVisible, position]);

  const getPositionClasses = () => {
    return 'fixed z-[9999]';
  };

  const getArrowClasses = () => {
    const baseClasses = 'absolute w-2 h-2 bg-gray-900 transform rotate-45';

    switch (actualPosition) {
      case 'top':
        return `${baseClasses} top-full left-1/2 transform -translate-x-1/2 -translate-y-1/2`;
      case 'bottom':
        return `${baseClasses} bottom-full left-1/2 transform -translate-x-1/2 translate-y-1/2`;
      case 'left':
        return `${baseClasses} left-full top-1/2 transform -translate-y-1/2 -translate-x-1/2`;
      case 'right':
        return `${baseClasses} right-full top-1/2 transform -translate-y-1/2 translate-x-1/2`;
      default:
        return `${baseClasses} top-full left-1/2 transform -translate-x-1/2 -translate-y-1/2`;
    }
  };

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return (
    <div
      ref={triggerRef}
      className={`relative inline-block ${className}`}
      onMouseEnter={showTooltip}
      onMouseLeave={hideTooltip}
      onFocus={showTooltip}
      onBlur={hideTooltip}
    >
      {children}

      <AnimatePresence>
        {isVisible && (
          <motion.div
            ref={tooltipRef}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.15 }}
            className={getPositionClasses()}
            style={tooltipStyle}
          >
            <div className='bg-gray-900 text-white text-sm rounded-lg px-3 py-2 shadow-lg max-w-xs relative'>
              {content}
              <div className={getArrowClasses()} />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Tooltip;
