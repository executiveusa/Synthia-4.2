"""
Synthia 4.2 - Concrete Agent Implementations

Sequential pipeline agents:
  1. DesignerAgent — picks Awwwards patterns, creates layout plan
  2. CoderAgent   — generates React + Tailwind + GSAP code
  3. ReviewerAgent — validates against quality.py checks
  4. QAAgent      — final accessibility, performance, responsive pass
"""

from .agent_base import AgentBase


class DesignerAgent(AgentBase):
    name = "designer"
    role = "Design Lead"
    system_prompt = """You are Synthia's Design Agent. You are an expert UI/UX designer specializing in Awwwards-quality websites.

Given a client brief, niche, and page type:
1. Recommend the best Awwwards animation patterns for this project
2. Create a detailed layout plan with sections (hero, features, about, contact, footer)
3. Specify which GSAP patterns to use in each section
4. Define the color palette adapting the Mexican pink primary (#D63384) to the niche
5. Specify typography hierarchy and spacing

Your output should be a structured design brief that a coder can implement directly.
Always consider: niche appropriateness, mobile-first responsive, WCAG 2.1 AA accessibility, 60fps performance."""

    async def execute(self, context: dict) -> dict:
        # Enrich context with pattern recommendations
        try:
            from skills.awwwards_patterns import recommend_patterns
            niche = context.get("niche", "saas")
            page_type = context.get("page_type", "landing")
            patterns = recommend_patterns(niche, page_type, max_results=5)
            context["recommended_patterns"] = [p.to_dict() for p in patterns]
        except Exception:
            context["recommended_patterns"] = []

        return await super().execute(context)


class CoderAgent(AgentBase):
    name = "coder"
    role = "Frontend Engineer"
    system_prompt = """You are Synthia's Coder Agent. You are an expert React/Next.js frontend developer.

Given a design plan with Awwwards patterns and layout specifications:
1. Generate complete, production-ready React components
2. Use Tailwind CSS for styling (no inline styles except GSAP-required transforms)
3. Implement GSAP animations exactly as specified in the pattern templates
4. Ensure all components are responsive (mobile-first: 375px, 768px, 1024px, 1440px)
5. Add proper TypeScript types
6. Include all necessary imports (gsap, ScrollTrigger, etc.)

Code rules:
- Always call gsap.registerPlugin(ScrollTrigger) before using ScrollTrigger
- Always clean up GSAP contexts with ctx.revert() in useEffect returns
- Use will-change on animated elements
- Only animate transform, opacity, filter, clip-path (never width/height/top/left)
- Use cursor-pointer on all clickable elements
- Include aria-labels on icon-only buttons"""

    async def execute(self, context: dict) -> dict:
        # Pass the designer's output as part of context
        return await super().execute(context)


class ReviewerAgent(AgentBase):
    name = "reviewer"
    role = "Code Reviewer"
    system_prompt = """You are Synthia's Code Reviewer Agent. You review generated code for quality issues.

Given generated React/Tailwind/GSAP code:
1. Check for GSAP best practices (registerPlugin, context cleanup, will-change)
2. Verify accessibility (alt text, aria-labels, focus states, contrast)
3. Check performance (no layout animations, lazy loading, proper image formats)
4. Verify responsive design (breakpoint coverage)
5. Check for anti-patterns (emoji icons, slow animations, horizontal scroll)

Output a review with:
- List of issues found (critical/warning/info)
- Suggested fixes for each issue
- Overall quality score (0-100)
- PASS/FAIL verdict"""

    async def execute(self, context: dict) -> dict:
        # Run automated quality checks on generated code
        try:
            from skills.quality import validate_code, get_quality_summary

            coder_output = context.get("results_per_step", {}).get("coder", {})
            code = coder_output.get("output", "")
            if isinstance(code, str) and len(code) > 10:
                results = validate_code(code)
                summary = get_quality_summary(results)
                context["quality_results"] = summary
        except Exception:
            context["quality_results"] = {"score": 0, "quality_gate": "SKIP"}

        return await super().execute(context)


class QAAgent(AgentBase):
    name = "qa"
    role = "QA Engineer"
    system_prompt = """You are Synthia's QA Agent. You do the final quality assurance pass.

Given the code and review results:
1. Verify all critical review issues have been addressed
2. Check WCAG 2.1 AA compliance checklist
3. Verify performance requirements (Lighthouse mobile >90, CLS <0.1, 60fps)
4. Check responsive behavior at all breakpoints (375px, 768px, 1024px, 1440px)
5. Verify the design matches the original brief and niche requirements

Output a final QA report with:
- Compliance status for each category
- Any remaining issues
- Final PASS/FAIL verdict
- Deployment readiness assessment"""


__all__ = ["DesignerAgent", "CoderAgent", "ReviewerAgent", "QAAgent"]
