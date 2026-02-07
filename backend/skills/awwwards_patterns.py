"""
Synthia 4.2 - Awwwards Pattern Library

10 award-winning GSAP animation patterns extracted from top Awwwards sites.
Each pattern includes: working GSAP+React code template, Tailwind classes,
niche-aware scoring (which industries each pattern fits/avoids), and
complexity + performance metadata.

Patterns sourced from adrianhajdin/award-winning-website analysis.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AwwwardsPattern:
    pattern_id: str
    name: str
    category: str  # hero | grid | text | scroll | shape | button | transition | loader
    gsap_template: str
    tailwind_classes: list[str] = field(default_factory=list)
    niche_fit: list[str] = field(default_factory=list)
    niche_avoid: list[str] = field(default_factory=list)
    complexity: int = 3  # 1-5
    performance_impact: str = "medium"  # low | medium | high
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "pattern_id": self.pattern_id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "tailwind_classes": self.tailwind_classes,
            "niche_fit": self.niche_fit,
            "niche_avoid": self.niche_avoid,
            "complexity": self.complexity,
            "performance_impact": self.performance_impact,
            "gsap_template": self.gsap_template,
        }


# ─── PATTERN REGISTRY ────────────────────────────────────────

PATTERNS: dict[str, AwwwardsPattern] = {}


def register_pattern(p: AwwwardsPattern) -> None:
    PATTERNS[p.pattern_id] = p


def get_pattern(pattern_id: str) -> Optional[AwwwardsPattern]:
    return PATTERNS.get(pattern_id)


def list_patterns(category: Optional[str] = None) -> list[AwwwardsPattern]:
    if category:
        return [p for p in PATTERNS.values() if p.category == category]
    return list(PATTERNS.values())


# ─── NICHE REASONING ENGINE ──────────────────────────────────

# Niche-to-trait mapping for scoring
NICHE_TRAITS: dict[str, list[str]] = {
    "saas": ["modern", "clean", "bold-type", "scroll-driven"],
    "portfolio": ["creative", "bold-type", "3d", "scroll-driven", "parallax"],
    "agency": ["creative", "bold-type", "video", "scroll-driven", "parallax"],
    "entertainment": ["video", "immersive", "3d", "bold-type", "parallax"],
    "ecommerce": ["clean", "fast", "product-focus"],
    "ecommerce-product": ["fast", "product-focus", "clean"],
    "tech": ["modern", "clean", "scroll-driven", "bold-type"],
    "media": ["video", "immersive", "bold-type"],
    "storytelling": ["scroll-driven", "parallax", "immersive"],
    "creative": ["bold-type", "3d", "parallax", "creative"],
    "nonprofit": ["warm", "clean", "accessible"],
    "government": ["clean", "accessible", "simple"],
    "construction": ["simple", "clean", "product-focus"],
    "legal": ["clean", "simple", "accessible"],
    "medical": ["clean", "accessible", "simple"],
    "finance": ["clean", "modern", "simple"],
    "restaurant": ["warm", "video", "creative"],
    "fashion": ["bold-type", "video", "creative", "immersive"],
}

PATTERN_TRAITS: dict[str, list[str]] = {
    "clip-path-hero-reveal": ["bold-type", "scroll-driven", "immersive"],
    "bento-tilt-grid": ["modern", "clean", "3d"],
    "text-character-reveal": ["bold-type", "scroll-driven", "creative"],
    "video-hero-transition": ["video", "immersive", "bold-type"],
    "scroll-pin-section": ["scroll-driven", "immersive", "parallax"],
    "geometric-shape-divider": ["creative", "warm", "clean"],
    "magnetic-button": ["modern", "clean"],
    "gradient-text-wipe": ["bold-type", "modern", "creative"],
    "preloader-count-up": ["modern", "clean"],
    "parallax-depth-layers": ["3d", "parallax", "immersive"],
}


def recommend_patterns(
    niche: str,
    page_type: str = "landing",
    max_results: int = 10,
) -> list[AwwwardsPattern]:
    """
    Recommend Awwwards patterns based on niche and page type.
    Returns patterns sorted by relevance score (highest first).
    Filters out patterns that are inappropriate for the niche.
    """
    niche_key = niche.lower().replace(" ", "-")
    niche_traits = NICHE_TRAITS.get(niche_key, ["modern", "clean"])

    scored: list[tuple[float, AwwwardsPattern]] = []
    for p in PATTERNS.values():
        # Hard filter: skip if niche is in avoid list
        if niche_key in p.niche_avoid:
            continue

        # Score: niche_fit gives +3, trait overlap gives +1 each
        score = 0.0
        if niche_key in p.niche_fit:
            score += 3.0

        # Trait overlap scoring
        p_traits = PATTERN_TRAITS.get(p.pattern_id, [])
        overlap = len(set(niche_traits) & set(p_traits))
        score += overlap

        # Page type bonus
        if page_type == "landing" and p.category in ("hero", "text", "scroll"):
            score += 1.0
        elif page_type == "product" and p.category in ("grid", "button"):
            score += 1.0
        elif page_type == "about" and p.category in ("scroll", "text", "shape"):
            score += 1.0

        # Penalize high complexity for simple niches
        if niche_key in ("government", "medical", "legal") and p.complexity > 3:
            score -= 2.0

        if score > 0:
            scored.append((score, p))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:max_results]]


# ═══════════════════════════════════════════════════════════════
# REGISTER ALL 10 PATTERNS
# ═══════════════════════════════════════════════════════════════

register_pattern(AwwwardsPattern(
    pattern_id="clip-path-hero-reveal",
    name="Clip-Path Hero Reveal",
    category="hero",
    description="Hero section with polygon clip-path that morphs on scroll via GSAP ScrollTrigger. Creates a cinematic reveal effect.",
    complexity=4,
    performance_impact="medium",
    niche_fit=["saas", "portfolio", "entertainment", "agency", "fashion"],
    niche_avoid=["government", "nonprofit", "construction"],
    tailwind_classes=["relative", "h-dvh", "w-screen", "overflow-hidden", "rounded-lg", "bg-blue-75"],
    gsap_template="""
