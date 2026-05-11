---
name: tailwind-css-ts
description: "Tailwind CSS v4 utility-first patterns for styling React components. Use when implementing UI with Tailwind utilities, configuring design tokens, building responsive layouts, implementing dark mode, creating reusable component styles, or fixing styling anti-patterns (inline styles, arbitrary values, missing breakpoints)."
---

# Tailwind CSS v4 (TypeScript/React)

Utility-first styling patterns, design tokens, responsive design, and dark mode.

## When to Use This Skill

- Styling React components with Tailwind utilities
- Configuring design tokens and theme customization
- Building responsive mobile-first layouts
- Implementing dark mode (system preference or manual toggle)
- Extracting reusable component styles
- Fixing CSS anti-slop patterns (inline styles, hardcoded values)

## Prerequisites

```bash
pnpm add tailwindcss @tailwindcss/vite    # Vite plugin
```

```typescript
// vite.config.ts
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [react(), tailwindcss()],
});
```

```css
/* src/index.css — import Tailwind */
@import "tailwindcss";
```

## Design Tokens (Theme Customization)

### Defining Custom Tokens

```css
/* src/index.css */
@import "tailwindcss";

@theme {
  /* Colors — semantic names, not raw hex */
  --color-brand-primary: oklch(0.63 0.237 25.331);
  --color-brand-secondary: oklch(0.75 0.15 200);
  --color-surface: #ffffff;
  --color-surface-dark: #0f172a;

  /* Spacing */
  --spacing-page: 2rem;
  --spacing-section: 4rem;

  /* Border radius */
  --radius-card: 0.75rem;

  /* Shadows */
  --shadow-card: 0 2px 8px rgb(0 0 0 / 0.08);

  /* Fonts */
  --font-sans: 'Inter', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}
```

These become utilities: `bg-brand-primary`, `px-page`, `rounded-card`, `shadow-card`.

### When to Use Tokens vs Arbitrary Values

| Scenario | Use |
|----------|-----|
| Reused across components | `@theme` token → `bg-brand-primary` |
| One-off layout adjustment | Arbitrary `w-[23rem]` (OK sparingly) |
| Matches existing scale | Standard utility → `p-4`, `rounded-lg` |

**Rule:** If you use an arbitrary value more than twice, extract it to `@theme`.

## Responsive Design (Mobile-First)

### Breakpoint Reference

| Prefix | Min-width | Target |
|--------|-----------|--------|
| (none) | 0 | Mobile (default) |
| `sm:` | 40rem (640px) | Large phones / small tablets |
| `md:` | 48rem (768px) | Tablets |
| `lg:` | 64rem (1024px) | Laptops |
| `xl:` | 80rem (1280px) | Desktops |
| `2xl:` | 96rem (1536px) | Large screens |

### Responsive Grid Pattern

```tsx
{/* Mobile: 1 col → Tablet: 2 cols → Desktop: 4 cols */}
<div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
  {items.map(item => <Card key={item.id} {...item} />)}
</div>
```

### Responsive Typography

```tsx
<h1 className="text-2xl font-bold sm:text-3xl lg:text-4xl">
  Dashboard
</h1>
```

### Container Queries (Component-Level Responsive)

```tsx
{/* Parent sets container context */}
<div className="@container">
  {/* Children respond to parent width, not viewport */}
  <div className="flex flex-col @md:flex-row @lg:gap-8">
    <Sidebar />
    <Content />
  </div>
</div>
```

Use container queries for reusable components that may appear in different layout contexts.

## Dark Mode

### System Preference (Default)

```tsx
{/* Automatically respects OS dark mode setting */}
<div className="bg-white text-gray-900 dark:bg-slate-900 dark:text-gray-100">
  <h1 className="text-gray-800 dark:text-gray-200">Title</h1>
  <p className="text-gray-600 dark:text-gray-400">Body text</p>
</div>
```

### Manual Toggle (Class Strategy)

```css
/* tailwind.config — enable class strategy */
@custom-variant dark (&:where(.dark, .dark *));
```

```tsx
// Toggle dark class on <html>
function ThemeToggle() {
  const { theme, setTheme } = usePrefsStore((s) => ({
    theme: s.theme,
    setTheme: s.setTheme,
  }));

  return (
    <button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}>
      {theme === 'dark' ? '☀️' : '🌙'}
    </button>
  );
}

// Apply in root layout
<html className={theme === 'dark' ? 'dark' : ''}>
```

### Dark Mode Anti-Pattern

```tsx
// ❌ BAD: Forgot text color — invisible in dark mode
<div className="bg-white dark:bg-slate-900">
  <p>This text disappears in dark mode!</p>
</div>

// ✅ GOOD: Always pair background + text colors
<div className="bg-white text-gray-900 dark:bg-slate-900 dark:text-gray-100">
  <p>Visible in both modes</p>
</div>
```

## Component Styling Patterns

### When to Extract vs Use Inline Utilities

| Pattern | Use |
|---------|-----|
| Utilities in JSX | Default — single-use or few-use styles |
| React component | Same utility set used 3+ times across files |
| `@layer components` | Framework-level shared styles (badge, tag, input base) |

