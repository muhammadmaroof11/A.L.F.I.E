---
name: interface-design
description: "High-craft digital product design rules inspired by Linear, Stripe, and Apple. Covers micro-interactions, optical alignment, typography rhythm, restrained dark/light systems, and state-of-the-art visual polish."
license: MIT
---

# Interface Design — High-Craft Product Polish

Master rules for achieving the highest tier of visual precision and interaction fidelity in modern software interfaces.

## 1. Optical Balance & Spatial Rhythm
- **Optical Center**: Visual weight is not strictly geometric. Center floating elements ~2-4% above the mathematical midpoint to prevent feeling "sunken".
- **Spatial Grid Units**: Use a strict 4px / 8px spacing scale (`4, 8, 12, 16, 24, 32, 48, 64, 96px`). Never use arbitrary ad-hoc margins.
- **Hierarchy through Scale & Weight**: Achieve hierarchy through font weight and size contrasts rather than introducing 5 different font colors.

## 2. Color Systems & Visual Depth
- **Neutrals with Character**: Avoid flat `#FFFFFF` and raw `#000000`. Use calibrated slate/obsidian neutrals (e.g., `#0F172A`, `#F8FAFC`, `#0B0F17`).
- **Precision Hairlines**: Use subtle borders (`1px solid rgba(15, 23, 42, 0.08)` in light mode, `1px solid rgba(255, 255, 255, 0.08)` in dark mode) instead of heavy drop shadows.
- **Surface Elevation**: Stack elevation layers using background lightness and subtle inner highlights (`inset 0 1px 0 rgba(255, 255, 255, 0.1)`).

## 3. Motion & Micro-Interactions
- **Natural Spring Curves**: Use `cubic-bezier(0.16, 1, 0.3, 1)` (ease-out quint) for interactive UI transitions.
- **Speed Disciplines**:
  - Micro-toggles & buttons: 100–180ms
  - Dialogs & dropdowns: 200–300ms
  - Page transitions: 350–500ms
- **Feedback on Action**: Every button click must provide immediate physical feedback (active scale `scale-[0.98]` or background tint).

## 4. Typography Rules
- **Headline Tracking**: Tighten letter-spacing on display headings (`-0.03em` to `-0.05em`) and set line-height to `1.05`–`1.15`.
- **Body Legibility**: Set body text tracking to normal (`0em` to `0.01em`) with line-height of `1.5`–`1.6`.
- **Monospace for Data**: Use monospace fonts (`JetBrains Mono`, `SF Mono`) for numbers, latency metrics, currencies, and code blocks for tabular alignment.
