"""
Flask/Jinja helpers for LM status badge (Phase-5).

These helpers consume LMIndicatorWidgetProps from `lm_indicator_adapter`
and expose a small badge to templates.
"""

from __future__ import annotations

from typing import Dict

from .lm_indicator_adapter import LMIndicatorWidgetProps, load_lm_indicator_widget_props


def get_lm_status_props() -> LMIndicatorWidgetProps:
    """
    Return the current LM indicator widget props (offline-safe by default).
    """
    return load_lm_indicator_widget_props()


def badge_context() -> Dict[str, str]:
    """
    Return a small context dict suitable for rendering a header badge.
    """
    props = get_lm_status_props()
    color = props["color"]
    label = props["label"]
    tooltip = "\n".join(props["tooltip_lines"])

    # Map LM color to simple CSS class names (tune in CSS as needed)
    color_class = {
        "grey": "lm-badge-grey",
        "green": "lm-badge-green",
        "yellow": "lm-badge-yellow",
        "red": "lm-badge-red",
    }.get(color, "lm-badge-grey")

    return {
        "label": label,
        "tooltip": tooltip,
        "color_class": color_class,
        "icon": props["icon"],
    }

