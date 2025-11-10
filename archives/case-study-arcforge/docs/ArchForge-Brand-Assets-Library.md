# ArchForge Brand Asset Library
**Quick Reference & Implementation Resources**

Ready-to-copy code snippets, color swatches, and assets for immediate use.

---

## Quick Color Reference

### Copy-Paste Hex Codes

```
Primary Colors:
Forge Black:   #1A1A1A
Spark Orange:  #FF6B35
Vector Blue:   #4A90E2

Supporting:
Anvil Grey:    #6B6B6B
Ember Glow:    #FF8C5A
Steel White:   #F5F5F5
Pure White:    #FFFFFF
```

### CSS Variables (Ready to Use)

```css
/* Add to your :root or variables file */
:root {
  --forge-black: #1A1A1A;
  --spark-orange: #FF6B35;
  --vector-blue: #4A90E2;
  --anvil-grey: #6B6B6B;
  --ember-glow: #FF8C5A;
  --steel-white: #F5F5F5;
}

/* Usage example */
.hero {
  background-color: var(--forge-black);
  color: white;
}

.cta-button {
  background-color: var(--spark-orange);
}
```

### Figma/Adobe Color Swatches

**RGB Values:**
```
Forge Black:   RGB(26, 26, 26)
Spark Orange:  RGB(255, 107, 53)
Vector Blue:   RGB(74, 144, 226)
Anvil Grey:    RGB(107, 107, 107)
Ember Glow:    RGB(255, 140, 90)
Steel White:   RGB(245, 245, 245)
```

**CMYK Values (for print):**
```
Forge Black:   CMYK(75, 68, 67, 90)
Spark Orange:  CMYK(0, 58, 79, 0)
Vector Blue:   CMYK(67, 36, 0, 11)
Anvil Grey:    CMYK(0, 0, 0, 58)
```

---

## Typography Snippets

### Google Fonts Import (Copy to HTML head)

```html
<!-- Add to <head> -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&family=Raleway:wght@700;800&display=swap" rel="stylesheet">
```

### CSS Font Families

```css
/* Primary font for everything */
body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI',
               'Roboto', 'Helvetica Neue', Arial, sans-serif;
  font-size: 16px;
  line-height: 1.6;
  color: #1A1A1A;
}

/* Accent font for CTAs */
.cta-button,
.cta-text {
  font-family: 'Raleway', 'Inter', sans-serif;
  font-weight: 700;
}
```

### Pre-Made Text Styles

```css
/* Hero Headline */
.hero-title {
  font-family: 'Inter', sans-serif;
  font-weight: 700;
  font-size: 56px;
  line-height: 1.1;
  letter-spacing: -0.02em;
  color: #1A1A1A;
}

/* Section Header */
.section-title {
  font-family: 'Inter', sans-serif;
  font-weight: 700;
  font-size: 40px;
  line-height: 1.2;
  letter-spacing: -0.01em;
  color: #1A1A1A;
}

/* Body Text */
.body-text {
  font-family: 'Inter', sans-serif;
  font-weight: 400;
  font-size: 16px;
  line-height: 1.6;
  color: #6B6B6B;
}

/* Accent Text (Orange) */
.accent-text {
  color: #FF6B35;
  font-weight: 600;
}
```

---

## Ready-to-Use Components

### Primary CTA Button

**HTML:**
```html
<button class="btn-primary">
  Forge It Now
</button>
```

**CSS:**
```css
.btn-primary {
  /* Visual */
  background: linear-gradient(135deg, #FF6B35 0%, #FF8C5A 100%);
  color: #FFFFFF;
  border: none;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(255, 107, 53, 0.2);

  /* Typography */
  font-family: 'Raleway', 'Inter', sans-serif;
  font-weight: 700;
  font-size: 18px;
  text-transform: uppercase;
  letter-spacing: 0.08em;

  /* Spacing */
  padding: 16px 32px;

  /* Interaction */
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(255, 107, 53, 0.4);
}

.btn-primary:active {
  transform: translateY(0);
}

.btn-primary:focus {
  outline: 2px solid #FF6B35;
  outline-offset: 4px;
}
```

### Secondary Button

```html
<button class="btn-secondary">
  Learn More
</button>
```

```css
.btn-secondary {
  background: transparent;
  color: #1A1A1A;
  border: 2px solid #1A1A1A;
  border-radius: 4px;

  font-family: 'Inter', sans-serif;
  font-weight: 600;
  font-size: 16px;

  padding: 14px 30px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: #1A1A1A;
  color: #FFFFFF;
}
```

### Feature Card

```html
<div class="feature-card">
  <div class="feature-card__icon">
    <!-- Icon SVG here -->
  </div>
  <h3 class="feature-card__title">Automated Bookkeeping</h3>
  <p class="feature-card__description">
    AI handles Xero categorization, reporting, and compliance—
    saving you 40% on admin time.
  </p>
</div>
```

