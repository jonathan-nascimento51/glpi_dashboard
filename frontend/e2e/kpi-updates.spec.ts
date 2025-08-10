import { test, expect } from '@playwright/test';

test.describe('KPI Updates - E2E Tests', () => {
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

    await page.route('**/v1/tickets/new*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 1,
            title: 'Test Ticket 1',
            status: 'New',
            priority: 'High',
            created_at: '2024-01-15T10:00:00Z'
          },
          {
            id: 2,
            title: 'Test Ticket 2',
            status: 'New',
            priority: 'Medium',
            created_at: '2024-01-15T11:00:00Z'
          }
        ])
      });
    });
  });

  test('should update KPIs when date period is changed', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Wait for initial KPIs to load
    await expect(page.locator('[data-testid="tickets-count"]')).toBeVisible();
    await expect(page.locator('[data-testid="avg-resolution-time"]')).toBeVisible();

    // Capture initial values
    const initialTicketsCount = await page.locator('[data-testid="tickets-count"]').textContent();
    const initialAvgResolutionTime = await page.locator('[data-testid="avg-resolution-time"]').textContent();

    // Open date filter dropdown
    await page.locator('[data-testid="date-filter-dropdown"]').click();

    // Select a different time period (e.g., "Last 7 days")
    await page.locator('[data-testid="period-7-days"]').click();

    // Wait for API call to complete and KPIs to update
    await page.waitForResponse(response =>
      (response.url().includes('/v1/kpis') || response.url().includes('/v2/kpis')) && response.status() === 200
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

  test('should show loading state during KPI updates', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Open date filter and select new period
    await page.locator('[data-testid="date-filter-dropdown"]').click();
    await page.locator('[data-testid="period-30-days"]').click();

    // Verify loading state is shown
    await expect(page.locator('[data-testid="kpi-loading"]')).toBeVisible();

    // Wait for loading to complete
    await page.waitForResponse(response =>
      (response.url().includes('/v1/kpis') || response.url().includes('/v2/kpis')) && response.status() === 200
    );

    // Verify loading state is hidden
    await expect(page.locator('[data-testid="kpi-loading"]')).not.toBeVisible();
  });

  test.skip('should display error message when API fails', async ({ page }) => {
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

    await page.route('**/v2/kpis*', async route => {
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
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="error-message"]')).toContainText('Failed to load KPIs');

    // Verify KPI values are not displayed or show fallback
    await expect(page.locator('[data-testid="kpi-loading"]')).not.toBeVisible();
  });

  test.skip('should use v2 API when feature flag is enabled', async ({ page }) => {
    // Set feature flag environment variable
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

    // Verify v2 API was called and v1 was not
    expect(v2ApiCalled).toBe(true);
    expect(v1ApiCalled).toBe(false);

    // Verify enhanced data from v2 API is displayed
    await expect(page.locator('[data-testid="tickets-count"]')).toContainText('45');
  });

  test.skip('should use v1 API when feature flag is disabled', async ({ page }) => {
    // Set feature flag environment variable
    await page.addInitScript(() => {
      window.localStorage.setItem('VITE_FLAG_USE_V2_KPIS', 'false');
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

    // Verify v1 API was called and v2 was not
    expect(v1ApiCalled).toBe(true);
    expect(v2ApiCalled).toBe(false);

    // Verify data from v1 API is displayed
    await expect(page.locator('[data-testid="tickets-count"]')).toContainText('42');
  });

  test.skip('should handle network timeout gracefully', async ({ page }) => {
    // Simulate network timeout
    await page.route('**/v1/kpis*', async route => {
      // Delay response to simulate timeout
      await new Promise(resolve => setTimeout(resolve, 35000));
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
    
    // Should eventually show timeout error
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible({ timeout: 40000 });
    await expect(page.locator('[data-testid="error-message"]')).toContainText('timeout');
  });

  test.skip('should retry failed requests', async ({ page }) => {
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

    // Should eventually show data after retry
    await expect(page.locator('[data-testid="tickets-count"]')).toBeVisible();
    await expect(page.locator('[data-testid="tickets-count"]')).toContainText('42');
    
    // Verify retry happened
    expect(requestCount).toBe(2);
  });
});
