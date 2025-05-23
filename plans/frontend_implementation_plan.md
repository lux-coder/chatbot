# Frontend Implementation Plan

## Overview
This plan outlines the complete implementation of the Next.js frontend to integrate with the existing backend and AI service, providing a secure, multi-tenant chatbot interface.

## Current State Analysis
- ✅ Backend API with authentication, chat, bot management, and tenant support
- ✅ AI Service with OpenAI and Llama.cpp integration
- ✅ Infrastructure (Docker, Nginx, PostgreSQL, Redis, Keycloak)
- ❌ Frontend (placeholder only)

## Phase 1: Project Foundation (1-2 days) ✅ COMPLETE

### 1.1 Project Structure Setup ✅
- **Status**: Complete
- All required directories and structure are in place
- Package.json with comprehensive dependencies
- Build configurations (Next.js, TypeScript, Tailwind)

### 1.2 Environment Configuration ✅
- **Status**: Complete
- Environment configuration constants implemented
- Keycloak and API configurations ready
- Example environment file documented

### 1.3 Dependencies Installation ✅
- **Status**: Complete
- All required dependencies installed
- UI Framework: Tailwind CSS + Headless UI
- State Management: React Query + Zustand
- Authentication: Keycloak-js
- HTTP Client: Axios
- Forms: React Hook Form + Zod validation
- Real-time: Socket.io (ready for Phase 6)

## Phase 2: Authentication Integration (2-3 days) ✅ COMPLETE

### 2.1 Keycloak Configuration ✅
- **Status**: Complete
- **File**: `lib/auth/keycloak.ts`
- Keycloak client initialization and configuration
- Token management with automatic refresh
- Authentication state management
- Role-based authorization utilities
- Silent SSO check support
- Event handling for auth lifecycle events

### 2.2 Authentication Context ✅
- **Status**: Complete
- **File**: `lib/auth/authContext.tsx`
- React Context provider for authentication state
- Automatic Keycloak initialization on app start
- Token refresh management and error handling
- Tenant information fetching and management
- Centralized authentication event handling

### 2.3 Authentication Guards ✅
- **Status**: Complete
- **Files**: 
  - `components/auth/AuthGuard.tsx`: Route protection with role-based access
  - `components/auth/LoginButton.tsx`: Smart login/logout component
  - `components/auth/UserProfile.tsx`: Complete user profile display
- Higher-order component wrapper support
- Custom fallback components
- Loading and error states
- **Supporting File**: `public/silent-check-sso.html` for Keycloak SSO

### 2.4 Authentication Hook ✅
- **Status**: Complete
- **File**: `lib/hooks/useAuth.ts`
- Clean interface for components to access auth functionality
- User information utilities (display name, initials, roles)
- Permission checking system
- Tenant management utilities
- Authentication action handlers

## Phase 3: API Integration Layer (2-3 days) → NEXT

### 3.1 HTTP Client Setup
- **Status**: Pending
- **File**: `lib/api/client.ts`

### 3.2 API Service Modules
- **Status**: Pending
- **Files**: 
  - `lib/api/tenant.ts`: Tenant discovery and management
  - `lib/api/bot.ts`: Bot CRUD operations
  - `lib/api/chat.ts`: Chat messaging and history

### 3.3 React Query Integration
- **Status**: Pending
- **Files**:
  - `lib/hooks/useChat.ts`: Chat messaging hooks
  - `lib/hooks/useTenant.ts`: Tenant management hooks
  - `lib/hooks/useBots.ts`: Bot management hooks

## Phase 4: Core UI Components (3-4 days)

### 4.1 Layout Components
```typescript
// components/layout/Layout.tsx
export const Layout = ({ children }) => {
  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
};
```

