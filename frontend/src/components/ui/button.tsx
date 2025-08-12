import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";
import { designTokens } from "@/lib/design-tokens";

/**
 * Variantes do componente Button com foco em acessibilidade
 * Todas as variantes seguem as diretrizes WCAG 2.1 AA para contraste
 */
const buttonVariants = cva(
  // Classes base com foco em acessibilidade
  [
    "inline-flex items-center justify-center gap-2 whitespace-nowrap",
    "rounded-md text-sm font-medium transition-colors duration-200",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
    "focus-visible:ring-offset-2 focus-visible:ring-offset-background",
    "disabled:pointer-events-none disabled:opacity-50",
    "[&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
    // Melhor suporte para leitores de tela
    "relative overflow-hidden",
    // Indicador de loading acessível
    "data-[loading=true]:text-transparent",
  ],
  {
    variants: {
      variant: {
        default: [
          "bg-primary text-primary-foreground shadow",
          "hover:bg-primary/90 active:bg-primary/95",
          "focus-visible:ring-primary/50",
        ],
        destructive: [
          "bg-destructive text-destructive-foreground shadow-sm",
          "hover:bg-destructive/90 active:bg-destructive/95",
          "focus-visible:ring-destructive/50",
        ],
        outline: [
          "border border-input bg-background shadow-sm",
          "hover:bg-accent hover:text-accent-foreground",
          "active:bg-accent/90",
          "focus-visible:ring-accent/50",
        ],
        secondary: [
          "bg-secondary text-secondary-foreground shadow-sm",
          "hover:bg-secondary/80 active:bg-secondary/90",
          "focus-visible:ring-secondary/50",
        ],
        ghost: [
          "hover:bg-accent hover:text-accent-foreground",
          "active:bg-accent/90",
          "focus-visible:ring-accent/50",
        ],
        link: [
          "text-primary underline-offset-4",
          "hover:underline focus-visible:underline",
          "focus-visible:ring-primary/50",
        ],
        // Nova variante para status de sucesso
        success: [
          "bg-green-600 text-white shadow",
          "hover:bg-green-700 active:bg-green-800",
          "focus-visible:ring-green-500/50",
        ],
        // Nova variante para status de aviso
        warning: [
          "bg-yellow-600 text-white shadow",
          "hover:bg-yellow-700 active:bg-yellow-800",
          "focus-visible:ring-yellow-500/50",
        ],
      },
      size: {
        default: "h-9 px-4 py-2",
        sm: "h-8 rounded-md px-3 text-xs",
        lg: "h-10 rounded-md px-8",
        xl: "h-12 rounded-lg px-10 text-base",
        icon: "h-9 w-9",
        "icon-sm": "h-8 w-8",
        "icon-lg": "h-10 w-10",
      },
      // Nova prop para estado de loading
      loading: {
        true: "cursor-not-allowed",
        false: "",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
      loading: false,
    },
  }
);

/**
 * Props do componente Button com melhorias de acessibilidade
 */
export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  /** Renderizar como um componente filho usando Radix Slot */
  asChild?: boolean;
  /** Estado de loading do botão */
  loading?: boolean;
  /** Ícone a ser exibido no botão */
  icon?: React.ReactNode;
  /** Posição do ícone */
  iconPosition?: "left" | "right";
  /** Texto alternativo para leitores de tela quando em loading */
  loadingText?: string;
  /** Tooltip acessível */
  tooltip?: string;
}

/**
 * Componente Button com foco em acessibilidade e design consistente
 * 
 * Características de acessibilidade:
 * - Suporte completo a navegação por teclado
 * - Estados de foco visíveis e bem contrastados
 * - Suporte a leitores de tela
 * - Estados de loading acessíveis
 * - Contraste de cores conforme WCAG 2.1 AA
 */
const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant,
      size,
      loading = false,
      icon,
      iconPosition = "left",
      loadingText = "Carregando...",
      tooltip,
      children,
      disabled,
      asChild = false,
      ...props
    },
    ref
  ) => {
    const Comp = asChild ? Slot : "button";
    const isDisabled = disabled || loading;

    // Componente de loading spinner acessível
    const LoadingSpinner = () => (
      <svg
        className="animate-spin h-4 w-4"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
    );

    const buttonContent = (
      <>
        {loading && (
          <span className="absolute inset-0 flex items-center justify-center">
            <LoadingSpinner />
            <span className="sr-only">{loadingText}</span>
          </span>
        )}
        
        {!loading && icon && iconPosition === "left" && (
          <span className="flex-shrink-0" aria-hidden="true">
            {icon}
          </span>
        )}
        
        <span className={loading ? "invisible" : ""}>
          {children}
        </span>
        
        {!loading && icon && iconPosition === "right" && (
          <span className="flex-shrink-0" aria-hidden="true">
            {icon}
          </span>
        )}
      </>
    );

    return (
      <Comp
        className={cn(
          buttonVariants({ variant, size, loading, className })
        )}
        ref={ref}
        disabled={isDisabled}
        data-loading={loading}
        title={tooltip}
        aria-disabled={isDisabled}
        aria-busy={loading}
        {...props}
      >
        {buttonContent}
      </Comp>
    );
  }
);

Button.displayName = "Button";

export { Button, buttonVariants };
export type { ButtonProps };
