"""
Synthia 4.2 Design System

Design token architecture derived from UI/UX Design Master spec.
Provides the canonical design tokens for all Synthia skills and outputs.
Mexico City market specialization with Awwwards-level quality bar.
"""

from .tokens import (
    DESIGN_TOKENS,
    get_color,
    get_typography,
    get_spacing,
    get_animation,
    get_tailwind_config,
)

__all__ = [
    "DESIGN_TOKENS",
    "get_color",
    "get_typography",
    "get_spacing",
    "get_animation",
    "get_tailwind_config",
]