import gsap from "gsap";
import { ScrollTrigger } from "gsap/all";
import { useGSAP } from "@gsap/react";

gsap.registerPlugin(ScrollTrigger);

export function ClipPathHeroReveal({ children }) {
  useGSAP(() => {
    gsap.set("#video-frame", {
      clipPath: "polygon(14% 0, 72% 0, 88% 90%, 0 95%)",
      borderRadius: "0% 0% 40% 10%",
    });
    gsap.from("#video-frame", {
      clipPath: "polygon(0% 0%, 100% 0%, 100% 100%, 0% 100%)",
      borderRadius: "0% 0% 0% 0%",
      ease: "power1.inOut",
      scrollTrigger: {
        trigger: "#video-frame",
        start: "center center",
        end: "bottom center",
        scrub: true,
      },
    });
  });

  return (
    <div className="relative h-dvh w-screen overflow-x-hidden">
      <div id="video-frame"
        className="relative z-10 h-dvh w-screen overflow-hidden rounded-lg">
        {children}
      </div>
    </div>
  );
}
""",
))

register_pattern(AwwwardsPattern(
    pattern_id="bento-tilt-grid",
    name="Bento Tilt Grid",
    category="grid",
    description="Bento-style grid cards with 3D perspective tilt on mouse hover. Cards scale slightly and rotate based on cursor position.",
    complexity=3,
    performance_impact="low",
    niche_fit=["saas", "portfolio", "tech", "agency"],
    niche_avoid=["construction", "legal"],
    tailwind_classes=["relative", "border-hsla", "col-span-2", "overflow-hidden", "rounded-md", "transition-transform", "duration-300", "ease-out"],
    gsap_template="""
