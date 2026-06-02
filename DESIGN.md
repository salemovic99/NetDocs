---
name: Operational Clarity
colors:
  surface: '#0b1326'
  surface-dim: '#0b1326'
  surface-bright: '#31394d'
  surface-container-lowest: '#060e20'
  surface-container-low: '#131b2e'
  surface-container: '#171f33'
  surface-container-high: '#222a3d'
  surface-container-highest: '#2d3449'
  on-surface: '#dae2fd'
  on-surface-variant: '#c2c6d6'
  inverse-surface: '#dae2fd'
  inverse-on-surface: '#283044'
  outline: '#8c909f'
  outline-variant: '#424754'
  surface-tint: '#adc6ff'
  primary: '#adc6ff'
  on-primary: '#002e6a'
  primary-container: '#4d8eff'
  on-primary-container: '#00285d'
  inverse-primary: '#005ac2'
  secondary: '#4edea3'
  on-secondary: '#003824'
  secondary-container: '#00a572'
  on-secondary-container: '#00311f'
  tertiary: '#ffb786'
  on-tertiary: '#502400'
  tertiary-container: '#df7412'
  on-tertiary-container: '#461f00'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#d8e2ff'
  primary-fixed-dim: '#adc6ff'
  on-primary-fixed: '#001a42'
  on-primary-fixed-variant: '#004395'
  secondary-fixed: '#6ffbbe'
  secondary-fixed-dim: '#4edea3'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#ffdcc6'
  tertiary-fixed-dim: '#ffb786'
  on-tertiary-fixed: '#311400'
  on-tertiary-fixed-variant: '#723600'
  background: '#0b1326'
  on-background: '#dae2fd'
  surface-variant: '#2d3449'
typography:
  h1:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.02em
  h2:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  h3:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
  h4:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
  body-lg:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  mono:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
  label-caps:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  gutter: 16px
  margin: 24px
---

## Brand & Style
The design system is engineered for high-stakes B2B IT environments where speed of comprehension is the primary metric of success. The brand personality is **precise, authoritative, and high-performance**, leaning into a **Modern Corporate** aesthetic with a heavy emphasis on **Information Density**.

The visual language avoids unnecessary decoration, focusing instead on structural integrity and clear hierarchy. It utilizes a refined palette of deep slates to establish a "command center" feel that minimizes eye strain during long periods of monitoring. The emotional response is one of calm control—transforming complex data streams into actionable intelligence.

## Colors
This design system utilizes a "Deep Slate" dark mode by default to reduce glare and highlight status indicators.

- **Foundational Neutrals:** `background` is near-black for maximum contrast with content. `surface` and `overlay` tiers create a clear Z-axis for modals and panels.
- **Operational Blue (#3B82F6):** Used for primary actions, active states, and focus indicators.
- **Success Emerald (#10B981):** Reserved strictly for "Healthy" or "Resolved" system states.
- **Semantic Feedback:** Warning (Amber) and Error (Red) are high-chroma to ensure they pierce through the neutral UI during critical incidents.

## Typography
The typographic system is built for **legibility and density**. 

- **Primary Type:** Inter is used for all UI elements due to its excellent x-height and readability at small scales.
- **Technical Type:** JetBrains Mono is employed for logs, code snippets, and ID strings to ensure character distinction (e.g., distinguishing `0` from `O`).
- **Scale:** The base body size is 12px for data grids and 14px for general reading. Headlines remain compact to preserve vertical screen real estate for dashboards.

## Layout & Spacing
The design system follows a strict **4px grid**. All padding, margins, and component heights must be multiples of 4.

- **Grid Model:** 12-column fluid grid for main dashboards.
- **Density:** Information-dense views (data tables, log streams) use `xs` and `sm` spacing. General settings and documentation use `md` and `lg` spacing.
- **Breakpoints:** 
  - Mobile (< 768px): Single column, sidebars hidden in hamburger menus. 
  - Tablet (768px - 1280px): Fixed width sidebar (240px), fluid content area.
  - Desktop (> 1280px): Fixed width sidebar (280px), content max-width of 1600px.

## Elevation & Depth
Depth is achieved through **Tonal Layering** supplemented by subtle **Low-Contrast Outlines**. 

1. **Level 0 (Background):** The lowest layer, used for the main application canvas.
2. **Level 1 (Surface):** Used for cards, tables, and sidebars. Defined by a 1px border (`#334155`).
3. **Level 2 (Overlay):** Used for dropdowns and popovers. Features a 1px border and a soft, diffused shadow (`0 4px 12px rgba(0,0,0,0.5)`).
4. **Level 3 (Modal):** The highest layer, utilizing a backdrop blur (8px) on the Level 0/1 content to maintain focus.

## Shapes
The shape language is **functional and architectural**. 

A base roundedness of **6px (0.375rem)** is applied to buttons, input fields, and cards to soften the technical interface without appearing "playful." Status indicators and small tags may use a pill shape to distinguish them from interactive buttons.

## Components
- **Buttons:** 
  - *Primary:* Solid Operational Blue, white text.
  - *Secondary:* Ghost style with 1px border (`#334155`), white text. 
  - *Sizing:* Compact (28px height) for toolbars; Standard (36px height) for forms.
- **Data Tables:** High-density, 32px row height. Use alternating row zebra-striping (Level 0 / Level 1) for tracking across wide monitors. Hover states must highlight the entire row.
- **Status Badges:** Small (18px height) with a subtle background tint (10% opacity of the semantic color) and a solid 2px dot indicator.
- **Inputs:** 1px border with `#334155`. On focus, the border changes to Operational Blue with a 2px outer glow.
- **Search Inputs:** Always include a leading search icon and a keyboard shortcut hint (e.g., `⌘K`) in the trailing edge.
- **Knowledge Cards:** Used for documentation snippets; include a `mono` font footer for "last updated" or "author" metadata.