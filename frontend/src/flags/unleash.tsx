import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { UnleashClient } from '@unleash/proxy-client-js';
import { LocalFlagsProvider, useLocalFlag } from './local';

type FlagsContextValue = { isEnabled: (flag: string) => boolean };
const FlagsContext = createContext<FlagsContextValue>({ isEnabled: () => false });

export function FlagsProvider({ children }: { children: React.ReactNode }) {
  const unleashUrl = import.meta.env.VITE_UNLEASH_PROXY_URL;
  const unleashKey = import.meta.env.VITE_UNLEASH_PROXY_CLIENT_KEY;
  
  // Se não há configuração do Unleash, usa flags locais
  if (!unleashUrl || !unleashKey) {
    return <LocalFlagsProvider>{children}</LocalFlagsProvider>;
  }

  const [client] = useState(() => new UnleashClient({
    url: unleashUrl,
    clientKey: unleashKey,
    appName: import.meta.env.VITE_UNLEASH_APP_NAME ?? 'gadpi-frontend',
  }));
  
  const [ready, setReady] = useState(false);
  
  useEffect(() => {
    client.on('ready', () => setReady(true));
    client.start();
    return () => client.stop();
  }, [client]);
  
  const value = useMemo<FlagsContextValue>(() => ({
    isEnabled: (flag: string) => ready ? client.isEnabled(flag) : false
  }), [client, ready]);
  
  return <FlagsContext.Provider value={value}>{children}</FlagsContext.Provider>;
}

export function useFlag(name: string): boolean {
  const unleashUrl = import.meta.env.VITE_UNLEASH_PROXY_URL;
  const unleashKey = import.meta.env.VITE_UNLEASH_PROXY_CLIENT_KEY;
  
  // Se não há configuração do Unleash, usa flags locais
  if (!unleashUrl || !unleashKey) {
    return useLocalFlag(name);
  }
  
  return useContext(FlagsContext).isEnabled(name);
}
