"""Synthetic contract tests for the Day 8 runner."""

from __future__ import annotations

import copy

import pandas as pd
import pytest

from scripts.run_ema_macd_baseline import (
    ARTIFACT_RELATIVE_DIRECTORY,
    DEVELOPMENT_DATASET_ID,
    _extract_spy_features,
    _validate_development_manifest,
)


VALID_SHA256 = "a" * 64


def make_manifest(
    *,
    row_count: int = 10,
) -> dict[str, object]:
    """Create one valid synthetic processed-data manifest."""

    return {
        "dataset_id": DEVELOPMENT_DATASET_ID,
        "dataset_kind": "bars",
        "row_count": row_count,
        "sha256": VALID_SHA256,
    }


def make_feature_bars() -> pd.DataFrame:
    """Create deterministic multi-symbol return features."""

    return pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                [
                    "2025-01-02 14:45:00+00:00",
                    "2025-01-02 14:30:00+00:00",
                    "2025-01-02 14:30:00+00:00",
                ]
            ),
            "symbol": ["spy", " SPY ", "QQQ"],
            "session_date": [
                "2025-01-02",
                "2025-01-02",
                "2025-01-02",
            ],
            "close": [101.0, 100.0, 200.0],
            "close_to_close_simple_return": [
                0.01,
                float("nan"),
                float("nan"),
            ],
        }
    )


def test_runner_constants_preserve_frozen_contract() -> None:
    assert DEVELOPMENT_DATASET_ID == (
        "spy_qqq_iwm_15min_"
        "2020-01-02_2025-12-31_"
        "sip_v3_development_canonical"
    )
    assert ARTIFACT_RELATIVE_DIRECTORY.as_posix() == (
        "artifacts/day08/ema_macd_baseline_v1"
    )


def test_valid_manifest_returns_normalized_digest() -> None:
    manifest = make_manifest(row_count=10)
    manifest["sha256"] = VALID_SHA256.upper()

    digest = _validate_development_manifest(
        manifest,
        expected_row_count=10,
    )

    assert digest == VALID_SHA256


def test_manifest_without_sha256_is_rejected() -> None:
    manifest = make_manifest()
    manifest.pop("sha256")

    with pytest.raises(
        RuntimeError,
        match="sha256",
    ):
        _validate_development_manifest(
            manifest,
            expected_row_count=10,
        )


def test_manifest_dataset_identifier_mismatch_is_rejected() -> None:
    manifest = make_manifest()
    manifest["dataset_id"] = "different-dataset"

    with pytest.raises(
        RuntimeError,
        match="dataset_id",
    ):
        _validate_development_manifest(
            manifest,
            expected_row_count=10,
        )


def test_manifest_row_count_mismatch_is_rejected() -> None:
    with pytest.raises(
        RuntimeError,
        match="row_count",
    ):
        _validate_development_manifest(
            make_manifest(row_count=11),
            expected_row_count=10,
        )


def test_spy_extraction_is_sorted_and_does_not_mutate_input() -> None:
    feature_bars = make_feature_bars()
    original = copy.deepcopy(feature_bars)

    spy_bars = _extract_spy_features(feature_bars)

    pd.testing.assert_frame_equal(
        feature_bars,
        original,
    )

    assert spy_bars["symbol"].tolist() == [
        "SPY",
        "SPY",
    ]
    assert spy_bars["timestamp"].is_monotonic_increasing
    assert spy_bars["close"].tolist() == [
        100.0,
        101.0,
    ]


def test_spy_extraction_rejects_empty_symbol_sample() -> None:
    feature_bars = make_feature_bars()
    feature_bars["symbol"] = "QQQ"

    with pytest.raises(
        RuntimeError,
        match="cannot be empty",
    ):
        _extract_spy_features(feature_bars)
