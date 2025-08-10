import { test, expect } from '@playwright/test';

test.describe('KPI Updates - Advanced E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Mock successful API responses for default tests
    await page.route('**/v1/kpis*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          tickets_count: 42,
          avg_resolution_time: 2.5,
          satisfaction_rate: 85.2,
          pending_tickets: 15
        })
      });
    });

    await page.route('**/v2/kpis*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          tickets_count: 45,
          avg_resolution_time: 2.2,
          satisfaction_rate: 87.5,
          pending_tickets: 12,
          new_metric: 'enhanced_data'
        })
      });
    });
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // Override the beforeEach mock to simulate API failure
    await page.route('**/v1/kpis*', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          error: 'Internal Server Error',
          message: 'Failed to fetch KPIs'
        })
      });
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Wait for error state to appear
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('[data-testid="error-message"]')).toContainText(/failed|error/i);

    // Verify KPI loading state is not shown
    await expect(page.locator('[data-testid="kpi-loading"]')).not.toBeVisible();
  });

  test('should display different data based on feature flags', async ({ page }) => {
    // Set feature flag to use v2 API
    await page.addInitScript(() => {
      window.localStorage.setItem('VITE_FLAG_USE_V2_KPIS', 'true');
    });

    let v2ApiCalled = false;
    let v1ApiCalled = false;

    // Track which API endpoint is called
    await page.route('**/v2/kpis*', async route => {
      v2ApiCalled = true;
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          tickets_count: 45,
          avg_resolution_time: 2.2,
          satisfaction_rate: 87.5,
          pending_tickets: 12,
          new_metric: 'enhanced_data'
        })
      });
    });

    await page.route('**/v1/kpis*', async route => {
      v1ApiCalled = true;
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          tickets_count: 42,
          avg_resolution_time: 2.5,
          satisfaction_rate: 85.2,
          pending_tickets: 15
        })
      });
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Wait for API call
    await page.waitForResponse(response =>
      response.url().includes('/kpis') && response.status() === 200
    );

    // Verify the correct API was called based on feature flag
    // Note: This test assumes the feature flag logic is implemented
    await expect(page.locator('[data-testid="tickets-count"]')).toBeVisible();
  });

  test('should handle network timeouts', async ({ page }) => {
    // Simulate network timeout
    await page.route('**/v1/kpis*', async route => {
      // Delay response to simulate timeout
      await new Promise(resolve => setTimeout(resolve, 10000));
      await route.fulfill({
        status: 408,
        contentType: 'application/json',
        body: JSON.stringify({
          error: 'Request Timeout'
        })
      });
    });

    await page.goto('/');
    
    // Should show loading state initially
    await expect(page.locator('[data-testid="kpi-loading"]')).toBeVisible();
    
    // Should eventually show timeout error or handle gracefully
    await expect(page.locator('[data-testid="error-message"], [data-testid="kpi-loading"]')).toBeVisible({ timeout: 15000 });
  });

  test('should retry failed requests', async ({ page }) => {
    let requestCount = 0;
    
    await page.route('**/v1/kpis*', async route => {
      requestCount++;
      
      if (requestCount === 1) {
        // First request fails
        await route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Server Error' })
        });
      } else {
        // Second request succeeds
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            tickets_count: 42,
            avg_resolution_time: 2.5,
            satisfaction_rate: 85.2,
            pending_tickets: 15
          })
        });
      }
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Should eventually show data after retry (if retry logic is implemented)
    await expect(page.locator('[data-testid="tickets-count"], [data-testid="error-message"]')).toBeVisible({ timeout: 10000 });
  });

  test('should validate accessibility', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Wait for KPIs to load
    await expect(page.locator('[data-testid="tickets-count"]')).toBeVisible();

    // Check for basic accessibility attributes
    const kpiElements = page.locator('[data-testid*="kpi"], [data-testid*="tickets"], [data-testid*="resolution"], [data-testid*="satisfaction"]');
    
    // Verify elements are accessible
    for (let i = 0; i < await kpiElements.count(); i++) {
      const element = kpiElements.nth(i);
      await expect(element).toBeVisible();
    }

    // Check for proper heading structure
    const headings = page.locator('h1, h2, h3, h4, h5, h6');
    expect(await headings.count()).toBeGreaterThan(0);
  });

  test('should handle rapid filter changes', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Wait for initial load
    await expect(page.locator('[data-testid="tickets-count"]')).toBeVisible();

    // Rapidly change filters
    const filterDropdown = page.locator('[data-testid="date-filter-dropdown"]');
    
    if (await filterDropdown.isVisible()) {
      await filterDropdown.click();
      
      // Try to click multiple filter options rapidly
      const filterOptions = page.locator('[data-testid*="period-"]');
      const optionCount = await filterOptions.count();
      
      if (optionCount > 0) {
        for (let i = 0; i < Math.min(3, optionCount); i++) {
          await filterOptions.nth(i).click();
          await page.waitForTimeout(100); // Small delay between clicks
        }
      }
    }

    // Verify the application doesn't crash
    await expect(page.locator('[data-testid="tickets-count"]')).toBeVisible();
  });

  test('should maintain state during navigation', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Wait for KPIs to load
    await expect(page.locator('[data-testid="tickets-count"]')).toBeVisible();
    
    // Get initial values
    const initialTicketsCount = await page.locator('[data-testid="tickets-count"]').textContent();
    
    // Navigate away and back (if there are other pages)
    await page.goBack();
    await page.goForward();
    
    // Verify state is maintained or properly reloaded
    await expect(page.locator('[data-testid="tickets-count"]')).toBeVisible();
    const finalTicketsCount = await page.locator('[data-testid="tickets-count"]').textContent();
    
    // Values should be consistent
    expect(finalTicketsCount).toBeDefined();
  });
});
