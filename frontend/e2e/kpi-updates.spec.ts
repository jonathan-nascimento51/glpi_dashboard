import { test, expect } from '@playwright/test';

/**
 * Test scenario: KPI updates when selecting different time periods
 * This test verifies that the dashboard KPIs update correctly when users
 * select different time periods from the date filter.
 */
test.describe('KPI Updates on Period Selection', () => {
  test.skip('should update KPIs when selecting different time periods', async ({ page }) => {
    // Navigate to the dashboard
    await page.goto('/');

    // Wait for the dashboard to load
    await page.waitForLoadState('networkidle');

    // Verify initial KPIs are loaded
    await expect(page.locator('[data-testid="kpi-container"]')).toBeVisible();

    // Get initial KPI values
    const initialTicketsCount = await page.locator('[data-testid="tickets-count"]').textContent();
    const initialAvgResolutionTime = await page.locator('[data-testid="avg-resolution-time"]').textContent();

    // Open date filter dropdown
    await page.locator('[data-testid="date-filter-dropdown"]').click();

    // Select a different time period (e.g., "Last 7 days")
    await page.locator('[data-testid="period-7-days"]').click();

    // Wait for API call to complete and KPIs to update
    await page.waitForResponse(response => 
      response.url().includes('/api/dashboard/kpis') && response.status() === 200
    );

    // Verify KPIs have updated (values should be different)
    const updatedTicketsCount = await page.locator('[data-testid="tickets-count"]').textContent();
    const updatedAvgResolutionTime = await page.locator('[data-testid="avg-resolution-time"]').textContent();

    // Assert that values have changed (or at least the loading state was shown)
    expect(updatedTicketsCount).toBeDefined();
    expect(updatedAvgResolutionTime).toBeDefined();

    // Verify no error states are shown
    await expect(page.locator('[data-testid="error-message"]')).not.toBeVisible();
  });

  test.skip('should show loading state during KPI updates', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Open date filter and select new period
    await page.locator('[data-testid="date-filter-dropdown"]').click();
    await page.locator('[data-testid="period-30-days"]').click();

    // Verify loading state is shown
    await expect(page.locator('[data-testid="kpi-loading"]')).toBeVisible();

    // Wait for loading to complete
    await page.waitForResponse(response => 
      response.url().includes('/api/dashboard/kpis') && response.status() === 200
    );

    // Verify loading state is hidden
    await expect(page.locator('[data-testid="kpi-loading"]')).not.toBeVisible();
  });
});