### React Component Extraction (Preferred)

```tsx
// shared/components/Badge.tsx
interface BadgeProps {
  variant: 'success' | 'warning' | 'error';
  children: ReactNode;
}

const variantStyles = {
  success: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  warning: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  error: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
} as const;

function Badge({ variant, children }: BadgeProps) {
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${variantStyles[variant]}`}>
      {children}
    </span>
  );
}
```

### CSS Layer Extraction (Rare)

```css
/* Only for base-level shared styles across the entire app */
@layer components {
  .btn-primary {
    @apply rounded-lg bg-blue-600 px-4 py-2 font-medium text-white
           hover:bg-blue-700 focus-visible:outline-2
           focus-visible:outline-offset-2 focus-visible:outline-blue-600;
  }
}
```

## Layout Patterns

### Sticky Header + Scrollable Content

```tsx
<div className="flex h-screen flex-col">
  <header className="sticky top-0 z-10 border-b bg-white px-page dark:bg-slate-900">
    <nav>...</nav>
  </header>
  <main className="flex-1 overflow-y-auto px-page py-section">
    {children}
  </main>
</div>
```

### Sidebar Layout

```tsx
<div className="flex h-screen">
  <aside className="hidden w-64 border-r bg-gray-50 lg:block dark:bg-slate-800">
    <nav>...</nav>
  </aside>
  <main className="flex-1 overflow-y-auto">
    {children}
  </main>
</div>
```

### Centered Content

```tsx
<div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
  {children}
</div>
```

## Accessibility + Tailwind

### Focus Indicators

```tsx
{/* Always visible focus ring for keyboard navigation */}
<button className="rounded-lg bg-blue-600 px-4 py-2 text-white
                    focus-visible:outline-2 focus-visible:outline-offset-2
                    focus-visible:outline-blue-600">
  Submit
</button>

{/* Screen reader only text */}
<span className="sr-only">Close navigation menu</span>
```

### Motion Safety

```tsx
{/* Respect prefers-reduced-motion */}
<div className="transition-transform duration-300 motion-reduce:transition-none">
```

## Anti-Slop Rules

| AI Anti-Pattern | Fix |
|----------------|-----|
| `style={{ color: 'red' }}` | `className="text-red-500"` |
| `bg-[#1e40af]` | `bg-blue-600` (use design token) |
| `p-[12px]` | `p-3` (use spacing scale: 3 × 4px = 12px) |
| `rounded-[8px]` | `rounded-lg` (use theme radius) |
| `className="grid-cols-4"` (no responsive) | `grid-cols-1 sm:grid-cols-2 lg:grid-cols-4` |
| `bg-white` without `dark:` variant | `bg-white dark:bg-slate-900` |
| `!important` | Fix specificity — check cascade order |
| `<div style="display: flex">` | `className="flex"` |
| Mixing CSS-in-JS for static styles | Use Tailwind utilities |
| `outline-none` without alternative | `focus-visible:outline-2 focus-visible:outline-blue-600` |
| Class string > 100 chars | Extract to React component |

## Tailwind Spacing Scale Reference

| Class | Value | Pixels |
|-------|-------|--------|
| `p-0` | 0 | 0px |
| `p-1` | 0.25rem | 4px |
| `p-2` | 0.5rem | 8px |
| `p-3` | 0.75rem | 12px |
| `p-4` | 1rem | 16px |
| `p-6` | 1.5rem | 24px |
| `p-8` | 2rem | 32px |
| `p-12` | 3rem | 48px |
| `p-16` | 4rem | 64px |

Same scale applies to `m-`, `gap-`, `w-`, `h-`, `space-x-`, `space-y-`, etc.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using `@apply` everywhere | Use utilities in JSX; extract React components |
| Creating separate CSS files per component | Use Tailwind utilities inline |
| Custom CSS overriding Tailwind | Use `@layer` for cascade control |
| Arbitrary values as first choice | Check theme scale first |
| Missing `dark:` pairs for bg/text | Always pair background + text for dark mode |
| Not using `sr-only` for icon buttons | Add screen reader text |

## CSS Validation

### Build-Time + Lint Verification (Default)

Two layers catch CSS issues out of the box — no extra tools needed:

1. **Biome** — Parses, lints, and formats CSS files. `biome check .` (via `pnpm check`) catches syntax errors, invalid rules, and style issues in `.css` files.
2. **Tailwind compiler** — The `@tailwindcss/vite` plugin validates utility classes at build time. Invalid classes produce warnings during `pnpm build`.

```bash
pnpm check    # Biome lints CSS + JS/TS
pnpm build    # Tailwind validates utility classes
```

### When to Add Stylelint

Skip it. Biome covers CSS linting natively. Only consider Stylelint if you need CSS-specific rules that Biome doesn't cover (rare).

### Quality Gate

The standard frontend quality gate covers everything:

```bash
pnpm typecheck && pnpm lint && pnpm build
```

- `pnpm lint` — Biome checks JS/TS **and CSS**
- `pnpm build` — Catches invalid Tailwind classes, missing imports
- `pnpm typecheck` — TypeScript catches style variant prop typos
