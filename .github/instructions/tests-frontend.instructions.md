---
applyTo: "**/*.test.{ts,tsx}"
description: Frontend test patterns and conventions for React/TypeScript testing with Vitest
---

# Frontend Testing Guidelines

> **Status:** Placeholder — to be completed after frontend stack selection.

## Structure

```
frontend/
  src/
    components/
      Button/
        Button.tsx
        Button.test.tsx     # Collocate tests with components
    hooks/
      useAuth.test.ts
  tests/
    integration/            # Cross-component / API integration tests
```

Run tests with `pnpm test`

## Non-Negotiable Rules

1. **Collocate tests** with the code they test (`Component.test.tsx` next to `Component.tsx`)
2. **No `any` types** in test files — same strictness as production code
3. **Use `screen` queries** from Testing Library — avoid direct container queries
4. **Prefer `userEvent` over `fireEvent`** for user interactions

## File & Naming Conventions

- Files: `<Component>.test.tsx` or `<hook>.test.ts`
- Describe blocks: `describe('<ComponentName>', () => { ... })`
- Tests: `it('should <expected behaviour>', () => { ... })`

## Testing Library Patterns

```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

it('should submit form with valid data', async () => {
  const user = userEvent.setup();
  render(<LoginForm onSubmit={mockSubmit} />);

  await user.type(screen.getByLabelText('Email'), 'test@example.com');
  await user.click(screen.getByRole('button', { name: /submit/i }));

  expect(mockSubmit).toHaveBeenCalledWith({ email: 'test@example.com' });
});
```

## Query Priority

Prefer queries that reflect how users interact with the UI:

1. `getByRole` — accessible roles (button, heading, textbox)
2. `getByLabelText` — form fields
3. `getByPlaceholderText` — when no label exists
4. `getByText` — visible text
5. `getByTestId` — last resort only

## Mocking

```tsx
// Mock API calls
vi.mock('../api/client', () => ({
  fetchUser: vi.fn(),
}));

// Mock hooks
vi.mock('../hooks/useAuth', () => ({
  useAuth: () => ({ user: mockUser, isLoading: false }),
}));
```

## What to Test

| Layer | Test focus |
|-------|-----------|
| Components | Rendering, user interactions, conditional display |
| Hooks | State changes, side effects, return values |
| Utils | Pure logic — test exhaustively |
| Integration | User flows across multiple components |

## What NOT to Test

- Implementation details (state variable names, internal methods)
- Third-party library internals
- CSS styling (use visual regression tools instead)
