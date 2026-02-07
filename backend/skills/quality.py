"""
Synthia 4.2 - Quality Assurance Engine

Pre-delivery checklist embedded in all skills. Every output is validated
against Synthia's quality standards before returning to the user.
"""

from dataclasses import dataclass
from enum import Enum


class CheckCategory(str, Enum):
    VISUAL = "visual"
    INTERACTION = "interaction"
    LIGHT_DARK = "light_dark_mode"
    LAYOUT = "layout"
    ACCESSIBILITY = "accessibility"
    PERFORMANCE = "performance"
    AWWWARDS = "awwwards_formula"
    ANTI_PATTERN = "anti_pattern"


@dataclass
class QualityCheck:
    id: str
    category: CheckCategory
    description: str
    severity: str  # "critical" | "warning" | "info"
    auto_checkable: bool = True


# ─── QUALITY CHECKLIST ────────────────────────────────────────────────

QUALITY_CHECKS: list[QualityCheck] = [
    # Visual Quality
    QualityCheck("vis-01", CheckCategory.VISUAL, "No emoji icons (SVG only via Lucide/Heroicons)", "critical"),
    QualityCheck("vis-02", CheckCategory.VISUAL, "Icons from consistent set", "warning"),
    QualityCheck("vis-03", CheckCategory.VISUAL, "Brand logos verified (Simple Icons)", "warning"),
    QualityCheck("vis-04", CheckCategory.VISUAL, "No layout shift on hover", "critical"),
    QualityCheck("vis-05", CheckCategory.VISUAL, "Icon sizing consistent (w-6 h-6)", "warning"),

    # Interaction
    QualityCheck("int-01", CheckCategory.INTERACTION, "cursor-pointer on ALL clickables", "critical"),
    QualityCheck("int-02", CheckCategory.INTERACTION, "Hover feedback clear (color/opacity, NOT scale)", "warning"),
    QualityCheck("int-03", CheckCategory.INTERACTION, "Transitions 150-300ms", "warning"),
    QualityCheck("int-04", CheckCategory.INTERACTION, "Focus states visible (ring-2 ring-primary)", "critical"),
    QualityCheck("int-05", CheckCategory.INTERACTION, "No hover-only interactions on mobile", "warning"),

    # Light/Dark Mode
    QualityCheck("ldm-01", CheckCategory.LIGHT_DARK, "Light mode readable (#0F172A text, contrast ≥4.5:1)", "critical"),
    QualityCheck("ldm-02", CheckCategory.LIGHT_DARK, "Light glass visible (bg-white/80+)", "warning"),
    QualityCheck("ldm-03", CheckCategory.LIGHT_DARK, "Dark mode readable (#F8FAFC text)", "critical"),
    QualityCheck("ldm-04", CheckCategory.LIGHT_DARK, "Dark glass visible (bg-black/40+)", "warning"),
    QualityCheck("ldm-05", CheckCategory.LIGHT_DARK, "Borders visible in both modes", "warning"),
    QualityCheck("ldm-06", CheckCategory.LIGHT_DARK, "BOTH modes tested before delivery", "critical"),

    # Layout
    QualityCheck("lay-01", CheckCategory.LAYOUT, "Floating navbar (top-4 NOT top-0)", "warning"),
    QualityCheck("lay-02", CheckCategory.LAYOUT, "Content padding accounts for fixed elements", "warning"),
    QualityCheck("lay-03", CheckCategory.LAYOUT, "Consistent max-width (max-w-6xl or max-w-7xl)", "warning"),
    QualityCheck("lay-04", CheckCategory.LAYOUT, "Responsive breakpoints tested (375px, 768px, 1024px, 1440px)", "critical"),
    QualityCheck("lay-05", CheckCategory.LAYOUT, "No horizontal scroll on mobile", "critical"),
    QualityCheck("lay-06", CheckCategory.LAYOUT, "Z-index scale used (10, 20, 30, 50)", "info"),

    # Accessibility (WCAG 2.1 AA)
    QualityCheck("a11y-01", CheckCategory.ACCESSIBILITY, "All images have alt text", "critical"),
    QualityCheck("a11y-02", CheckCategory.ACCESSIBILITY, "Icon-only buttons have aria-label", "critical"),
    QualityCheck("a11y-03", CheckCategory.ACCESSIBILITY, "Form inputs have labels (htmlFor + id)", "critical"),
    QualityCheck("a11y-04", CheckCategory.ACCESSIBILITY, "Color not the only indicator", "critical"),
    QualityCheck("a11y-05", CheckCategory.ACCESSIBILITY, "Keyboard navigation works", "critical"),
    QualityCheck("a11y-06", CheckCategory.ACCESSIBILITY, "Focus states visible", "critical"),
    QualityCheck("a11y-07", CheckCategory.ACCESSIBILITY, "Touch targets ≥44x44px", "warning"),
    QualityCheck("a11y-08", CheckCategory.ACCESSIBILITY, "prefers-reduced-motion respected", "warning"),

    # Performance
    QualityCheck("perf-01", CheckCategory.PERFORMANCE, "Images: WebP, srcset, lazy loading", "warning"),
    QualityCheck("perf-02", CheckCategory.PERFORMANCE, "Animations: transform/opacity only (NO width/height/top/left)", "critical"),
    QualityCheck("perf-03", CheckCategory.PERFORMANCE, "CLS < 0.1", "critical"),
    QualityCheck("perf-04", CheckCategory.PERFORMANCE, "60fps animations (verified in DevTools)", "warning"),
    QualityCheck("perf-05", CheckCategory.PERFORMANCE, "Lighthouse Mobile >90, Desktop >95", "warning"),
    QualityCheck("perf-06", CheckCategory.PERFORMANCE, "No unused dependencies", "info"),

    # Awwwards Magic Formula
    QualityCheck("aww-01", CheckCategory.AWWWARDS, "Scroll-triggered animations (GSAP or Framer Motion)", "warning"),
    QualityCheck("aww-02", CheckCategory.AWWWARDS, "Parallax effects (Lenis or Locomotive Scroll)", "info"),
    QualityCheck("aww-03", CheckCategory.AWWWARDS, "Bold typography (≥48px headlines, variable fonts)", "warning"),
    QualityCheck("aww-04", CheckCategory.AWWWARDS, "Oversized visual elements (hero images, 3D objects)", "info"),
    QualityCheck("aww-05", CheckCategory.AWWWARDS, "Interactive micro-animations (hover, click, scroll)", "warning"),
    QualityCheck("aww-06", CheckCategory.AWWWARDS, "Smooth 60fps performance (no jank)", "critical"),

    # Anti-Pattern Detection
    QualityCheck("anti-01", CheckCategory.ANTI_PATTERN, "No emoji icons anywhere", "critical"),
    QualityCheck("anti-02", CheckCategory.ANTI_PATTERN, "No layout shift on hover (CLS validation)", "critical"),
    QualityCheck("anti-03", CheckCategory.ANTI_PATTERN, "No poor contrast (<4.5:1)", "critical"),
    QualityCheck("anti-04", CheckCategory.ANTI_PATTERN, "No slow animations (>500ms)", "warning"),
    QualityCheck("anti-05", CheckCategory.ANTI_PATTERN, "No generic templates or carousels", "warning"),
    QualityCheck("anti-06", CheckCategory.ANTI_PATTERN, "No auto-playing audio", "critical"),
]


