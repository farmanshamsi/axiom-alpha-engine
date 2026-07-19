"""Validate and resample the Day 03 SPY development sample."""

from pathlib import Path

import pandas as pd

from cqf_al.data.config_loader import (
    load_project_config,
    resolve_data_directories,
)
from cqf_al.data.local_store import LocalParquetStore
from cqf_al.data.resampling import resample_bars
from cqf_al.data.validators import assert_valid_bars


RAW_PATH = Path(
    "data/raw/bars/spy_1min_2025-12-15_iex.parquet"
)


def main() -> None:
    config = load_project_config()
    directories = resolve_data_directories(config)

    raw = pd.read_parquet(RAW_PATH)

    report = assert_valid_bars(
        raw,
        expected_minutes=1,
        exchange_timezone=config["market"]["exchange_timezone"],
    )

    print("Raw validation passed:", report.passed)
    print("Raw rows:", report.row_count)
    print("Internal missing bars:", report.internal_missing_bars)

    store = LocalParquetStore(
        data_root=directories["processed"],
        metadata_root=directories["metadata"] / "processed",
        allow_overwrite=False,
    )

    for minutes in (15, 30, 60):
        processed = resample_bars(
            raw,
            timeframe_minutes=minutes,
        )

        artifact = store.write(
            processed,
            dataset_kind="bars",
            dataset_id=f"spy_{minutes}min_2025-12-15_iex",
            metadata={
                "source_dataset": str(RAW_PATH),
                "source_sha256": (
                    "bb62191d6cf015d1ac24f680fdc8ac902"
                    "ae8fa1ce985badf8b9934ba52b4298e"
                ),
                "resampling_minutes": minutes,
                "aggregation": {
                    "open": "first",
                    "high": "maximum",
                    "low": "minimum",
                    "close": "last",
                    "volume": "sum",
                    "trade_count": "sum",
                    "vwap": "volume_weighted",
                },
            },
        )

        print(
            f"{minutes}-minute bars:",
            artifact.row_count,
            artifact.data_path,
        )


if __name__ == "__main__":
    main()
