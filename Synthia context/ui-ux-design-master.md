# UI/UX Design Master Skill

## skill_id
`ui-ux-design-master`

## display_name
UI/UX Design Master - End-to-End Product Design Partner

## Purpose

The **UI/UX Design Master** is Synthia's core design intelligence, serving as an autonomous product design partner that combines cognitive psychology (Don't Make Me Think), award-winning patterns (Awwwards/FWA), and the comprehensive UI/UX Pro Max knowledge base (50+ styles, 97 palettes, 57 font pairings).

This skill analyzes existing components, proposes flows and wireframes, generates UX specs, and ensures every design decision follows UDIP v2.1 ULTIMATE principles with WCAG 2.1 AA accessibility compliance.

**Target Audience:** Mexico City design seekers, quality-focused clients, international brands requiring world-class digital experiences.

**Core Competency:** Transform user needs into production-ready design systems that combine accessibility, performance, and Awwwards-level aesthetics.

## When to Use

Trigger this skill when:

- **Product design requests**: "Design a dashboard", "Create a landing page flow"
- **Component analysis**: "Review our design system", "Analyze component accessibility"
- **UX strategy**: "How should we structure this user journey?", "What's the best onboarding flow?"
- **Design system work**: "Generate design tokens", "Create component library"
- **Accessibility audits**: "Check WCAG compliance", "Fix contrast issues"
- **Performance optimization**: "Reduce CLS", "Optimize animation performance"
- **Awwwards trends**: "What are current design trends?", "How do winners do X?"
- **Mexico City market**: "Design for CDMX audience", "Latin American design preferences"

## Inputs

### Required
```typescript
{
  design_request: {
    type: "new_design" | "analysis" | "refactor" | "trend_research",
    description: string,  // Natural language description of what's needed
    target_audience?: string,  // Default: "Mexico City quality seekers"
    product_type?: string  // e.g., "SaaS dashboard", "E-commerce site", "Landing page"
  }
}
```

### Optional
```typescript
{
  constraints: {
    existing_design_system?: boolean,  // Use current tokens or create new
    awwwards_level_required?: boolean,  // Default: true
    accessibility_priority?: "WCAG_AA" | "WCAG_AAA",  // Default: WCAG_AA
    performance_budget?: {
      mobile_lighthouse?: number,  // Default: 90
      desktop_lighthouse?: number,  // Default: 95
      max_cls?: number,  // Default: 0.1
      max_fcp?: number  // Default: 1.5s
    },
    tech_stack?: string[],  // Default: Next.js 15, React 19, Tailwind, shadcn/ui
    style_preference?: string  // Reference to UI/UX Pro Max style (e.g., "glassmorphism dark")
  },
  context: {
    existing_components?: string[],  // List of available components
    design_system_path?: string,  // Path to design-system/MASTER.md
    page_override_path?: string,  // Path to design-system/pages/{page}.md
    competitor_references?: string[],  // URLs to analyze
    brand_guidelines?: string  // Path to brand docs
  }
}
```

### Examples

```json
// Example 1: New landing page
{
  "design_request": {
    "type": "new_design",
    "description": "Create a landing page for a Mexico City design studio showcasing our portfolio with smooth scroll animations",
    "target_audience": "International brands seeking Mexican design talent",
    "product_type": "Agency portfolio site"
  },
  "constraints": {
    "awwwards_level_required": true,
    "style_preference": "dark glassmorphism cinematic"
  }
}

// Example 2: Component analysis
{
  "design_request": {
    "type": "analysis",
    "description": "Audit our navigation component for accessibility and performance issues"
  },
  "context": {
    "existing_components": ["Navbar", "MobileMenu", "SearchBar"],
    "design_system_path": "design-system/MASTER.md"
  }
}

// Example 3: Trend research
{
  "design_request": {
    "type": "trend_research",
    "description": "Analyze current Awwwards winners for scroll animation patterns"
  }
}
```

## Outputs

