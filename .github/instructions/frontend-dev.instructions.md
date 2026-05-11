---
description: TypeScript/React coding conventions, component patterns, and quality enforcement
applyTo: "**/*.{ts,tsx,js,jsx}"
---

# Frontend (TypeScript/React)

**Read [Frontend Coding Standard](../../docs/standards/frontend.md)** — Complete reference for patterns, anti-slop rules, project structure, and examples.

## Quality Gate

```bash
pnpm check  # MUST pass before committing or marking tasks as Done
```

## Non-Negotiables

1. **Follow the [project structure](../../docs/standards/frontend.md#project-structure)** exactly:
   - `frontend/src/features/<name>/` for feature modules (api/, components/, hooks/, stores/, types.ts, index.ts)
   - `shared/components/` for design system / UI primitives only
   - `app/` for app shell (routes/, providers.tsx, App.tsx)
   - `generated/` for auto-generated types (never hand-edit)

2. **No `any` types** — Use `unknown` and narrow; leverage `satisfies` and `as const`

3. **Zod for I/O boundaries** — Validate API responses and form inputs:
   ```typescript
   const data = UserSchema.parse(await api.getUser(id));  // ✅
   ```

4. **TanStack Query for server state** — Never `useEffect` + `fetch`; never put API data in Zustand

5. **Semantic HTML + accessibility** — `<button>` for actions, `<a>` for navigation; every `<input>` needs `<label htmlFor>`

6. **Tailwind utilities over inline styles** — Mobile-first responsive; design tokens not arbitrary values

7. **Function components only** — No `React.FC`; type props at function signature

## State Management

| State Type | Tool | Example |
|-----------|------|---------|
| Server/async | TanStack Query | API responses, user data |
| Client UI | Zustand | Modal open, sidebar collapsed |
| Forms | React Hook Form + Zod | Input values, validation |
| URL-shareable | URL search params | Filters, pagination, sort |
| Ephemeral | `useState` | Hover, focus, animation |

## Component Registries

For animated/creative components, use [ReactBits](https://reactbits.dev) via shadcn MCP tools (search with `tool_search_tool_regex("shadcn")` first) or CLI fallback. See **frontend-components-ts** skill below for details.

## Skills (Load on Demand)

- **frontend-components-ts**: ReactBits, shadcn MCP, animations (when working with component registries)
- **tanstack-query-ts**: Server state, caching, mutations
- **react-hook-form-ts**: Form validation, Zod, multi-step wizards
- **tailwind-css-ts**: Design tokens, responsive, dark mode


## Commands

| Task | Command |
|------|---------|
| Dev server | `pnpm dev` |
| All checks | `pnpm check` |
| Lint + format | `pnpm lint` |
| Type check | `pnpm typecheck` |
| Tests | `pnpm test` |
| Generate types | `pnpm generate` |