def validate_code(code: str) -> list[dict]:
    """Run automated quality checks against generated code."""
    results = []

    # Emoji detection
    import re
    emoji_pattern = re.compile(
        "[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]+",
        flags=re.UNICODE,
    )
    if emoji_pattern.search(code):
        results.append({"check": "anti-01", "status": "fail", "message": "Emoji icons detected — use SVG icons only"})
    else:
        results.append({"check": "anti-01", "status": "pass", "message": "No emoji icons found"})

    # cursor-pointer check
    clickable_patterns = re.findall(r'<(button|a |Link )', code)
    has_cursor_pointer = "cursor-pointer" in code
    if clickable_patterns and not has_cursor_pointer:
        results.append({"check": "int-01", "status": "warn", "message": "Clickable elements found but no cursor-pointer class detected"})
    else:
        results.append({"check": "int-01", "status": "pass", "message": "cursor-pointer usage OK"})

    # Focus state check
    if "focus:" in code or "focus-visible:" in code or "focus:ring" in code:
        results.append({"check": "int-04", "status": "pass", "message": "Focus states detected"})
    elif clickable_patterns:
        results.append({"check": "int-04", "status": "fail", "message": "No focus states found on interactive elements"})

    # aria-label check for icon buttons
    icon_buttons = re.findall(r'<button[^>]*>[^<]*<(?:svg|[A-Z]\w+Icon|Lucide)', code)
    if icon_buttons:
        if "aria-label" not in code:
            results.append({"check": "a11y-02", "status": "fail", "message": "Icon-only buttons missing aria-label"})
        else:
            results.append({"check": "a11y-02", "status": "pass", "message": "aria-label found on icon buttons"})

    # Alt text check
    img_tags = re.findall(r'<img\s', code)
    if img_tags:
        alt_attrs = re.findall(r'<img[^>]*alt=', code)
        if len(alt_attrs) < len(img_tags):
            results.append({"check": "a11y-01", "status": "fail", "message": f"{len(img_tags) - len(alt_attrs)} img tags missing alt text"})
        else:
            results.append({"check": "a11y-01", "status": "pass", "message": "All images have alt text"})

    # Animation performance check
    bad_animations = re.findall(r'transition[:\-][^;]*(width|height|top|left|right|bottom)', code)
    if bad_animations:
        results.append({"check": "perf-02", "status": "fail", "message": "Animating layout properties (use transform/opacity instead)"})
    else:
        results.append({"check": "perf-02", "status": "pass", "message": "No layout-triggering animations detected"})

    # Transition duration check
    slow_transitions = re.findall(r'duration-\[?([5-9]\d{2,}|[1-9]\d{3,})ms', code)
    if slow_transitions:
        results.append({"check": "anti-04", "status": "warn", "message": f"Slow animations detected: {slow_transitions[0]}ms (keep ≤500ms)"})
    else:
        results.append({"check": "anti-04", "status": "pass", "message": "Animation durations within budget"})

    # ─── GSAP Quality Checks ───────────────────────────────────────
    # GSAP-01: Must register ScrollTrigger plugin
    if 'ScrollTrigger' in code and 'registerPlugin' not in code:
        results.append({"check": "gsap-01", "status": "fail", "message": "ScrollTrigger used without gsap.registerPlugin(ScrollTrigger)"})
    elif 'ScrollTrigger' in code:
        results.append({"check": "gsap-01", "status": "pass", "message": "ScrollTrigger plugin registered"})

    # GSAP-02: GSAP context cleanup
    if 'useGSAP' not in code and 'gsap.context' not in code and ('gsap.to' in code or 'gsap.from' in code):
        results.append({"check": "gsap-02", "status": "warn", "message": "GSAP animations without useGSAP hook or gsap.context - may cause memory leaks"})
    elif 'useGSAP' in code or 'gsap.context' in code:
        results.append({"check": "gsap-02", "status": "pass", "message": "GSAP context/cleanup present"})

    # GSAP-03: will-change on animated elements
    if ('gsap.to' in code or 'gsap.from' in code) and 'will-change' not in code:
        results.append({"check": "gsap-03", "status": "warn", "message": "Animated elements should use will-change for GPU compositing"})

    # GSAP-04: Never animate width/height/top/left
    layout_anim = re.findall(r'gsap\.(?:to|from|fromTo)\([^)]*(?:width|height|top|left|right|bottom)\s*:', code)
    if layout_anim:
        results.append({"check": "gsap-04", "status": "fail", "message": "Animating layout properties (width/height/top/left) causes reflow - use transform instead"})
    else:
        results.append({"check": "gsap-04", "status": "pass", "message": "No layout property animations detected"})

    return results


def get_quality_summary(results: list[dict]) -> dict:
    """Summarize quality check results."""
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "pass")
    failed = sum(1 for r in results if r["status"] == "fail")
    warnings = sum(1 for r in results if r["status"] == "warn")

    return {
        "total_checks": total,
        "passed": passed,
        "failed": failed,
        "warnings": warnings,
        "score": round((passed / total) * 100, 1) if total > 0 else 0,
        "quality_gate": "PASS" if failed == 0 else "FAIL",
        "results": results,
    }


def get_checklist_for_category(category: CheckCategory) -> list[dict]:
    """Get all checks for a specific category."""
    return [
        {"id": c.id, "description": c.description, "severity": c.severity}
        for c in QUALITY_CHECKS
        if c.category == category
    ]