### Standard Output Format
```typescript
{
  status: "draft" | "ready_for_review" | "approved",
  design_deliverables: {
    wireframes?: string,  // Structured text/component tree representation
    ux_specs?: {
      user_flows: string[],
      acceptance_criteria: string[],
      copy_guidelines: string[]
    },
    design_system_updates?: {
      new_tokens: Record<string, any>,
      new_components: ComponentSpec[],
      updated_components: ComponentSpec[]
    },
    accessibility_report?: {
      wcag_compliance: "AA" | "AAA",
      issues_found: AccessibilityIssue[],
      recommendations: string[]
    },
    performance_analysis?: {
      lighthouse_scores: { mobile: number, desktop: number },
      cls_score: number,
      optimization_suggestions: string[]
    },
    awwwards_alignment?: {
      magic_formula_check: MagicFormulaResult,
      winning_patterns_used: string[],
      anti_patterns_avoided: string[]
    }
  },
  implementation_ready: {
    component_code?: string,  // Production-ready React/Next.js code
    tailwind_config?: object,
    design_tokens?: object
  },
  next_actions: string[]
}
```

### Example Output

```json
{
  "status": "ready_for_review",
  "design_deliverables": {
    "wireframes": "Hero Section (full viewport)\n├─ Animated background (Three.js particles)\n├─ H1: Large kinetic typography (responds to cursor)\n├─ CTA: Primary button (Framer Motion hover)\n└─ Scroll indicator (Lenis smooth scroll)\n\nPortfolio Grid\n├─ Masonry layout (react-grid-layout)\n├─ Project cards (glass morphism bg-black/40)\n└─ Hover state: Scale 1.02 + opacity shift",
    "ux_specs": {
      "user_flows": [
        "1. Land on hero → Immediate visual impact (3D background animation)",
        "2. Scroll down → Smooth Lenis scroll reveals portfolio grid",
        "3. Hover project → Subtle scale + opacity change (NO layout shift)",
        "4. Click project → Full-screen modal with case study"
      ],
      "acceptance_criteria": [
        "Hero section must load and animate within 1.5s (FCP)",
        "All text contrast must meet 4.5:1 minimum (WCAG AA)",
        "Scroll animations must maintain 60fps",
        "Mobile version must not have horizontal scroll",
        "All interactive elements must have visible focus states"
      ],
      "copy_guidelines": [
        "Hero headline: 8-12 words, verb-driven, bilingual (ES/EN)",
        "Project titles: 2-5 words, descriptive",
        "CTA: Action verbs (\"Ver Portfolio\", \"Contactar\")"
      ]
    },
    "design_system_updates": {
      "new_tokens": {
        "colors": {
          "glass-dark": "rgba(0, 0, 0, 0.4)",
          "glass-light": "rgba(255, 255, 255, 0.8)",
          "accent-mexico": "#D63384"  // Mexican pink
        },
        "spacing": {
          "hero-padding": "clamp(2rem, 8vw, 8rem)"
        }
      },
      "new_components": ["HeroKinetic", "PortfolioGrid", "ProjectModal"]
    },
    "accessibility_report": {
      "wcag_compliance": "AA",
      "issues_found": [],
      "recommendations": [
        "Add aria-label to portfolio filter buttons",
        "Ensure skip-to-content link for keyboard users",
        "Test with screen reader (NVDA/VoiceOver)"
      ]
    },
    "performance_analysis": {
      "lighthouse_scores": { "mobile": 92, "desktop": 96 },
      "cls_score": 0.08,
      "optimization_suggestions": [
        "Lazy load portfolio images below fold",
        "Use WebP format with srcset",
        "Preload hero background video"
      ]
    },
    "awwwards_alignment": {
      "magic_formula_check": {
        "cinematic": true,
        "scroll": true,
        "parallax": true,
        "bold": true,
        "oversized": true,
        "interactive": true,
        "smooth": true
      },
      "winning_patterns_used": [
        "Full-viewport hero with 3D background",
        "Kinetic typography (cursor-responsive)",
        "Glass morphism cards",
        "Smooth scroll storytelling",
        "Micro-interactions (150-300ms)"
      ],
      "anti_patterns_avoided": [
        "No emoji icons",
        "No layout shift on hover",
        "No slow animations (all <500ms)",
        "No auto-playing audio"
      ]
    }
  },
  "implementation_ready": {
    "component_code": "[Full React component code would be here]",
    "tailwind_config": {
      "extend": {
        "colors": {
          "glass-dark": "rgba(0, 0, 0, 0.4)"
        }
      }
    }
  },
  "next_actions": [
    "Review wireframes and UX specs",
    "Approve design system token updates",
    "Proceed to web-artifacts-builder-plus for implementation",
    "Run accessibility tests in NVDA/VoiceOver"
  ]
}
```

