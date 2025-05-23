# Secure Chatbot Frontend

A modern, secure Next.js frontend for the multi-tenant chatbot application with Keycloak authentication and AI integration.

## 🚀 Project Status

### ✅ Foundation Complete (Current State)
- Modern Next.js 14 setup with TypeScript
- Tailwind CSS with custom theming
- Production-ready Docker configuration
- Comprehensive type definitions
- Security headers and optimizations
- Development tools (ESLint, Prettier, Storybook, Jest)

### 🔄 In Progress
- Authentication integration (Keycloak)
- API client implementation
- Core UI components

### 📋 Planned
- Chat interface
- Bot management
- Real-time features
- Testing suite
- Performance optimizations

## 🛠 Tech Stack

### Core Framework
- **Next.js 14** - React framework with SSR and optimization
- **TypeScript** - Type safety and developer experience
- **React 18** - Latest React features including concurrent rendering

### UI & Styling
- **Tailwind CSS** - Utility-first CSS framework
- **Headless UI** - Unstyled, accessible UI components
- **Heroicons** - Beautiful hand-crafted SVG icons
- **Custom CSS** - Theme variables and component styles

### State Management
- **React Query** - Server state management and caching
- **Zustand** - Client state management
- **React Hook Form** - Form state and validation

### Authentication & Security
- **Keycloak-js** - Authentication and authorization
- **Zod** - Runtime type validation
- **Security Headers** - CSP, HSTS, and more

### Development Tools
- **ESLint & Prettier** - Code quality and formatting
- **Jest & Testing Library** - Unit testing
- **Playwright** - End-to-end testing
- **Storybook** - Component development and documentation

## 📁 Project Structure

```
frontend/
├── components/           # React components
│   ├── auth/            # Authentication components
│   ├── chat/            # Chat interface components
│   ├── bot/             # Bot management components
│   ├── layout/          # Layout components
│   └── common/          # Reusable components
├── lib/                 # Utility libraries
│   ├── api/             # API client and services
│   ├── auth/            # Authentication utilities
│   ├── hooks/           # Custom React hooks
│   └── utils/           # Helper functions and constants
├── pages/               # Next.js pages
│   ├── api/             # API routes
│   ├── chat/            # Chat pages
│   └── bots/            # Bot management pages
├── styles/              # Global styles and CSS
├── public/              # Static assets
└── plans/               # Implementation documentation
```

## 🔧 Development Setup

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Docker (for containerized development)

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Set up environment variables:**
   ```bash
   # Copy the example file
   cp .env.local.example .env.local
   
   # Edit with your configuration
   nano .env.local
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Open in browser:**
   ```
   http://localhost:3000
   ```

### Environment Variables

Create a `.env.local` file with these required variables:

```bash
# Application
NEXT_PUBLIC_APP_NAME=Secure Chatbot
NEXT_PUBLIC_API_URL=https://localhost/api/v1

# Keycloak
NEXT_PUBLIC_KEYCLOAK_URL=http://localhost:8080
NEXT_PUBLIC_KEYCLOAK_REALM=chatbot
NEXT_PUBLIC_KEYCLOAK_CLIENT_ID=chatbot-frontend

# Feature Flags
NEXT_PUBLIC_ENABLE_REAL_TIME=true
NEXT_PUBLIC_ENABLE_FEEDBACK=true
```

## 📝 Available Scripts

```bash
# Development
npm run dev              # Start development server
npm run build           # Build for production
npm run start           # Start production server

# Code Quality
npm run lint            # Run ESLint
npm run lint:fix        # Fix ESLint issues
npm run type-check      # Run TypeScript checks

# Testing
npm test                # Run unit tests
npm run test:watch      # Run tests in watch mode
npm run test:e2e        # Run E2E tests with Playwright

# Documentation
npm run storybook       # Start Storybook
npm run build-storybook # Build Storybook static files
```

## 🐳 Docker Development

### Build and run with Docker:

```bash
# Build the image
docker build -t chatbot-frontend .

