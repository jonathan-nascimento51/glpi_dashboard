import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";
import { designTokens } from "@/lib/design-tokens";

/**
 * Variantes de tipografia baseadas nos design tokens
 */
const typographyVariants = cva("", {
  variants: {
    variant: {
      // Headings
      h1: [
        "scroll-m-20 text-4xl font-extrabold tracking-tight lg:text-5xl",
        "text-foreground",
      ],
      h2: [
        "scroll-m-20 border-b pb-2 text-3xl font-semibold tracking-tight",
        "first:mt-0 text-foreground",
      ],
      h3: [
        "scroll-m-20 text-2xl font-semibold tracking-tight",
        "text-foreground",
      ],
      h4: [
        "scroll-m-20 text-xl font-semibold tracking-tight",
        "text-foreground",
      ],
      h5: [
        "scroll-m-20 text-lg font-semibold tracking-tight",
        "text-foreground",
      ],
      h6: [
        "scroll-m-20 text-base font-semibold tracking-tight",
        "text-foreground",
      ],
      
      // Body text
      body: [
        "leading-7 text-foreground",
      ],
      bodyLarge: [
        "text-lg leading-7 text-foreground",
      ],
      bodySmall: [
        "text-sm leading-6 text-foreground",
      ],
      
      // Specialized text
      lead: [
        "text-xl text-muted-foreground",
      ],
      large: [
        "text-lg font-semibold text-foreground",
      ],
      small: [
        "text-sm font-medium leading-none text-foreground",
      ],
      muted: [
        "text-sm text-muted-foreground",
      ],
      
      // Code and technical
      code: [
        "relative rounded bg-muted px-[0.3rem] py-[0.2rem]",
        "font-mono text-sm font-semibold text-foreground",
      ],
      
      // Dashboard specific
      metric: [
        "text-2xl font-bold tracking-tight text-foreground",
      ],
      metricLabel: [
        "text-sm font-medium text-muted-foreground uppercase tracking-wide",
      ],
      kpi: [
        "text-3xl font-bold tracking-tight text-foreground",
      ],
      kpiLabel: [
        "text-xs font-medium text-muted-foreground uppercase tracking-wider",
      ],
      
      // Status and alerts
      success: [
        "text-green-700 dark:text-green-400 font-medium",
      ],
      warning: [
        "text-yellow-700 dark:text-yellow-400 font-medium",
      ],
      error: [
        "text-red-700 dark:text-red-400 font-medium",
      ],
      info: [
        "text-blue-700 dark:text-blue-400 font-medium",
      ],
    },
    align: {
      left: "text-left",
      center: "text-center",
      right: "text-right",
      justify: "text-justify",
    },
    weight: {
      light: "font-light",
      normal: "font-normal",
      medium: "font-medium",
      semibold: "font-semibold",
      bold: "font-bold",
      extrabold: "font-extrabold",
    },
  },
  defaultVariants: {
    variant: "body",
    align: "left",
  },
});

/**
 * Props do componente Typography
 */
export interface TypographyProps
  extends React.HTMLAttributes<HTMLElement>,
    VariantProps<typeof typographyVariants> {
  /** Elemento HTML a ser renderizado */
  as?: keyof JSX.IntrinsicElements;
  /** Se o texto deve ser truncado com ellipsis */
  truncate?: boolean;
  /** Número máximo de linhas antes de truncar */
  lineClamp?: number;
}

/**
 * Mapeamento de variantes para elementos HTML semânticos
 */
const variantToElement = {
  h1: "h1",
  h2: "h2",
  h3: "h3",
  h4: "h4",
  h5: "h5",
  h6: "h6",
  body: "p",
  bodyLarge: "p",
  bodySmall: "p",
  lead: "p",
  large: "div",
  small: "small",
  muted: "p",
  code: "code",
  metric: "div",
  metricLabel: "div",
  kpi: "div",
  kpiLabel: "div",
  success: "span",
  warning: "span",
  error: "span",
  info: "span",
} as const;