## Tools & Integrations

### Core Tools

**UI/UX Pro Max Knowledge Base:**
```bash
# Mandatory workflow before any design generation
python3 skills/ui-ux-pro-max/scripts/search.py "<query>" --design-system -p "Synthia" --page "landing"

# Domain-specific searches
python3 skills/ui-ux-pro-max/scripts/search.py "dark glassmorphism" --domain style
python3 skills/ui-ux-pro-max/scripts/search.py "luxury elegant" --domain typography
python3 skills/ui-ux-pro-max/scripts/search.py "smooth animations" --domain ux

# Stack selection
--stack nextjs  # or: html-tailwind, react, vue, svelte, shadcn
```

**Awwwards Trend Analysis:**
- Daily scraping of awwwards.com winners
- Pattern extraction via Agent Lightning
- Trend reports in `./agent-lightning/reports/`

**Design System Hierarchy:**
```bash
# ALWAYS check before designing:
1. Read design-system/MASTER.md (base tokens and guidelines)
2. Read design-system/pages/{current-page}.md (page-specific overrides)
3. Page overrides take precedence over MASTER

# Example:
cat design-system/MASTER.md  # Get base colors, typography, spacing
cat design-system/pages/landing.md  # Get landing-specific hero styles
```

**Component Analysis Tools:**
- `bash_tool` for code analysis
- `view` tool for design system inspection
- `str_replace` for token updates

**Accessibility Validation:**
- Automated contrast checking (WebAIM API)
- Lighthouse CI in Docker pipeline
- ARIA attribute validation

**Performance Monitoring:**
- Chrome DevTools Performance API
- CLS tracking in production
- Framer Motion performance profiler

### Integration Points

**MCP Servers:**
- **Puppeteer MCP**: Visual regression testing, screenshot validation
- **GitHub MCP**: Design system updates via PR
- **Filesystem MCP**: Direct design-system/ updates

**External Services:**
- **Figma API**: Import design files (OAuth flow)
- **Awwwards API**: Trend data scraping
- **WebAIM**: Contrast validation
- **PageSpeed Insights**: Performance scoring

**Agent Coordination:**
```bash
# Check for design-related messages
resource://inbox/UIUXDesignMaster?project=$(pwd)

# Reserve design system files
file_reservation_paths --agent_name="UIUXDesignMaster" \
  --paths='["design-system/**", "components/**/*.tsx"]' \
  --exclusive=true
```

## Project-Specific Guidelines

### Mexico City Market Specialization

**Cultural Design Considerations:**
- **Color Palettes**: Vibrant yet sophisticated (inspired by Mexican art traditions)
- **Typography**: Bold, confident, bilingual ES/EN support required
- **Imagery**: High-quality, locally relevant, diverse representation
- **Tone**: Professional but warm, less corporate than US market
- **Trust Signals**: Portfolio, testimonials, local case studies prominent

**Technical Context:**
- **Internet Infrastructure**: Optimize for variable speeds (CDMX has good connectivity but assume 3G)
- **Device Mix**: Mobile-first (60%+ traffic), iOS and Android balanced
- **Payment Preferences**: Local payment methods (OXXO, SPEI) alongside cards
- **Language**: Spanish primary, English secondary for international appeal

### Synthia-Specific Design System

**Base Architecture (from OpenKombai fork):**
- Next.js 15 + App Router
- React 19 with Server Components
- Tailwind CSS 3 with custom configuration
- shadcn/ui (Radix primitives)

**Animation Stack:**
- Framer Motion (React components)
- GSAP (complex timelines)
- React Spring (physics-based)
- Lenis (smooth scroll)

**3D Integration:**
- Three.js + React Three Fiber
- @react-three/drei for helpers
- Spline embeds for no-code 3D

