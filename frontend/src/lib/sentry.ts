import * as Sentry from '@sentry/react';

/**
 * Initialize Sentry for error monitoring and performance tracking
 * Only initializes if VITE_SENTRY_DSN environment variable is set
 */
export function initSentry() {
  const dsn = import.meta.env.VITE_SENTRY_DSN;
  
  // Only initialize if DSN is provided
  if (!dsn) {
    console.log('Sentry DSN not provided, skipping initialization');
    return;
  }

  Sentry.init({
    dsn,
    environment: import.meta.env.VITE_ENVIRONMENT || 'development',
    release: import.meta.env.VITE_RELEASE || 'local',
    integrations: [
      Sentry.browserTracingIntegration(),
      Sentry.replayIntegration(),
    ],
    // Set tracing origins to connect the frontend to the backend
    tracePropagationTargets: [
      'localhost',
      /^https:\/\/yourapi\.domain\.com\/api/,
    ],
    // Performance Monitoring
    tracesSampleRate: parseFloat(import.meta.env.VITE_SENTRY_TRACES_SAMPLE_RATE || '0.1'),
    // Session Replay
    replaysSessionSampleRate: parseFloat(import.meta.env.VITE_SENTRY_REPLAYS_SESSION_SAMPLE_RATE || '0.1'),
    replaysOnErrorSampleRate: parseFloat(import.meta.env.VITE_SENTRY_REPLAYS_ON_ERROR_SAMPLE_RATE || '1.0'),
  });

  console.log('Sentry initialized successfully');
}