```css
.feature-card {
  background: #FFFFFF;
  border-radius: 8px;
  padding: 32px;
  box-shadow: 0 4px 16px rgba(26, 26, 26, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(26, 26, 26, 0.12);
}

.feature-card__icon {
  width: 48px;
  height: 48px;
  margin-bottom: 16px;
  color: #FF6B35;
}

.feature-card__title {
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  font-size: 24px;
  line-height: 1.3;
  margin-bottom: 12px;
  color: #1A1A1A;
}

.feature-card__description {
  font-family: 'Inter', sans-serif;
  font-weight: 400;
  font-size: 16px;
  line-height: 1.6;
  color: #6B6B6B;
}
```

### Input Field

```html
<div class="form-group">
  <label for="email" class="form-label">Email Address</label>
  <input
    type="email"
    id="email"
    class="form-input"
    placeholder="you@company.com.au"
  >
</div>
```

```css
.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  font-family: 'Inter', sans-serif;
  font-weight: 500;
  font-size: 14px;
  color: #1A1A1A;
  margin-bottom: 8px;
}

.form-input {
  width: 100%;
  padding: 16px;
  font-family: 'Inter', sans-serif;
  font-size: 16px;
  border: 2px solid #6B6B6B;
  border-radius: 4px;
  background: #FFFFFF;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.form-input:focus {
  border-color: #4A90E2;
  box-shadow: 0 0 0 4px rgba(74, 144, 226, 0.1);
  outline: none;
}

.form-input::placeholder {
  color: #6B6B6B;
  opacity: 0.6;
}
```

---

## Common Gradients

### Forge Glow (Orange gradient)

```css
/* Primary CTA gradient */
.forge-glow {
  background: linear-gradient(135deg, #FF6B35 0%, #FF8C5A 100%);
}
```

### Depth Field (Blue to black)

```css
/* Parallax background */
.depth-field {
  background: radial-gradient(circle at 50% 50%, #4A90E2 0%, #1A1A1A 100%);
}
```

### Black to Orange (Hero backgrounds)

```css
.hero-gradient {
  background: linear-gradient(135deg, #1A1A1A 0%, #FF6B35 100%);
}
```

---

## Spacing Utilities

### Margin & Padding Classes

```css
/* Spacing utilities (8px base unit) */
.m-0 { margin: 0; }
.m-1 { margin: 8px; }
.m-2 { margin: 16px; }
.m-3 { margin: 24px; }
.m-4 { margin: 32px; }
.m-6 { margin: 48px; }
.m-8 { margin: 64px; }

.p-0 { padding: 0; }
.p-1 { padding: 8px; }
.p-2 { padding: 16px; }
.p-3 { padding: 24px; }
.p-4 { padding: 32px; }
.p-6 { padding: 48px; }
.p-8 { padding: 64px; }

/* Top/Bottom specific */
.mt-3 { margin-top: 24px; }
.mb-3 { margin-bottom: 24px; }
.pt-3 { padding-top: 24px; }
.pb-3 { padding-bottom: 24px; }
```

---

## Layout Snippets

### Container (Max-width wrapper)

```css
.container {
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
  padding-left: 60px;
  padding-right: 60px;
}

@media (max-width: 768px) {
  .container {
    padding-left: 24px;
    padding-right: 24px;
  }
}
```

### Section Spacing

```css
.section {
  padding-top: 96px;
  padding-bottom: 96px;
}

.section--small {
  padding-top: 48px;
  padding-bottom: 48px;
}

@media (max-width: 768px) {
  .section {
    padding-top: 64px;
    padding-bottom: 64px;
  }
}
```

### Two-Column Grid

```html
<div class="grid-2col">
  <div>Column 1 content</div>
  <div>Column 2 content</div>
</div>
```

```css
.grid-2col {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 64px;
}

@media (max-width: 768px) {
  .grid-2col {
    grid-template-columns: 1fr;
    gap: 32px;
  }
}
```

### Three-Column Card Grid

```css
.grid-3col {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 32px;
}

@media (max-width: 992px) {
  .grid-3col {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 576px) {
  .grid-3col {
    grid-template-columns: 1fr;
  }
}
```

---

## Brand Voice Examples

### Headlines (Copy-Paste Ready)

```
Hero Headlines:
- "Forge Your Future"
- "AI That Builds Your Empire"
- "From Admin Chaos to Strategic Calm"
- "Australian SMBs, Meet Your AI Advantage"

Feature Headlines:
- "40% Faster Bookkeeping. Guaranteed."
- "Your Xero, Supercharged"
- "Private AI. Public Results."
- "Voice Commands, Instant Compliance"

CTA Text:
- "Forge It Now"
- "Start Your Free Audit"
- "Claim Your AI Advantage"
- "See the Magic"
```

