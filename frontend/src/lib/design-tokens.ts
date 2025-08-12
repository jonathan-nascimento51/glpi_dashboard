/**
 * Design Tokens - Sistema de Design GLPI Dashboard
 * 
 * Define tokens de design para cores, tipografia, espaçamentos,
 * sombras e outros elementos visuais com foco em acessibilidade.
 */

// Tokens de Cor - Baseados em HSL para melhor controle de acessibilidade
export const colorTokens = {
  // Cores Primárias - Azul GLPI
  primary: {
    50: "hsl(210, 100%, 97%)",   // Muito claro
    100: "hsl(210, 100%, 94%)",  // Claro
    200: "hsl(210, 100%, 87%)",  // Claro médio
    300: "hsl(210, 100%, 80%)",  // Médio claro
    400: "hsl(210, 100%, 66%)",  // Médio
    500: "hsl(210, 100%, 50%)",  // Base - #0066FF
    600: "hsl(210, 100%, 45%)",  // Escuro médio
    700: "hsl(210, 100%, 35%)",  // Escuro
    800: "hsl(210, 100%, 25%)",  // Muito escuro
    900: "hsl(210, 100%, 15%)",  // Mais escuro
  },

  // Cores Secundárias - Verde para sucesso
  secondary: {
    50: "hsl(142, 76%, 97%)",
    100: "hsl(142, 76%, 94%)",
    200: "hsl(142, 76%, 87%)",
    300: "hsl(142, 76%, 80%)",
    400: "hsl(142, 76%, 66%)",
    500: "hsl(142, 76%, 50%)",   // Base - #22C55E
    600: "hsl(142, 76%, 45%)",
    700: "hsl(142, 76%, 35%)",
    800: "hsl(142, 76%, 25%)",
    900: "hsl(142, 76%, 15%)",
  },

  // Cores de Status
  status: {
    success: {
      light: "hsl(142, 76%, 50%)",    // Verde
      DEFAULT: "hsl(142, 76%, 45%)",
      dark: "hsl(142, 76%, 35%)",
    },
    warning: {
      light: "hsl(45, 93%, 58%)",     // Amarelo
      DEFAULT: "hsl(45, 93%, 47%)",
      dark: "hsl(45, 93%, 37%)",
    },
    error: {
      light: "hsl(0, 84%, 60%)",      // Vermelho
      DEFAULT: "hsl(0, 84%, 50%)",
      dark: "hsl(0, 84%, 40%)",
    },
    info: {
      light: "hsl(199, 89%, 58%)",    // Azul claro
      DEFAULT: "hsl(199, 89%, 48%)",
      dark: "hsl(199, 89%, 38%)",
    },
  },

  // Cores Neutras - Escala de cinza
  neutral: {
    0: "hsl(0, 0%, 100%)",      // Branco
    50: "hsl(210, 20%, 98%)",
    100: "hsl(210, 20%, 95%)",
    200: "hsl(210, 16%, 93%)",
    300: "hsl(210, 14%, 89%)",
    400: "hsl(210, 14%, 83%)",
    500: "hsl(210, 11%, 71%)",
    600: "hsl(210, 7%, 56%)",
    700: "hsl(210, 9%, 31%)",
    800: "hsl(210, 10%, 23%)",
    900: "hsl(210, 11%, 15%)",
    950: "hsl(210, 11%, 7%)",
    1000: "hsl(0, 0%, 0%)",     // Preto
  },
} as const;

// Tokens de Tipografia
export const typographyTokens = {
  fontFamily: {
    sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
    mono: ["JetBrains Mono", "Consolas", "Monaco", "monospace"],
  },
  
  fontSize: {
    xs: "0.75rem",      // 12px
    sm: "0.875rem",     // 14px
    base: "1rem",       // 16px
    lg: "1.125rem",     // 18px
    xl: "1.25rem",      // 20px
    "2xl": "1.5rem",    // 24px
    "3xl": "1.875rem",  // 30px
    "4xl": "2.25rem",   // 36px
    "5xl": "3rem",      // 48px
  },
  
  fontWeight: {
    light: "300",
    normal: "400",
    medium: "500",
    semibold: "600",
    bold: "700",
    extrabold: "800",
  },
  
  lineHeight: {
    tight: "1.25",
    normal: "1.5",
    relaxed: "1.75",
  },
  
  letterSpacing: {
    tight: "-0.025em",
    normal: "0",
    wide: "0.025em",
  },
} as const;

