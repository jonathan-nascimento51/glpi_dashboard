import 'vitest/globals';
import type { TestingLibraryMatchers } from '@testing-library/jest-dom/matchers';
import type { AxeMatchers } from 'jest-axe';
import type { ImageSnapshotMatchers } from 'jest-image-snapshot';

// Playwright-like matchers for E2E tests
interface PlaywrightMatchers<T = any> {
  toBeVisible(): T;
  toContainText(text: string): T;
  toHaveText(text: string): T;
  toHaveValue(value: string): T;
  toBeEnabled(): T;
  toBeDisabled(): T;
  toBeChecked(): T;
  toHaveAttribute(name: string, value?: string): T;
  toHaveClass(className: string): T;
}

declare module 'vitest' {
  interface Assertion<T = any>
    extends jest.Matchers<void, T>,
      TestingLibraryMatchers<T, void>,
      AxeMatchers,
      ImageSnapshotMatchers,
      PlaywrightMatchers<T> {
    toHaveNoViolations(): T;
    toMatchImageSnapshot(options?: any): T;
  }
  interface AsymmetricMatchersContaining
    extends jest.Matchers<void, any>,
      TestingLibraryMatchers<any, void>,
      AxeMatchers,
      ImageSnapshotMatchers,
      PlaywrightMatchers<any> {
    toHaveNoViolations(): any;
    toMatchImageSnapshot(options?: any): any;
  }
}
