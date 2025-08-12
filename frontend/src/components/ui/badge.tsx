import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";
import { designTokens } from "@/lib/design-tokens";

/**
 * Variantes do componente Badge com foco em acessibilidade e status
 */
const badgeVariants = cva(
  [
    "inline-flex items-center rounded-md border px-2.5 py-0.5",
    "text-xs font-semibold transition-colors",
    "focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
    // Melhor legibilidade
    "whitespace-nowrap",
  ],
  {
    variants: {
      variant: {
        default: [
          "border-transparent bg-primary text-primary-foreground",
          "shadow hover:bg-primary/80",
        ],
        secondary: [
          "border-transparent bg-secondary text-secondary-foreground",
          "hover:bg-secondary/80",
        ],
        destructive: [
          "border-transparent bg-destructive text-destructive-foreground",
          "shadow hover:bg-destructive/80",
        ],
        outline: [
          "text-foreground border-border",
          "hover:bg-accent hover:text-accent-foreground",
        ],
        // Variantes de status com cores semânticas
        success: [
          "border-transparent bg-green-100 text-green-800",
          "dark:bg-green-900 dark:text-green-100",
          "hover:bg-green-200 dark:hover:bg-green-800",
        ],
        warning: [
          "border-transparent bg-yellow-100 text-yellow-800",
          "dark:bg-yellow-900 dark:text-yellow-100",
          "hover:bg-yellow-200 dark:hover:bg-yellow-800",
        ],
        error: [
          "border-transparent bg-red-100 text-red-800",
          "dark:bg-red-900 dark:text-red-100",
          "hover:bg-red-200 dark:hover:bg-red-800",
        ],
        info: [
          "border-transparent bg-blue-100 text-blue-800",
          "dark:bg-blue-900 dark:text-blue-100",
          "hover:bg-blue-200 dark:hover:bg-blue-800",
        ],
        // Variantes específicas para status de tickets
        open: [
          "border-transparent bg-blue-100 text-blue-800",
          "dark:bg-blue-900 dark:text-blue-100",
        ],
        inProgress: [
          "border-transparent bg-yellow-100 text-yellow-800",
          "dark:bg-yellow-900 dark:text-yellow-100",
        ],
        resolved: [
          "border-transparent bg-green-100 text-green-800",
          "dark:bg-green-900 dark:text-green-100",
        ],
        closed: [
          "border-transparent bg-gray-100 text-gray-800",
          "dark:bg-gray-800 dark:text-gray-100",
        ],
        // Variantes para prioridades
        low: [
          "border-transparent bg-gray-100 text-gray-600",
          "dark:bg-gray-800 dark:text-gray-300",
        ],
        medium: [
          "border-transparent bg-yellow-100 text-yellow-700",
          "dark:bg-yellow-900 dark:text-yellow-200",
        ],
        high: [
          "border-transparent bg-orange-100 text-orange-700",
          "dark:bg-orange-900 dark:text-orange-200",
        ],
        critical: [
          "border-transparent bg-red-100 text-red-700",
          "dark:bg-red-900 dark:text-red-200",
        ],
      },
      size: {
        sm: "px-2 py-0.5 text-xs",
        default: "px-2.5 py-0.5 text-xs",
        lg: "px-3 py-1 text-sm",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

/**
 * Props do componente Badge
 */
export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {
  /** Ícone a ser exibido no badge */
  icon?: React.ReactNode;
  /** Posição do ícone */
  iconPosition?: "left" | "right";
  /** Se o badge pode ser removido */
  dismissible?: boolean;
  /** Função chamada quando o badge é removido */
  onDismiss?: () => void;
  /** Texto alternativo para leitores de tela */
  ariaLabel?: string;
}

/**
 * Componente Badge para exibir status, categorias e informações concisas
 * 
 * Características de acessibilidade:
 * - Suporte a leitores de tela com aria-label
 * - Cores com contraste adequado (WCAG 2.1 AA)
 * - Suporte a navegação por teclado quando dismissible
 * - Ícones com aria-hidden apropriado
 */
const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(
  (
    {
      className,
      variant,
      size,
      icon,
      iconPosition = "left",
      dismissible = false,
      onDismiss,
      ariaLabel,
      children,
      ...props
    },
    ref
  ) => {
    const handleKeyDown = (event: React.KeyboardEvent) => {
      if (dismissible && onDismiss && (event.key === "Enter" || event.key === " ")) {
        event.preventDefault();
        onDismiss();
      }
    };

    const DismissIcon = () => (
      <button
        type="button"
        className="ml-1 inline-flex h-4 w-4 items-center justify-center rounded-full hover:bg-black/10 focus:outline-none focus:ring-1 focus:ring-black/20"
        onClick={onDismiss}
        aria-label="Remover badge"
      >
        <svg
          className="h-3 w-3"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </button>
    );

    return (
      <span
        ref={ref}
        className={cn(badgeVariants({ variant, size }), className)}
        aria-label={ariaLabel}
        tabIndex={dismissible ? 0 : undefined}
        onKeyDown={dismissible ? handleKeyDown : undefined}
        role={dismissible ? "button" : undefined}
        {...props}
      >
        {icon && iconPosition === "left" && (
          <span className="mr-1 flex-shrink-0" aria-hidden="true">
            {icon}
          </span>
        )}
        
        <span>{children}</span>
        
        {icon && iconPosition === "right" && (
          <span className="ml-1 flex-shrink-0" aria-hidden="true">
            {icon}
          </span>
        )}
        
        {dismissible && onDismiss && <DismissIcon />}
      </span>
    );
  }
);

Badge.displayName = "Badge";

/**
 * Utilitários para mapear status para variantes de badge
 */
export const statusToBadgeVariant = {
  // Status de tickets
  1: "open" as const,        // Novo
  2: "inProgress" as const,  // Em andamento
  3: "inProgress" as const,  // Planejado
  4: "inProgress" as const,  // Pendente
  5: "resolved" as const,    // Solucionado
  6: "closed" as const,      // Fechado
  
  // Prioridades
  priority_1: "low" as const,
  priority_2: "low" as const,
  priority_3: "medium" as const,
  priority_4: "high" as const,
  priority_5: "critical" as const,
  priority_6: "critical" as const,
} as const;

/**
 * Utilitários para mapear urgência para variantes de badge
 */
export const urgencyToBadgeVariant = {
  1: "low" as const,
  2: "low" as const,
  3: "medium" as const,
  4: "high" as const,
  5: "critical" as const,
} as const;

/**
 * Hook para obter a variante correta do badge baseada no status
 */
export const useBadgeVariant = (status: number | string, type: "status" | "priority" | "urgency" = "status") => {
  if (type === "status") {
    return statusToBadgeVariant[status as keyof typeof statusToBadgeVariant] || "default";
  }
  
  if (type === "priority") {
    return statusToBadgeVariant[`priority_${status}` as keyof typeof statusToBadgeVariant] || "default";
  }
  
  if (type === "urgency") {
    return urgencyToBadgeVariant[status as keyof typeof urgencyToBadgeVariant] || "default";
  }
  
  return "default";
};

export { Badge, badgeVariants };
export type { BadgeProps };