**Icon System:**
- Lucide React (primary)
- Heroicons (alternative)
- Simple Icons (brand logos ONLY)
- **NEVER emoji**

### Design Token Architecture

```typescript
// design-system/MASTER.md structure
export const designTokens = {
  colors: {
    // Light mode
    light: {
      text: "#0F172A",  // slate-900, contrast 16:1
      background: "#FFFFFF",
      glass: "rgba(255, 255, 255, 0.8)",  // Min 80% opacity
      border: "rgba(15, 23, 42, 0.1)"
    },
    // Dark mode
    dark: {
      text: "#F8FAFC",  // slate-50, contrast 16:1
      background: "#0F172A",
      glass: "rgba(0, 0, 0, 0.4)",  // Min 40% opacity
      border: "rgba(248, 250, 252, 0.1)"
    },
    // Accent (México-inspired)
    accent: {
      primary: "#D63384",  // Mexican pink
      secondary: "#8B4513",  // Terracotta
      tertiary: "#006847"  // Verde México
    }
  },
  typography: {
    // Scale: 1.25 (Major Third)
    scale: [12, 15, 19, 24, 30, 38, 48, 60, 75],
    families: {
      heading: "var(--font-geist-sans)",
      body: "var(--font-geist-sans)",
      mono: "var(--font-geist-mono)"
    },
    weights: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700
    }
  },
  spacing: {
    // Tailwind defaults + custom
    hero: "clamp(4rem, 12vw, 16rem)"
  },
  layout: {
    maxWidth: "1280px",  // max-w-6xl
    containerPadding: "clamp(1rem, 5vw, 3rem)",
    navbarOffset: "1rem"  // top-4 (floating navbar)
  },
  animation: {
    duration: {
      fast: "150ms",
      normal: "300ms",
      slow: "500ms"
    },
    easing: {
      default: "cubic-bezier(0.4, 0, 0.2, 1)",
      spring: "cubic-bezier(0.68, -0.55, 0.265, 1.55)"
    }
  },
  zIndex: {
    navbar: 50,
    modal: 100,
    tooltip: 200,
    notification: 300
  }
};
```

### Quality Enforcement

**Pre-Delivery Checklist (MANDATORY):**

Every design must pass before delivery:

✅ **Awwwards Magic Formula** (all 7 elements present)
✅ **Accessibility** (WCAG 2.1 AA minimum, AAA preferred)
✅ **Performance** (Lighthouse >90/95, CLS <0.1, 60fps animations)
✅ **Responsiveness** (tested at 375px, 768px, 1024px, 1440px)
✅ **Light/Dark Mode** (both tested, contrast verified)
✅ **Icons** (SVG only, no emoji anywhere)
✅ **Interactions** (cursor-pointer, focus states, hover feedback)
✅ **Layout** (no shift on hover, floating navbar, consistent max-width)
✅ **Typography** (scale consistency, readability, bilingual support)
✅ **Brand Alignment** (matches Synthia design system)

**Violations Result in Rejection:**
- Emoji icons anywhere in design
- Poor contrast (<4.5:1 for normal text, <3:1 for large text)
- Layout shift on hover (CLS >0.1)
- Missing focus states
- Slow animations (>500ms)
- Horizontal scroll on mobile
- Missing alt text on images
- Icon-only buttons without aria-label

## Example Interactions

### Example 1: New Landing Page Design

**User Request:**
> "Design a landing page for Synthia showing our design portfolio. Make it Awwwards-level with smooth animations. Target audience is international brands looking for Mexican design talent."

**Skill Execution:**

```bash
# 1. Memory-first scan
project_knowledge_search "Synthia landing page design portfolio"
conversation_search "previous design decisions"

# 2. Check design system
cat design-system/MASTER.md
cat design-system/pages/landing.md  # If exists

# 3. Query UI/UX Pro Max
python3 skills/ui-ux-pro-max/scripts/search.py \
  "portfolio agency dark glassmorphism international" \
  --design-system -p "Synthia" --page "landing" \
  --stack nextjs

# 4. Analyze Awwwards trends
cat agent-lightning/reports/$(date +%Y-%m-%d)-awwwards-trends.md

# 5. Generate design
```