import { useState, useRef } from "react";

export function BentoTilt({ children, className = "" }) {
  const [transformStyle, setTransformStyle] = useState("");
  const itemRef = useRef(null);

  const handleMouseMove = (event) => {
    if (!itemRef.current) return;
    const { left, top, width, height } = itemRef.current.getBoundingClientRect();
    const relativeX = (event.clientX - left) / width;
    const relativeY = (event.clientY - top) / height;
    const tiltX = (relativeY - 0.5) * 5;
    const tiltY = (relativeX - 0.5) * -5;
    setTransformStyle(
      `perspective(700px) rotateX(${tiltX}deg) rotateY(${tiltY}deg) scale3d(.95, .95, .95)`
    );
  };

  const handleMouseLeave = () => setTransformStyle("");

  return (
    <div ref={itemRef} className={className}
      onMouseMove={handleMouseMove} onMouseLeave={handleMouseLeave}
      style={{ transform: transformStyle }}>
      {children}
    </div>
  );
}
""",
))

register_pattern(AwwwardsPattern(
    pattern_id="text-character-reveal",
    name="Text Character Reveal",
    category="text",
    description="Words fade in with 3D rotation on scroll. Each word staggers in from a rotated/translated state using ScrollTrigger.",
    complexity=3,
    performance_impact="low",
    niche_fit=["agency", "portfolio", "entertainment", "fashion", "storytelling"],
    niche_avoid=["medical", "finance"],
    tailwind_classes=["flex", "flex-col", "gap-1", "text-7xl", "uppercase", "leading-[.8]"],
    gsap_template="""
import { gsap } from "gsap";
import { useEffect, useRef } from "react";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

export function AnimatedTitle({ title, containerClass }) {
  const containerRef = useRef(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      const tl = gsap.timeline({
        scrollTrigger: {
          trigger: containerRef.current,
          start: "100 bottom",
          end: "center bottom",
          toggleActions: "play none none reverse",
        },
      });
      tl.to(".animated-word", {
        opacity: 1,
        transform: "translate3d(0, 0, 0) rotateY(0deg) rotateX(0deg)",
        ease: "power2.inOut",
        stagger: 0.02,
      }, 0);
    }, containerRef);
    return () => ctx.revert();
  }, []);

  return (
    <div ref={containerRef} className={containerClass}>
      {title.split("<br />").map((line, i) => (
        <div key={i} className="flex-center max-w-full flex-wrap gap-2 px-10 md:gap-3">
          {line.split(" ").map((word, j) => (
            <span key={j} className="animated-word"
              dangerouslySetInnerHTML={{ __html: word }} />
          ))}
        </div>
      ))}
    </div>
  );
}

/* CSS required:
  .animated-word {
    @apply font-black opacity-0;
    transform: translate3d(10px, 51px, -60px) rotateY(60deg) rotateX(-40deg);
    transform-origin: 50% 50% -150px !important;
    will-change: opacity, transform;
  }
*/
""",
))

register_pattern(AwwwardsPattern(
    pattern_id="video-hero-transition",
    name="Video Hero Transition",
    category="hero",
    description="Click-to-expand video hero with smooth GSAP scale transition. Mini preview expands to full-screen video on interaction.",
    complexity=4,
    performance_impact="high",
    niche_fit=["entertainment", "agency", "media", "ecommerce", "fashion"],
    niche_avoid=["government"],
    tailwind_classes=["absolute-center", "absolute", "z-50", "size-64", "cursor-pointer", "overflow-hidden", "rounded-lg"],
    gsap_template="""
import gsap from "gsap";
import { useGSAP } from "@gsap/react";
import { useRef, useState } from "react";

