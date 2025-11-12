# ADR-002: Atomic Components + Page Layouts Strategy

**Status**: Accepted
**Date**: 2025-11-12
**Deciders**: Project Lead, Architecture Team
**Context**: DesignForge scope expansion from brand-only to full frontend design automation

---

## Context and Problem Statement

DesignForge is expanding from brand asset generation (logos, color palettes) to complete frontend design automation. We need to decide the granularity of design generation:

1. **Full Pages Only**: Generate complete landing pages, dashboards as single units
2. **Atomic Components Only**: Generate buttons, forms, cards in isolation
3. **Atomic Components + Page Layouts**: Generate both atomic components AND full page compositions

The decision impacts:
- Quality and consistency of generated designs
- Component reusability across projects
- Code export feasibility (HTML/CSS/framework components)
- Budget constraints ($30-60/month for image generation)
- Development timeline and agent allocation

## Decision Drivers

1. **User Requirements**: Need both logos (immediate priority v1.5) and full page layouts (v2.5)
2. **Design System Integrity**: Components must be consistent and reusable
3. **Code Export Viability**: Framework components (React, Vue) require atomic units
4. **Quality Control**: Smaller units easier to validate for accessibility and consistency
5. **Budget Efficiency**: Generate components once, compose into pages vs regenerating entire pages
6. **Iterative Refinement**: Easier to refine a button than an entire dashboard

## Considered Options

### Option 1: Full Pages Only
Generate complete page layouts (landing pages, dashboards) as single monolithic images.

**Pros**:
- Simpler generation workflow (fewer API calls)
- Holistic composition ensures visual harmony
- Faster initial delivery (no component assembly)

**Cons**:
- No component reusability (regenerate entire page for variations)
- Code export extremely difficult (reverse engineering from full page)
- Inconsistency across pages (buttons look different on each page)
- Accessibility validation harder (whole-page analysis vs component-level)
- Budget inefficiency (regenerating full pages vs reusing components)
- Limited iteration (can't refine just a button without regenerating page)

### Option 2: Atomic Components Only
Generate only atomic UI components (buttons, forms, cards, navigation) without full page layouts.

**Pros**:
- Maximum component reusability
- Easy code export (one component = one React/Vue component)
- Consistent design system (buttons always look the same)
- Efficient budget (generate 100 components, compose into infinite pages)
- Component-level quality validation (accessibility per component)

**Cons**:
- No complete page examples (users must compose manually)
- Composition quality uncertain (will components look good together?)
- Misses user need for full landing page designs
- No layout guidance (spacing, grid systems only inferred)

### Option 3: Atomic Components + Page Layouts (SELECTED)
Generate atomic components first, then compose them into full page layouts, validating composition quality.

**Pros**:
- **Best of both worlds**: Component reusability + complete page examples
- **Budget efficiency**: Generate 100 components, compose into 50+ page variations
- **Code export viability**: Components export to React/Vue, pages export to HTML/templates
- **Design system validation**: Pages validate component consistency (composition scoring)
- **Quality layering**: Component-level validation (accessibility) + page-level validation (composition)
- **User deliverables**: Logos (v1.5) → Components (v2.0) → Pages (v2.5) → Code (v3.0)
- **Iterative refinement**: Refine button once, improvements propagate to all pages
- **Framework support**: Matches React/Vue/Svelte mental model (components compose into pages)

**Cons**:
- More complex generation pipeline (2 stages: components, then layouts)
- Component composition logic needed (layout constraints, spacing rules)
- Longer timeline (v2.0 components + v2.5 layouts vs just v2.0 pages)

## Decision Outcome

**Chosen Option**: Option 3 - Atomic Components + Page Layouts

### Rationale

1. **Aligns with user requirements**: Delivers logos (v1.5), component libraries (v2.0), and full page layouts (v2.5)
2. **Enables code export (v3.0)**: Framework components require atomic units (Button.jsx, Card.vue)
3. **Budget efficiency**: Generate 100 components + 50 layouts < 500 full pages for same coverage
4. **Design system integrity**: Pages validate component consistency via composition scoring
5. **Industry best practice**: Mirrors design system methodology (atomic design by Brad Frost)

### Implementation Plan

**v2.0 Component Library Generation (Weeks 7-12)**:
- Epic #15: Generate atomic components (buttons, forms, cards, navigation)
- Epic #16: Component quality scoring (accessibility, visual hierarchy, consistency)
- Epic #17: Design token extraction (colors, spacing, typography from components)

**v2.5 Page Layout Generation (Weeks 13-18)**:
- Epic #18: Landing page generator (composing hero, features, CTA, footer from components)
- Epic #19: Marketing sections (pricing, testimonials, blog layouts)
- Epic #20: Dashboard layouts (web app screens with sidebar + content area)
- Epic #21: Responsive design validation (mobile-first, breakpoints, touch optimization)

**v3.0 Code Export (Weeks 19-24)**:
- Epic #22: HTML/CSS generation (semantic markup, responsive media queries)
- Epic #23: Framework exports (React, Vue, Svelte components from atomic units)
- Epic #24: CSS framework integration (Tailwind, CSS-in-JS, Sass)
- Epic #25: Production optimization (minification, bundle size, performance budgets)

### Quality Gates

**Component Level (v2.0)**:
- WCAG AA compliance: 90%+ components
- Consistency scoring: 85%+ similarity across component variations
- Design token adherence: 95%+ components use extracted tokens

**Page Level (v2.5)**:
- Component reuse validation: Pages use atomic components (not regenerating buttons per page)
- Composition scoring: 80%+ quality vs human judgment
- Responsive validation: 4 breakpoints (mobile, tablet, desktop, wide)

**Code Export Level (v3.0)**:
- Bundle size budgets: <100KB components, <500KB pages
- Accessibility: WCAG AA compliance in generated code
- Framework compatibility: Valid React/Vue/Svelte syntax with no errors

## Consequences

### Positive

- **Component reusability**: 100 components → 1000s of page variations via composition
- **Budget savings**: ~40% cost reduction vs full-page-only approach (fewer API calls)
- **Code export feasibility**: Atomic components map 1:1 to framework components
- **Design system validation**: Page composition validates component consistency
- **Iterative refinement**: Improve button once, all pages benefit
- **Framework alignment**: Matches React/Vue/Svelte component model

### Negative

- **Pipeline complexity**: 2-stage generation (components → layouts) vs 1-stage (full pages)
- **Composition logic needed**: Must define layout constraints, spacing rules for assembly
- **Longer timeline**: v2.0 (components) + v2.5 (layouts) = 12 weeks vs 6 weeks for pages-only
- **Validation overhead**: Component-level + page-level scoring (2x validation work)

### Neutral

- **Agent allocation shift**: More agents on code generation (Epic #22-25) vs fewer on initial image generation
- **Storage requirements**: 100 components + 50 layouts = 150 images vs 500 full pages (net savings)

## Related Decisions

- **ADR-001**: Model Knowledge Base architecture (static YAML for v1.0, scales to component library in v2.0)
- **Future ADR-003**: Component Composition Engine (defining layout constraints and assembly rules for v2.5)

## References

- Atomic Design Methodology by Brad Frost: https://atomicdesign.bradfrost.com/
- Design Systems by Alla Kholmatova: https://www.smashingmagazine.com/design-systems-book/
- React Component Patterns: https://reactpatterns.com/
- Tailwind CSS Component Libraries: https://tailwindui.com/

---

**Review Date**: 2025-12-12 (after v2.0 component library completion)
