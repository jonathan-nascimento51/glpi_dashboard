/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  readonly VITE_LOG_LEVEL: string;
  readonly VITE_SHOW_PERFORMANCE: string;
  readonly VITE_SHOW_API_CALLS: string;
  readonly VITE_SHOW_CACHE_HITS: string;
  readonly DEV: boolean;
  readonly PROD: boolean;
  readonly MODE: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