### Body Copy Templates

```
Problem Statement:
"60% of Australian SMBs struggle with admin overload.
Time that could be spent growing your business is lost
to repetitive bookkeeping, compliance checks, and manual reporting."

Solution Statement:
"ArchForge builds private AI agents that handle the grunt work—
Xero automation, voice-integrated workflows, and compliance
monitoring—so you can focus on what matters: building your empire."

Value Proposition:
"Get 40% of your time back. Guaranteed. Our AI agents integrate
with your existing tools (Xero, Slack, email) and deliver results
in weeks, not months. No complex onboarding. No code required."

Guarantee:
"We guarantee double your time savings, or we refund 100% and
work for free until you see results. That's the ArchForge promise."
```

---

## Email Signature

```html
<!-- Copy to email client -->
<div style="font-family: 'Inter', Arial, sans-serif; font-size: 14px; color: #1A1A1A;">
  <strong style="font-size: 16px;">Samuel Rodda</strong><br>
  Founder, ArchForge.au<br>
  <span style="color: #6B6B6B;">AI-Powered Efficiency for Australian SMBs</span><br>
  <a href="mailto:your@email.com" style="color: #4A90E2;">your@email.com</a> |
  <a href="https://archforge.au" style="color: #FF6B35;">archforge.au</a><br>
  <span style="font-size: 12px; color: #6B6B6B;">ABN: [Your ABN]</span>
</div>
```

---

## LinkedIn Post Templates

### Format 1: Stat + Story

```
60% of AU SMBs are drowning in admin work.

I just helped Horizon Pro Dental get 12 hours/week back
with a simple AI agent that categorizes their Xero invoices.

No code. No complexity. Just results.

That's what happens when you forge AI to fit YOUR business—
not the other way around.

Want a free audit? 👇
[Link to archforge.au]

#AustralianBusiness #AIAutomation #SMB #Xero
```

### Format 2: Problem/Solution

```
"I don't have time to learn AI."

Heard this from 5 dental practices last week.

Here's the truth: You don't need to learn AI.
You need AI that learns YOUR business.

ArchForge builds private agents that plug into Xero,
understand your workflow, and just... work.

Setup: 4 weeks.
ROI: 40% time savings. Guaranteed.

Australian SMBs deserve tools that build empires, not headaches.

DM me "FORGE" for a free audit.

#SmallBusiness #Australia #Automation
```

---

## Social Media Specs

### Profile Images
- **Square:** 400x400px minimum (LinkedIn, Twitter, Facebook)
- **File format:** PNG with transparency
- **Content:** Logo mark only (no wordmark at small sizes)

### Cover Images
- **LinkedIn:** 1584x396px
- **Twitter:** 1500x500px
- **Facebook:** 820x312px
- **Content:** Brand gradient + tagline "AI That Builds Your Empire"

### Post Graphics
- **LinkedIn:** 1200x627px (link preview), 1080x1080px (image post)
- **Instagram:** 1080x1080px (square)
- **Template:** Orange accent frame + bold stat + logo

---

## File Naming Conventions

```
Logos:
- archforge-logo-primary.svg
- archforge-logo-monochrome.svg
- archforge-logo-icon-only.svg

Colors:
- archforge-colors-primary.png (swatch card)
- archforge-colors-palette.ase (Adobe swatch)

Marketing:
- archforge-linkedin-post-001.png
- archforge-hero-image.jpg
- archforge-cta-banner.svg
```

---

## Quick Start Checklist

For Week 1 launch, you need:

- [ ] Logo selected and exported (SVG + PNG)
- [ ] Brand colors saved in design tool (Figma/Canva)
- [ ] Fonts loaded (Inter + Raleway via Google Fonts)
- [ ] Primary button styled and tested
- [ ] Hero section with gradient background
- [ ] Feature cards (3x) with icons
- [ ] CTA form (email capture)
- [ ] LinkedIn profile updated with brand assets
- [ ] Email signature updated

---

**Next Steps:**
1. Choose your logo from the 4 concepts
2. Set up website framework (Framer/Webflow)
3. Copy-paste these assets into your site
4. Test on mobile + desktop
5. Launch! 🚀

**Asset Files Location:**
- Logo concepts: `/home/samuel/Documents/ArchForge-Logo-Concepts.pdf`
- Brand strategy: `/home/samuel/Documents/ArchForge-Brand-Strategy.md`
- Design system: `/home/samuel/Documents/ArchForge-Design-System.md`
- This library: `/home/samuel/Documents/ArchForge-Brand-Assets-Library.md`
