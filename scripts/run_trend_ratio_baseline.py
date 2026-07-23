"""Run the predeclared Day 6 development-only trend baseline."""

from __future__ import annotations

from pathlib import Path
from typing import Final

from cqf_al.analysis.day06_trend_baseline import (
    ANNUALIZATION_FACTOR,
    write_trend_baseline_artifacts,
)
from cqf_al.analysis.eda_features import (
    build_return_features,
)
from cqf_al.data.config_loader import (
    find_project_root,
    load_project_config,
)
from cqf_al.data.local_store import LocalParquetStore
from cqf_al.data.sample_windows import SampleWindow
from cqf_al.strategies.trend_ratio import (
    TrendRatioParameters,
    build_trend_ratio_strategy,
)


DEVELOPMENT_DATASET_ID: Final[str] = (
    "spy_qqq_iwm_15min_"
    "2020-01-02_2025-12-31_"
    "sip_v3_development_canonical"
)

ARTIFACT_RELATIVE_DIRECTORY: Final[Path] = Path(
    "artifacts/day06/trend_ratio_baseline_v1"
)

SYMBOL: Final[str] = "SPY"
SHORT_WINDOW: Final[int] = 8
LONG_WINDOW: Final[int] = 32
NEUTRAL_BAND: Final[float] = 0.001
COST_BPS_PER_TURNOVER: Final[float] = 1.0
PRICE_COLUMN: Final[str] = "close"
RETURN_COLUMN: Final[str] = (
    "close_to_close_simple_return"
)


def main() -> None:
    """Execute the fixed development-only baseline."""
    config = load_project_config()
    sample_window = SampleWindow.from_project_config(
        config
    )

    store = LocalParquetStore.from_project_config(
        config,
        tier="processed",
    )

    bars = store.read(
        dataset_kind="bars",
        dataset_id=DEVELOPMENT_DATASET_ID,
        verify_hash=True,
    )
    bars = sample_window.validate_development_frame(
        bars
    )

    manifest = store.read_manifest(
        dataset_kind="bars",
        dataset_id=DEVELOPMENT_DATASET_ID,
    )

    if "symbol" not in bars.columns:
        raise RuntimeError(
            "Permitted development dataset has no symbol column."
        )

    symbols = set(
        bars["symbol"]
        .astype("string")
        .str.strip()
        .str.upper()
        .dropna()
    )

    if SYMBOL not in symbols:
        raise RuntimeError(
            "Permitted development dataset does not contain SPY."
        )

    features = build_return_features(
        bars
    )

    spy_bars = (
        features.bars.loc[
            features.bars["symbol"].eq(SYMBOL)
        ]
        .copy()
        .reset_index(drop=True)
    )

    if spy_bars.empty:
        raise RuntimeError(
            "SPY return features cannot be empty."
        )

    parameters = TrendRatioParameters(
        short_window=SHORT_WINDOW,
        long_window=LONG_WINDOW,
        neutral_band=NEUTRAL_BAND,
        cost_bps_per_turnover=(
            COST_BPS_PER_TURNOVER
        ),
        price_column=PRICE_COLUMN,
        return_column=RETURN_COLUMN,
    )

    baseline = build_trend_ratio_strategy(
        spy_bars,
        parameters=parameters,
    )

    metadata = {
        "artifact_version": (
            "trend_ratio_baseline_v1"
        ),
        "dataset_identifier": (
            DEVELOPMENT_DATASET_ID
        ),
        "dataset_manifest_sha256": (
            manifest["sha256"]
        ),
        "symbol": SYMBOL,
        "frequency": "15-minute",
        "sample_start": (
            baseline.observations[
                "timestamp"
            ].min().isoformat()
        ),
        "sample_end": (
            baseline.observations[
                "timestamp"
            ].max().isoformat()
        ),
        "observations": int(
            len(baseline.observations)
        ),
        "development_window_start": (
            sample_window.development_start
            .date()
            .isoformat()
        ),
        "development_window_end": (
            sample_window.development_end_inclusive
            .date()
            .isoformat()
        ),
        "locked_period_accessed": False,
        "short_window": SHORT_WINDOW,
        "long_window": LONG_WINDOW,
        "neutral_band": NEUTRAL_BAND,
        "price_column": PRICE_COLUMN,
        "return_column": RETURN_COLUMN,
        "transaction_cost_convention": (
            "One basis point per unit of absolute "
            "position change; direct reversal turnover is 2."
        ),
        "cost_bps_per_turnover": (
            COST_BPS_PER_TURNOVER
        ),
        "annualization_factor": (
            ANNUALIZATION_FACTOR
        ),
        "risk_free_rate_convention": "zero",
        "signal_timing": (
            "Signal z_t uses prices through bar t."
        ),
        "position_timing": (
            "Position p_t equals z_(t-1)."
        ),
        "overnight_position_rule": (
            "Positions may carry overnight."
        ),
        "session_boundary_rule": (
            "Rolling averages do not reset at "
            "session boundaries."
        ),
        "signal_warmup_observations": (
            LONG_WINDOW - 1
        ),
        "position_warmup_observations": (
            LONG_WINDOW
        ),
    }

    output_dir = (
        find_project_root()
        / ARTIFACT_RELATIVE_DIRECTORY
    )

    paths = write_trend_baseline_artifacts(
        output_dir=output_dir,
        observations=baseline.observations,
        diagnostics=baseline.diagnostics,
        metadata=metadata,
    )

    print(
        "===== DAY 6 TREND-RATIO BASELINE ====="
    )
    print(
        "Development dataset:",
        DEVELOPMENT_DATASET_ID,
    )
    print(
        "Manifest SHA256:",
        manifest["sha256"],
    )
    print(
        "SPY observations:",
        len(baseline.observations),
    )
    print(
        "Sample start:",
        metadata["sample_start"],
    )
    print(
        "Sample end:",
        metadata["sample_end"],
    )
    print(
        "Locked period accessed:",
        metadata["locked_period_accessed"],
    )
    print("Artifacts:")

    for filename in paths:
        print(filename)

    print(
        "DAY 6 TREND-RATIO BASELINE PASSED"
    )


if __name__ == "__main__":
    main()
