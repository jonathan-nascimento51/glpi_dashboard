# Centro de Comando - Tech Department Dashboard

## Overview

A real-time monitoring dashboard for the technology department that displays system metrics, performance data, and operational status. The application features a Flask backend serving both a traditional server-rendered HTML interface and REST API endpoints, with plans to migrate to React components. The dashboard provides comprehensive system monitoring including CPU usage, memory consumption, disk usage, network status, and active user tracking through interactive charts and metrics cards.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Flask Web Framework**: Lightweight Python web server handling both API routes and template rendering
- **Service Layer Pattern**: `APIService` class handles external API communications with configurable timeout and error handling
- **Environment-based Configuration**: Uses environment variables for API URLs, keys, and secrets
- **CORS Integration**: Configured for cross-origin requests to support frontend-backend separation

### Frontend Architecture
- **Multi-Pattern Design**: Currently uses traditional server-rendered templates with plans for React migration
- **Component-based JavaScript**: Modular ES6 classes for Dashboard, MetricsGrid, ChartWidget, SearchPanel, and ThemeSwitcher
- **CSS Custom Properties**: Comprehensive theming system with light/dark modes and CSS variables
- **Real-time Updates**: Auto-refresh functionality with configurable intervals

### Data Visualization
- **Chart.js Integration**: Interactive charts for performance metrics, resource usage, and network monitoring
- **Responsive Metrics Cards**: Dynamic status indicators with configurable thresholds for warnings and critical states
- **Live Status Updates**: Real-time system monitoring with visual feedback

### State Management
- **Client-side State**: JavaScript classes manage component state and global application state
- **Local Storage**: Theme preferences and user settings persistence
- **Error Handling**: Global error handlers with user-friendly notifications and auto-recovery

### UI/UX Features
- **Advanced Search**: Debounced search functionality with results filtering
- **Theme System**: Multiple theme options (light, dark, corporate, tech) with instant switching
- **Responsive Design**: Mobile-first approach with Bootstrap integration
- **Progressive Enhancement**: Graceful degradation for offline functionality

## External Dependencies

### Core Technologies
- **Flask**: Python web framework for backend services
- **Bootstrap 5.3.0**: CSS framework for responsive design and components
- **Chart.js**: JavaScript charting library for data visualization
- **Font Awesome 6.5.0**: Icon library for UI elements

### Fonts and Typography
- **Google Fonts**: Inter font family for UI text and JetBrains Mono for code/data display
- **Font loading optimization**: Preconnect directives for improved performance

### Backend APIs
- **External Backend API**: Configurable endpoint (`BACKEND_API_URL`) for metrics and system data
- **Authentication**: Bearer token support for API requests
- **Timeout Configuration**: 30-second timeout with comprehensive error handling

### Browser APIs
- **Service Worker**: Planned offline capability support
- **Performance API**: Page load monitoring and performance metrics
- **Local Storage**: Theme and preference persistence
- **Fetch API**: Modern HTTP client for API communications

### Development Tools
- **Environment Variables**: Secure configuration management for API keys and URLs
- **Logging**: Python logging system for debugging and monitoring
- **Error Tracking**: Global error handlers for client-side and server-side errors