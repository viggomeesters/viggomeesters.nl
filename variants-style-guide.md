# Homepage Variants — Style Guide

Five unique creative directions for viggomeesters.nl. All share: dark base, per-project color system, same content/icons, responsive, production-ready.

---

## Variant 1: "Neon Arcade"

**Concept:** Retro gaming cabinet meets modern developer portfolio. CRT monitor vibes with scanline overlay, pixel-influenced borders, and neon glow effects. The page feels like you're selecting a game from an arcade menu.

**Typography:**
- Display: `Chakra Petch` — angular, techy, game UI feel
- Body: `Space Mono` — monospace with character

**Key Visual Elements:**
- Scanline overlay (repeating 2px lines at low opacity)
- Cards have a top "title bar" stripe in their project color
- Name rendered large and clean in white — no gradients, no shimmer
- Neon glow on hover (colored box-shadow pulses)
- Dotted grid background pattern instead of aurora
- CRT screen curvature subtle border-radius on main container
- Project tags styled as pixel-art badges

**Color Strategy:**
- Base: `#0a0a0f` (deeper black, almost CRT off-state)
- Cards: `#111116` with `1px` bright-colored top border
- Accents: Project colors at full saturation for borders/glows

**Hover Effect:**
- Neon flicker: box-shadow pulses between 0.3 and 0.6 opacity
- Slight CRT "static" shake (1px translate jitter)
- Card brightens as if screen is activating

**Layout:** Single column, full-width cards stacked vertically like a menu list. Each card is a horizontal bar with icon left, text center, tag right.

---

## Variant 2: "Scattered Studio"

**Concept:** Creative chaos. Cards appear as if scattered on a dark desk/cork board, slightly rotated at random angles. Picking one up (hover) straightens and lifts it. Feels human, tactile, anti-digital.

**Typography:**
- Display: `Caveat` — handwritten, personal, warm
- Body: `Nunito` — soft, rounded, friendly

**Key Visual Elements:**
- Cards rotated between -3deg and +3deg randomly via nth-child
- Paper/card stock texture on card backgrounds (subtle noise)
- Pin/pushpin accent dot in card corner (the project color)
- Masking tape strip across top of some cards (CSS pseudo-element)
- Name written large in handwriting font — natural, not AI
- No strict grid — cards overlap slightly with negative margins
- Polaroid-style avatar (white border, slight shadow, rotation)

**Color Strategy:**
- Base: `#0d0d10` with warm undertone
- Cards: `#18181d` with cream-ish tint (`#1c1c20`)
- Text slightly warmer than pure grey

**Hover Effect:**
- Card straightens (rotate to 0deg)
- Lifts dramatically (translateY -12px, scale 1.05)
- Deep shadow appears underneath (paper lifting off desk)
- Other cards slightly push away (CSS gap increase via sibling selectors)

**Layout:** 2-column masonry-feel grid but with rotated cards. Profile section is centered, large handwriting name.

---

## Variant 3: "Terminal"

**Concept:** The entire page is styled as a terminal session. Everything is monospace. Sections are "commands" with `$` prompts. Cards look like process listings. The developer identity shines through the aesthetic itself.

**Typography:**
- Display: `JetBrains Mono` — the developer's choice, bold weight
- Body: `JetBrains Mono` — everything monospace, lighter weight

**Key Visual Elements:**
- Terminal window chrome at top of page (three dots: red/yellow/green)
- Name typed out with blinking cursor animation
- Section headers prefixed with `$ ` command prompt
- Cards styled as terminal output blocks with colored left pipe `|`
- ASCII-art-style dividers (`----` or `====`)
- Tags rendered as `[LIVE]` and `[WIP]` in brackets
- Blinking cursor after the name
- Scrolling "boot sequence" animation on page load

**Color Strategy:**
- Base: `#0c0c0c` (pure dark terminal)
- Text: `#a0e8a0` (classic terminal green) for structure
- Project colors used for the pipe indicators and tags
- Amber `#ffb347` for prompts and commands

**Hover Effect:**
- Card background brightens slightly (like selecting a terminal line)
- Left pipe gets brighter, text gets full white
- Subtle scanline flicker

**Layout:** Single column, no grid. Everything stacked vertically like terminal output. Narrower max-width (560px) to feel like a terminal window.

---

## Variant 4: "Magazine Editorial"

**Concept:** High-end design magazine spread. Dramatic oversized serif typography for the name. Elegant negative space. Cards in an asymmetric editorial grid where featured projects get more space. Refined, sophisticated, but still bold with color.

**Typography:**
- Display: `Playfair Display` — high contrast, editorial elegance
- Body: `Libre Franklin` — clean grotesque complement

**Key Visual Elements:**
- Name in massive italic serif (3.5em+), taking up visual space
- Horizontal rule accents in project colors
- Cards in varied sizes: first 2 cards are large "feature" cards, rest smaller
- Generous whitespace/padding
- Pull-quote style tagline with oversized quotation marks
- Section labels in ultra-light weight, widely tracked
- Colored accent lines (not borders — actual decorative lines)

**Color Strategy:**
- Base: `#0b0b0e`
- Surface: `#131316` — barely there
- Accent: Project colors used sparingly as editorial accent lines
- Text hierarchy: bright white for name, warm grey for body

**Hover Effect:**
- Subtle and refined: colored underline slides in from left
- Card lifts minimally (2px), border-bottom color accent appears
- Icon receives a soft color halo

**Layout:** Asymmetric grid. Top 2 projects in large 1x2 cards, bottom 6 in 3x2 smaller grid. Generous 48px section spacing. Profile section with large italic name on its own line.

---

## Variant 5: "Bento Box"

**Concept:** Apple-style bento grid where everything is a tile, including the profile. Varying card sizes create visual rhythm. Bold, saturated color fills on hover. Playful spring animations. The grid IS the design — compact, modular, toy-like.

**Typography:**
- Display: `Sora` — geometric, modern, slightly playful
- Body: `Sora` — same family, lighter weight for cohesion

**Key Visual Elements:**
- Everything is a tile in one unified grid (profile, projects, links, contact)
- Profile tile spans full width, has colored gradient background
- Some project tiles are larger (2-column span) for visual variety
- Cards filled with more color: subtle gradient background using card-color
- Rounded corners cranked up (20px+)
- Bouncy spring transitions (cubic-bezier overshoot)
- Icon centered and large inside tile, text below
- No dividers — the grid gaps are the structure
- Contact form is also a tile in the grid

**Color Strategy:**
- Base: `#0e0e12`
- Tiles: each tile has a subtle wash of its project color (0.08 opacity bg)
- On hover: color fills to 0.20, creating a bold colored tile
- Bright white text on hover for contrast

**Hover Effect:**
- Bouncy scale (1.03 with overshoot easing)
- Background floods with card color (opacity 0.08 → 0.22)
- Icon scales up and gets color shadow
- Spring-physics feel via `cubic-bezier(0.34, 1.56, 0.64, 1)`

**Layout:** Unified CSS Grid. Profile = full width. Projects = mixed 1-col and 2-col spans. Links + Contact = grid tiles alongside projects. Everything is part of one flowing bento.