/**
 * Componente Typography para texto consistente e acessível
 * 
 * Características de acessibilidade:
 * - Elementos HTML semânticos apropriados
 * - Hierarquia de headings respeitada
 * - Contraste adequado para todas as variantes
 * - Suporte a leitores de tela
 */
const Typography = React.forwardRef<HTMLElement, TypographyProps>(
  (
    {
      className,
      variant = "body",
      align,
      weight,
      as,
      truncate = false,
      lineClamp,
      children,
      ...props
    },
    ref
  ) => {
    // Determina o elemento HTML baseado na prop 'as' ou na variante
    const Element = as || (variant ? variantToElement[variant] : "p") as keyof JSX.IntrinsicElements;

    // Classes para truncamento
    const truncateClasses = truncate
      ? "truncate"
      : lineClamp
      ? `line-clamp-${lineClamp}`
      : "";

    return React.createElement(
      Element,
      {
        ref,
        className: cn(
          typographyVariants({ variant, align, weight }),
          truncateClasses,
          className
        ),
        ...props,
      },
      children
    );
  }
);

Typography.displayName = "Typography";

/**
 * Componentes especializados para casos comuns
 */

/**
 * Componente para exibir métricas com formatação consistente
 */
export const MetricDisplay = React.forwardRef<
  HTMLDivElement,
  {
    value: string | number;
    label: string;
    trend?: "up" | "down" | "neutral";
    trendValue?: string;
    className?: string;
  }
>(({ value, label, trend, trendValue, className, ...props }, ref) => {
  const trendIcon = {
    up: "",
    down: "",
    neutral: "",
  };

  const trendColor = {
    up: "text-green-600 dark:text-green-400",
    down: "text-red-600 dark:text-red-400",
    neutral: "text-gray-600 dark:text-gray-400",
  };

  return (
    <div ref={ref} className={cn("space-y-1", className)} {...props}>
      <Typography variant="metricLabel">{label}</Typography>
      <div className="flex items-baseline gap-2">
        <Typography variant="metric">{value}</Typography>
        {trend && trendValue && (
          <span className={cn("text-sm font-medium", trendColor[trend])}>
            {trendIcon[trend]} {trendValue}
          </span>
        )}
      </div>
    </div>
  );
});

MetricDisplay.displayName = "MetricDisplay";

/**
 * Componente para exibir KPIs com formatação consistente
 */
export const KpiDisplay = React.forwardRef<
  HTMLDivElement,
  {
    value: string | number;
    label: string;
    description?: string;
    status?: "success" | "warning" | "error" | "info";
    className?: string;
  }
>(({ value, label, description, status, className, ...props }, ref) => {
  return (
    <div ref={ref} className={cn("space-y-2", className)} {...props}>
      <Typography variant="kpiLabel">{label}</Typography>
      <Typography 
        variant="kpi" 
        className={status ? typographyVariants({ variant: status }) : undefined}
      >
        {value}
      </Typography>
      {description && (
        <Typography variant="muted" className="text-xs">
          {description}
        </Typography>
      )}
    </div>
  );
});

KpiDisplay.displayName = "KpiDisplay";

/**
 * Componente para texto de status com ícone
 */
export const StatusText = React.forwardRef<
  HTMLSpanElement,
  {
    status: "success" | "warning" | "error" | "info";
    children: React.ReactNode;
    showIcon?: boolean;
    className?: string;
  }
>(({ status, children, showIcon = true, className, ...props }, ref) => {
  const icons = {
    success: "",
    warning: "",
    error: "",
    info: "ℹ",
  };

  return (
    <Typography
      ref={ref}
      as="span"
      variant={status}
      className={cn("inline-flex items-center gap-1", className)}
      {...props}
    >
      {showIcon && (
        <span aria-hidden="true">{icons[status]}</span>
      )}
      {children}
    </Typography>
  );
});

StatusText.displayName = "StatusText";

export { Typography, typographyVariants };
export type { TypographyProps };
