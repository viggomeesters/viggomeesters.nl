# Design Manifest — viggomeesters.nl

This document is the single source of truth for all design decisions on this site.
Every change must be checked against these principles. If it conflicts, the change loses.

---

## Principles

1. **Practical first.** Every element must serve a clear purpose. If removing it changes nothing for the visitor, it shouldn't exist.
2. **Fast by default.** Single HTML file, no build step, minimal external dependencies. The page must load instantly on any connection. The only external resource is Google Fonts (Sora), loaded with `preconnect` + `display=swap` for non-blocking rendering. If Google Fonts is unavailable, `system-ui` takes over with zero layout shift.
3. **Consistent everywhere.** What works in Chrome must work in Safari, Firefox, and mobile browsers. No feature detection hacks, no progressive enhancement layers that create two-tier experiences.
4. **CSS does the work.** Visual effects live in CSS. JavaScript is reserved for things CSS genuinely cannot do (form submission). Decorative JS is not allowed.
5. **Quiet confidence.** The design communicates through color, typography, and spatial composition — not through motion tricks, particle effects, or interactive gimmicks. Bold but restrained.

---

## Architecture

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Format | Single `index.html` per page | Zero build complexity, instant deploy |
| CSS | Inline `<style>` block | One request, no FOUC |
| JS | Inline `<script>` block, bottom of body | Only for functional behavior |
| Hosting | Vercel via GitHub `main` branch | Auto-deploy on push |
| Subpages | Own `index.html` in subdirectory | Same architecture, shared visual language |

### File budget

The homepage HTML file should stay under **30 KB** uncompressed. If it grows past that, something unnecessary was added.

### Allowed JavaScript

JS is only permitted for one use case:

- **Form submission** — Formspree POST with loading/success/error states

That's it. No other JS is allowed on the homepage without updating this manifest first.

---

## Color System

### Base palette

Near-black neutrals with no color bias. The background should feel like a dark canvas, not a colored surface.

| Token | Hex | Usage |
|-------|-----|-------|
| `--bg` | `#0c0c0f` | Page background |
| `--bg-surface` | `#141418` | Card/tile background |
| `--bg-elevated` | `#1a1a20` | Hover states, raised surfaces |
| `--border` | `#2a2a32` | Active/hover borders |
| `--border-subtle` | `#1e1e26` | Default borders |
| `--text` | `#c8cbd5` | Body text |
| `--text-secondary` | `#8a90a6` | Tagline, descriptions |
| `--text-muted` | `#777c90` | Labels, meta text, placeholders (4.72:1 contrast on `--bg`) |

### Per-project signature colors

Each project has a unique accent color. These are applied via inline `style` attributes using CSS custom properties `--card-color` and `--card-soft`.

| Project | Color | Hex | Soft (10% opacity) |
|---------|-------|-----|---------------------|
| Minimal ETL Modeler | Electric blue | `#3b82f6` | `rgba(59,130,246,0.10)` |
| Money Shower | Vivid gold | `#eab308` | `rgba(234,179,8,0.10)` |
| Visual PM | Purple | `#a855f7` | `rgba(168,85,247,0.10)` |
| Kraamweek | Coral pink | `#f472b6` | `rgba(244,114,182,0.10)` |
| Dimma | Teal/cyan | `#06b6d4` | `rgba(6,182,212,0.10)` |
| Agent Brain | Emerald | `#22c55e` | `rgba(34,197,94,0.10)` |
| Raycast Life OS | Orange | `#f97316` | `rgba(249,115,22,0.10)` |
| Life OS Starter | Indigo/violet | `#818cf8` | `rgba(129,140,248,0.10)` |

**Rule:** Accent colors are only used for borders, icon tints, tag backgrounds, and glow on hover. Never for body text or large surface fills.

### Link tile colors

| Link | Color | Hex | Soft |
|------|-------|-----|------|
| GitHub | Light gray | `#e8eaf0` | `rgba(232,234,240,0.04)` |
| LinkedIn | Sky blue | `#38bdf8` | `rgba(56,189,248,0.05)` |

### Section dots

Label tiles use a colored dot (`7px`, with matching `box-shadow` glow):

| Section | Color | Hex |
|---------|-------|-----|
| Try me | Blue | `#3b82f6` |
| Systems | Green | `#22c55e` |
| Links | Green | `#22c55e` |
| Contact | Purple | `#a855f7` |

---

## Typography

| Property | Value |
|----------|-------|
| Font family | `'Sora', system-ui, -apple-system, sans-serif` |
| Loaded weights | 400, 500, 600, 700 |
| Base size | `14px` |
| Line height | `1.6` |
| Rendering | `-webkit-font-smoothing: antialiased` |

### Scale

