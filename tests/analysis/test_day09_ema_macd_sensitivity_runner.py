"""Synthetic contract tests for the Day 9 runner."""

from __future__ import annotations

import copy

import numpy as np
import pandas as pd
import pytest

from scripts.run_ema_macd_sensitivity import (
    ARTIFACT_RELATIVE_DIRECTORY,
    DAILY_VOLATILITY_RELATIVE_PATH,
    DEVELOPMENT_DATASET_ID,
    _extract_spy_features,
    _select_baseline_row,
    _select_highest_finite_row,
    _validate_daily_volatility,
    _validate_development_manifest,
)


VALID_SHA256 = "a" * 64


def make_manifest(
    *,
    row_count: int = 4,
) -> dict[str, object]:
    return {
        "dataset_id": DEVELOPMENT_DATASET_ID,
        "dataset_kind": "bars",
        "row_count": row_count,
        "sha256": VALID_SHA256,
    }


def make_feature_bars() -> pd.DataFrame:
    timestamps = pd.to_datetime(
        [
            "2025-01-02 14:45:00+00:00",
            "2025-01-02 14:30:00+00:00",
            "2025-01-03 14:30:00+00:00",
            "2025-01-02 14:30:00+00:00",
        ]
    )

    return pd.DataFrame(
        {
            "timestamp": timestamps,
            "symbol": [
                "spy",
                " SPY ",
                "SPY",
                "QQQ",
            ],
            "session_date": [
                "2025-01-02",
                "2025-01-02",
                "2025-01-03",
                "2025-01-02",
            ],
            "close": [
                101.0,
                100.0,
                102.0,
                200.0,
            ],
            "close_to_close_simple_return": [
                0.01,
                np.nan,
                0.009900990099,
                np.nan,
            ],
        }
    )


def make_daily_volatility() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "symbol": ["SPY", "SPY"],
            "session_date": [
                "2025-01-02",
                "2025-01-03",
            ],
            "annualized_total_realized_volatility": [
                0.20,
                0.25,
            ],
        }
    )


def make_parameter_results() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "configuration_id": [
                "f008_s026_m009_b0p00050",
                "f012_s026_m009_b0p00050",
                "f016_s026_m009_b0p00050",
            ],
            "fast_window": [8, 12, 16],
            "slow_window": [26, 26, 26],
            "signal_window": [9, 9, 9],
            "neutral_band": [
                0.0005,
                0.0005,
                0.0005,
            ],
            "net_sharpe_ratio": [
                0.30,
                0.20,
                0.30,
            ],
        }
    )


def test_runner_constants_preserve_frozen_paths() -> None:
    assert DEVELOPMENT_DATASET_ID == (
        "spy_qqq_iwm_15min_"
        "2020-01-02_2025-12-31_"
        "sip_v3_development_canonical"
    )
    assert (
        DAILY_VOLATILITY_RELATIVE_PATH.as_posix()
        == (
            "artifacts/day05/"
            "volatility_seasonality_v1/"
            "data/daily_volatility.parquet"
        )
    )
    assert (
        ARTIFACT_RELATIVE_DIRECTORY.as_posix()
        == (
            "artifacts/day09/"
            "ema_macd_sensitivity_v1"
        )
    )


def test_manifest_validation_normalizes_digest() -> None:
    manifest = make_manifest()
    manifest["sha256"] = VALID_SHA256.upper()

    assert _validate_development_manifest(
        manifest,
        expected_row_count=4,
    ) == VALID_SHA256


def test_manifest_validation_rejects_row_mismatch() -> None:
    with pytest.raises(
        RuntimeError,
        match="row_count",
    ):
        _validate_development_manifest(
            make_manifest(row_count=5),
            expected_row_count=4,
        )


def test_spy_and_volatility_validation_is_non_mutating() -> None:
    features = make_feature_bars()
    volatility = make_daily_volatility()

    original_features = copy.deepcopy(features)
    original_volatility = copy.deepcopy(
        volatility
    )

    validated_volatility = (
        _validate_daily_volatility(
            volatility,
            development_start=pd.Timestamp(
                "2020-01-02"
            ),
            development_end_inclusive=pd.Timestamp(
                "2025-12-31"
            ),
        )
    )
    spy = _extract_spy_features(
        features,
        validated_volatility,
    )

    pd.testing.assert_frame_equal(
        features,
        original_features,
    )
    pd.testing.assert_frame_equal(
        volatility,
        original_volatility,
    )

    assert spy["symbol"].tolist() == [
        "SPY",
        "SPY",
        "SPY",
    ]
    assert spy["timestamp"].is_monotonic_increasing
    assert spy["session_date"].dt.tz is None
    assert spy["close"].tolist() == [
        100.0,
        101.0,
        102.0,
    ]


def test_missing_regime_session_is_rejected() -> None:
    volatility = make_daily_volatility().iloc[
        :1
    ]

    validated = _validate_daily_volatility(
        volatility,
        development_start=pd.Timestamp(
            "2020-01-02"
        ),
        development_end_inclusive=pd.Timestamp(
            "2025-12-31"
        ),
    )

    with pytest.raises(
        RuntimeError,
        match="missing Day 5 volatility coverage",
    ):
        _extract_spy_features(
            make_feature_bars(),
            validated,
        )


def test_baseline_must_appear_exactly_once() -> None:
    parameter_results = make_parameter_results()

    baseline = _select_baseline_row(
        parameter_results
    )

    assert baseline["configuration_id"] == (
        "f012_s026_m009_b0p00050"
    )

    duplicated = pd.concat(
        [
            parameter_results,
            parameter_results.iloc[[1]],
        ],
        ignore_index=True,
    )

    with pytest.raises(
        RuntimeError,
        match="exactly once",
    ):
        _select_baseline_row(duplicated)


def test_highest_finite_row_uses_stable_tie_break() -> None:
    parameter_results = make_parameter_results()

    selected = _select_highest_finite_row(
        parameter_results,
        value_column="net_sharpe_ratio",
    )

    assert selected["configuration_id"] == (
        "f008_s026_m009_b0p00050"
    )

    parameter_results[
        "net_sharpe_ratio"
    ] = np.nan

    with pytest.raises(
        RuntimeError,
        match="No finite",
    ):
        _select_highest_finite_row(
            parameter_results,
            value_column="net_sharpe_ratio",
        )
