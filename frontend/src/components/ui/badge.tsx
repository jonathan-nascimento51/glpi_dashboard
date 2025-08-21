import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { STATUS_COLORS } from '@/config/constants';
import { cn } from '@/lib/utils';

const badgeVariants = cva(
  'inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
  {
    variants: {
      variant: {
        default: 'border-transparent bg-primary text-primary-foreground shadow hover:bg-primary/80',
        secondary:
          'border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80',
        destructive:
          'border-transparent bg-destructive text-destructive-foreground shadow hover:bg-destructive/80',
        outline: 'text-foreground',
        // Status variants with optimized contrast
        success: `${STATUS_COLORS.success.bg} ${STATUS_COLORS.success.text} ${STATUS_COLORS.success.border} ${STATUS_COLORS.success.hover}`,
        warning: `${STATUS_COLORS.warning.bg} ${STATUS_COLORS.warning.text} ${STATUS_COLORS.warning.border} ${STATUS_COLORS.warning.hover}`,
        error: `${STATUS_COLORS.error.bg} ${STATUS_COLORS.error.text} ${STATUS_COLORS.error.border} ${STATUS_COLORS.error.hover}`,
        info: `${STATUS_COLORS.info.bg} ${STATUS_COLORS.info.text} ${STATUS_COLORS.info.border} ${STATUS_COLORS.info.hover}`,
        pending: `${STATUS_COLORS.pending.bg} ${STATUS_COLORS.pending.text} ${STATUS_COLORS.pending.border} ${STATUS_COLORS.pending.hover}`,
        progress: `${STATUS_COLORS.progress.bg} ${STATUS_COLORS.progress.text} ${STATUS_COLORS.progress.border} ${STATUS_COLORS.progress.hover}`,
        resolved: `${STATUS_COLORS.resolved.bg} ${STATUS_COLORS.resolved.text} ${STATUS_COLORS.resolved.border} ${STATUS_COLORS.resolved.hover}`,
        new: `${STATUS_COLORS.new.bg} ${STATUS_COLORS.new.text} ${STATUS_COLORS.new.border} ${STATUS_COLORS.new.hover}`,
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