| Element | Size | Weight | Color |
|---------|------|--------|-------|
| Name (h1) | `1.7em` (mobile: `1.4em`) | 700 | `#eeeff4` |
| Card name | `0.95em` | 600 | `#e0e1e8` |
| Tagline | `0.9em` | 400 | `--text-secondary` |
| Card description | `0.8em` | 400 | `--text-muted` |
| Labels | `0.7em` uppercase, `0.15em` tracking | 500 | `--text-muted` |
| Tags | `0.68em` | 600 | `--card-color` |
| Footer | `0.72em` | 400 | `--text-muted` |

**Rule:** The name uses tight letter-spacing (`-0.02em`). The McCoy company name in the tagline is gold (`#eab308`, weight 600).

---

## Layout

### Grid

Two-column bento grid (`grid-template-columns: 1fr 1fr`, `gap: 10px`). Single column below `640px`.

### Mobile breakpoint (`max-width: 640px`)

| Property | Desktop | Mobile |
|----------|---------|--------|
| Grid | 2 columns | 1 column |
| Page padding | `60px 16px` | `40px 12px` |
| Name (h1) | `1.7em` | `1.4em` |
| Avatar | `80px` | `64px` |
| Avatar ring inset | `-4px` / `-10px` | `-3px` / `-7px` |
| Profile tile | `gap: 20px`, `padding: 28px` | `gap: 14px`, `padding: 20px` |
| Form row | Horizontal (flex row) | Stacked (flex column) |

### Content width

`max-width: 640px`, centered with `margin: 0 auto` inside `<main class="page">`. Padding: `60px 16px`.

### Tile system

Every element in the grid is a `.tile`. Shared properties:

- `background: var(--bg-surface)`
- `border: 1px solid var(--border-subtle)`
- `border-radius: 20px`
- `padding: 24px`
- `overflow: hidden`

Tile variants:

| Variant | Span | Special |
|---------|------|---------|
| `.tile.profile` | Full width | Gradient background, flex row with avatar |
| `.tile.label` | Full width | Transparent, no border, section header |
| `.tile.card` (link) | Single column | Colored left border (3px), flex column |
| `.tile.link` | Single column | Colored left border (3px), flex row |
| `.tile.contact` | Full width | Contains Formspree form |
| `.tile.footer` | Full width | Transparent, centered text |

---

## Visual Effects (CSS-only)

### Aurora mesh

Two layers of overlapping radial gradients (`::before` and `::after` on `.aurora`), creating a subtle multi-color atmospheric background. Positioned `fixed`, behind all content (`z-index: 0`).

- Opacity range: `0.05–0.08` per gradient
- Colors used: blue, purple, gold, pink, cyan, green, orange (from the project palette)
- Static — no animation or drift. The gradients are fixed in place.
- **Rule:** Aurora is atmosphere, not decoration. It should be barely noticeable on first glance.

### Avatar ring

Conic gradient using all 8 project colors, applied as `::before` (solid, `0.55` opacity, `inset: -4px`) and `::after` (blurred glow, `0.12` opacity, `14px` blur, `inset: -10px`).

- **Rule:** Static only. No spinning, morphing, or animated effects on the avatar ring.

### Hover effects

All hover effects are guarded by `@media (hover: hover)` to prevent sticky states on touch devices. Touch devices get `:active { transform: scale(0.97) }` instead.

**Cards:**
- `transform: scale(1.03)`
- Background shifts to slightly brighter gradient
- `box-shadow` adds colored glow + depth shadow
- Border becomes `--card-color`
- Icon wrapper scales to `1.1` with colored glow
- Card name brightens to `#ffffff`

**Links:**
- `transform: scale(1.02)`
- Background fills with `--link-soft`
- Arrow shifts right `3px`
- Icon scales and increases opacity

**Contact button:**
- `translateY(-2px) scale(1.02)` with shadow

### Hover transition easing

All hover transitions use `cubic-bezier(0.34, 1.56, 0.64, 1)` (stored as `--bounce`). This creates a slight overshoot that gives cards a physical "spring" feel without visible animation.

### Form states

- **Success:** Form hides, green banner appears (`rgba(34,197,94,0.08)` background, `rgba(34,197,94,0.2)` border)
- **Loading:** Button text changes to "Sending...", button disabled
- **Error:** Button text changes to "Error — try again", button re-enabled
- **Spam prevention:** Hidden honeypot field (`_gotcha`) — bots fill it, Formspree rejects the submission

### Focus states

Form inputs on `:focus` get a purple ring: `border-color: rgba(168, 85, 247, 0.4)` with a dual glow `box-shadow` (purple + blue). This matches the contact section's purple dot accent.

### Reduced motion

`@media (prefers-reduced-motion: reduce)` sets all `transition-duration` to `0.01ms` and disables `smooth` scrolling. There are no CSS animations on the page — only transitions on hover/focus.

---

## Accessibility

### Semantic structure

The page uses `<main>` as its root landmark. Section labels ("Projects", "Links") are `<h2>` elements for proper heading hierarchy.

