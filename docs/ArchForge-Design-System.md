# ArchForge Design System
**Version 1.0 | Technical Specification**

Complete design system for consistent implementation across all ArchForge brand touchpoints.

---

## Table of Contents
1. [Color System](#color-system)
2. [Typography](#typography)
3. [Spacing & Grid](#spacing--grid)
4. [Components](#components)
5. [Iconography](#iconography)
6. [Motion & Animation](#motion--animation)
7. [Implementation Guidelines](#implementation-guidelines)

---

## Color System

### Primary Palette

#### Forge Black
```
Hex: #1A1A1A
RGB: 26, 26, 26
CMYK: 75, 68, 67, 90
Pantone: Black 6 C (closest)
```
**Usage:** Primary backgrounds (70%), logo base, headings, body text on light backgrounds
**Accessibility:** WCAG AAA on white (#FFFFFF) - 15.3:1 contrast ratio

#### Spark Orange
```
Hex: #FF6B35
RGB: 255, 107, 53
CMYK: 0, 58, 79, 0
Pantone: 171 C (closest)
```
**Usage:** CTAs (20%), accent elements, hover states, spark animations, urgency indicators
**Accessibility:** WCAG AA on white (#FFFFFF) - 3.52:1 contrast ratio (use for large text only)

#### Vector Blue
```
Hex: #4A90E2
RGB: 74, 144, 226
CMYK: 67, 36, 0, 11
Pantone: 2727 C (closest)
```
**Usage:** Data visualizations (10%), icons, AI/tech elements, secondary accents
**Accessibility:** WCAG AA on white (#FFFFFF) - 3.64:1 contrast ratio (use for large text only)

### Supporting Palette

#### Anvil Grey
```
Hex: #6B6B6B
RGB: 107, 107, 107
CMYK: 0, 0, 0, 58
```
**Usage:** Secondary text, captions, disabled states, subtle backgrounds
**Accessibility:** WCAG AA on white - 4.54:1 contrast ratio

#### Ember Glow
```
Hex: #FF8C5A
RGB: 255, 140, 90
CMYK: 0, 45, 65, 0
```
**Usage:** Orange tints in gradients, lighter hover states
**Accessibility:** WCAG AA on dark backgrounds only

#### Steel White
```
Hex: #F5F5F5
RGB: 245, 245, 245
CMYK: 0, 0, 0, 4
```
**Usage:** Light backgrounds, cards, alternating sections
**Accessibility:** Use with dark text only (Forge Black provides 13.7:1 contrast)

#### Pure White
```
Hex: #FFFFFF
RGB: 255, 255, 255
CMYK: 0, 0, 0, 0
```
**Usage:** Text on dark backgrounds, high-contrast elements

### Gradient Specifications

#### Forge Glow (Primary Gradient)
```css
background: linear-gradient(135deg, #1A1A1A 0%, #FF6B35 100%);
```
**Usage:** Hero sections, CTA button backgrounds, feature highlights

#### Depth Field (Parallax Gradient)
```css
background: radial-gradient(circle at 50% 50%, #4A90E2 0%, #1A1A1A 100%);
```
**Usage:** Parallax background layers, depth effects

#### Ember Fade (Subtle Accent)
```css
background: linear-gradient(90deg, rgba(255, 107, 53, 0) 0%, rgba(255, 107, 53, 0.2) 100%);
```
**Usage:** Hover overlays, section transitions

### Semantic Colors

#### Success States
```
Primary: #2ECC71 (Green)
Background: #E8F8F5
```

#### Warning States
```
Primary: #F39C12 (Amber)
Background: #FEF5E7
```

#### Error States
```
Primary: #E74C3C (Red)
Background: #FADBD8
```

#### Info States
```
Primary: #4A90E2 (Vector Blue)
Background: #EBF5FB
```

---

## Typography

### Font Stack

#### Primary Typeface: Inter
- **Source:** Google Fonts (https://fonts.google.com/specimen/Inter)
- **License:** Open Font License
- **Variable Font:** Supports weights 100-900

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&display=swap');

font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto',
             'Helvetica Neue', Arial, sans-serif;
```

#### Accent Typeface: Raleway (for CTAs)
- **Source:** Google Fonts (https://fonts.google.com/specimen/Raleway)
- **License:** Open Font License

```css
@import url('https://fonts.googleapis.com/css2?family=Raleway:wght@700;800&display=swap');

font-family: 'Raleway', 'Inter', sans-serif;
```

### Type Scale

Based on 16px base with 1.250 (Major Third) ratio for desktop, 1.200 (Minor Third) for mobile.

#### Desktop Scale (16px base)
```
H1: 56px / 3.5rem    | Inter Bold 700  | Line Height 1.1  | Letter Spacing -0.02em
H2: 40px / 2.5rem    | Inter Bold 700  | Line Height 1.2  | Letter Spacing -0.01em
H3: 32px / 2rem      | Inter SemiBold 600 | Line Height 1.3 | Letter Spacing 0
H4: 24px / 1.5rem    | Inter SemiBold 600 | Line Height 1.4 | Letter Spacing 0
H5: 20px / 1.25rem   | Inter Medium 500   | Line Height 1.5 | Letter Spacing 0
Body Large: 18px / 1.125rem | Inter Regular 400 | Line Height 1.6 | Letter Spacing 0
Body: 16px / 1rem    | Inter Regular 400 | Line Height 1.6 | Letter Spacing 0
Body Small: 14px / 0.875rem | Inter Regular 400 | Line Height 1.5 | Letter Spacing 0
Caption: 12px / 0.75rem | Inter Medium 500 | Line Height 1.4 | Letter Spacing 0.02em
```

#### Mobile Scale (16px base)
```
H1: 40px / 2.5rem    | Inter Bold 700
H2: 32px / 2rem      | Inter Bold 700
H3: 24px / 1.5rem    | Inter SemiBold 600
H4: 20px / 1.25rem   | Inter SemiBold 600
Body: 16px / 1rem    | Inter Regular 400
```

### Typography Usage Guidelines

#### Headings
- **H1:** Page titles only (one per page max)
- **H2:** Section headers
- **H3:** Subsection headers, feature titles
- **H4:** Card titles, component headers
- **H5:** Small component labels

#### Body Text
- **Body Large (18px):** Introductory paragraphs, key value propositions
- **Body (16px):** Standard paragraph text, list items
- **Body Small (14px):** Secondary information, metadata
- **Caption (12px):** Image captions, form helper text, footnotes

#### Special Effects

**Arched Text (Hero Headlines)**
```css
/* Apply to H1 hero elements */
.hero-title {
  font-size: 72px;
  font-weight: 700;
  letter-spacing: -0.02em;
}

/* SVG path for arch effect */
<textPath href="#archPath" startOffset="50%" text-anchor="middle">
  Forge Your Future
</textPath>
```

**CTA Text**
```css
.cta-text {
  font-family: 'Raleway', sans-serif;
  font-weight: 700;
  font-size: 18px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
```

---

## Spacing & Grid

### Spacing Scale

8px base unit system (rem-based for accessibility):

```
0.125rem = 2px   | Hairline dividers
0.25rem  = 4px   | Icon padding, micro-spacing
0.5rem   = 8px   | Tight element spacing
0.75rem  = 12px  | Default gap between related items
1rem     = 16px  | Standard vertical rhythm
1.5rem   = 24px  | Section spacing (small)
2rem     = 32px  | Component spacing
3rem     = 48px  | Section spacing (medium)
4rem     = 64px  | Section spacing (large)
6rem     = 96px  | Major section breaks
8rem     = 128px | Hero spacing
```

### Grid System

#### Desktop Grid (1200px max-width container)
```
Columns: 12
Gutter: 24px (1.5rem)
Margin: 60px (3.75rem) each side
```

#### Tablet Grid (768px - 1199px)
```
Columns: 8
Gutter: 16px (1rem)
Margin: 40px (2.5rem) each side
```

#### Mobile Grid (<768px)
```
Columns: 4
Gutter: 16px (1rem)
Margin: 24px (1.5rem) each side
```

### Breakpoints

```css
/* Mobile first approach */
$breakpoint-sm: 576px;   /* Small tablets */
$breakpoint-md: 768px;   /* Tablets */
$breakpoint-lg: 992px;   /* Small laptops */
$breakpoint-xl: 1200px;  /* Desktops */
$breakpoint-xxl: 1440px; /* Large desktops */
```

### Layout Patterns

#### Single-Page Scroll Layout
```
- Full viewport height sections
- 100vh minimum per major section
- Sticky navigation (60px height)
- Footer (auto height, min 200px)
```

#### Card Grid
```
Desktop: 3 columns (4rem gap)
Tablet: 2 columns (2rem gap)
Mobile: 1 column (1.5rem gap)
Card padding: 2rem
Card border-radius: 8px
```

---

## Components

### Buttons

#### Primary Button (CTA)
```css
.btn-primary {
  background: linear-gradient(135deg, #FF6B35 0%, #FF8C5A 100%);
  color: #FFFFFF;
  font-family: 'Raleway', sans-serif;
  font-weight: 700;
  font-size: 18px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 16px 32px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(255, 107, 53, 0.4);
  /* Add spark animation */
}

.btn-primary:active {
  transform: translateY(0);
}
```

#### Secondary Button
```css
.btn-secondary {
  background: transparent;
  color: #1A1A1A;
  border: 2px solid #1A1A1A;
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  font-size: 16px;
  padding: 14px 30px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: #1A1A1A;
  color: #FFFFFF;
}
```

#### Ghost Button (Minimal)
```css
.btn-ghost {
  background: transparent;
  color: #4A90E2;
  border: none;
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  font-size: 16px;
  padding: 12px 24px;
  cursor: pointer;
  text-decoration: underline;
  text-underline-offset: 4px;
  transition: color 0.2s ease;
}

.btn-ghost:hover {
  color: #FF6B35;
}
```

### Forms

#### Input Fields
```css
.input-field {
  width: 100%;
  padding: 16px;
  font-family: 'Inter', sans-serif;
  font-size: 16px;
  border: 2px solid #6B6B6B;
  border-radius: 4px;
  background: #FFFFFF;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.input-field:focus {
  border-color: #4A90E2;
  box-shadow: 0 0 0 4px rgba(74, 144, 226, 0.1);
  outline: none;
}

.input-field::placeholder {
  color: #6B6B6B;
  font-style: italic;
}
```

#### Natural Language Input (Special)
```css
.input-natural {
  width: 100%;
  min-height: 80px;
  padding: 20px;
  font-family: 'Inter', sans-serif;
  font-size: 18px;
  border: 2px solid #1A1A1A;
  border-radius: 8px;
  background: #F5F5F5;
  resize: vertical;
}

.input-natural::placeholder {
  color: #6B6B6B;
  content: "Tell us about your business...";
}
```

### Cards

#### Feature Card
```css
.card-feature {
  background: #FFFFFF;
  border-radius: 8px;
  padding: 32px;
  box-shadow: 0 4px 16px rgba(26, 26, 26, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card-feature:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(26, 26, 26, 0.12);
}

.card-feature__icon {
  width: 48px;
  height: 48px;
  margin-bottom: 16px;
}

.card-feature__title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #1A1A1A;
}

.card-feature__description {
  font-size: 16px;
  line-height: 1.6;
  color: #6B6B6B;
}
```

#### Offer Card (Pricing)
```css
.card-offer {
  background: #FFFFFF;
  border: 3px solid #F5F5F5;
  border-radius: 12px;
  padding: 40px;
  position: relative;
  transition: border-color 0.3s ease, transform 0.3s ease;
}

.card-offer--featured {
  border-color: #FF6B35;
  transform: scale(1.05);
}

.card-offer:hover {
  border-color: #4A90E2;
}

.card-offer__badge {
  position: absolute;
  top: -16px;
  left: 50%;
  transform: translateX(-50%);
  background: #FF6B35;
  color: #FFFFFF;
  padding: 6px 20px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}
```

### Navigation

#### Desktop Nav
```css
.nav-primary {
  position: sticky;
  top: 0;
  background: rgba(26, 26, 26, 0.95);
  backdrop-filter: blur(10px);
  height: 60px;
  padding: 0 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  z-index: 1000;
}

.nav-primary__logo {
  height: 36px;
}

.nav-primary__menu {
  display: flex;
  gap: 32px;
}

.nav-primary__link {
  color: #FFFFFF;
  font-size: 16px;
  font-weight: 500;
  text-decoration: none;
  transition: color 0.2s ease;
}

.nav-primary__link:hover {
  color: #FF6B35;
}
```

### Badges & Pills

#### Status Badge
```css
.badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.badge--new {
  background: #FF6B35;
  color: #FFFFFF;
}

.badge--popular {
  background: #4A90E2;
  color: #FFFFFF;
}
```

---

## Iconography

### Icon Style Guidelines

- **Style:** Line icons with 2px stroke weight
- **Size Grid:** 16px, 24px, 32px, 48px
- **Corner Radius:** 2px rounded corners
- **Motifs:** Tools (anvil, hammer, wrench) + Tech (nodes, circuits, vectors)

### Icon Set Requirements

#### Core Icons (Required)
```
- anvil (forge/build metaphor)
- spark (transformation/energy)
- network (AI/connections)
- dashboard (analytics/output)
- checkmark (success/completion)
- arrow-right (navigation/CTA)
- menu (mobile nav)
- close (dismiss)
```

#### Feature Icons
```
- automation (gears + AI)
- bookkeeping (ledger + robot)
- voice (waveform + chip)
- integration (puzzle pieces + nodes)
- security (shield + lock)
- analytics (chart + insights)
```

### Icon Color Usage

- **Default:** `#1A1A1A` (Forge Black)
- **Interactive:** `#4A90E2` (Vector Blue)
- **Accent:** `#FF6B35` (Spark Orange)
- **Disabled:** `#6B6B6B` (Anvil Grey) at 50% opacity

---

## Motion & Animation

### Animation Principles

1. **Purposeful:** Every animation serves a functional purpose
2. **Responsive:** Feels immediate (< 200ms for feedback)
3. **Natural:** Easing curves mimic real physics
4. **Subtle:** Never distracting from content

### Timing Functions

```css
/* Standard easing */
--ease-standard: cubic-bezier(0.4, 0.0, 0.2, 1);

/* Deceleration (element entering screen) */
--ease-decelerate: cubic-bezier(0.0, 0.0, 0.2, 1);

/* Acceleration (element leaving screen) */
--ease-accelerate: cubic-bezier(0.4, 0.0, 1, 1);

/* Sharp (quick transitions) */
--ease-sharp: cubic-bezier(0.4, 0.0, 0.6, 1);
```

### Duration Scale

```css
--duration-instant: 100ms;   /* Button feedback */
--duration-quick: 200ms;     /* Hover states */
--duration-standard: 300ms;  /* Default transitions */
--duration-slow: 500ms;      /* Page transitions */
--duration-deliberate: 800ms; /* Parallax effects */
```

### Signature Animations

#### Spark Particle Effect (CTA Hover)
```css
@keyframes spark-float {
  0% {
    transform: translate(0, 0) scale(1);
    opacity: 1;
  }
  100% {
    transform: translate(var(--spark-x), var(--spark-y)) scale(0);
    opacity: 0;
  }
}

.btn-primary:hover::before {
  content: '';
  position: absolute;
  width: 4px;
  height: 4px;
  background: #FFFFFF;
  border-radius: 50%;
  animation: spark-float 0.6s ease-out;
  /* Randomize --spark-x and --spark-y via JS */
}
```

#### Fade-In with Scale (Content Reveal)
```css
@keyframes reveal {
  from {
    opacity: 0;
    transform: translateY(24px) scale(0.96);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.reveal-on-scroll {
  animation: reveal 0.6s var(--ease-decelerate) forwards;
}
```

#### Parallax Layers (Hero Section)
```css
.parallax-layer {
  transform: translateZ(0); /* Hardware acceleration */
  transition: transform 0.8s var(--ease-standard);
}

/* Via JS: Apply different speeds to layers */
.parallax-layer--bg {
  transform: translateY(calc(var(--scroll) * -0.5px));
}

.parallax-layer--mid {
  transform: translateY(calc(var(--scroll) * -0.3px));
}

.parallax-layer--fg {
  transform: translateY(calc(var(--scroll) * -0.1px));
}
```

### Reduced Motion

Always respect user preferences:

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Implementation Guidelines

### CSS Custom Properties (Design Tokens)

```css
:root {
  /* Colors */
  --color-forge-black: #1A1A1A;
  --color-spark-orange: #FF6B35;
  --color-vector-blue: #4A90E2;
  --color-anvil-grey: #6B6B6B;
  --color-steel-white: #F5F5F5;
  --color-ember-glow: #FF8C5A;

  /* Typography */
  --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-accent: 'Raleway', 'Inter', sans-serif;

  /* Spacing */
  --space-xs: 0.5rem;   /* 8px */
  --space-sm: 1rem;     /* 16px */
  --space-md: 1.5rem;   /* 24px */
  --space-lg: 2rem;     /* 32px */
  --space-xl: 3rem;     /* 48px */
  --space-2xl: 4rem;    /* 64px */
  --space-3xl: 6rem;    /* 96px */

  /* Shadows */
  --shadow-sm: 0 2px 8px rgba(26, 26, 26, 0.08);
  --shadow-md: 0 4px 16px rgba(26, 26, 26, 0.12);
  --shadow-lg: 0 12px 32px rgba(26, 26, 26, 0.16);
  --shadow-glow-orange: 0 8px 24px rgba(255, 107, 53, 0.4);
  --shadow-glow-blue: 0 8px 24px rgba(74, 144, 226, 0.3);

  /* Border Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 9999px;

  /* Animation */
  --duration-quick: 200ms;
  --duration-standard: 300ms;
  --ease-standard: cubic-bezier(0.4, 0.0, 0.2, 1);
}
```

### Accessibility Checklist

- [ ] All text meets WCAG AA contrast ratios (4.5:1 for body, 3:1 for large text)
- [ ] Interactive elements have 44x44px minimum touch target (mobile)
- [ ] Focus states are clearly visible (2px outline, high contrast)
- [ ] Color is never the only indicator (use icons + text)
- [ ] Images have descriptive alt text
- [ ] Forms have proper labels and error messages
- [ ] Keyboard navigation works throughout
- [ ] Screen reader announcements for dynamic content
- [ ] Respects `prefers-reduced-motion`
- [ ] Semantic HTML5 elements used correctly

### Performance Optimization

#### Font Loading
```html
<!-- Preconnect to Google Fonts -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

<!-- Load fonts with display=swap -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Raleway:wght@700&display=swap" rel="stylesheet">
```

#### Image Optimization
- SVG for logos and icons (inline critical, lazy-load others)
- WebP with JPEG fallback for photos
- Responsive images with srcset
- Lazy loading for below-fold images

#### CSS Organization
```
styles/
├── 0-tokens/
│   └── variables.css       /* Design tokens */
├── 1-base/
│   ├── reset.css          /* Normalize/reset */
│   └── typography.css      /* Type scale */
├── 2-components/
│   ├── buttons.css
│   ├── forms.css
│   └── cards.css
├── 3-layouts/
│   ├── grid.css
│   └── sections.css
└── main.css               /* Import all */
```

### Framework Integration

#### Tailwind CSS Config
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        'forge-black': '#1A1A1A',
        'spark-orange': '#FF6B35',
        'vector-blue': '#4A90E2',
        'anvil-grey': '#6B6B6B',
        'steel-white': '#F5F5F5',
      },
      fontFamily: {
        'sans': ['Inter', 'sans-serif'],
        'display': ['Raleway', 'Inter', 'sans-serif'],
      },
      spacing: {
        '18': '4.5rem',  // 72px
        '22': '5.5rem',  // 88px
      }
    }
  }
}
```

---

## Version History

- **1.0 (Nov 2025):** Initial design system
- Future: Add dark mode variants, expanded icon set, component library

---

## Support & Questions

For design system questions or contribution guidelines, contact: [Your Email]

**Design System Ownership:** Samuel Rodda (ArchForge Founder)
**Review Cadence:** Monthly refinements based on implementation feedback
