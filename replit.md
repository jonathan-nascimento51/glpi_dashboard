# Overview

The GLPI Dashboard is a comprehensive web application that provides real-time monitoring and metrics visualization for GLPI (IT Service Management) systems. The application consists of a Python Flask backend that integrates with GLPI APIs and a React TypeScript frontend for data visualization. The dashboard displays technician rankings, ticket metrics by service levels (N1-N4), and provides filtering capabilities by date ranges and entities.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Architecture (Python Flask)

The backend follows a service-oriented architecture with clear separation of concerns:

### Core Components
- **Flask Application (`app.py`)**: Main entry point with observability middleware, CORS configuration, and cache setup
- **API Routes (`api/routes.py`)**: RESTful endpoints for metrics, technician rankings, and status checks
- **GLPI Service (`services/glpi_service.py`)**: Handles all interactions with GLPI REST API, including authentication, data fetching, and field mapping
- **Configuration Management (`config/settings.py`)**: Environment-based configuration with support for development, testing, and production

### Key Design Patterns
- **Service Layer Pattern**: Business logic encapsulated in service classes, particularly the GLPIService
- **Repository Pattern**: Data access abstracted through service methods that interact with GLPI API
- **Middleware Pattern**: Observability and monitoring implemented as Flask middleware
- **Decorator Pattern**: Date validation and logging implemented using Python decorators

### Data Processing
- **Field ID Discovery**: Dynamic field mapping to handle GLPI schema variations
- **Technician Identification**: Multiple strategies for finding active technicians (Profile_User table, ticket assignments)
- **Service Level Mapping**: Configurable mapping of technicians to N1-N4 service levels
- **Caching Strategy**: Flask-Caching with Redis support for performance optimization

### Monitoring and Observability
- **Structured Logging**: Comprehensive logging with timestamps and operation tracking
- **Prometheus Metrics**: Performance metrics collection for monitoring
- **Alert System**: Automated alerting for data consistency issues
- **Health Checks**: API endpoints for system status monitoring

## Frontend Architecture (React TypeScript)

The frontend uses modern React patterns with TypeScript for type safety:

### Core Structure
- **Component-Based Architecture**: Reusable UI components (StatusCard, MetricsGrid, LevelMetricsGrid)
- **Custom Hooks**: Data fetching and state management through custom React hooks
- **API Integration**: HTTP client with proper error handling and loading states
- **Responsive Design**: Mobile-first CSS with Grid and Flexbox layouts

### State Management
- **Local Component State**: React useState for component-specific data
- **API State Management**: Custom hooks for server state synchronization
- **Loading States**: Comprehensive loading and error state handling

### Testing Strategy
- **Unit Testing**: Vitest for component and utility testing
- **Integration Testing**: API integration tests with mock data
- **Accessibility Testing**: WCAG compliance validation
- **Visual Regression Testing**: Snapshot testing for UI consistency

## Data Flow Architecture

### API Communication
- **RESTful Design**: Standard HTTP methods with JSON payloads
- **Error Handling**: Consistent error response format with proper HTTP status codes
- **Request Validation**: Input validation using decorators and middleware
- **Response Normalization**: Standardized API response structure

### Caching Strategy
- **Multi-Level Caching**: Application-level caching with Redis backend
- **Cache Invalidation**: Time-based and event-based cache invalidation
- **Performance Optimization**: Reduced GLPI API calls through intelligent caching

## Security Architecture

### Authentication and Authorization
- **GLPI Session Management**: Secure session handling with GLPI API
- **Request Validation**: Input sanitization and validation
- **CORS Configuration**: Proper cross-origin resource sharing setup

### Data Protection
- **Environment Variables**: Sensitive configuration stored in environment variables
- **Input Sanitization**: Protection against injection attacks
- **Rate Limiting**: API rate limiting to prevent abuse

# External Dependencies

## Backend Dependencies
- **Flask 2.3.3**: Web framework for API development
- **Flask-CORS**: Cross-origin resource sharing support
- **Flask-Caching**: Caching framework with Redis support
- **Requests**: HTTP client for GLPI API integration
- **Python-dotenv**: Environment variable management
- **Gunicorn**: WSGI server for production deployment

## Frontend Dependencies
- **React 18**: Frontend framework with hooks and modern features
- **TypeScript**: Type-safe JavaScript superset
- **Vite**: Build tool and development server
- **Vitest**: Testing framework for unit and integration tests

## External Services and APIs
- **GLPI REST API**: Primary data source for tickets, users, and metrics
- **Redis**: Caching backend for performance optimization
- **Prometheus**: Metrics collection and monitoring (optional)

## Development and Testing Tools
- **pytest**: Python testing framework with async support
- **Bandit**: Security vulnerability scanner
- **Black, flake8, isort**: Python code formatting and linting
- **ESLint, Prettier**: TypeScript/JavaScript code quality tools

## Infrastructure Dependencies
- **Docker**: Containerization support (optional)
- **Node.js 18+**: JavaScript runtime for frontend development
- **Python 3.9+**: Backend runtime environment