### Form labels

All form inputs have visually-hidden `<label>` elements (using `.sr-only`) with `for`/`id` associations. Screen readers announce field names; sighted users see placeholders.

### Color contrast

All text passes WCAG AA (4.5:1 minimum). Key ratios on `--bg` (`#0c0c0f`):

| Token | Hex | Ratio | Status |
|-------|-----|-------|--------|
| `--text` | `#c8cbd5` | 10.4:1 | AAA |
| `--text-secondary` | `#8a90a6` | 6.1:1 | AA |
| `--text-muted` | `#777c90` | 4.72:1 | AA |

**Rule:** `--text-muted` is the lowest-contrast text allowed. Nothing below 4.5:1 on `--bg`.

### Keyboard navigation

All interactive elements (cards, links, form inputs, button) are natively focusable (`<a>`, `<input>`, `<textarea>`, `<button>`). No custom `tabindex` overrides. Focus order follows DOM order.

---

## Iconography

All icons are **inline SVG**, sized `22x22` in a `44x44` container (`card-icon-wrap`) with `12px` border-radius and `--card-soft` background.

- Stroke icons: `stroke="currentColor"` with `stroke-width="2"`, round caps/joins
- Filled icons: `fill="currentColor"` (used for Kraamweek heart, Raycast arrow, Life OS gem)
- Color: `var(--card-color)` via `currentColor` inheritance

**Rule:** No external icon libraries, no emoji, no Unicode symbols. All icons are hand-crafted inline SVG under 500 bytes each.

---

## Meta & SEO

| Tag | Value |
|-----|-------|
| `title` | Viggo Meesters |
| `description` | SAP Data Management at McCoy. Tinkering with code on the side. |
| `theme-color` | `#0c0c0f` |
| `og:image` | `/og-image.png` (1200x630) |
| `og:url` | `https://viggomeesters.nl` |
| `twitter:card` | `summary_large_image` |
| Favicon | Inline SVG data URI — "VM" monogram with blue→purple→orange gradient |

---

## What We Don't Do

These are explicit prohibitions. They exist because they were tried and removed.

| Category | Prohibition | Why |
|----------|-------------|-----|
| **JS effects** | Cursor blobs, trails, particles, confetti | Gimmicky, inconsistent cross-browser, performance cost |
| **JS effects** | 3D tilt, parallax, gyroscope | Conflicts with CSS animations (`fill-mode: forwards` vs inline `transform`), buggy on edge cases |
| **JS effects** | Typewriter text, letter-by-letter animation | Delays content visibility, breaks accessibility |
| **JS effects** | Sound/audio on hover or click | Unexpected, intrusive, requires permission handling |
| **CSS effects** | Shimmer/holographic overlays | Looks AI-generated, adds visual noise |
| **CSS effects** | Morphing blob shapes on avatar | Distracting, fights with the clean ring aesthetic |
| **CSS effects** | Gradient text (purple shimmer, rainbow) | Screams "AI made this" |
| **API dependencies** | View Transitions API | Not supported in all browsers, conflicts with existing CSS animations |
| **API dependencies** | DeviceOrientationEvent | Requires permission prompt on iOS, unreliable |
| **API dependencies** | Web Audio API for UI sounds | Unexpected, blocked by autoplay policies |
| **Scroll-linked** | Scroll progress bar, scroll velocity effects | Adds visual clutter for no practical benefit |
| **Scroll-linked** | Spotlight/flashlight following cursor | Performance overhead, distracting |
| **CSS animation** | Grain/noise texture overlay | Invisible at usable opacity, unnecessary complexity |
| **CSS animation** | Aurora drift/movement | Nobody watches a background for 40 seconds |
| **CSS animation** | Card entrance animations (pop-in, stagger) | Delays content visibility for no benefit |
| **JS animation** | Scroll reveal / fade-in on scroll | Same — delays content, adds JS for a decorative effect |

**The test:** Before adding any visual feature, ask: "Would a visitor notice if I removed this?" If the answer is no, or if they'd only notice because something stopped being annoying, don't add it.

---

## Subpages

Subpages (`/agent-brain/`, `/raycast-life-os/`) follow the same visual language but are independent HTML files with their own content structure.

**Shared with homepage:**
- Same color tokens and Sora font
- Same tile/card styling patterns
- Same aurora background
- Same hover behavior and reduced-motion support

**Subpage-specific:**
- May use their own accent color as dominant (e.g., emerald for Agent Brain)
- May have different layout structures (e.g., stat grids, accordion sections)
- Same architecture rules: single HTML file, inline CSS/JS, no build tools

---

## Updating This Manifest

When a design change is proposed:

1. Check it against the principles (section 1)
2. Check it against the prohibitions (section "What We Don't Do")
3. If it passes both, implement it and update the relevant section here
4. If it conflicts, the manifest wins — update the manifest first if you have good reason to override
