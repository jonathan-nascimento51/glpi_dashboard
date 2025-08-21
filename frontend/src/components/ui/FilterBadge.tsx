import React from 'react';
import { motion } from 'framer-motion';
import { X } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface FilterBadgeProps {
  label: string;
  value: string | number;
  onRemove: () => void;
  className?: string;
  variant?: 'default' | 'secondary' | 'outline' | 'info';
}

const FilterBadge: React.FC<FilterBadgeProps> = ({
  label,
  value,
  onRemove,
  className,
  variant = 'info'
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.8 }}
      transition={{ duration: 0.2 }}
      className={cn('inline-flex', className)}
    >
      <Badge
        variant={variant}
        className="flex items-center gap-2 pr-1 text-xs font-medium border shadow-sm hover:shadow-md transition-shadow"
      >
        <span className="truncate max-w-32">
          {label}: {value}
        </span>
        <motion.button
          onClick={onRemove}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          className="hover:bg-white/20 rounded-full p-0.5 ml-1 transition-colors"
          aria-label={`Remover filtro ${label}`}
        >
          <X className="w-3 h-3" />
        </motion.button>
      </Badge>
    </motion.div>
  );
};

export default FilterBadge;