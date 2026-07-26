"""Contract tests for the canonical Day 12 replay runner."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

import scripts.run_day12_trend_family_event_replay as runner


def make_compact_canonical() -> pd.DataFrame:
    """Create compact canonical-shaped multi-symbol rows."""

    frames: list[pd.DataFrame] = []

    for symbol in ("SPY", "QQQ", "IWM"):
        for session_date, count in (
            ("2020-01-02", 14),
            ("2025-12-31", 26),
        ):
            timestamps = pd.date_range(
                f"{session_date} 14:30:00+00:00",
                periods=count,
                freq="15min",
            )
            frames.append(
                pd.DataFrame(
                    {
                        "timestamp": timestamps,
                        "session_date": session_date,
                        "symbol": symbol,
                        "open": 100.0,
                        "high": 101.0,
                        "low": 99.0,
                        "close": 100.5,
                        "volume": 1_000.0,
                        "trade_count": 20,
                        "vwap": 100.25,
                        "source": "alpaca",
                        "feed": "sip",
                    }
                )
            )

    return pd.concat(
        frames,
        ignore_index=True,
    )


def test_cli_is_narrow_and_has_overwrite_control() -> None:
    arguments = runner.parse_args(
        [
            "--artifact-directory",
            "custom/day12",
            "--overwrite",
            "--generation-timestamp",
            "2026-07-27T12:00:00Z",
        ]
    )

    assert arguments.artifact_directory == Path(
        "custom/day12"
    )
    assert arguments.overwrite is True
    assert not hasattr(arguments, "dataset_path")


def test_dataset_audit_filters_only_spy_after_full_validation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bars = make_compact_canonical()
    monkeypatch.setattr(
        runner,
        "EXPECTED_CANONICAL_ROWS",
        len(bars),
    )
    monkeypatch.setattr(
        runner,
        "EXPECTED_SPY_ROWS",
        40,
    )
    monkeypatch.setattr(
        runner,
        "EXPECTED_SPY_SESSIONS",
        2,
    )

    canonical = runner._validate_canonical_bars(
        bars,
        manifest_sha256="b" * 64,
    )

    assert canonical.bars["symbol"].eq("SPY").all()
    assert len(canonical.bars) == 40
    assert canonical.audit.canonical_row_count == len(
        bars
    )


def test_dataset_audit_rejects_2026_and_unexpected_symbols(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bars = make_compact_canonical()
    monkeypatch.setattr(
        runner,
        "EXPECTED_CANONICAL_ROWS",
        len(bars),
    )
    monkeypatch.setattr(
        runner,
        "EXPECTED_SPY_ROWS",
        40,
    )
    monkeypatch.setattr(
        runner,
        "EXPECTED_SPY_SESSIONS",
        2,
    )
    locked = bars.copy(deep=True)
    locked.loc[
        locked.index[-1],
        "timestamp",
    ] = pd.Timestamp(
        "2026-01-02 14:30:00+00:00"
    )

    with pytest.raises(
        runner.Day12RunnerError,
        match="2026|development",
    ):
        runner._validate_canonical_bars(
            locked,
            manifest_sha256="b" * 64,
        )

    unexpected = bars.copy(deep=True)
    unexpected.loc[
        unexpected["symbol"].eq("IWM"),
        "symbol",
    ] = "DIA"

    with pytest.raises(
        runner.Day12RunnerError,
        match="symbols",
    ):
        runner._validate_canonical_bars(
            unexpected,
            manifest_sha256="b" * 64,
        )


def test_runner_source_uses_public_replay_study_without_strategy_math() -> None:
    source = Path(runner.__file__).read_text(
        encoding="utf-8"
    ).lower()

    assert "run_day12_replay_study" in source

    for token in (
        "build_trend_ratio_strategy",
        "build_ema_macd_strategy",
        "trend_ratio_sensitivity",
        "ema_macd_sensitivity",
        "day07",
        "day09",
    ):
        assert token not in source