export function VideoHeroTransition({ videos }) {
  const [currentIndex, setCurrentIndex] = useState(1);
  const [hasClicked, setHasClicked] = useState(false);
  const nextVdRef = useRef(null);

  const handleClick = () => {
    setHasClicked(true);
    setCurrentIndex((prev) => (prev % videos.length) + 1);
  };

  useGSAP(() => {
    if (hasClicked) {
      gsap.set("#next-video", { visibility: "visible" });
      gsap.to("#next-video", {
        transformOrigin: "center center",
        scale: 1, width: "100%", height: "100%",
        duration: 1, ease: "power1.inOut",
        onStart: () => nextVdRef.current?.play(),
      });
      gsap.from("#current-video", {
        transformOrigin: "center center",
        scale: 0, duration: 1.5, ease: "power1.inOut",
      });
    }
  }, { dependencies: [currentIndex], revertOnUpdate: true });

  return (
    <div className="relative h-dvh w-screen overflow-hidden">
      <div onClick={handleClick}
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-50 size-64 cursor-pointer overflow-hidden rounded-lg">
        <video ref={nextVdRef} src={videos[(currentIndex % videos.length)]}
          loop muted id="current-video"
          className="size-64 origin-center scale-150 object-cover object-center opacity-0 transition-all duration-500 hover:opacity-100 hover:scale-100" />
      </div>
      <video src={videos[currentIndex - 1]} autoPlay loop muted
        className="absolute left-0 top-0 size-full object-cover object-center" />
    </div>
  );
}
""",
))

register_pattern(AwwwardsPattern(
    pattern_id="scroll-pin-section",
    name="Scroll Pin Section",
    category="scroll",
    description="Section that pins in place while a clip-path mask expands to reveal full content. Creates an immersive scroll-driven storytelling effect.",
    complexity=3,
    performance_impact="medium",
    niche_fit=["storytelling", "portfolio", "saas", "agency", "entertainment"],
    niche_avoid=["ecommerce-product"],
    tailwind_classes=["min-h-screen", "w-screen"],
    gsap_template="""
import gsap from "gsap";
import { useGSAP } from "@gsap/react";
import { ScrollTrigger } from "gsap/all";

gsap.registerPlugin(ScrollTrigger);

export function ScrollPinSection({ children, imageSrc }) {
  useGSAP(() => {
    const clipAnimation = gsap.timeline({
      scrollTrigger: {
        trigger: "#clip",
        start: "center center",
        end: "+=800 center",
        scrub: 0.5,
        pin: true,
        pinSpacing: true,
      },
    });
    clipAnimation.to(".mask-clip-path", {
      width: "100vw", height: "100vh", borderRadius: 0,
    });
  });

  return (
    <div className="min-h-screen w-screen">
      {children}
      <div className="h-dvh w-screen" id="clip">
        <div className="mask-clip-path absolute left-1/2 top-0 z-20 h-[60vh] w-96 origin-center -translate-x-1/2 overflow-hidden rounded-3xl md:w-[30vw]">
          <img src={imageSrc} alt="Background"
            className="absolute left-0 top-0 size-full object-cover" />
        </div>
      </div>
    </div>
  );
}

/* CSS: .mask-clip-path { clip-path: polygon(0 0, 100% 0, 100% 100%, 0 100%); } */
""",
))

register_pattern(AwwwardsPattern(
    pattern_id="geometric-shape-divider",
    name="Geometric Shape Divider",
    category="shape",
    description="Layered clip-path polygon compositions for section dividers. Multiple overlapping shapes create depth and visual interest.",
    complexity=2,
    performance_impact="low",
    niche_fit=["agency", "nonprofit", "creative", "restaurant", "fashion"],
    niche_avoid=[],
    tailwind_classes=["relative", "rounded-lg", "bg-black", "py-24", "text-blue-50", "overflow-hidden"],
    gsap_template="""
