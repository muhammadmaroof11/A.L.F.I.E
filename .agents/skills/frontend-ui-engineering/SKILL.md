---
name: frontend-ui-engineering
description: "Production-grade frontend engineering standards. Focuses on component architecture, WCAG AAA accessibility, fluid responsive behavior, performance optimization, and robust UI state management."
license: MIT
---

# Frontend UI Engineering

This skill provides expert directives for building production-grade, highly performant, accessible, and maintainable user interfaces across React, Vue, Svelte, and modern web stacks.

## 1. Architectural Integrity & Component Design
- **Single Responsibility**: Components must have a singular, well-defined purpose. Break monolithic views into clean sub-components.
- **Composition over Configuration**: Prefer slots, compound components, and children over dozens of boolean flags.
- **Semantic HTML First**: Use `<main>`, `<header>`, `<nav>`, `<section>`, `<article>`, `<aside>`, `<button>` rather than endless nested `<div>` tags.

## 2. Accessibility (WCAG 2.1 AAA / AA)
- **Contrast Ratios**: Body text must achieve at least 4.5:1 contrast against its background; large text (18pt+) must achieve at least 3.0:1.
- **Keyboard Navigation**: All interactive elements must be focusable with clear `:focus-visible` styling (minimum 2px offset outline).
- **Aria Attributes**: Provide `aria-label`, `aria-expanded`, and `aria-live` regions where visual cues are dynamic.
- **Form Controls**: Always associate `<label>` with `<input>` using `id` and `htmlFor`. Never use placeholders as replacement for labels.

## 3. Performance & Layout Stability (Core Web Vitals)
- **Cumulative Layout Shift (CLS < 0.1)**: Always reserve aspect ratios (`aspect-[16/9]`, `aspect-square`) for images, videos, and 3D canvases to prevent jarring layout jumps.
- **Asset Optimization**: Deliver modern formats (WebP/AVIF for images, optimized MP4 for videos, compressed GLB for 3D).
- **Main Thread Budget**: Debounce search inputs, throttle resize/scroll listeners, and use `requestAnimationFrame` for custom visual animations.

## 4. State & Feedback Hierarchy
- **Predictable States**: Every dynamic component must cleanly handle `idle`, `loading`, `success`, `empty`, and `error` states.
- **Optimistic UI Updates**: Provide instant visual feedback for user actions (100–200ms spring transitions) before asynchronous requests complete.
- **Error Boundaries**: Contain component failures gracefully without crashing the whole application view.
