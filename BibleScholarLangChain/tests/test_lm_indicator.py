from pathlib import Path
import json
from typing import cast

from BibleScholarLangChain.src.utils.lm_indicator_adapter import (
    LMIndicatorWidgetProps,
    load_lm_indicator_widget_props,
)
from BibleScholarLangChain.src.utils import lm_status_helper


def _write_indicator(tmp_path: Path, payload: dict) -> Path:
    p = tmp_path / "lm_indicator.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    return p


def test_adapter_healthy(tmp_path: Path) -> None:
    p = _write_indicator(
        tmp_path,
        {
            "status": "healthy",
            "reason": "ok",
            "success_rate": 0.95,
            "error_rate": 0.05,
            "total_calls": 100,
            "db_off": False,
            "top_error_reason": None,
            "window_days": 7,
            "generated_at": "2025-11-15T00:00:00Z",
        },
    )
    props = cast(LMIndicatorWidgetProps, load_lm_indicator_widget_props(path=p))
    assert props["status"] == "healthy"
    assert props["reason"] == "ok"
    assert props["color"] == "green"
    assert props["icon"] == "status-healthy"


def test_adapter_missing_file_offline_safe() -> None:
    props = cast(
        LMIndicatorWidgetProps,
        load_lm_indicator_widget_props(path=Path("does-not-exist.json")),
    )
    assert props["status"] == "offline"
    assert "offline-safe mode" in props["label"]


def test_badge_context_uses_adapter(monkeypatch, tmp_path: Path) -> None:
    p = _write_indicator(
        tmp_path,
        {
            "status": "degraded",
            "reason": "high_error_rate",
            "success_rate": 0.7,
            "error_rate": 0.3,
            "total_calls": 50,
            "db_off": False,
            "top_error_reason": "timeout",
            "window_days": 7,
            "generated_at": "2025-11-15T00:00:00Z",
        },
    )

    def _fake_loader():
        return load_lm_indicator_widget_props(path=p)

    monkeypatch.setattr(lm_status_helper, "get_lm_status_props", _fake_loader, raising=False)
    ctx = lm_status_helper.badge_context()
    assert "label" in ctx
    assert "tooltip" in ctx
    assert "color_class" in ctx

