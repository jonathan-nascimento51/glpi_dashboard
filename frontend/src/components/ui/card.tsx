import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";
import { designTokens } from "@/lib/design-tokens";

/**
 * Variantes do componente Card com foco em acessibilidade e consistência visual
 */
const cardVariants = cva(
  [
    "rounded-lg border bg-card text-card-foreground shadow-sm",
    "transition-all duration-200",
    // Melhor suporte para navegação por teclado
    "focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2",
  ],
  {
    variants: {
      variant: {
        default: "border-border",
        elevated: "shadow-md hover:shadow-lg",
        outlined: "border-2 border-border shadow-none",
        filled: "bg-muted border-transparent",
        interactive: [
          "cursor-pointer hover:shadow-md hover:bg-accent/5",
          "focus-visible:outline-none focus-visible:ring-2",
          "focus-visible:ring-ring focus-visible:ring-offset-2",
        ],
      },
      size: {
        sm: "p-4",
        default: "p-6",
        lg: "p-8",
      },
      status: {
        default: "",
        success: "border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-950",
        warning: "border-yellow-200 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-950",
        error: "border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-950",
        info: "border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-950",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
      status: "default",
    },
  }
);

/**
 * Props do componente Card
 */
export interface CardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {
  /** Se o card é interativo (clicável) */
  interactive?: boolean;
  /** Função de clique para cards interativos */
  onClick?: () => void;
  /** Texto alternativo para leitores de tela */
  ariaLabel?: string;
  /** Descrição adicional para leitores de tela */
  ariaDescription?: string;
}

/**
 * Componente Card principal com suporte a acessibilidade
 */
const Card = React.forwardRef<HTMLDivElement, CardProps>(
  (
    {
      className,
      variant,
      size,
      status,
      interactive,
      onClick,
      ariaLabel,
      ariaDescription,
      children,
      ...props
    },
    ref
  ) => {
    const isInteractive = interactive || !!onClick;
    const Component = isInteractive ? "button" : "div";

    return (
      <Component
        ref={ref as any}
        className={cn(
          cardVariants({
            variant: isInteractive ? "interactive" : variant,
            size,
            status,
            className,
          })
        )}
        onClick={onClick}
        aria-label={ariaLabel}
        aria-description={ariaDescription}
        role={isInteractive ? "button" : undefined}
        tabIndex={isInteractive ? 0 : undefined}
        {...props}
      >
        {children}
      </Component>
    );
  }
);
Card.displayName = "Card";

/**
 * Header do Card com tipografia consistente
 */
const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    /** Se deve incluir padding bottom */
    noPaddingBottom?: boolean;
  }
>(({ className, noPaddingBottom = false, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "flex flex-col space-y-1.5",
      noPaddingBottom ? "p-6 pb-0" : "p-6",
      className
    )}
    {...props}
  />
));
CardHeader.displayName = "CardHeader";

/**
 * Título do Card com hierarquia semântica
 */
const CardTitle = React.forwardRef<
  HTMLHeadingElement,
  React.HTMLAttributes<HTMLHeadingElement> & {
    /** Nível do heading (h1-h6) */
    level?: 1 | 2 | 3 | 4 | 5 | 6;
    /** Tamanho visual do título */
    size?: "sm" | "default" | "lg" | "xl";
  }
>(({ className, level = 3, size = "default", children, ...props }, ref) => {
  const Component = `h${level}` as keyof JSX.IntrinsicElements;
  
  const sizeClasses = {
    sm: "text-sm font-medium",
    default: "text-lg font-semibold leading-none tracking-tight",
    lg: "text-xl font-semibold leading-none tracking-tight",
    xl: "text-2xl font-bold leading-none tracking-tight",
  };

  return (
    <Component
      ref={ref as any}
      className={cn(sizeClasses[size], className)}
      {...props}
    >
      {children}
    </Component>
  );
});
CardTitle.displayName = "CardTitle";

/**
 * Descrição do Card com tipografia secundária
 */
const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-sm text-muted-foreground leading-relaxed", className)}
    {...props}
  />
));
CardDescription.displayName = "CardDescription";

/**
 * Conteúdo principal do Card
 */
const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    /** Se deve incluir padding top */
    noPaddingTop?: boolean;
  }
>(({ className, noPaddingTop = false, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      noPaddingTop ? "p-6 pt-0" : "p-6",
      className
    )}
    {...props}
  />
));
CardContent.displayName = "CardContent";

/**
 * Footer do Card para ações e informações secundárias
 */
const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    /** Alinhamento dos itens */
    align?: "start" | "center" | "end" | "between" | "around";
  }
>(({ className, align = "start", ...props }, ref) => {
  const alignClasses = {
    start: "justify-start",
    center: "justify-center",
    end: "justify-end",
    between: "justify-between",
    around: "justify-around",
  };

  return (
    <div
      ref={ref}
      className={cn(
        "flex items-center p-6 pt-0 gap-2",
        alignClasses[align],
        className
      )}
      {...props}
    />
  );
});
CardFooter.displayName = "CardFooter";

/**
 * Componente para métricas/KPIs com formatação consistente
 */
const CardMetric = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    /** Valor principal da métrica */
    value: string | number;
    /** Label da métrica */
    label: string;
    /** Valor de comparação (opcional) */
    comparison?: {
      value: string | number;
      trend: "up" | "down" | "neutral";
      label?: string;
    };
    /** Ícone da métrica */
    icon?: React.ReactNode;
  }
>(
  (
    {
      className,
      value,
      label,
      comparison,
      icon,
      ...props
    },
    ref
  ) => {
    const trendColors = {
      up: "text-green-600 dark:text-green-400",
      down: "text-red-600 dark:text-red-400",
      neutral: "text-muted-foreground",
    };

    return (
      <div
        ref={ref}
        className={cn("space-y-2", className)}
        {...props}
      >
        <div className="flex items-center justify-between">
          <p className="text-sm font-medium text-muted-foreground">
            {label}
          </p>
          {icon && (
            <div className="text-muted-foreground" aria-hidden="true">
              {icon}
            </div>
          )}
        </div>
        
        <div className="space-y-1">
          <p className="text-2xl font-bold leading-none">
            {value}
          </p>
          
          {comparison && (
            <p className={cn("text-xs", trendColors[comparison.trend])}>
              {comparison.value} {comparison.label}
            </p>
          )}
        </div>
      </div>
    );
  }
);
CardMetric.displayName = "CardMetric";

export {
  Card,
  CardHeader,
  CardFooter,
  CardTitle,
  CardDescription,
  CardContent,
  CardMetric,
  cardVariants,
};

export type { CardProps };
