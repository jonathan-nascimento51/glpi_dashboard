import { test, expect } from '@playwright/test';

/**
 * Test scenario: API error handling and visible error states
 * This test verifies that the dashboard shows appropriate error states
 * when the API is down or returns error responses.
 */
test.describe('API Error Handling', () => {
  test.skip('should show error state when API is down', async ({ page }) => {
    // Mock API failure for dashboard KPIs
    await page.route('**/api/dashboard/kpis**', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' })
      });
    });

    // Navigate to the dashboard
    await page.goto('/');

    // Wait for the failed API call
    await page.waitForResponse(response => 
      response.url().includes('/api/dashboard/kpis') && response.status() === 500
    );

    // Verify error state is visible
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="error-message"]')).toContainText(/erro|falha|indisponível/i);

    // Verify retry button is available
    await expect(page.locator('[data-testid="retry-button"]')).toBeVisible();

    // Verify KPI containers show error state instead of data
    await expect(page.locator('[data-testid="kpi-error-state"]')).toBeVisible();
  });

  test.skip('should allow retry after API error', async ({ page }) => {
    let apiCallCount = 0;

    // Mock API failure on first call, success on retry
    await page.route('**/api/dashboard/kpis**', route => {
      apiCallCount++;
      if (apiCallCount === 1) {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Internal Server Error' })
        });
      } else {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            tickets_count: 150,
            avg_resolution_time: '2.5 hours',
            satisfaction_rate: 85
          })
        });
      }
    });

    await page.goto('/');

    // Wait for initial error
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();

    // Click retry button
    await page.locator('[data-testid="retry-button"]').click();

    // Wait for successful retry
    await page.waitForResponse(response => 
      response.url().includes('/api/dashboard/kpis') && response.status() === 200
    );

    // Verify error state is hidden and data is shown
    await expect(page.locator('[data-testid="error-message"]')).not.toBeVisible();
    await expect(page.locator('[data-testid="kpi-container"]')).toBeVisible();
    await expect(page.locator('[data-testid="tickets-count"]')).toContainText('150');
  });

  test.skip('should show network error state when offline', async ({ page }) => {
    // Simulate network failure
    await page.route('**/api/**', route => {
      route.abort('failed');
    });

    await page.goto('/');

    // Verify network error state
    await expect(page.locator('[data-testid="network-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="network-error"]')).toContainText(/conexão|rede|offline/i);

    // Verify offline indicator is shown
    await expect(page.locator('[data-testid="offline-indicator"]')).toBeVisible();
  });

  test.skip('should handle partial API failures gracefully', async ({ page }) => {
    // Mock success for KPIs but failure for charts
    await page.route('**/api/dashboard/kpis**', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          tickets_count: 100,
          avg_resolution_time: '3 hours'
        })
      });
    });

    await page.route('**/api/dashboard/charts**', route => {
      route.fulfill({
        status: 503,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Service Unavailable' })
      });
    });

    await page.goto('/');

    // Verify KPIs load successfully
    await expect(page.locator('[data-testid="kpi-container"]')).toBeVisible();
    await expect(page.locator('[data-testid="tickets-count"]')).toContainText('100');

    // Verify charts show error state
    await expect(page.locator('[data-testid="chart-error-state"]')).toBeVisible();
    await expect(page.locator('[data-testid="chart-retry-button"]')).toBeVisible();
  });
});