**Output:**

```markdown
# Landing Page Design - Synthia Portfolio

## Wireframe Structure

### Hero Section (100vh)
```
┌─────────────────────────────────────┐
│  [Floating Nav] top-4 left-4 right-4│
│                                     │
│    ⚡ Synthia                       │
│                                     │
│    [3D Particle Background]        │
│                                     │
│    We design                        │
│    world-class                      │
│    digital                          │
│    experiences                      │
│                                     │
│    From Mexico City                 │
│    to the world                     │
│                                     │
│    [Ver Portfolio CTA]              │
│    ↓ Scroll indicator              │
└─────────────────────────────────────┘
```

### Portfolio Grid (Scroll-triggered)
```
┌─────────────────────────────────────┐
│  Selected Work                      │
│                                     │
│  ┌───────┐  ┌───────┐  ┌───────┐  │
│  │ Proj1 │  │ Proj2 │  │ Proj3 │  │
│  │[Glass]│  │[Glass]│  │[Glass]│  │
│  └───────┘  └───────┘  └───────┘  │
│  ┌───────┐  ┌───────┐              │
│  │ Proj4 │  │ Proj5 │              │
│  └───────┘  └───────┘              │
└─────────────────────────────────────┘
```

## UX Specifications

**User Flow:**
1. **First 3 seconds**: Hero with animated 3D background loads, typography fades in
2. **Scroll engagement**: Lenis smooth scroll reveals portfolio grid with parallax
3. **Project exploration**: Hover shows project preview, click opens full case study
4. **CTA conversion**: Bottom CTA for contact, sticky floating button for quick access

**Acceptance Criteria:**
- Hero FCP < 1.5s
- All scroll animations 60fps (verified in Performance tab)
- Each project card has glass bg-black/40 in dark mode, bg-white/80 in light
- Bilingual: Spanish primary, English toggle
- Mobile: Single column grid, touch-friendly cards (min 44x44px)

## Design Tokens (New)

```json
{
  "colors": {
    "hero-gradient": "linear-gradient(135deg, #D63384 0%, #006847 100%)",
    "glass-dark": "rgba(0, 0, 0, 0.4)",
    "glass-light": "rgba(255, 255, 255, 0.85)"
  },
  "typography": {
    "hero-size": "clamp(3rem, 8vw, 6rem)",
    "hero-weight": 700,
    "hero-line-height": 1.1
  }
}
```

## Accessibility Check: ✅ WCAG AA

- All text contrast >4.5:1 (verified against gradient background)
- Alt text: "Synthia logo", "Project: [Name] - [Description]"
- Keyboard nav: Tab through projects, Enter to open
- Screen reader: aria-label on all icon buttons
- Focus states: ring-2 ring-primary on all interactive elements

## Performance Budget: ✅ Met

- Lighthouse Mobile: 92
- Lighthouse Desktop: 96
- CLS: 0.06
- FCP: 1.3s
- 60fps animations (transform/opacity only)

## Awwwards Formula: ✅ All 7 Elements

✅ Cinematic: 3D particle background (Three.js)
✅ Scroll: Lenis smooth scroll + parallax
✅ Parallax: Background moves slower than foreground
✅ Bold: Hero typography 6rem, 700 weight
✅ Oversized: Full-viewport hero, large project cards
✅ Interactive: Hover states on projects, kinetic typography
✅ Smooth: All animations 150-300ms, 60fps

**Next Actions:**
1. Approve wireframes and tokens
2. Generate production code via `web-artifacts-builder-plus`
3. Deploy to staging for user testing
```

### Example 2: Component Accessibility Audit

**User Request:**
> "Audit our navigation component for accessibility issues"

**Skill Execution:**

```bash
# 1. Locate component
view components/Navbar.tsx

# 2. Check design system
cat design-system/MASTER.md

# 3. Run automated checks
```

**Output:**

