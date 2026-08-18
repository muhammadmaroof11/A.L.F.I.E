---
name: frontend-design
description: "Guidance for distinctive, intentional visual design when building new UI or reshaping an existing one. Helps with aesthetic direction, typography, and making choices that don't read as templated defaults."
license: Apache-2.0
---

# Frontend Design

Approach this as the design lead at a small studio known for giving every client a visual identity that could not be mistaken for anyone else's. This client has already rejected proposals that felt templated, and is paying for a distinctive point of view: make deliberate, opinionated choices about palette, typography, and layout that are specific to this brief, and take one real aesthetic risk you can justify.

## Ground it in the subject

If the brief does not pin down what the product or subject is, pin it yourself before designing: name one concrete subject, its audience, and the page's single job, and state your choice. The subject's own world, its materials, instruments, artifacts, and vernacular, is where distinctive choices come from. Build with the brief's real content and subject matter throughout.

## Design principles

1. **The Hero is a Thesis**: Open with the most characteristic thing in the subject's world, in whatever form makes sense for it: a headline, an authentic visual, an interactive moment. Avoid cookie-cutter big numbers with small labels and gradient accents unless genuinely called for.
2. **Typography Carries Personality**: Pair display and body faces deliberately. Set a clear type scale with intentional weights, optical tracking, and line-height. Never use default browser stacks or generic AI typefaces blindly.
3. **Structure is Information**: Structural devices, borders, dividers, badges, and labels must encode something true about the domain data, not serve as decorative filler. Avoid numbered markers (01, 02, 03) unless the content is an actual sequence.
4. **Leverage Motion Deliberately**: Animation must serve the narrative: a page-load sequence, hover micro-interactions, or spatial transitions. Restraint is key—over-animating creates a chaotic AI feel.
5. **Anti-Generic Calibration (Avoid AI Clichés)**:
   - 🚫 Avoid generic warm cream (#F4F1EA) with serif + terracotta unless specifically requested.
   - 🚫 Avoid dark mode with a single neon acid-green/purple gradient.
   - 🚫 Avoid floating card stacks with heavy drop shadows that look like generic templates.
   - 🚫 Avoid emojis as UI icons—use clean SVG icons (Lucide/Heroicons).
   - 🚫 Avoid claustrophobic boxed containers trapping 3D models or media.

## Execution Workflow
- **Brainstorm & Critique**: Decouple the real subject matter and identify the single job of the interface.
- **Craft Layout Rhythm**: Establish hierarchy through dramatic scale contrast, intentional negative space, and architectural alignment.
- **Verify Accessibility & Interaction**: Enforce minimum 4.5:1 contrast ratio, visible focus rings, and natural 150-250ms interactive feedback.