export function GeometricShapeDivider({ children }) {
  return (
    <div className="relative rounded-lg bg-black py-24 text-blue-50 sm:overflow-hidden">
      <div className="absolute -left-20 top-0 hidden h-full w-72 overflow-hidden sm:block lg:left-20 lg:w-96">
        <div className="contact-clip-path-1">
          <img src="/img/shape-1.webp" alt="" className="object-cover" />
        </div>
        <div className="contact-clip-path-2 lg:translate-y-40 translate-y-60">
          <img src="/img/shape-2.webp" alt="" className="object-cover" />
        </div>
      </div>
      <div className="flex flex-col items-center text-center">
        {children}
      </div>
    </div>
  );
}

/* CSS:
  .contact-clip-path-1 { clip-path: polygon(25% 0%, 74% 0, 69% 64%, 34% 73%); }
  .contact-clip-path-2 { clip-path: polygon(29% 15%, 85% 30%, 50% 100%, 10% 64%); }
*/
""",
))

register_pattern(AwwwardsPattern(
    pattern_id="magnetic-button",
    name="Magnetic Button",
    category="button",
    description="Button with translateY/skewY text swap on hover. Text slides up and a duplicate slides in from below for a magnetic feel.",
    complexity=1,
    performance_impact="low",
    niche_fit=["saas", "portfolio", "agency", "tech", "entertainment", "ecommerce", "fashion"],
    niche_avoid=[],
    tailwind_classes=["group", "relative", "z-10", "w-fit", "cursor-pointer", "overflow-hidden", "rounded-full", "px-7", "py-3"],
    gsap_template="""
export function MagneticButton({ title, leftIcon, rightIcon, containerClass, id }) {
  return (
    <button id={id}
      className={`group relative z-10 w-fit cursor-pointer overflow-hidden rounded-full bg-violet-50 px-7 py-3 text-black ${containerClass || ""}`}>
      {leftIcon}
      <span className="relative inline-flex overflow-hidden font-general text-xs uppercase">
        <div className="translate-y-0 skew-y-0 transition duration-500 group-hover:translate-y-[-160%] group-hover:skew-y-12">
          {title}
        </div>
        <div className="absolute translate-y-[164%] skew-y-12 transition duration-500 group-hover:translate-y-0 group-hover:skew-y-0">
          {title}
        </div>
      </span>
      {rightIcon}
    </button>
  );
}
""",
))

register_pattern(AwwwardsPattern(
    pattern_id="gradient-text-wipe",
    name="Gradient Text Wipe",
    category="text",
    description="CSS gradient animation that wipes across text, combined with special font feature settings for bold character styling.",
    complexity=2,
    performance_impact="low",
    niche_fit=["saas", "tech", "agency", "portfolio", "fashion"],
    niche_avoid=["medical", "legal"],
    tailwind_classes=["uppercase", "font-black", "text-5xl", "sm:text-7xl", "md:text-9xl"],
    gsap_template="""
export function GradientTextWipe({ text, className }) {
  return (
    <h1 className={`special-font hero-heading ${className || ""}`}>
      {text.split("").map((char, i) =>
        char === "*" ? <b key={i}>{text[i+1]}</b> :
        (i > 0 && text[i-1] === "*") ? null :
        <span key={i}>{char}</span>
      )}
    </h1>
  );
}

/* CSS:
  .special-font b {
    font-family: "Zentry", sans-serif;
    font-feature-settings: "ss01" on;
  }
  .hero-heading {
    @apply uppercase font-black text-5xl sm:text-7xl md:text-9xl lg:text-[12rem];
    background: linear-gradient(90deg, var(--accent-primary), var(--accent-tertiary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-size: 200% 100%;
    animation: textWipe 3s ease-in-out infinite alternate;
  }
  @keyframes textWipe {
    0% { background-position: 0% 50%; }
    100% { background-position: 100% 50%; }
  }
*/
""",
))

register_pattern(AwwwardsPattern(
    pattern_id="preloader-count-up",
    name="Preloader Count-Up",
    category="loader",
    description="Three-body CSS orbital loader with video preload counting. Shows loading state while assets load, then reveals content.",
    complexity=2,
    performance_impact="low",
    niche_fit=["saas", "portfolio", "agency", "tech", "entertainment", "ecommerce", "fashion"],
    niche_avoid=[],
    tailwind_classes=["flex-center", "absolute", "z-[100]", "h-dvh", "w-screen", "overflow-hidden"],
    gsap_template="""