```markdown
# Navbar Component - Accessibility Audit

## Current Implementation Analysis

**File**: `components/Navbar.tsx`

### Issues Found: 3 Critical, 2 Warnings

#### 🚨 CRITICAL ISSUES

1. **Missing ARIA Labels on Icon Buttons**
   ```tsx
   // CURRENT (BAD)
   <button onClick={toggleMenu}>
     <MenuIcon className="w-6 h-6" />
   </button>
   
   // FIX
   <button onClick={toggleMenu} aria-label="Toggle navigation menu">
     <MenuIcon className="w-6 h-6" />
   </button>
   ```

2. **No Focus Visible State**
   ```tsx
   // CURRENT (BAD)
   <Link href="/portfolio" className="hover:text-accent">
   
   // FIX
   <Link href="/portfolio" 
     className="hover:text-accent focus:outline-none focus:ring-2 focus:ring-primary">
   ```

3. **Poor Color Contrast in Dark Mode**
   - Current: #666666 on #0F172A = 2.8:1 ❌
   - Required: 4.5:1 minimum for WCAG AA
   - Fix: Use #94A3B8 (slate-400) = 5.2:1 ✅

#### ⚠️ WARNINGS

1. **Mobile Menu Not Keyboard Accessible**
   - Current: Click-only toggle
   - Recommendation: Add keyboard event handlers (Enter, Space, Escape)

2. **No Skip to Content Link**
   - Recommendation: Add skip link for screen reader users

## Recommended Fixes

```tsx
// components/Navbar.tsx - FIXED VERSION
export function Navbar() {
  return (
    <>
      {/* Skip to content link */}
      <a 
        href="#main-content" 
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4"
      >
        Skip to main content
      </a>

      <nav 
        className="fixed top-4 left-4 right-4 z-50"
        aria-label="Main navigation"
      >
        {/* Logo */}
        <Link href="/" aria-label="Synthia home">
          <Logo />
        </Link>

        {/* Desktop Nav Links */}
        <div className="hidden md:flex gap-8">
          {navLinks.map(link => (
            <Link
              key={link.href}
              href={link.href}
              className="hover:text-accent focus:outline-none focus:ring-2 focus:ring-primary rounded px-2 py-1"
            >
              {link.label}
            </Link>
          ))}
        </div>

        {/* Mobile Menu Toggle */}
        <button
          onClick={toggleMenu}
          aria-label="Toggle navigation menu"
          aria-expanded={isMenuOpen}
          className="md:hidden focus:outline-none focus:ring-2 focus:ring-primary rounded p-2"
        >
          <MenuIcon className="w-6 h-6" />
        </button>
      </nav>

      {/* Mobile Menu */}
      {isMenuOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/80"
          role="dialog"
          aria-modal="true"
        >
          {/* Menu items */}
        </div>
      )}
    </>
  );
}
```

## Accessibility Checklist: After Fixes

✅ All icon buttons have aria-label
✅ All interactive elements have visible focus states
✅ Color contrast meets WCAG AA (4.5:1 minimum)
✅ Keyboard navigation works (Tab, Enter, Escape)
✅ Skip to content link present
✅ Semantic HTML (nav, button, a tags)
✅ ARIA roles and properties correct

## Performance Impact: Minimal

- Focus ring adds ~0.1KB gzipped
- No runtime performance change
- Improves keyboard navigation speed

**Next Actions:**
1. Apply recommended fixes
2. Test with screen reader (NVDA/VoiceOver)
3. Test keyboard-only navigation
4. Re-run Lighthouse accessibility audit
```

### Example 3: Awwwards Trend Research

**User Request:**
> "What are the current trends in scroll animations on Awwwards winners?"

**Skill Execution:**

```bash
# 1. Check latest learning report
cat agent-lightning/reports/$(date +%Y-%m-%d)-awwwards-trends.md

# 2. Query UI/UX Pro Max
python3 skills/ui-ux-pro-max/scripts/search.py \
  "scroll animations parallax" --domain ux

# 3. Synthesize findings
```

**Output:**

