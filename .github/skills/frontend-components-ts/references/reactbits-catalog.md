# ReactBits Component Catalog

Curated core components from [ReactBits](https://reactbits.dev). Use the shadcn MCP or browse `reactbits.dev` for the full 120+ component library.

## Core Components

### Text Animations

| Component | Use For | Dependencies |
|-----------|---------|--------------|
| **SplitText** | Hero headings — animates by chars/words/lines | gsap |
| **BlurText** | Subtitle reveals — blur-to-sharp transition | — |
| **ScrollReveal** | Section headings — reveals on scroll | gsap |
| **CountUp** | Stats/metrics — animated number counter | — |
| **ShinyText** | Badges/CTAs — shimmer effect | — |
| **GradientText** | Accent text — animated gradient sweep | — |

### Animations

| Component | Use For | Dependencies |
|-----------|---------|--------------|
| **AnimatedContent** | Scroll-triggered section enter/exit | gsap |
| **FadeContent** | Fade in/out on scroll | gsap |
| **ClickSpark** | Spark particles on click | — |
| **GlareHover** | Card/button hover shine effect | — |
| **StarBorder** | Animated sparkle border | — |
| **LogoLoop** | Client/partner logo carousel | — |

### Backgrounds

| Component | Use For | Dependencies |
|-----------|---------|--------------|
| **Aurora** | Hero — northern lights effect (lightweight) | — |
| **Particles** | Hero — particle field with mouse interaction | — |
| **Waves** | Section dividers — animated wave | — |
| **DotGrid** | Subtle ambient grid pattern | — |
| **Dither** | Creative — dithered gradient | — |

### Components

| Component | Use For | Dependencies |
|-----------|---------|--------------|
| **SpotlightCard** | Feature cards — cursor spotlight | — |
| **TiltedCard** | Product cards — 3D tilt on hover | — |
| **Carousel** | Image/content slideshow | gsap |
| **Masonry** | Image gallery grid | — |
| **AnimatedList** | Feed/list items with stagger animation | framer-motion |
| **Dock** | macOS-style navigation dock | framer-motion |

## Dependencies

Most core components need only GSAP:

```bash
pnpm add gsap @gsap/react
```

Add `framer-motion` only if using AnimatedList or Dock.

## Beyond Core

For components not listed here, use the shadcn MCP to browse and install:

- *"Show me all backgrounds from React Bits"*
- *"Find a 3D gallery component from React Bits"*
- *"Add the LiquidChrome background from React Bits"*

Or browse: `https://reactbits.dev/<category>/<component>`