import { useEffect, useState } from "react";

export function PreloaderCountUp({ totalAssets = 4, children, onLoaded }) {
  const [loading, setLoading] = useState(true);
  const [loadedCount, setLoadedCount] = useState(0);

  useEffect(() => {
    if (loadedCount >= totalAssets - 1) {
      setLoading(false);
      onLoaded?.();
    }
  }, [loadedCount, totalAssets, onLoaded]);

  const handleAssetLoad = () => setLoadedCount((prev) => prev + 1);

  return (
    <div className="relative h-dvh w-screen overflow-x-hidden">
      {loading && (
        <div className="flex justify-center items-center absolute z-[100] h-dvh w-screen overflow-hidden bg-violet-50">
          <div className="three-body">
            <div className="three-body__dot" />
            <div className="three-body__dot" />
            <div className="three-body__dot" />
          </div>
        </div>
      )}
      {children({ handleAssetLoad })}
    </div>
  );
}

/* CSS: three-body loader from Uiverse.io - see index.css */
""",
))

register_pattern(AwwwardsPattern(
    pattern_id="parallax-depth-layers",
    name="Parallax Depth Layers",
    category="scroll",
    description="3D parallax effect using perspective + cursor-driven rotation. Container and inner content move in opposite directions for depth.",
    complexity=4,
    performance_impact="medium",
    niche_fit=["portfolio", "entertainment", "agency", "fashion", "storytelling"],
    niche_avoid=["ecommerce-product"],
    tailwind_classes=["absolute", "z-50", "size-full", "overflow-hidden", "rounded-lg"],
    gsap_template="""
import { gsap } from "gsap";
import { useState, useRef, useEffect } from "react";

export function ParallaxDepthLayers({ children }) {
  const [isHovering, setIsHovering] = useState(false);
  const sectionRef = useRef(null);
  const contentRef = useRef(null);

  const handleMouseMove = ({ clientX, clientY, currentTarget }) => {
    const rect = currentTarget.getBoundingClientRect();
    const xOffset = clientX - (rect.left + rect.width / 2);
    const yOffset = clientY - (rect.top + rect.height / 2);
    if (isHovering) {
      gsap.to(sectionRef.current, {
        x: xOffset, y: yOffset,
        rotationY: xOffset / 2, rotationX: -yOffset / 2,
        transformPerspective: 500, duration: 1, ease: "power1.out",
      });
      gsap.to(contentRef.current, {
        x: -xOffset, y: -yOffset, duration: 1, ease: "power1.out",
      });
    }
  };

  useEffect(() => {
    if (!isHovering) {
      gsap.to(sectionRef.current, {
        x: 0, y: 0, rotationY: 0, rotationX: 0, duration: 1, ease: "power1.out",
      });
      gsap.to(contentRef.current, {
        x: 0, y: 0, duration: 1, ease: "power1.out",
      });
    }
  }, [isHovering]);

  return (
    <section ref={sectionRef}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
      className="absolute z-50 size-full overflow-hidden rounded-lg"
      style={{ perspective: "500px" }}>
      <div ref={contentRef} className="origin-center rounded-lg"
        style={{ transformStyle: "preserve-3d" }}>
        {children}
      </div>
    </section>
  );
}
""",
))

__all__ = [
    "AwwwardsPattern",
    "PATTERNS",
    "register_pattern",
    "get_pattern",
    "list_patterns",
    "recommend_patterns",
    "NICHE_TRAITS",
    "PATTERN_TRAITS",
]
