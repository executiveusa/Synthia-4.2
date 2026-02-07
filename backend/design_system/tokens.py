"""
Synthia 4.2 - Design Token Architecture

Canonical design tokens for all Synthia skills and outputs.
Based on UI/UX Design Master spec with Mexico City market specialization.

Token hierarchy:
  design-system/MASTER.md  →  base tokens (this file, programmatic)
  design-system/pages/{page}.md  →  page-specific overrides
"""

from typing import Any, Optional


# ═══════════════════════════════════════════════════════════════
# DESIGN TOKENS - Single source of truth
# ═══════════════════════════════════════════════════════════════

DESIGN_TOKENS: dict[str, Any] = {
    # ─── Colors ───────────────────────────────────────────────
    "colors": {
        "light": {
            "text": "#0F172A",          # slate-900, contrast 16:1
            "text_muted": "#64748B",    # slate-500
            "background": "#FFFFFF",
            "surface": "#F8FAFC",       # slate-50
            "glass": "rgba(255, 255, 255, 0.8)",  # min 80% opacity
            "border": "rgba(15, 23, 42, 0.1)",
            "border_strong": "rgba(15, 23, 42, 0.2)",
        },
        "dark": {
            "text": "#F8FAFC",          # slate-50, contrast 16:1
            "text_muted": "#94A3B8",    # slate-400
            "background": "#0F172A",    # slate-900
            "surface": "#1E293B",       # slate-800
            "glass": "rgba(0, 0, 0, 0.4)",  # min 40% opacity
            "border": "rgba(248, 250, 252, 0.1)",
            "border_strong": "rgba(248, 250, 252, 0.2)",
        },
        # México-inspired accent palette
        "accent": {
            "primary": "#D63384",       # Mexican pink (Rosa Mexicano)
            "secondary": "#8B4513",     # Terracotta
            "tertiary": "#006847",      # Verde México (flag green)
            "warm": "#F59E0B",          # Amber / Marigold
            "cool": "#3B82F6",          # Blue
        },
        # Semantic colors
        "semantic": {
            "success": "#22C55E",
            "warning": "#EAB308",
            "error": "#EF4444",
            "info": "#3B82F6",
        },
        # Glass morphism
        "glass": {
            "light_bg": "rgba(255, 255, 255, 0.8)",
            "light_border": "rgba(255, 255, 255, 0.3)",
            "dark_bg": "rgba(0, 0, 0, 0.4)",
            "dark_border": "rgba(255, 255, 255, 0.1)",
            "backdrop_blur": "blur(16px)",
        },
    },

    # ─── Typography ───────────────────────────────────────────
    "typography": {
        # Major Third scale (1.25)
        "scale": [12, 15, 19, 24, 30, 38, 48, 60, 75],
        "families": {
            "heading": "var(--font-geist-sans)",
            "body": "var(--font-geist-sans)",
            "mono": "var(--font-geist-mono)",
        },
        "weights": {
            "normal": 400,
            "medium": 500,
            "semibold": 600,
            "bold": 700,
        },
        "line_heights": {
            "tight": 1.1,      # Headlines
            "snug": 1.25,      # Subheads
            "normal": 1.5,     # Body
            "relaxed": 1.75,   # Long-form
        },
        # Hero text sizing
        "hero": {
            "size": "clamp(3rem, 8vw, 6rem)",
            "weight": 700,
            "line_height": 1.1,
        },
        # Minimum headline size for Awwwards
        "min_headline_px": 48,
    },

    # ─── Spacing ──────────────────────────────────────────────
    "spacing": {
        "hero_padding": "clamp(4rem, 12vw, 16rem)",
        "section_gap": "clamp(4rem, 8vw, 8rem)",
        "container_padding": "clamp(1rem, 5vw, 3rem)",
        "card_padding": "1.5rem",
        "grid_gap": "1.5rem",
    },

    # ─── Layout ───────────────────────────────────────────────
    "layout": {
        "max_width": "1280px",      # max-w-6xl
        "max_width_wide": "1536px", # max-w-7xl
        "container_padding": "clamp(1rem, 5vw, 3rem)",
        "navbar_offset": "1rem",    # top-4 (floating navbar)
        "breakpoints": {
            "sm": "375px",
            "md": "768px",
            "lg": "1024px",
            "xl": "1440px",
        },
    },

    # ─── Animation ────────────────────────────────────────────
    "animation": {
        "duration": {
            "fast": "150ms",
            "normal": "300ms",
            "slow": "500ms",
        },
        "easing": {
            "default": "cubic-bezier(0.4, 0, 0.2, 1)",
            "in": "cubic-bezier(0.4, 0, 1, 1)",
            "out": "cubic-bezier(0, 0, 0.2, 1)",
            "spring": "cubic-bezier(0.68, -0.55, 0.265, 1.55)",
        },
        # CRITICAL: Only animate these for 60fps
        "safe_properties": ["transform", "opacity", "filter", "clip-path"],
        "forbidden_properties": ["width", "height", "top", "left", "right", "bottom", "margin", "padding"],
    },

    # ─── Z-Index Scale ────────────────────────────────────────
    "z_index": {
        "base": 0,
        "elevated": 10,
        "dropdown": 20,
        "sticky": 30,
        "navbar": 50,
        "modal_backdrop": 90,
        "modal": 100,
        "tooltip": 200,
        "notification": 300,
    },

    # ─── Icon System ──────────────────────────────────────────
    "icons": {
        "primary_set": "lucide-react",
        "alternative_set": "heroicons",
        "brand_logos": "simple-icons",
        "default_size": "w-6 h-6",
        "small_size": "w-4 h-4",
        "large_size": "w-8 h-8",
        # CRITICAL: No emoji icons - SVG only
        "emoji_forbidden": True,
    },

    # ─── Stack ────────────────────────────────────────────────
    "tech_stack": {
        "framework": "Next.js 15 (App Router)",
        "react": "React 19 (Server Components)",
        "styling": "Tailwind CSS",
        "components": "shadcn/ui (Radix primitives)",
        "animation_libs": [
            "Framer Motion (React component animations)",
            "GSAP (complex timelines & ScrollTrigger)",
            "React Spring (physics-based)",
            "Lenis (smooth scrolling)",
        ],
        "3d": [
            "Three.js + React Three Fiber",
            "@react-three/drei (helpers)",
            "Spline (no-code 3D embeds)",
        ],
    },

    # ─── Accessibility ────────────────────────────────────────
    "accessibility": {
        "standard": "WCAG 2.1 AA",
        "min_contrast_text": 4.5,       # Normal text
        "min_contrast_large": 3.0,      # Large text (≥24px or bold ≥19px)
        "min_touch_target": "44px",
        "focus_ring": "ring-2 ring-primary ring-offset-2",
        "required_aria": [
            "aria-label on icon-only buttons",
            "alt text on all images",
            "htmlFor + id on form labels",
            "role attributes on custom widgets",
        ],
    },

    # ─── Performance Budgets ──────────────────────────────────
    "performance": {
        "lighthouse_mobile_min": 90,
        "lighthouse_desktop_min": 95,
        "max_cls": 0.1,
        "max_fcp_seconds": 1.5,
        "target_fps": 60,
        "image_format": "WebP with srcset + lazy loading",
    },

    # ─── Mexico City Market ───────────────────────────────────
    "market": {
        "primary_language": "es-MX",
        "secondary_language": "en",
        "mobile_traffic_pct": 60,
        "optimize_for_3g": True,
        "local_payment_methods": ["OXXO", "SPEI", "Mercado Pago"],
        "cultural_notes": [
            "Vibrant sophisticated palettes inspired by Mexican art traditions",
            "Bold, confident typography with bilingual ES/EN support",
            "Professional but warm tone, less corporate than US market",
            "Diverse representation in imagery",
            "Trust signals: portfolio, testimonials, local case studies",
        ],
    },
}


