import { http, HttpResponse } from 'msw';
export const handlers = [
  http.get('http://localhost:8000/v1/kpis', () => HttpResponse.json([
    { level: 'N1', total: 20, open: 5, in_progress: 10, closed: 5 },
    { level: 'N2', total: 12, open: 2, in_progress: 7, closed: 3 },
    { level: 'N3', total: 7, open: 1, in_progress: 3, closed: 3 },
    { level: 'N4', total: 3, open: 0, in_progress: 1, closed: 2 },
  ])),
];