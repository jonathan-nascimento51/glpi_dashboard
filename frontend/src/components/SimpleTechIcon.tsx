import React from 'react';
import { Cpu } from 'lucide-react';

interface SimpleTechIconProps {
  className?: string;
  size?: number;
}

export const SimpleTechIcon: React.FC<SimpleTechIconProps> = ({ className = "", size = 24 }) => {
  return (
    <div className={`relative ${className}`}>
      <Cpu 
        size={size} 
        className="text-slate-600 dark:text-white/90 drop-shadow-sm" 
        strokeWidth={1.5}
      />
      {/* Indicador de status */}
      <div className="absolute -top-1 -right-1 w-2 h-2 bg-green-400 rounded-full border border-white/50 animate-pulse" />
    </div>
  );
};