```markdown
# Awwwards Scroll Animation Trends - February 2026

## Top 5 Winning Patterns

### 1. **Horizontal Scroll Sections** (40% of winners)

**What:** Sections scroll horizontally while page scrolls vertically

**Implementation:**
- GSAP ScrollTrigger with horizontal: true
- Locomotive Scroll with data-scroll-direction="horizontal"
- Framer Motion with useScroll + useTransform

**Example Sites:**
- [Design Studio X] - Portfolio grid scrolls horizontally
- [Brand Y] - Timeline moves sideways on vertical scroll

**Code Pattern:**
```tsx
import { useScroll, useTransform } from "framer-motion";

const { scrollYProgress } = useScroll({
  target: sectionRef,
  offset: ["start end", "end start"]
});

const x = useTransform(scrollYProgress, [0, 1], ["0%", "-100%"]);

<motion.div style={{ x }}>
  {/* Horizontal content */}
</motion.div>
```

### 2. **Layered Parallax Depth** (35% of winners)

**What:** Multiple layers moving at different speeds creating depth

**Implementation:**
- 3-5 layers (background slowest, foreground fastest)
- Speed ratios: 0.3x, 0.6x, 1x, 1.3x, 1.6x
- Lenis smooth scroll for butter-smooth feel

**Code Pattern:**
```tsx
<div className="relative h-[300vh]">
  <div className="sticky top-0">
    <motion.div style={{ y: useParallax(0.3) }}>Background</motion.div>
    <motion.div style={{ y: useParallax(0.6) }}>Midground</motion.div>
    <motion.div style={{ y: useParallax(1.0) }}>Foreground</motion.div>
  </div>
</div>
```

### 3. **Scroll-Controlled Video** (30% of winners)

**What:** Video playback synced to scroll position

**Implementation:**
- Canvas-based frame rendering
- Pre-loaded image sequence
- GSAP ScrollTrigger scrub: true

**Use Cases:**
- Product reveals (Apple-style)
- Storytelling sequences
- 3D object rotation

### 4. **Text Reveal Animations** (45% of winners)

**What:** Text appears with sophisticated animations as you scroll

**Variations:**
- Line-by-line fade + slide
- Character-by-character typewriter
- Split text with stagger

**Libraries:**
- react-split-text
- GSAP SplitText
- Framer Motion with custom hooks

### 5. **Scroll-Triggered WebGL** (25% of winners)

**What:** 3D graphics that respond to scroll position

**Tech Stack:**
- Three.js + React Three Fiber
- @react-three/drei useScroll hook
- Shader-based effects

**Performance Notes:**
- Requires GPU optimization
- Mobile: simplified version or fallback
- Use Intersection Observer to load only when visible

## Anti-Trends (What Winners Avoid)

❌ jQuery-based scroll plugins (outdated)
❌ Scroll hijacking (prevents browser back button)
❌ Excessive scroll distance (>500vh)
❌ Scroll animations on mobile (poor performance)
❌ Auto-scroll sections (user loses control)

## Implementation Recommendations for Synthia

**Priority 1 - Implement Now:**
- Layered parallax (easy, high impact)
- Text reveal animations (moderate effort, very impressive)

**Priority 2 - Upcoming Projects:**
- Horizontal scroll sections (for portfolio showcase)
- Scroll-controlled video (for case study storytelling)

**Priority 3 - Advanced / Experimental:**
- WebGL integration (requires performance optimization)

**Performance Budget:**
- Max scroll distance: 300vh per section
- 60fps target on modern devices
- Mobile: reduce/remove complex scroll effects

**Next Actions:**
1. Create scroll animation component library
2. Add patterns to web-artifacts-builder-plus
3. Test on low-end devices (60fps requirement)
```

---

## Maintenance & Updates

**Daily Learning:**
- Awwwards scraping automated via Agent Lightning
- New patterns added to UI/UX Pro Max knowledge base
- Trend reports generated automatically

**Monthly Reviews:**
- Accessibility standards updates (WCAG revisions)
- Performance budget adjustments (Web Vitals changes)
- Design system token refinements
- Mexico City market preference updates

**Continuous Improvement:**
- User feedback integrated into acceptance criteria
- Component library expanded based on usage patterns
- Design system evolved with brand maturity

---

**UI/UX Design Master v1.0**  
**Synthia Cloud Skills**  
**Last Updated:** 2026-02-07  
**Status:** ✅ PRODUCTION READY