### 4.2 Chat Interface Components
```typescript
// components/chat/ChatInterface.tsx
export const ChatInterface = ({ botId }: { botId: string }) => {
  const [currentConversation, setCurrentConversation] = useState(null);
  const { sendMessage, chatHistory } = useChat(currentConversation?.id);
  
  return (
    <div className="flex h-full">
      <ConversationList 
        botId={botId}
        onSelectConversation={setCurrentConversation}
      />
      <div className="flex-1 flex flex-col">
        <MessageList messages={chatHistory.data?.messages || []} />
        <MessageInput onSendMessage={sendMessage.mutate} />
      </div>
    </div>
  );
};

// components/chat/MessageList.tsx
export const MessageList = ({ messages }) => {
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
    </div>
  );
};

// components/chat/MessageInput.tsx
export const MessageInput = ({ onSendMessage, disabled }) => {
  const [message, setMessage] = useState('');
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim()) {
      onSendMessage({ message: message.trim() });
      setMessage('');
    }
  };
  
  return (
    <form onSubmit={handleSubmit} className="p-4 border-t">
      <div className="flex space-x-2">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your message..."
          disabled={disabled}
          className="flex-1 p-2 border rounded-lg"
        />
        <button
          type="submit"
          disabled={disabled || !message.trim()}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg"
        >
          Send
        </button>
      </div>
    </form>
  );
};
```

### 4.3 Bot Management Components
```typescript
// components/bot/BotManager.tsx
export const BotManager = () => {
  const { data: bots, isLoading } = useBots();
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">My Chatbots</h1>
        <Link href="/bots/create">
          <button className="px-4 py-2 bg-blue-500 text-white rounded-lg">
            Create New Bot
          </button>
        </Link>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {bots?.map((bot) => (
          <BotCard key={bot.id} bot={bot} />
        ))}
      </div>
    </div>
  );
};

// components/bot/BotForm.tsx
export const BotForm = ({ bot, onSubmit }) => {
  const { register, handleSubmit, formState: { errors } } = useForm({
    defaultValues: bot || {
      name: '',
      style: 'professional',
      language: 'english',
      icon: 'default'
    }
  });
  
  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-1">Bot Name</label>
        <input
          {...register('name', { required: 'Name is required' })}
          className="w-full p-2 border rounded-lg"
        />
        {errors.name && (
          <p className="text-red-500 text-sm">{errors.name.message}</p>
        )}
      </div>
      
      <div>
        <label className="block text-sm font-medium mb-1">Style</label>
        <select
          {...register('style')}
          className="w-full p-2 border rounded-lg"
        >
          <option value="professional">Professional</option>
          <option value="casual">Casual</option>
          <option value="technical">Technical</option>
        </select>
      </div>
      
      <button
        type="submit"
        className="w-full py-2 bg-blue-500 text-white rounded-lg"
      >
        {bot ? 'Update Bot' : 'Create Bot'}
      </button>
    </form>
  );
};
```

## Phase 5: Pages and Routing (2-3 days)

### 5.1 Main Application Pages
```typescript
// pages/_app.tsx
export default function MyApp({ Component, pageProps }) {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Layout>
          <Component {...pageProps} />
        </Layout>
      </AuthProvider>
    </QueryClientProvider>
  );
}

// pages/index.tsx
export default function HomePage() {
  const { authenticated } = useAuth();
  
  if (!authenticated) {
    return <LandingPage />;
  }
  
  return <Dashboard />;
}

// pages/chat/[botId].tsx
export default function ChatPage() {
  const router = useRouter();
  const { botId } = router.query;
  
  return (
    <AuthGuard>
      <ChatInterface botId={botId as string} />
    </AuthGuard>
  );
}

// pages/bots/index.tsx
export default function BotsPage() {
  return (
    <AuthGuard>
      <BotManager />
    </AuthGuard>
  );
}

// pages/bots/create.tsx
export default function CreateBotPage() {
  const router = useRouter();
  const createBot = useCreateBot();
  
  const handleSubmit = async (data) => {
    try {
      await createBot.mutateAsync(data);
      router.push('/bots');
    } catch (error) {
      // Handle error
    }
  };
  
  return (
    <AuthGuard>
      <div className="max-w-md mx-auto">
        <h1 className="text-2xl font-bold mb-6">Create New Chatbot</h1>
        <BotForm onSubmit={handleSubmit} />
      </div>
    </AuthGuard>
  );
}
```

