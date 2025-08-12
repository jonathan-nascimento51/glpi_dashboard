import React from "react";
import type { RefObject } from "react";

/**
 * Configuração do axe-core para validação de acessibilidade
 */
const axeConfig = {
  tags: ["wcag2a", "wcag2aa", "wcag21aa"],
  rules: {
    "color-contrast": { enabled: true },
    "keyboard-navigation": { enabled: true },
    "focus-order-semantics": { enabled: true },
    "aria-required-attr": { enabled: true },
    "aria-valid-attr-value": { enabled: true },
    "button-name": { enabled: true },
    "link-name": { enabled: true },
    "image-alt": { enabled: true },
    "label": { enabled: true },
    "landmark-one-main": { enabled: true },
    "page-has-heading-one": { enabled: true },
    "region": { enabled: true },
    "skip-link": { enabled: true },
    "tabindex": { enabled: true },
  },
};

/**
 * Inicializa o axe-core para desenvolvimento
 */
export const initializeAxe = async (): Promise<void> => {
  if (process.env.NODE_ENV !== "development") {
    return;
  }

  try {
    const { default: axeCore } = await import("axe-core");
    axeCore.configure(axeConfig);
    console.log(" Axe-core inicializado para validação de acessibilidade");
  } catch (error) {
    console.error("Erro ao inicializar axe-core:", error);
  }
};

/**
 * Hook para validação de acessibilidade em componentes específicos
 */
export const useAxeValidation = (
  ref: RefObject<HTMLElement | null>,
  options: {
    enabled?: boolean;
    debounceMs?: number;
    tags?: string[];
  } = {}
): void => {
  const { enabled = true, debounceMs = 1000, tags = ["wcag2a", "wcag2aa"] } = options;

  React.useEffect(() => {
    if (!enabled || process.env.NODE_ENV !== "development" || !ref.current) {
      return;
    }

    let timeoutId: NodeJS.Timeout;

    const validateAccessibility = async () => {
      try {
        const { default: axeCore } = await import("axe-core");
        
        if (!ref.current) return;

        const results = await axeCore.run(ref.current, {
          tags,
          rules: axeConfig.rules,
        });

        if (results.violations.length > 0) {
          console.group(" Acessibilidade: Violations no componente");
          results.violations.forEach((violation) => {
            console.warn(`${violation.id}: ${violation.description}`);
            console.log("Elementos:", violation.nodes);
            console.log("Ajuda:", violation.helpUrl);
          });
          console.groupEnd();
        }
      } catch (error) {
        console.error("Erro na validação de acessibilidade:", error);
      }
    };

    const debouncedValidate = () => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(validateAccessibility, debounceMs);
    };

    if (ref.current) {
      const observer = new MutationObserver(debouncedValidate);
      observer.observe(ref.current, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ["aria-*", "role", "tabindex", "class"],
      });

      debouncedValidate();

      return () => {
        clearTimeout(timeoutId);
        observer.disconnect();
      };
    }
  }, [ref, enabled, debounceMs, tags]);
};

/**
 * Executa uma auditoria completa de acessibilidade
 */
export const runFullAccessibilityAudit = async () => {
  try {
    const { default: axeCore } = await import("axe-core");
    
    const results = await axeCore.run(document.body, axeConfig);
    
    const summary = {
      total: results.violations.length,
      critical: results.violations.filter(v => v.impact === "critical").length,
      serious: results.violations.filter(v => v.impact === "serious").length,
      moderate: results.violations.filter(v => v.impact === "moderate").length,
      minor: results.violations.filter(v => v.impact === "minor").length,
    };

    return {
      passed: results.violations.length === 0,
      violations: results.violations,
      summary,
    };
  } catch (error) {
    console.error("Erro na auditoria de acessibilidade:", error);
    return {
      passed: false,
      violations: [],
      summary: { total: 0, critical: 0, serious: 0, moderate: 0, minor: 0 },
    };
  }
};

/**
 * Componente wrapper para validação automática de acessibilidade
 */
interface AccessibilityValidatorProps {
  children: React.ReactNode;
  name?: string;
  disabled?: boolean;
}

export const AccessibilityValidator: React.FC<AccessibilityValidatorProps> = ({ 
  children, 
  name = "component", 
  disabled = false 
}) => {
  const ref = React.useRef<HTMLDivElement>(null);

  useAxeValidation(disabled ? { current: null } : ref);

  return React.createElement(
    "div",
    {
      ref: ref,
      "data-testid": `a11y-validator-${name}`,
    },
    children
  );
};

/**
 * Utilitários para testes de acessibilidade em Jest/Testing Library
 */
export const testAccessibility = async (container: HTMLElement) => {
  const { default: axeCore } = await import("axe-core");

  const results = await axeCore.run(container, {
    tags: ["wcag2a", "wcag2aa"],
  });

  const criticalViolations = results.violations.filter(
    (violation) => violation.impact === "critical" || violation.impact === "serious"
  );

  if (criticalViolations.length > 0) {
    const errorMessage = criticalViolations
      .map((violation) => `${violation.id}: ${violation.description}`)
      .join("\n");
    
    throw new Error(`Violations críticas de acessibilidade encontradas:\n${errorMessage}`);
  }

  return results;
};

/**
 * Tipos para TypeScript
 */
export interface AccessibilityAuditResult {
  passed: boolean;
  violations: any[];
  summary: {
    total: number;
    critical: number;
    serious: number;
    moderate: number;
    minor: number;
  };
}

export interface AxeValidationOptions {
  enabled?: boolean;
  debounceMs?: number;
  tags?: string[];
}

/**
 * Constantes úteis
 */
export const ACCESSIBILITY_TAGS = {
  WCAG_2A: "wcag2a",
  WCAG_2AA: "wcag2aa",
  WCAG_21AA: "wcag21aa",
  BEST_PRACTICES: "best-practice",
  EXPERIMENTAL: "experimental",
} as const;

export const IMPACT_LEVELS = {
  CRITICAL: "critical",
  SERIOUS: "serious",
  MODERATE: "moderate",
  MINOR: "minor",
} as const;
