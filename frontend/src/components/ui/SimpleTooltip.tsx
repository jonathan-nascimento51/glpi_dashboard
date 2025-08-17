import React, { useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';

interface SimpleTooltipProps {
  children: React.ReactNode;
  content: string;
  className?: string;
}

export const SimpleTooltip: React.FC<SimpleTooltipProps> = ({
  children,
  content,
  className = '',
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const triggerRef = useRef<HTMLDivElement>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const showTooltip = (e: React.MouseEvent) => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    const rect = triggerRef.current?.getBoundingClientRect();
    if (rect) {
      const tooltipWidth = 280; // Largura estimada do tooltip
      const tooltipHeight = 80; // Altura estimada do tooltip
      const padding = 16; // Padding das bordas da tela

      let x = rect.left + rect.width / 2;
      let y = rect.top - 10;

      // Verificar se o tooltip sai da borda direita
      if (x + tooltipWidth / 2 > window.innerWidth - padding) {
        x = window.innerWidth - tooltipWidth / 2 - padding;
      }

      // Verificar se o tooltip sai da borda esquerda
      if (x - tooltipWidth / 2 < padding) {
        x = tooltipWidth / 2 + padding;
      }

      // Verificar se o tooltip sai da borda superior
      if (y - tooltipHeight < padding) {
        y = rect.bottom + 10; // Mostrar abaixo do elemento
      }

      setPosition({ x, y });
    }

    timeoutRef.current = setTimeout(() => {
      setIsVisible(true);
    }, 200);
  };

  const hideTooltip = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    setIsVisible(false);
  };

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  const tooltipElement = isVisible ? (
    <div
      className='bg-slate-900 text-slate-100 text-sm rounded-xl px-4 py-3 shadow-2xl border border-slate-700 backdrop-blur-sm max-w-[280px] leading-relaxed font-medium'
      style={{
        position: 'fixed',
        left: position.x,
        top: position.y,
        transform:
          position.y > window.innerHeight / 2 ? 'translate(-50%, -100%)' : 'translate(-50%, 10px)',
        zIndex: 99999,
        pointerEvents: 'none',
        animation: 'fadeIn 0.2s ease-out',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.1)',
      }}
    >
      <div className='whitespace-pre-wrap break-words text-slate-100'>{content}</div>
      <div
        className={`absolute left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-[6px] border-r-[6px] border-transparent ${
          position.y > window.innerHeight / 2
            ? 'top-full border-t-[6px] border-t-slate-900'
            : 'bottom-full border-b-[6px] border-b-slate-900'
        }`}
        style={{ filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.4))' }}
      />
    </div>
  ) : null;

  return (
    <>
      <div
        ref={triggerRef}
        className={`inline-block cursor-help ${className}`}
        onMouseEnter={showTooltip}
        onMouseLeave={hideTooltip}
      >
        {children}
      </div>
      {tooltipElement && createPortal(tooltipElement, document.body)}
    </>
  );
};

export default SimpleTooltip;
