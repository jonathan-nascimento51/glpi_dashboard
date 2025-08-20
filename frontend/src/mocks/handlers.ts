import { http, HttpResponse } from 'msw';
import { mockData } from './mockData';
import type { MockApiResponse, MockRequestParams } from '../types/mock';

const API_BASE_URL = 'http://localhost:8000';

export const handlers = [
  // Dashboard metrics
  http.get(`${API_BASE_URL}/api/dashboard/metrics`, ({ request }) => {
    const url = new URL(request.url);
    const startDate = url.searchParams.get('start_date');
    const endDate = url.searchParams.get('end_date');

    // Simula filtro por data
    let metrics = mockData.dashboardMetrics;
    if (startDate && endDate) {
      // Simula filtro de data (aqui apenas retorna os mesmos dados)
      metrics = {
        ...metrics,
        filtered: true,
        start_date: startDate,
        end_date: endDate,
      };
    }

    const response: MockApiResponse = {
      success: true,
      data: metrics,
      timestamp: new Date().toISOString(),
    };

    return HttpResponse.json(response, {
      headers: { 'Content-Type': 'application/json' },
    });
  }),

  // Tickets list
  http.get(`${API_BASE_URL}/api/tickets`, ({ request }) => {
    const url = new URL(request.url);
    const page = parseInt(url.searchParams.get('page') || '1');
    const limit = parseInt(url.searchParams.get('limit') || '10');
    const status = url.searchParams.get('status');
    const priority = url.searchParams.get('priority');
    const search = url.searchParams.get('search');

    let tickets = [...mockData.tickets];

    // Filtros
    if (status) {
      tickets = tickets.filter(ticket => ticket.status === status);
    }
    if (priority) {
      tickets = tickets.filter(ticket => ticket.priority === priority);
    }
    if (search) {
      tickets = tickets.filter(
        ticket =>
          ticket.title.toLowerCase().includes(search.toLowerCase()) ||
          ticket.description.toLowerCase().includes(search.toLowerCase())
      );
    }

    // Paginação
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;
    const paginatedTickets = tickets.slice(startIndex, endIndex);

    const response: MockApiResponse = {
      success: true,
      data: paginatedTickets,
      pagination: {
        page,
        limit,
        total: tickets.length,
        pages: Math.ceil(tickets.length / limit),
      },
    };

    return HttpResponse.json(response);
  }),

  // Single ticket
  http.get(`${API_BASE_URL}/api/tickets/:id`, ({ params }) => {
    const { id } = params;
    const ticket = mockData.tickets.find(t => t.id === parseInt(id as string));

    if (!ticket) {
      return HttpResponse.json(
        {
          success: false,
          error: 'Ticket not found',
        },
        { status: 404 }
      );
    }

    const response: MockApiResponse = {
      success: true,
      data: ticket,
    };

    return HttpResponse.json(response);
  }),

  // Create ticket
  http.post(`${API_BASE_URL}/api/tickets`, async ({ request }) => {
    const body = await request.json();

    const response: MockApiResponse = {
      success: true,
      data: {
        id: Date.now(),
        ...body,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    };

    return HttpResponse.json(response, { status: 201 });
  }),

  // Update ticket
  http.put(`${API_BASE_URL}/api/tickets/:id`, async ({ params, request }) => {
    const { id } = params;
    const body = await request.json();
    const ticketIndex = mockData.tickets.findIndex(t => t.id === parseInt(id as string));

    if (ticketIndex === -1) {
      return HttpResponse.json(
        {
          success: false,
          error: 'Ticket not found',
        },
        { status: 404 }
      );
    }

    const updatedTicket = {
      ...mockData.tickets[ticketIndex],
      ...body,
      updated_at: new Date().toISOString(),
    };

    mockData.tickets[ticketIndex] = updatedTicket;

    const response: MockApiResponse = {
      success: true,
      data: updatedTicket,
    };

    return HttpResponse.json(response);
  }),

  // Delete ticket
  http.delete(`${API_BASE_URL}/api/tickets/:id`, ({ params }) => {
    const { id } = params;
    const ticketIndex = mockData.tickets.findIndex(t => t.id === parseInt(id as string));

    if (ticketIndex === -1) {
      return HttpResponse.json(
        {
          success: false,
          error: 'Ticket not found',
        },
        { status: 404 }
      );
    }

    mockData.tickets.splice(ticketIndex, 1);

    return new HttpResponse(null, { status: 204 });
  }),

  // Users list
  http.get(`${API_BASE_URL}/api/users`, () => {
    const response: MockApiResponse = {
      success: true,
      data: mockData.users,
    };

    return HttpResponse.json(response);
  }),

  // Performance metrics
  http.get(`${API_BASE_URL}/api/performance`, ({ request }) => {
    const url = new URL(request.url);
    const period = url.searchParams.get('period') || '7d';

    const response: MockApiResponse = {
      success: true,
      data: mockData.performanceMetrics[period] || mockData.performanceMetrics['7d'],
    };

    return HttpResponse.json(response);
  }),

  // Trends data
  http.get(`${API_BASE_URL}/api/trends`, ({ request }) => {
    const url = new URL(request.url);
    const metric = url.searchParams.get('metric') || 'tickets';
    const period = url.searchParams.get('period') || '30d';

    const response: MockApiResponse = {
      success: true,
      data: mockData.trendsData[metric] || mockData.trendsData.tickets,
    };

    return HttpResponse.json(response);
  }),

  // Health check
  http.get(`${API_BASE_URL}/api/health`, () => {
    const response: MockApiResponse = {
      success: true,
      data: {
        status: 'healthy',
        timestamp: new Date().toISOString(),
        services: {
          database: 'connected',
          glpi: 'connected',
          cache: 'active',
        },
        uptime: Math.floor(Math.random() * 86400), // Random uptime in seconds
      },
    };

    return HttpResponse.json(response);
  }),

  // GLPI health check
  http.get(`${API_BASE_URL}/api/health/glpi`, () => {
    const response: MockApiResponse = {
      success: true,
      data: {
        status: 'connected',
        version: '10.0.7',
        response_time: Math.floor(Math.random() * 100) + 50, // 50-150ms
        last_sync: new Date(Date.now() - Math.random() * 300000).toISOString(), // Last 5 minutes
      },
    };

    return HttpResponse.json(response);
  }),

  // Export data
  http.get(`${API_BASE_URL}/api/export`, ({ request }) => {
    const url = new URL(request.url);
    const format = url.searchParams.get('format') || 'json';
    const type = url.searchParams.get('type') || 'tickets';

    let data;
    switch (type) {
      case 'tickets':
        data = mockData.tickets;
        break;
      case 'users':
        data = mockData.users;
        break;
      default:
        data = mockData.dashboardMetrics;
    }

    const response: MockApiResponse = {
      success: true,
      data: {
        format,
        type,
        records: data,
        exported_at: new Date().toISOString(),
      },
    };

    return HttpResponse.json(response);
  }),

  // File upload
  http.post(`${API_BASE_URL}/api/upload`, () => {
    const response: MockApiResponse = {
      success: true,
      data: {
        file_id: `file_${Date.now()}`,
        filename: 'uploaded_file.txt',
        size: Math.floor(Math.random() * 1000000), // Random size
        uploaded_at: new Date().toISOString(),
      },
    };

    return HttpResponse.json(response, { status: 201 });
  }),

  // Search
  http.get(`${API_BASE_URL}/api/search`, ({ request }) => {
    const url = new URL(request.url);
    const query = url.searchParams.get('q') || '';
    const type = url.searchParams.get('type') || 'all';

    let results: any[] = [];

    if (type === 'all' || type === 'tickets') {
      const ticketResults = mockData.tickets
        .filter(
          ticket =>
            ticket.title.toLowerCase().includes(query.toLowerCase()) ||
            ticket.description.toLowerCase().includes(query.toLowerCase())
        )
        .map(ticket => ({ ...ticket, type: 'ticket' }));
      results = [...results, ...ticketResults];
    }

    if (type === 'all' || type === 'users') {
      const userResults = mockData.users
        .filter(
          user =>
            user.name.toLowerCase().includes(query.toLowerCase()) ||
            user.email.toLowerCase().includes(query.toLowerCase())
        )
        .map(user => ({ ...user, type: 'user' }));
      results = [...results, ...userResults];
    }

    const response: MockApiResponse = {
      success: true,
      data: results,
      query,
      total: results.length,
    };

    return HttpResponse.json(response);
  }),

  // Notifications
  http.get(`${API_BASE_URL}/api/notifications`, () => {
    const response: MockApiResponse = {
      success: true,
      data: mockData.notifications,
    };

    return HttpResponse.json(response);
  }),

  // Mark notification as read
  http.put(`${API_BASE_URL}/api/notifications/:id/read`, () => {
    const response: MockApiResponse = {
      success: true,
      data: { read: true },
    };

    return HttpResponse.json(response);
  }),

  // Settings
  http.get(`${API_BASE_URL}/api/settings`, () => {
    const response: MockApiResponse = {
      success: true,
      data: mockData.settings,
    };

    return HttpResponse.json(response);
  }),

  // Update settings
  http.put(`${API_BASE_URL}/api/settings`, async ({ request }) => {
    const body = await request.json();
    const response: MockApiResponse = {
      success: true,
      data: {
        ...mockData.settings,
        ...body,
        updated_at: new Date().toISOString(),
      },
    };

    return HttpResponse.json(response);
  }),

  // Catch-all handler for unmatched requests
  http.all('*', ({ request }) => {
    console.warn(`Unhandled ${request.method} request to ${request.url}`);
    return HttpResponse.json(
      {
        success: false,
        error: 'Endpoint not found',
        message: `No handler found for ${request.method} ${request.url}`,
      },
      { status: 404 }
    );
  }),
];