// Tokens de Espaçamento
export const spacingTokens = {
  0: "0",
  1: "0.25rem",   // 4px
  2: "0.5rem",    // 8px
  3: "0.75rem",   // 12px
  4: "1rem",      // 16px
  5: "1.25rem",   // 20px
  6: "1.5rem",    // 24px
  8: "2rem",      // 32px
  10: "2.5rem",   // 40px
  12: "3rem",     // 48px
  16: "4rem",     // 64px
  20: "5rem",     // 80px
  24: "6rem",     // 96px
  32: "8rem",     // 128px
} as const;

// Tokens de Raio de Borda
export const radiusTokens = {
  none: "0",
  sm: "0.125rem",   // 2px
  base: "0.25rem",  // 4px
  md: "0.375rem",   // 6px
  lg: "0.5rem",     // 8px
  xl: "0.75rem",    // 12px
  "2xl": "1rem",    // 16px
  "3xl": "1.5rem",  // 24px
  full: "9999px",
} as const;

// Tokens de Sombra
export const shadowTokens = {
  none: "none",
  sm: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
  base: "0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)",
  md: "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)",
  lg: "0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)",
  xl: "0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)",
  "2xl": "0 25px 50px -12px rgb(0 0 0 / 0.25)",
  inner: "inset 0 2px 4px 0 rgb(0 0 0 / 0.05)",
} as const;

// Tokens de Transição
export const transitionTokens = {
  duration: {
    fast: "150ms",
    normal: "200ms",
    slow: "300ms",
  },
  timing: {
    ease: "ease",
    easeIn: "ease-in",
    easeOut: "ease-out",
    easeInOut: "ease-in-out",
  },
} as const;

// Tokens de Z-Index
export const zIndexTokens = {
  hide: -1,
  auto: "auto",
  base: 0,
  docked: 10,
  dropdown: 1000,
  sticky: 1100,
  banner: 1200,
  overlay: 1300,
  modal: 1400,
  popover: 1500,
  skipLink: 1600,
  toast: 1700,
  tooltip: 1800,
} as const;

// Tokens de Breakpoint
export const breakpointTokens = {
  sm: "640px",
  md: "768px",
  lg: "1024px",
  xl: "1280px",
  "2xl": "1536px",
} as const;

// Tokens Semânticos - Mapeamento de tokens para uso específico
export const semanticTokens = {
  colors: {
    // Backgrounds
    background: {
      primary: colorTokens.neutral[0],
      secondary: colorTokens.neutral[50],
      tertiary: colorTokens.neutral[100],
      inverse: colorTokens.neutral[900],
    },
    
    // Textos
    text: {
      primary: colorTokens.neutral[900],
      secondary: colorTokens.neutral[700],
      tertiary: colorTokens.neutral[600],
      inverse: colorTokens.neutral[0],
      disabled: colorTokens.neutral[400],
    },
    
    // Bordas
    border: {
      primary: colorTokens.neutral[200],
      secondary: colorTokens.neutral[300],
      focus: colorTokens.primary[500],
      error: colorTokens.status.error.DEFAULT,
    },
    
    // Interações
    interactive: {
      primary: colorTokens.primary[500],
      primaryHover: colorTokens.primary[600],
      primaryActive: colorTokens.primary[700],
      secondary: colorTokens.neutral[100],
      secondaryHover: colorTokens.neutral[200],
      secondaryActive: colorTokens.neutral[300],
    },
  },
  
  spacing: {
    component: {
      padding: spacingTokens[4],
      margin: spacingTokens[4],
      gap: spacingTokens[3],
    },
    layout: {
      containerPadding: spacingTokens[6],
      sectionGap: spacingTokens[12],
    },
  },
} as const;

// Exportar todos os tokens
export const designTokens = {
  colors: colorTokens,
  typography: typographyTokens,
  spacing: spacingTokens,
  radius: radiusTokens,
  shadow: shadowTokens,
  transition: transitionTokens,
  zIndex: zIndexTokens,
  breakpoint: breakpointTokens,
  semantic: semanticTokens,
} as const;

export type DesignTokens = typeof designTokens;
export type ColorTokens = typeof colorTokens;
export type TypographyTokens = typeof typographyTokens;
export type SpacingTokens = typeof spacingTokens;
export type RadiusTokens = typeof radiusTokens;
export type ShadowTokens = typeof shadowTokens;
export type TransitionTokens = typeof transitionTokens;
export type ZIndexTokens = typeof zIndexTokens;
export type BreakpointTokens = typeof breakpointTokens;
export type SemanticTokens = typeof semanticTokens;
