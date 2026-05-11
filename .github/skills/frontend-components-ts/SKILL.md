---
name: frontend-components-ts
description: "Creative animated React components via component registries (ReactBits, shadcn). Use when adding animations, scroll effects, text effects, animated backgrounds, interactive UI elements, creative landing pages, or setting up component registries."
argument-hint: "Describe the component or effect you need (e.g., hero with aurora background, animated card grid)"
---

# Frontend Components (TypeScript/React)

Creative, animated component patterns using registry-based component libraries. Components are copy-pasted into your project — no runtime dependency on the registry.

> **IMPORTANT**: Follow the Registry Setup steps below in order — install the MCP first, then use MCP tools. Only fall back to manual CLI if the MCP is unavailable.

## When to Use This Skill

- Adding animated/interactive UI elements to a React project
- Building creative landing pages, hero sections, or portfolios
- Setting up component registries (`@react-bits`, shadcn)
- Choosing the right animation component for a use case
- Combining animated components into cohesive page sections

## Registry Setup

Follow these steps **in order**. The goal is to use MCP tools for component discovery and installation. If MCP setup fails, fall back to manual CLI.

### Step 1: Check for Existing MCP Tools

Use `tool_search_tool_regex` with pattern `shadcn` to check if MCP tools are already available.

- **If tools are found** → Skip to [Step 3: Use MCP Tools](#step-3-use-mcp-tools)
- **If no tools found** → Continue to Step 2

### Step 2: Install the shadcn MCP Server

Run in terminal:

```bash
npx -y shadcn@latest mcp init --client vscode
```

This configures the MCP server in `.vscode/mcp.json` non-interactively.

After installation, search again with `tool_search_tool_regex` pattern `shadcn` to confirm tools are now available.

- **If tools are found** → Continue to Step 3
- **If still no tools** → Skip to [Manual Fallback](#manual-fallback-only-if-mcp-unavailable)

### Step 3: Use MCP Tools

The MCP provides component discovery, browsing, and installation with automatic dependency tracking.

```
# Browse a category
shadcn_list_components(registry="@react-bits", category="text-animations")

# Search by use case
shadcn_search_components(query="aurora background")

# Install a component
shadcn_add_component(name="split-text", registry="@react-bits")
```

Common tool names after loading: `shadcn_list_components`, `shadcn_add_component`, `shadcn_search_components`. Exact names may vary — use the `tool_search_tool_regex` results to confirm.

### Manual Fallback (Only if MCP Unavailable)

If MCP installation failed or tools remain unavailable:

1. **Configure the Registry** — Add to `components.json`:
   ```json
   {
     "registries": {
       "@react-bits": "https://reactbits.dev/r/{name}.json"
     }
   }
   ```

2. **Install components via CLI**:
   ```bash
   npx -y shadcn@latest add "@react-bits/split-text"
   ```

### Install Dependencies

**When using MCP:** The shadcn MCP tools often handle dependencies automatically when installing components.

**For manual installs or missing dependencies:**

| Dependency | Components That Use It |
|------------|----------------------|
| `gsap` + `@gsap/react` | Most text animations, AnimatedContent, FadeContent, scroll effects |
| `three` + `@react-three/fiber` + `@react-three/drei` | 3D backgrounds (Galaxy, BallPit), ModelViewer |
| `ogl` | Some backgrounds (Iridescence, LiquidChrome) |
| `framer-motion` | Some components (AnimatedList, Dock) |

```bash
# Most common — covers ~60% of components
pnpm add gsap @gsap/react
```

## Component Categories

ReactBits provides 120+ components in 4 categories. See [ReactBits Catalog](./references/reactbits-catalog.md) for the full list.

| Category | Count | Use For |
|----------|-------|---------|
| **Text Animations** | 22 | Hero headings, reveal effects, scroll-driven text |
| **Animations** | 29 | Cursor effects, transitions, hover states, scroll reveals |
| **Backgrounds** | 35 | Full-page or section backgrounds, ambient effects |
| **Components** | 34 | Cards, galleries, navigation, menus, interactive layouts |

## Common Patterns

### Hero Section

```tsx
import SplitText from "./SplitText";
import Aurora from "./Aurora";

function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center">
      <Aurora className="absolute inset-0 -z-10" />
      <SplitText
        text="Welcome to the Future"
        className="text-6xl font-bold"
        delay={80}
        splitType="chars"
      />
    </section>
  );
}
```

### Scroll-Driven Content

```tsx
import AnimatedContent from "./AnimatedContent";
import ScrollReveal from "./ScrollReveal";

function Features() {
  return (
    <section className="space-y-24 py-32">
      {features.map((feature) => (
        <AnimatedContent key={feature.id} distance={80} direction="vertical">
          <div className="grid grid-cols-2 gap-12">
            <ScrollReveal>
              <h3 className="text-3xl font-semibold">{feature.title}</h3>
            </ScrollReveal>
            <p className="text-muted-foreground">{feature.description}</p>
          </div>
        </AnimatedContent>
      ))}
    </section>
  );
}
```

### Interactive Cards

```tsx
import SpotlightCard from "./SpotlightCard";
import TiltedCard from "./TiltedCard";

function CardGrid() {
  return (
    <div className="grid grid-cols-3 gap-6">
      {items.map((item) => (
        <SpotlightCard key={item.id} className="p-6 rounded-2xl">
          <TiltedCard>
            <h4>{item.title}</h4>
            <p>{item.description}</p>
          </TiltedCard>
        </SpotlightCard>
      ))}
    </div>
  );
}
```

## Integration with Tailwind

Components are copy-pasted source code — style them with Tailwind utilities like any other component:

- Pass `className` props for layout and spacing
- Override internal styles by editing the component source
- Use Tailwind's `dark:` variants — most components respect CSS custom properties

## Guidelines

1. **Don't over-animate** — Pick 2-3 animation effects per page max. Too many competing animations create visual noise.
2. **Performance** — GSAP and Three.js add to bundle size. Use dynamic imports for heavy components:
   ```tsx
   const Galaxy = lazy(() => import("./Galaxy"));
   ```
3. **Accessibility** — Respect `prefers-reduced-motion`. Most ReactBits components don't handle this automatically — add it:
   ```tsx
   const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
   ```
4. **Mobile** — 3D/WebGL backgrounds can be heavy on mobile. Conditionally render simpler alternatives.
5. **Components are yours** — Once installed, the source code is in your project. Modify freely.

## Troubleshooting

### MCP Install Fails

If `npx -y shadcn@latest mcp init --client vscode` errors out:
1. Check that `npx` and `node` are available on the PATH
2. Try running `npm install -g shadcn@latest` first, then `shadcn mcp init --client vscode`
3. If all else fails, use the [Manual Fallback](#manual-fallback-only-if-mcp-unavailable) workflow