# ═══════════════════════════════════════════════════════════════
# Helper functions
# ═══════════════════════════════════════════════════════════════

def get_color(mode: str, key: str) -> Optional[str]:
    """Get a color token by mode (light/dark) and key."""
    return DESIGN_TOKENS["colors"].get(mode, {}).get(key)


def get_accent(key: str) -> Optional[str]:
    """Get an accent color token."""
    return DESIGN_TOKENS["colors"]["accent"].get(key)


def get_typography(key: str) -> Any:
    """Get a typography token."""
    return DESIGN_TOKENS["typography"].get(key)


def get_spacing(key: str) -> Optional[str]:
    """Get a spacing token."""
    return DESIGN_TOKENS["spacing"].get(key)


def get_animation(key: str) -> Any:
    """Get an animation token."""
    return DESIGN_TOKENS["animation"].get(key)


# ─── GSAP / Awwwards Extended Tokens ──────────────────────────

DESIGN_TOKENS["gsap_defaults"] = {
    "scroll_trigger": {
        "start": "top 80%",
        "end": "bottom 20%",
        "scrub": True,
        "toggleActions": "play none none reverse",
    },
    "ease": {
        "hero": "power1.inOut",
        "text": "power2.inOut",
        "button": "power1.out",
        "parallax": "none",
    },
    "stagger": {
        "text_char": 0.02,
        "grid_item": 0.05,
        "list_item": 0.1,
    },
}