# Run the container
docker run -p 3000:3000 chatbot-frontend
```

### Or use with docker-compose:

```bash
# From project root
docker-compose up frontend
```

## 🎨 Design System

### Color Palette
- **Primary**: Blue shades for main actions and branding
- **Secondary**: Gray shades for text and borders
- **Success**: Green for positive actions
- **Warning**: Orange for caution states
- **Error**: Red for error states

### Typography
- **Font**: Inter (system fallback: system-ui, sans-serif)
- **Weights**: 400 (normal), 500 (medium), 600 (semibold), 700 (bold)
- **Scale**: Responsive typography with proper line heights

### Components
- **Buttons**: Primary, secondary, danger, ghost variants
- **Inputs**: Standard inputs with error states
- **Cards**: Container components with hover effects
- **Message Bubbles**: Chat-specific styling

## 🔐 Security Features

### Headers
- Content Security Policy (CSP)
- HTTP Strict Transport Security (HSTS)
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block

### Authentication
- JWT token management
- Automatic token refresh
- Secure storage practices
- Role-based access control

### Input Validation
- Client-side validation with Zod
- XSS prevention
- CSRF protection
- Input sanitization

## 🎯 Key Features (Planned)

### Authentication
- [x] Keycloak integration setup
- [ ] JWT token management
- [ ] Role-based access control
- [ ] Automatic session refresh

### Chat Interface
- [ ] Real-time messaging
- [ ] Message history
- [ ] Typing indicators
- [ ] File uploads
- [ ] Message reactions

### Bot Management
- [ ] Create and configure bots
- [ ] Bot style customization
- [ ] Multi-language support
- [ ] Bot analytics

### User Experience
- [ ] Responsive design
- [ ] Dark mode support
- [ ] Accessibility compliance
- [ ] Progressive Web App (PWA)

## 🔗 API Integration

The frontend integrates with the backend API through:

### Authentication
- Keycloak JWT tokens
- Tenant context headers (`X-Tenant-ID`)
- Automatic token refresh

### Endpoints
- `/api/v1/tenant/info` - Tenant discovery
- `/api/v1/chat` - Chat messaging
- `/api/v1/bot` - Bot management
- `/api/v1/auth/me` - User profile

### Error Handling
- Automatic retry with exponential backoff
- User-friendly error messages
- Network connectivity detection
- Graceful degradation

## 📊 Performance

### Optimizations
- Next.js automatic code splitting
- Image optimization
- Bundle analyzer integration
- Webpack optimizations

### Monitoring
- Core Web Vitals tracking
- Error boundary implementation
- Performance metrics
- User analytics (optional)

## 🧪 Testing Strategy

### Unit Tests
- Component testing with React Testing Library
- Hook testing with React Hooks Testing Library
- Utility function testing
- 80%+ code coverage target

### Integration Tests
- API integration testing
- Authentication flow testing
- User journey testing

### E2E Tests
- Critical user paths
- Cross-browser testing
- Mobile responsive testing
- Accessibility testing

## 📚 Documentation

### Component Documentation
- Storybook for component library
- Props documentation
- Usage examples
- Design tokens

### API Documentation
- TypeScript interfaces
- Request/response examples
- Error handling guides

## 🚀 Deployment

### Production Build
```bash
npm run build
npm run start
```

### Docker Deployment
```bash
docker build -t chatbot-frontend .
docker run -p 3000:3000 chatbot-frontend
```

### Environment Configuration
- Environment-specific builds
- Feature flag management
- CDN integration
- Performance monitoring

## 🤝 Contributing

### Code Style
- Follow TypeScript strict mode
- Use Prettier for formatting
- Follow ESLint rules
- Write comprehensive tests

### Component Guidelines
- Use TypeScript interfaces for props
- Implement proper error boundaries
- Include accessibility attributes
- Follow responsive design principles

### Git Workflow
- Feature branch development
- Pull request reviews
- Automated testing
- Semantic versioning

## 📖 Next Steps

See the detailed implementation plan in `plans/frontend_implementation_plan.md` for:

1. **Phase 1**: Authentication Integration
2. **Phase 2**: API Integration Layer  
3. **Phase 3**: Core UI Components
4. **Phase 4**: Chat Interface
5. **Phase 5**: Pages and Routing

## 📄 License

This project is part of an academic demonstration for secure web application development.

## 📞 Support

For implementation questions, refer to:
- `plans/frontend_implementation_plan.md` - Detailed implementation guide
- `plans/frontend_foundation_summary.md` - Foundation completion status
- Component documentation in Storybook (when available) 