### 5.2 Tenant Management Integration
```typescript
// lib/hooks/useTenant.ts
export const useTenant = () => {
  const { data: tenantInfo, isLoading } = useQuery(
    'tenant-info',
    tenantApi.getTenantInfo,
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1
    }
  );
  
  const tenantId = tenantInfo?.tenant_id;
  
  return { tenantId, tenantInfo, isLoading };
};
```

## Phase 6: Advanced Features (3-4 days)

### 6.1 Real-time Chat Updates
```typescript
// lib/hooks/useRealtimeChat.ts
export const useRealtimeChat = (conversationId: string) => {
  const queryClient = useQueryClient();
  
  useEffect(() => {
    if (!conversationId) return;
    
    const eventSource = new EventSource(
      `/api/chat/${conversationId}/stream`
    );
    
    eventSource.onmessage = (event) => {
      const message = JSON.parse(event.data);
      queryClient.setQueryData(
        ['chat-history', conversationId],
        (old) => ({
          ...old,
          messages: [...old.messages, message]
        })
      );
    };
    
    return () => eventSource.close();
  }, [conversationId]);
};
```

### 6.2 Error Handling and Notifications
```typescript
// components/common/ErrorBoundary.tsx
export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }
  
  static getDerivedStateFromError(error) {
    return { hasError: true };
  }
  
  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }
  
  render() {
    if (this.state.hasError) {
      return (
        <div className="text-center p-8">
          <h2 className="text-xl font-bold text-red-600">
            Something went wrong
          </h2>
          <button
            onClick={() => this.setState({ hasError: false })}
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded"
          >
            Try again
          </button>
        </div>
      );
    }
    
    return this.props.children;
  }
}

// lib/hooks/useNotifications.ts
export const useNotifications = () => {
  const [notifications, setNotifications] = useState([]);
  
  const addNotification = (notification) => {
    const id = Date.now();
    setNotifications(prev => [...prev, { ...notification, id }]);
    
    if (notification.type !== 'error') {
      setTimeout(() => {
        removeNotification(id);
      }, 5000);
    }
  };
  
  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };
  
  return { notifications, addNotification, removeNotification };
};
```

### 6.3 Responsive Design and Accessibility
```typescript
// Implement responsive design with Tailwind CSS
// Add proper ARIA labels and keyboard navigation
// Ensure color contrast and screen reader compatibility
```

## Phase 7: Security Implementation (2-3 days)

### 7.1 Content Security Policy
```typescript
// pages/_document.tsx
export default class MyDocument extends Document {
  render() {
    return (
      <Html>
        <Head>
          <meta
            httpEquiv="Content-Security-Policy"
            content="default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;"
          />
        </Head>
        <body>
          <Main />
          <NextScript />
        </body>
      </Html>
    );
  }
}
```

### 7.2 Input Validation and Sanitization
```typescript
// lib/utils/validation.ts
import { z } from 'zod';

export const chatMessageSchema = z.object({
  message: z.string()
    .min(1, 'Message cannot be empty')
    .max(4096, 'Message too long')
    .refine(
      (val) => !containsXSS(val),
      'Invalid characters detected'
    )
});

export const botCreationSchema = z.object({
  name: z.string().min(1).max(255),
  style: z.enum(['professional', 'casual', 'technical']),
  language: z.enum(['english', 'spanish', 'french']),
  icon: z.string().optional()
});
```

### 7.3 Token Management and Security
```typescript
// lib/auth/tokenManager.ts
export class TokenManager {
  private static instance: TokenManager;
  
  static getInstance() {
    if (!TokenManager.instance) {
      TokenManager.instance = new TokenManager();
    }
    return TokenManager.instance;
  }
  
  storeToken(token: string) {
    // Store in secure httpOnly cookie or secure storage
    // Implement token rotation
  }
  
  getToken(): string | null {
    // Retrieve token securely
    // Check expiration
    // Refresh if needed
  }
  
  clearToken() {
    // Secure token cleanup
  }
}
```

## Phase 8: Testing and Quality Assurance (3-4 days)