DESIGN_TOKENS["clip_paths"] = {
    "hero_polygon": "polygon(14% 0, 72% 0, 88% 90%, 0 95%)",
    "hero_full": "polygon(0% 0%, 100% 0%, 100% 100%, 0% 100%)",
    "mask_reveal": "polygon(0 0, 100% 0, 100% 100%, 0 100%)",
    "geometric_1": "polygon(25% 0%, 74% 0, 69% 64%, 34% 73%)",
    "geometric_2": "polygon(29% 15%, 85% 30%, 50% 100%, 10% 64%)",
}

DESIGN_TOKENS["video_hero"] = {
    "mini_preview_size": "size-64",
    "transition_duration": 1,
    "scale_in_duration": 1.5,
    "border_radius": "rounded-lg",
    "supported_formats": ["mp4", "webm"],
}


def get_tailwind_config() -> dict:
    """Generate a Tailwind CSS config extend object from design tokens."""
    tokens = DESIGN_TOKENS
    return {
        "theme": {
            "extend": {
                "colors": {
                    "glass-dark": tokens["colors"]["glass"]["dark_bg"],
                    "glass-light": tokens["colors"]["glass"]["light_bg"],
                    "accent-mexico": tokens["colors"]["accent"]["primary"],
                    "accent-terracotta": tokens["colors"]["accent"]["secondary"],
                    "accent-verde": tokens["colors"]["accent"]["tertiary"],
                },
                "fontFamily": {
                    "heading": [tokens["typography"]["families"]["heading"]],
                    "body": [tokens["typography"]["families"]["body"]],
                    "mono": [tokens["typography"]["families"]["mono"]],
                },
                "maxWidth": {
                    "content": tokens["layout"]["max_width"],
                    "wide": tokens["layout"]["max_width_wide"],
                },
                "zIndex": {
                    str(k): str(v) for k, v in tokens["z_index"].items()
                },
                "transitionDuration": {
                    "fast": tokens["animation"]["duration"]["fast"],
                    "normal": tokens["animation"]["duration"]["normal"],
                    "slow": tokens["animation"]["duration"]["slow"],
                },
                "transitionTimingFunction": {
                    "default": tokens["animation"]["easing"]["default"],
                    "spring": tokens["animation"]["easing"]["spring"],
                },
            }
        }
    }


def validate_token_usage(code: str) -> list[dict]:
    """Validate that generated code uses proper design tokens."""
    issues = []

    # Check for hardcoded colors that should be tokens
    import re

    # Common anti-patterns
    hardcoded_colors = re.findall(r'(?:color|background|bg|border)[:\s-]+#[0-9a-fA-F]{3,8}', code)
    if hardcoded_colors:
        issues.append({
            "type": "warning",
            "message": f"Found {len(hardcoded_colors)} hardcoded colors - consider using design tokens",
            "details": hardcoded_colors[:5],
        })

    # Check for emoji icons
    emoji_pattern = re.compile(
        "[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]+",
        flags=re.UNICODE,
    )
    if emoji_pattern.search(code):
        issues.append({
            "type": "critical",
            "message": "Emoji icons detected - SVG only via Lucide/Heroicons",
        })

    # Check for forbidden animation properties
    for prop in DESIGN_TOKENS["animation"]["forbidden_properties"]:
        pattern = rf'transition[:\-][^;]*{prop}'
        if re.search(pattern, code):
            issues.append({
                "type": "critical",
                "message": f"Animating layout property '{prop}' - use transform/opacity only for 60fps",
            })

    return issues
