---
name: tanstack-query-ts
description: "TanStack Query v5 patterns for server state, caching, mutations, and API integration. Use when fetching data from APIs, managing server state, implementing optimistic updates, cache invalidation, or integrating with Zustand for client state. Also covers openapi-typescript for type-safe API clients."
---

# TanStack Query + API Integration (TypeScript)

Server state management with TanStack Query v5, type-safe API clients, and Zustand for client-only state.

## When to Use This Skill

- Fetching data from REST APIs in React components
- Implementing mutations (create/update/delete) with optimistic updates
- Cache invalidation and stale time configuration
- Generating type-safe API clients from OpenAPI specs
- Coordinating server state (TanStack Query) with client state (Zustand)
- Infinite scroll, pagination, or polling patterns

## Prerequisites

```bash
pnpm add @tanstack/react-query zustand
pnpm add -D openapi-typescript    # Type generation from OpenAPI
```

## State Management Decision Matrix

| State type | Tool | Why |
|-----------|------|-----|
| Server/async data | TanStack Query | Caching, dedup, background refresh, error retry |
| Client-only UI | Zustand | Modal open, sidebar collapsed, theme |
| Form state | React Hook Form | See react-hook-form-ts skill |
| URL-shareable | URL search params | Filters, pagination, sort |
| Ephemeral | `useState` | Hover, focus, local toggle |

**Rule:** Never store server data in Zustand. TanStack Query is the cache.

## Query Patterns

### Query Key Convention

Use hierarchical keys for granular invalidation:

```typescript
// Pattern: [entity, scope, id, filters]
['users', 'list']                              // All users
['users', 'list', { role: 'admin' }]           // Filtered
['users', 'detail', userId]                    // Single user
['users', userId, 'posts']                     // User's posts
['users', userId, 'posts', { status: 'draft' }] // Filtered nested
```

Keys must be serializable (no functions, no class instances).

### Basic Query

```typescript
import { useQuery, useSuspenseQuery } from '@tanstack/react-query';

// Standard query with loading/error states
function UserList() {
  const { data: users, isLoading, error } = useQuery({
    queryKey: ['users', 'list'],
    queryFn: () => api.users.list(),
    staleTime: 5 * 60 * 1000, // 5 min fresh
  });

  if (isLoading) return <Spinner />;
  if (error) return <ErrorMessage error={error} />;
  return <ul>{users.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
}

// Suspense query — cleaner, use with <Suspense> + <ErrorBoundary>
function UserList() {
  const { data: users } = useSuspenseQuery({
    queryKey: ['users', 'list'],
    queryFn: () => api.users.list(),
  });
  return <ul>{users.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
}
```

### Dependent Queries

```typescript
function UserPosts({ userId }: { userId: string }) {
  const { data: user } = useQuery({
    queryKey: ['users', userId],
    queryFn: () => api.users.get(userId),
  });

  const { data: posts } = useQuery({
    queryKey: ['users', userId, 'posts'],
    queryFn: () => api.posts.listByUser(userId),
    enabled: !!user, // Only fetch when user is loaded
  });
}
```

## Mutation Patterns

### Basic Mutation with Cache Invalidation

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';

function CreateUserButton() {
  const queryClient = useQueryClient();

  const createUser = useMutation({
    mutationFn: (data: CreateUserInput) => api.users.create(data),
    onSuccess: () => {
      // Invalidate and refetch user lists
      queryClient.invalidateQueries({ queryKey: ['users', 'list'] });
    },
  });

  return (
    <button
      onClick={() => createUser.mutate({ name: 'New User' })}
      disabled={createUser.isPending}
    >
      {createUser.isPending ? 'Creating...' : 'Create User'}
    </button>
  );
}
```

### Optimistic Update Pattern

```typescript
const updateUser = useMutation({
  mutationFn: (data: UpdateUserInput) => api.users.update(data.id, data),

  onMutate: async (newData) => {
    // Cancel in-flight queries
    await queryClient.cancelQueries({ queryKey: ['users', newData.id] });

    // Snapshot previous value
    const previous = queryClient.getQueryData(['users', newData.id]);

    // Optimistically update cache
    queryClient.setQueryData(['users', newData.id], (old: User) => ({
      ...old,
      ...newData,
    }));

    return { previous }; // Context for rollback
  },

  onError: (_err, _vars, context) => {
    // Rollback on error
    if (context?.previous) {
      queryClient.setQueryData(['users', context.previous.id], context.previous);
    }
  },

  onSettled: (_data, _err, vars) => {
    // Always refetch after settle to ensure consistency
    queryClient.invalidateQueries({ queryKey: ['users', vars.id] });
  },
});
```

## Cache Configuration

### `staleTime` vs `gcTime`

| Setting | Default | Purpose |
|---------|---------|---------|
| `staleTime` | 0 ms | How long data is "fresh" (no background refetch) |
| `gcTime` | 5 min | How long unused data stays in memory |

**Rule:** `staleTime ≤ gcTime` always.

```typescript
// Global defaults in QueryClient
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000,  // 1 min default fresh
      gcTime: 5 * 60 * 1000, // 5 min cache
      retry: (count, error) => count < 3 && (error as ApiError).status !== 401,
    },
  },
});
```

### When to Use `invalidateQueries` vs `setQueryData`

| Scenario | Method | Why |
|----------|--------|-----|
| Mutation succeeded, trust server | `invalidateQueries` | Server is source of truth |
| Optimistic update | `setQueryData` then `invalidateQueries` | Immediate UI + eventual consistency |
| Known delta, avoid request | `setQueryData` | E.g., toggling a boolean flag |
| Multiple queries affected | `invalidateQueries` with prefix | Cascade invalidation |

## Type-Safe API Client (openapi-typescript)

### Generate Types

```bash
# In package.json scripts:
# "generate:api": "openapi-typescript http://localhost:8000/openapi.json -o src/generated/api.ts"
pnpm generate:api
```

### Fetch Wrapper

```typescript
// api/client.ts
import type { paths } from '@/generated/api';

