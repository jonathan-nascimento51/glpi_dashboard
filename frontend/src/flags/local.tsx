import { createContext, useContext, useMemo } from 'react';

type FlagsContextValue = { isEnabled: (flag: string) => boolean };
const FlagsContext = createContext<FlagsContextValue>({ isEnabled: () => false });

// Configuração local de feature flags
const LOCAL_FLAGS: Record<string, boolean> = {
  'use_v2_kpis': false, // Desligado por padrão
};

export function LocalFlagsProvider({ children }: { children: React.ReactNode }) {
  const value = useMemo<FlagsContextValue>(() => ({
    isEnabled: (flag: string) => {
      // Verifica primeiro as variáveis de ambiente
      const envFlag = import.meta.env[`VITE_FLAG_${flag.toUpperCase()}`];
      if (envFlag !== undefined) {
        return envFlag === 'true';
      }
      // Fallback para configuração local
      return LOCAL_FLAGS[flag] ?? false;
    }
  }), []);

  return <FlagsContext.Provider value={value}>{children}</FlagsContext.Provider>;
}

export function useLocalFlag(name: string): boolean {
  return useContext(FlagsContext).isEnabled(name);
}
