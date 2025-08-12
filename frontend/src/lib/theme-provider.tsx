import React, { createContext, useContext, useEffect, useState } from "react";
import { designTokens } from "./design-tokens";

// Tipos para o tema
export type ThemeMode = "light" | "dark" | "auto";

export interface ThemeContextType {
  mode: ThemeMode;
  setMode: (mode: ThemeMode) => void;
  tokens: typeof designTokens;
  isDark: boolean;
  toggleTheme: () => void;
}

// Context do tema
const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

// Hook para usar o tema
export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme deve ser usado dentro de um ThemeProvider");
  }
  return context;
};

// Props do ThemeProvider
export interface ThemeProviderProps {
  children: React.ReactNode;
  defaultMode?: ThemeMode;
  storageKey?: string;
}

// Função para detectar preferência do sistema
const getSystemTheme = (): "light" | "dark" => {
  if (typeof window === "undefined") return "light";
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
};

// Função para aplicar o tema no documento
const applyTheme = (isDark: boolean) => {
  if (typeof document === "undefined") return;
  
  const root = document.documentElement;
  
  if (isDark) {
    root.classList.add("dark");
    root.style.setProperty("--background", designTokens.semantic.colors.background.inverse);
    root.style.setProperty("--foreground", designTokens.semantic.colors.text.inverse);
    root.style.setProperty("--card", designTokens.colors.neutral[800]);
    root.style.setProperty("--card-foreground", designTokens.colors.neutral[100]);
    root.style.setProperty("--popover", designTokens.colors.neutral[800]);
    root.style.setProperty("--popover-foreground", designTokens.colors.neutral[100]);
    root.style.setProperty("--primary", designTokens.colors.primary[400]);
    root.style.setProperty("--primary-foreground", designTokens.colors.neutral[900]);
    root.style.setProperty("--secondary", designTokens.colors.neutral[700]);
    root.style.setProperty("--secondary-foreground", designTokens.colors.neutral[100]);
    root.style.setProperty("--muted", designTokens.colors.neutral[700]);
    root.style.setProperty("--muted-foreground", designTokens.colors.neutral[400]);
    root.style.setProperty("--accent", designTokens.colors.neutral[700]);
    root.style.setProperty("--accent-foreground", designTokens.colors.neutral[100]);
    root.style.setProperty("--destructive", designTokens.colors.status.error.light);
    root.style.setProperty("--destructive-foreground", designTokens.colors.neutral[100]);
    root.style.setProperty("--border", designTokens.colors.neutral[700]);
    root.style.setProperty("--input", designTokens.colors.neutral[700]);
    root.style.setProperty("--ring", designTokens.colors.primary[400]);
  } else {
    root.classList.remove("dark");
    root.style.setProperty("--background", designTokens.semantic.colors.background.primary);
    root.style.setProperty("--foreground", designTokens.semantic.colors.text.primary);
    root.style.setProperty("--card", designTokens.colors.neutral[0]);
    root.style.setProperty("--card-foreground", designTokens.colors.neutral[900]);
    root.style.setProperty("--popover", designTokens.colors.neutral[0]);
    root.style.setProperty("--popover-foreground", designTokens.colors.neutral[900]);
    root.style.setProperty("--primary", designTokens.colors.primary[500]);
    root.style.setProperty("--primary-foreground", designTokens.colors.neutral[0]);
    root.style.setProperty("--secondary", designTokens.colors.neutral[100]);
    root.style.setProperty("--secondary-foreground", designTokens.colors.neutral[900]);
    root.style.setProperty("--muted", designTokens.colors.neutral[100]);
    root.style.setProperty("--muted-foreground", designTokens.colors.neutral[600]);
    root.style.setProperty("--accent", designTokens.colors.neutral[100]);
    root.style.setProperty("--accent-foreground", designTokens.colors.neutral[900]);
    root.style.setProperty("--destructive", designTokens.colors.status.error.DEFAULT);
    root.style.setProperty("--destructive-foreground", designTokens.colors.neutral[0]);
    root.style.setProperty("--border", designTokens.semantic.colors.border.primary);
    root.style.setProperty("--input", designTokens.semantic.colors.border.primary);
    root.style.setProperty("--ring", designTokens.semantic.colors.border.focus);
  }
};

// ThemeProvider Component
export const ThemeProvider: React.FC<ThemeProviderProps> = ({
  children,
  defaultMode = "auto",
  storageKey = "glpi-dashboard-theme",
}) => {
  const [mode, setModeState] = useState<ThemeMode>(defaultMode);
  const [systemTheme, setSystemTheme] = useState<"light" | "dark">("light");

  // Determinar se o tema atual é escuro
  const isDark = mode === "dark" || (mode === "auto" && systemTheme === "dark");

  // Função para alterar o modo do tema
  const setMode = (newMode: ThemeMode) => {
    setModeState(newMode);
    if (typeof window !== "undefined") {
      localStorage.setItem(storageKey, newMode);
    }
  };

  // Função para alternar entre light e dark
  const toggleTheme = () => {
    setMode(isDark ? "light" : "dark");
  };

  // Efeito para carregar o tema do localStorage
  useEffect(() => {
    if (typeof window === "undefined") return;
    
    const stored = localStorage.getItem(storageKey) as ThemeMode;
    if (stored && ["light", "dark", "auto"].includes(stored)) {
      setModeState(stored);
    }
    
    // Detectar tema do sistema
    setSystemTheme(getSystemTheme());
  }, [storageKey]);

  // Efeito para escutar mudanças na preferência do sistema
  useEffect(() => {
    if (typeof window === "undefined") return;
    
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    const handleChange = (e: MediaQueryListEvent) => {
      setSystemTheme(e.matches ? "dark" : "light");
    };
    
    mediaQuery.addEventListener("change", handleChange);
    return () => mediaQuery.removeEventListener("change", handleChange);
  }, []);

  // Efeito para aplicar o tema
  useEffect(() => {
    applyTheme(isDark);
  }, [isDark]);

  const value: ThemeContextType = {
    mode,
    setMode,
    tokens: designTokens,
    isDark,
    toggleTheme,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};

// Hook para acessar tokens específicos
export const useDesignTokens = () => {
  const { tokens } = useTheme();
  return tokens;
};

// Hook para acessar apenas o modo do tema
export const useThemeMode = () => {
  const { mode, setMode, isDark, toggleTheme } = useTheme();
  return { mode, setMode, isDark, toggleTheme };
};

// Utilitários para classes CSS baseadas no tema
export const themeClasses = {
  // Backgrounds
  bgPrimary: "bg-background",
  bgSecondary: "bg-muted",
  bgCard: "bg-card",
  
  // Textos
  textPrimary: "text-foreground",
  textSecondary: "text-muted-foreground",
  textAccent: "text-accent-foreground",
  
  // Bordas
  border: "border-border",
  borderInput: "border-input",
  
  // Estados interativos
  hover: "hover:bg-accent hover:text-accent-foreground",
  focus: "focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  
  // Transições
  transition: "transition-colors duration-200",
} as const;

export default ThemeProvider;