### 8.1 Unit Tests
```typescript
// components/__tests__/MessageInput.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { MessageInput } from '../chat/MessageInput';

describe('MessageInput', () => {
  test('sends message on form submission', () => {
    const mockSend = jest.fn();
    render(<MessageInput onSendMessage={mockSend} />);
    
    const input = screen.getByPlaceholderText('Type your message...');
    const button = screen.getByText('Send');
    
    fireEvent.change(input, { target: { value: 'Hello world' } });
    fireEvent.click(button);
    
    expect(mockSend).toHaveBeenCalledWith({ message: 'Hello world' });
  });
});
```

### 8.2 Integration Tests
```typescript
// __tests__/auth.integration.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { AuthProvider } from '../lib/auth/authContext';

describe('Authentication Integration', () => {
  test('redirects to login when not authenticated', async () => {
    render(
      <AuthProvider>
        <AuthGuard>
          <div>Protected Content</div>
        </AuthGuard>
      </AuthProvider>
    );
    
    await waitFor(() => {
      expect(screen.getByText('Login')).toBeInTheDocument();
    });
  });
});
```

### 8.3 E2E Tests
```typescript
// e2e/chat.spec.ts
import { test, expect } from '@playwright/test';

test('complete chat flow', async ({ page }) => {
  await page.goto('/');
  
  // Login
  await page.click('[data-testid="login-button"]');
  
  // Wait for authentication
  await page.waitForSelector('[data-testid="chat-interface"]');
  
  // Send a message
  await page.fill('[data-testid="message-input"]', 'Hello bot');
  await page.click('[data-testid="send-button"]');
  
  // Verify response
  await page.waitForSelector('[data-testid="bot-message"]');
  expect(await page.textContent('[data-testid="bot-message"]')).toBeTruthy();
});
```

## Phase 9: Performance Optimization (2-3 days)

### 9.1 Code Splitting and Lazy Loading
```typescript
// Implement dynamic imports for route-based code splitting
const ChatInterface = dynamic(() => import('../components/chat/ChatInterface'), {
  loading: () => <Loading />,
  ssr: false
});

// Lazy load heavy components
const BotAnalytics = lazy(() => import('../components/bot/BotAnalytics'));
```

### 9.2 Caching Strategies
```typescript
// Implement proper cache policies for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      refetchOnWindowFocus: false,
    },
  },
});
```

### 9.3 Bundle Optimization
```typescript
// next.config.js
module.exports = {
  experimental: {
    optimizeCss: true,
  },
  webpack: (config) => {
    config.optimization.splitChunks = {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          priority: 10,
          enforce: true,
        },
      },
    };
    return config;
  },
};
```

## Phase 10: Deployment and Documentation (1-2 days)

### 10.1 Docker Configuration
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine AS builder
WORKDIR /app
COPY . .
COPY --from=deps /app/node_modules ./node_modules
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
CMD ["node", "server.js"]
```

### 10.2 Environment Configuration
```typescript
// Update docker-compose.yml to include frontend service
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_KEYCLOAK_URL=http://keycloak:8080
      - NEXT_PUBLIC_API_URL=https://nginx/api/v1
    depends_on:
      - backend
      - keycloak
```

### 10.3 Documentation
```markdown
# Frontend Documentation
- Component documentation with Storybook
- API integration guide
- Deployment instructions
- Security best practices
- Troubleshooting guide
```

## Success Criteria

1. **Authentication**: Users can log in via Keycloak and access tenant-specific data
2. **Bot Management**: Users can create, edit, and manage chatbot instances
3. **Chat Interface**: Users can have conversations with bots and view history
4. **Responsive Design**: Application works on desktop, tablet, and mobile
5. **Security**: All security measures implemented (CSP, input validation, token management)
6. **Performance**: Application loads quickly and provides smooth user experience
7. **Testing**: Comprehensive test coverage (unit, integration, e2e)
8. **Deployment**: Application can be deployed via Docker Compose

## Estimated Timeline: 20-25 days

This plan provides a complete frontend implementation that integrates seamlessly with the existing backend and AI service, delivering a production-ready secure chatbot application. 