type ApiResponse<T> = { data: T; status: number };

async function apiClient<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...init?.headers,
    },
    credentials: 'include', // Send cookies for auth
  });

  if (!response.ok) {
    throw new ApiError(response.status, await response.text());
  }

  return response.json() as Promise<T>;
}

// Type-safe endpoint functions
type UserListResponse = paths['/api/users']['get']['responses']['200']['content']['application/json'];
type UserCreateBody = paths['/api/users']['post']['requestBody']['content']['application/json'];

export const api = {
  users: {
    list: () => apiClient<UserListResponse>('/api/users'),
    get: (id: string) => apiClient<UserListResponse>(`/api/users/${id}`),
    create: (body: UserCreateBody) =>
      apiClient<UserListResponse>('/api/users', { method: 'POST', body: JSON.stringify(body) }),
  },
};
```

## Zustand — Client-Only State

### Small, Focused Stores

```typescript
// stores/uiStore.ts — one concern per store
import { create } from 'zustand';

interface UIState {
  sidebarOpen: boolean;
  toggleSidebar: () => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: true,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
}));
```

### Granular Selectors (Prevent Re-renders)

```typescript
// ✅ GOOD: Select only what you need
const sidebarOpen = useUIStore((s) => s.sidebarOpen);

// ❌ BAD: Full store subscription (re-renders on any change)
const store = useUIStore();
```

### Zustand Anti-Patterns

- **Never store server data** — use TanStack Query
- **Never create monolithic stores** — split by concern (auth, ui, preferences)
- **Never use Zustand for form state** — use React Hook Form
- **Never mutate without `set()`** — breaks reactivity tracking

### Persist Middleware

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const usePrefsStore = create<PrefsState>()(
  persist(
    (set) => ({
      theme: 'system' as const,
      setTheme: (theme: Theme) => set({ theme }),
    }),
    {
      name: 'user-prefs',
      version: 1,
      partialize: (state) => ({ theme: state.theme }), // Only persist safe fields
    }
  )
);
```

## URL State for Filters/Pagination

```typescript
import { useSearchParams } from 'react-router-dom';

function useFilters() {
  const [params, setParams] = useSearchParams();

  return {
    page: parseInt(params.get('page') ?? '1', 10),
    sort: params.get('sort') ?? 'date',
    setPage: (p: number) => {
      const next = new URLSearchParams(params);
      next.set('page', String(p));
      setParams(next);
    },
  };
}

// Derive query key from URL state
function ProductList() {
  const { page, sort } = useFilters();
  const { data } = useQuery({
    queryKey: ['products', 'list', { page, sort }],
    queryFn: () => api.products.list({ page, sort }),
  });
}
```

## Error Handling Pattern

```typescript
// Global error handler via QueryCache
const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError: (error) => {
      if ((error as ApiError).status === 401) {
        // Redirect to login
        window.location.href = '/login';
      }
    },
  }),
});

// Per-query retry logic
const { data } = useQuery({
  queryKey: ['users'],
  queryFn: () => api.users.list(),
  retry: (count, error) => {
    if ((error as ApiError).status === 404) return false; // Don't retry 404s
    return count < 3;
  },
});
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Server data in Zustand | Use TanStack Query; Zustand is for UI state only |
| Unstable query keys (new object each render) | Extract filter objects or use `useMemo` |
| Missing `enabled: false` for conditional queries | Add `enabled: !!dependency` |
| Forgetting `onSettled` invalidation after optimistic update | Always invalidate to sync with server |
| Manually refetching instead of invalidating | Use `invalidateQueries`; it handles stale checks |
| Not using `credentials: 'include'` | Required for cookie-based auth |
