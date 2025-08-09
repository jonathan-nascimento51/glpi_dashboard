import { rest } from 'msw';
import { mockData } from './mockData';

const API_BASE_URL = 'http://localhost:8000';

export const handlers = [
  // Dashboard metrics
  rest.get(`${API_BASE_URL}/api/dashboard/metrics`, (req, res, ctx) => {
    const startDate = req.url.searchParams.get('start_date');
    const endDate = req.url.searchParams.get('end_date');
    
    // Simula filtro por data
    let metrics = mockData.dashboardMetrics;
    if (startDate && endDate) {
      // Simula filtro de data (aqui apenas retorna os mesmos dados)
      metrics = {
        ...metrics,
        filtered: true,
        start_date: startDate,
        end_date: endDate
      };
    }
    
    return res(
      ctx.delay(100), // Simula latência da rede
      ctx.status(200),
      ctx.json({
        success: true,
        data: metrics,
        timestamp: new Date().toISOString()
      })
    );
  }),

  // Tickets list
  rest.get(`${API_BASE_URL}/api/tickets`, (req, res, ctx) => {
    const page = parseInt(req.url.searchParams.get('page') || '1');
    const limit = parseInt(req.url.searchParams.get('limit') || '10');
    const status = req.url.searchParams.get('status');
    const priority = req.url.searchParams.get('priority');
    const search = req.url.searchParams.get('search');
    
    let tickets = [...mockData.tickets];
    
    // Filtros
    if (status) {
      tickets = tickets.filter(ticket => ticket.status === status);
    }
    if (priority) {
      tickets = tickets.filter(ticket => ticket.priority === priority);
    }
    if (search) {
      tickets = tickets.filter(ticket => 
        ticket.title.toLowerCase().includes(search.toLowerCase()) ||
        ticket.description.toLowerCase().includes(search.toLowerCase())
      );
    }
    
    // Paginação
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;
    const paginatedTickets = tickets.slice(startIndex, endIndex);
    
    return res(
      ctx.delay(150),
      ctx.status(200),
      ctx.json({
        success: true,
        data: paginatedTickets,
        pagination: {
          page,
          limit,
          total: tickets.length,
          pages: Math.ceil(tickets.length / limit)
        }
      })
    );
  }),

  // Single ticket
  rest.get(`${API_BASE_URL}/api/tickets/:id`, (req, res, ctx) => {
    const { id } = req.params;
    const ticket = mockData.tickets.find(t => t.id === parseInt(id as string));
    
    if (!ticket) {
      return res(
        ctx.status(404),
        ctx.json({
          success: false,
          error: 'Ticket not found'
        })
      );
    }
    
    return res(
      ctx.delay(100),
      ctx.status(200),
      ctx.json({
        success: true,
        data: ticket
      })
    );
  }),

  // Create ticket
  rest.post(`${API_BASE_URL}/api/tickets`, (req, res, ctx) => {
    return res(
      ctx.delay(200),
      ctx.status(201),
      ctx.json({
        success: true,
        data: {
          id: Date.now(),
          ...req.body,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
      })
    );
  }),

  // Update ticket
  rest.put(`${API_BASE_URL}/api/tickets/:id`, (req, res, ctx) => {
    const { id } = req.params;
    const ticket = mockData.tickets.find(t => t.id === parseInt(id as string));
    
    if (!ticket) {
      return res(
        ctx.status(404),
        ctx.json({
          success: false,
          error: 'Ticket not found'
        })
      );
    }
    
    return res(
      ctx.delay(150),
      ctx.status(200),
      ctx.json({
        success: true,
        data: {
          ...ticket,
          ...req.body,
          updated_at: new Date().toISOString()
        }
      })
    );
  }),

  // Delete ticket
  rest.delete(`${API_BASE_URL}/api/tickets/:id`, (req, res, ctx) => {
    const { id } = req.params;
    const ticket = mockData.tickets.find(t => t.id === parseInt(id as string));
    
    if (!ticket) {
      return res(
        ctx.status(404),
        ctx.json({
          success: false,
          error: 'Ticket not found'
        })
      );
    }
    
    return res(
      ctx.delay(100),
      ctx.status(204)
    );
  }),

  // Users list
  rest.get(`${API_BASE_URL}/api/users`, (req, res, ctx) => {
    return res(
      ctx.delay(100),
      ctx.status(200),
      ctx.json({
        success: true,
        data: mockData.users
      })
    );
  }),

  // Performance metrics
  rest.get(`${API_BASE_URL}/api/performance`, (req, res, ctx) => {
    const period = req.url.searchParams.get('period') || '7d';
    
    return res(
      ctx.delay(200),
      ctx.status(200),
      ctx.json({
        success: true,
        data: mockData.performanceMetrics[period] || mockData.performanceMetrics['7d']
      })
    );
  }),

  // Trends data
  rest.get(`${API_BASE_URL}/api/trends`, (req, res, ctx) => {
    const metric = req.url.searchParams.get('metric') || 'tickets';
    const period = req.url.searchParams.get('period') || '30d';
    
    return res(
      ctx.delay(150),
      ctx.status(200),
      ctx.json({
        success: true,
        data: mockData.trendsData[metric] || mockData.trendsData.tickets
      })
    );
  }),

  // Health check
  rest.get(`${API_BASE_URL}/api/health`, (req, res, ctx) => {
    return res(
      ctx.delay(50),
      ctx.status(200),
      ctx.json({
        success: true,
        data: {
          status: 'healthy',
          timestamp: new Date().toISOString(),
          version: '1.0.0',
          uptime: '5d 12h 30m'
        }
      })
    );
  }),

  // GLPI health check
  rest.get(`${API_BASE_URL}/api/health/glpi`, (req, res, ctx) => {
    return res(
      ctx.delay(100),
      ctx.status(200),
      ctx.json({
        success: true,
        data: {
          status: 'connected',
          response_time: '120ms',
          last_check: new Date().toISOString()
        }
      })
    );
  }),

  // Export data
  rest.get(`${API_BASE_URL}/api/export`, (req, res, ctx) => {
    const format = req.url.searchParams.get('format') || 'json';
    const type = req.url.searchParams.get('type') || 'tickets';
    
    if (format === 'csv') {
      return res(
        ctx.delay(300),
        ctx.status(200),
        ctx.set('Content-Type', 'text/csv'),
        ctx.set('Content-Disposition', `attachment; filename="${type}.csv"`),
        ctx.text('id,title,status,priority\n1,"Test Ticket",open,high')
      );
    }
    
    return res(
      ctx.delay(200),
      ctx.status(200),
      ctx.json({
        success: true,
        data: mockData.tickets,
        format,
        type
      })
    );
  }),

  // Upload file
  rest.post(`${API_BASE_URL}/api/upload`, (req, res, ctx) => {
    return res(
      ctx.delay(500),
      ctx.status(200),
      ctx.json({
        success: true,
        data: {
          file_id: 'file_' + Date.now(),
          filename: 'uploaded_file.txt',
          size: 1024,
          url: '/uploads/file_' + Date.now() + '.txt'
        }
      })
    );
  }),

  // Search
  rest.get(`${API_BASE_URL}/api/search`, (req, res, ctx) => {
    const query = req.url.searchParams.get('q') || '';
    const type = req.url.searchParams.get('type') || 'all';
    
    let results: any[] = [];
    
    if (type === 'all' || type === 'tickets') {
      const ticketResults = mockData.tickets
        .filter(ticket => 
          ticket.title.toLowerCase().includes(query.toLowerCase()) ||
          ticket.description.toLowerCase().includes(query.toLowerCase())
        )
        .map(ticket => ({ ...ticket, type: 'ticket' }));
      results = [...results, ...ticketResults];
    }
    
    if (type === 'all' || type === 'users') {
      const userResults = mockData.users
        .filter(user => 
          user.name.toLowerCase().includes(query.toLowerCase()) ||
          user.email.toLowerCase().includes(query.toLowerCase())
        )
        .map(user => ({ ...user, type: 'user' }));
      results = [...results, ...userResults];
    }
    
    return res(
      ctx.delay(200),
      ctx.status(200),
      ctx.json({
        success: true,
        data: results,
        query,
        total: results.length
      })
    );
  }),

  // Notifications
  rest.get(`${API_BASE_URL}/api/notifications`, (req, res, ctx) => {
    return res(
      ctx.delay(100),
      ctx.status(200),
      ctx.json({
        success: true,
        data: mockData.notifications
      })
    );
  }),

  // Mark notification as read
  rest.put(`${API_BASE_URL}/api/notifications/:id/read`, (req, res, ctx) => {
    return res(
      ctx.delay(100),
      ctx.status(200),
      ctx.json({
        success: true,
        data: { read: true }
      })
    );
  }),

  // Settings
  rest.get(`${API_BASE_URL}/api/settings`, (req, res, ctx) => {
    return res(
      ctx.delay(100),
      ctx.status(200),
      ctx.json({
        success: true,
        data: mockData.settings
      })
    );
  }),

  // Update settings
  rest.put(`${API_BASE_URL}/api/settings`, (req, res, ctx) => {
    return res(
      ctx.delay(150),
      ctx.status(200),
      ctx.json({
        success: true,
        data: {
          ...mockData.settings,
          ...req.body,
          updated_at: new Date().toISOString()
        }
      })
    );
  }),

  // Fallback handler para requisições não mapeadas
  rest.all('*', (req, res, ctx) => {
    console.warn(`Unhandled ${req.method} request to ${req.url}`);
    return res(
      ctx.status(404),
      ctx.json({
        success: false,
        error: 'Endpoint not found',
        path: req.url.pathname
      })
    );
  }),
];