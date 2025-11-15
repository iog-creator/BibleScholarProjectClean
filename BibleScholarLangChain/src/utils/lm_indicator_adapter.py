"""
LM Indicator adapter for BibleScholar (Phase-5).

- Hermetic: reads only Gemantria's `lm_indicator.json` file (no DB or LM calls).
- Fail-closed: missing/invalid indicator -> offline-safe widget props.
- Contract: mirrors Gemantria's `LMIndicatorWidgetProps` (LM_WIDGETS SSOT).

This module is a downstream consumer of the canonical signal:
    Gemantria.v2/share/atlas/control_plane/lm_indicator.json
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, TypedDict

# Path to Gemantria's lm_indicator.json (adjust if your local layout differs)
INDICATOR_PATH = (
    Path(__file__)
    .resolve()
    .parents[3]
    / "Gemantria.v2"
    / "share"
    / "atlas"
    / "control_plane"
    / "lm_indicator.json"
)

LmStatus = Literal["offline", "healthy", "degraded"]
LmReason = Literal["db_off", "no_calls", "high_error_rate", "ok"]
LmColor = Literal["grey", "green", "yellow", "red"]


class MetricsProps(TypedDict):
    successRate: Optional[float]
    errorRate: Optional[float]
    totalCalls: Optional[int]
    dbOff: bool
    topErrorReason: Optional[str]
    windowDays: int
    generatedAt: str


class LMIndicatorWidgetProps(TypedDict):
    status: LmStatus
    reason: LmReason
    label: str
    color: LmColor
    icon: str
    tooltip_lines: List[str]
    metrics: MetricsProps
    source: Dict[str, str]


OFFLINE_SAFE_DEFAULT: LMIndicatorWidgetProps = {
    "status": "offline",
    "reason": "db_off",
    "label": "LM status unknown (offline-safe mode)",
    "color": "grey",
    "icon": "status-offline",
    "tooltip_lines": [
        "LM status unavailable",
        "Operating in offline-safe mode",
    ],
    "metrics": {
        "successRate": None,
        "errorRate": None,
        "totalCalls": None,
        "dbOff": True,
        "topErrorReason": None,
        "windowDays": 7,
        "generatedAt": "1970-01-01T00:00:00Z",
    },
    "source": {"path": str(INDICATOR_PATH)},
}


@dataclass
class RawIndicator:
    status: str
    reason: str
    success_rate: Optional[float]
    error_rate: Optional[float]
    total_calls: Optional[int]
    db_off: bool
    top_error_reason: Optional[str]
    window_days: int
    generated_at: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RawIndicator":
        return cls(
            status=str(data.get("status", "offline")),
            reason=str(data.get("reason", "db_off")),
            success_rate=_to_optional_float(data.get("success_rate")),
            error_rate=_to_optional_float(data.get("error_rate")),
            total_calls=_to_optional_int(data.get("total_calls")),
            db_off=bool(data.get("db_off", False)),
            top_error_reason=_to_optional_str(data.get("top_error_reason")),
            window_days=_to_int_or(data.get("window_days"), 7),
            generated_at=str(data.get("generated_at", "1970-01-01T00:00:00Z")),
        )


def _to_optional_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_optional_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _to_int_or(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _to_optional_str(value: Any) -> Optional[str]:
    if value is None:
        return None
    value_str = str(value).strip()
    return value_str or None


def _normalize_status(status: str) -> LmStatus:
    if status in ("offline", "healthy", "degraded"):
        return status  # type: ignore[return-value]
    return "offline"


def _normalize_reason(reason: str) -> LmReason:
    if reason in ("db_off", "no_calls", "high_error_rate", "ok"):
        return reason  # type: ignore[return-value]
    return "db_off"


def _color_for(ind: RawIndicator, status: LmStatus) -> LmColor:
    if status == "offline":
        return "grey"
    if status == "healthy":
        return "green"
    if ind.error_rate is not None and ind.error_rate >= 0.5:
        return "red"
    return "yellow"


def _icon_for(status: LmStatus) -> str:
    if status == "offline":
        return "status-offline"
    if status == "healthy":
        return "status-healthy"
    return "status-degraded"


def _label_for(status: LmStatus, reason: LmReason) -> str:
    if status == "offline":
        if reason == "db_off":
            return "LM Studio offline (database unavailable)"
        if reason == "no_calls":
            return "LM Studio offline (no recent activity)"
        return "LM Studio offline"
    if status == "degraded":
        if reason == "high_error_rate":
            return "LM Studio degraded (high error rate)"
        return "LM Studio degraded"
    return "LM Studio healthy"


def _tooltip_lines(ind: RawIndicator, status: LmStatus, reason: LmReason) -> List[str]:
    sr = ind.success_rate
    er = ind.error_rate
    calls = ind.total_calls
    window_days = ind.window_days
    top_error = ind.top_error_reason
    generated_at = ind.generated_at

    lines: List[str] = [
        f"Status: {status}",
        f"Reason: {reason}",
        f"Success rate: {sr * 100:.1f}%" if sr is not None else "Success rate: n/a",
        f"Error rate: {er * 100:.1f}%" if er is not None else "Error rate: n/a",
        f"Total calls (last {window_days}d): {calls if calls is not None else 'n/a'}",
        f"Top error: {top_error}" if top_error else "Top error: —",
        f"As of: {generated_at}",
    ]
    return lines


def _metrics_for(ind: RawIndicator) -> MetricsProps:
    return {
        "successRate": ind.success_rate,
        "errorRate": ind.error_rate,
        "totalCalls": ind.total_calls,
        "dbOff": ind.db_off,
        "topErrorReason": ind.top_error_reason,
        "windowDays": ind.window_days,
        "generatedAt": ind.generated_at,
    }


def load_lm_indicator_widget_props(path: Optional[Path] = None) -> LMIndicatorWidgetProps:
    """
    Load LM Indicator widget props for BibleScholar.

    Hermetic:
        - Reads only the indicator JSON file (no DB or LM calls).
    Fail-closed:
        - On missing/invalid file or invalid content, returns an offline-safe default.
    """
    indicator_path = path or INDICATOR_PATH

    try:
        text = indicator_path.read_text(encoding="utf-8")
        data = json.loads(text)
    except Exception:
        return OFFLINE_SAFE_DEFAULT

    try:
        raw = RawIndicator.from_dict(data)
        status = _normalize_status(raw.status)
        reason = _normalize_reason(raw.reason)
        color = _color_for(raw, status)
        icon = _icon_for(status)
        label = _label_for(status, reason)
        tooltip = _tooltip_lines(raw, status, reason)
        metrics = _metrics_for(raw)
        return {
            "status": status,
            "reason": reason,
            "label": label,
            "color": color,
            "icon": icon,
            "tooltip_lines": tooltip,
            "metrics": metrics,
            "source": {"path": str(indicator_path)},
        }
    except Exception:
        return OFFLINE_SAFE_DEFAULT

