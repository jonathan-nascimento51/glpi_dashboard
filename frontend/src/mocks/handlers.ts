import { http, HttpResponse } from 'msw';
import { mockData } from './mockData';

const API_BASE_URL = 'http://localhost:8000';

export const handlers = [
  // KPIs endpoint
  http.get(`${API_BASE_URL}/v1/kpis`, () => {
    return HttpResponse.json([
      { level: 'N1', total: 20, open: 5, in_progress: 10, closed: 5 },
      { level: 'N2', total: 12, open: 2, in_progress: 7, closed: 3 },
      { level: 'N3', total: 7, open: 1, in_progress: 3, closed: 3 },
      { level: 'N4', total: 3, open: 0, in_progress: 1, closed: 2 }
    ], { status: 200 });
  }),

  // Search endpoint
  http.get(`${API_BASE_URL}/api/search`, ({ request }) => {
    const url = new URL(request.url);
    const query = url.searchParams.get('q');
    
    if (!query) {
      return HttpResponse.json({ error: 'Query parameter required' }, { status: 400 });
    }

    const results = mockData.searchResults.filter(item => 
      item.title.toLowerCase().includes(query.toLowerCase()) ||
      item.description.toLowerCase().includes(query.toLowerCase())
    );

    return HttpResponse.json({
      query,
      results,
      total: results.length
    });
  }),

  // Notifications endpoint
  http.get(`${API_BASE_URL}/api/notifications`, () => {
    return HttpResponse.json(mockData.notifications);
  }),

  // Settings endpoint
  http.get(`${API_BASE_URL}/api/settings`, () => {
    return HttpResponse.json(mockData.settings);
  }),

  http.put(`${API_BASE_URL}/api/settings`, async ({ request }) => {
    const updatedSettings = await request.json();
    return HttpResponse.json({ ...mockData.settings, ...updatedSettings });
  }),

  // Fallback handler for unmatched requests
  http.all('*', ({ request }) => {
    console.warn(`Unhandled ${request.method} request to ${request.url}`);
    return HttpResponse.json(
      { error: 'Not found' },
      { status: 404 }
    );
  })
];
