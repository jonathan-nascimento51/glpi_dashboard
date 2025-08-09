import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { UnleashClient } from '@unleash/proxy-client-js';
type FlagsContextValue = { isEnabled: (flag: string) => boolean };
const FlagsContext = createContext<FlagsContextValue>({ isEnabled: () => false });
export function FlagsProvider({ children }: { children: React.ReactNode }) {
  const [client] = useState(() => new UnleashClient({
    url: import.meta.env.VITE_UNLEASH_PROXY_URL ?? '',
    clientKey: import.meta.env.VITE_UNLEASH_PROXY_CLIENT_KEY ?? '',
    appName: import.meta.env.VITE_UNLEASH_APP_NAME ?? 'gadpi-frontend',
  }));
  const [ready, setReady] = useState(false);
  useEffect(() => { client.on('ready', () => setReady(true)); client.start(); return () => client.stop(); }, [client]);
  const value = useMemo<FlagsContextValue>(() => ({ isEnabled: (flag: string) => ready ? client.isEnabled(flag) : false }), [client, ready]);
  return <FlagsContext.Provider value={value}>{children}</FlagsContext.Provider>;
}
export function useFlag(name: string): boolean { return useContext(FlagsContext).isEnabled(name); }