import pandas as pd
import pytest

from cqf_al.data.development_dataset import (
    DevelopmentDatasetError,
    build_yearly_development_chunks,
    combine_canonical_bar_chunks,
)
from cqf_al.data.sample_windows import SampleWindow


def sample_window() -> SampleWindow:
    return SampleWindow.from_project_config(
        {
            "sample": {
                "development_start": "2020-01-02",
                "development_end": "2025-12-31",
                "final_test_start": "2026-01-02",
                "final_test_end": "2026-06-30",
            }
        }
    )


def make_bars(
    *,
    symbol: str,
    timestamps: list[str],
) -> pd.DataFrame:
    row_count = len(timestamps)

    return pd.DataFrame(
        {
            "timestamp": timestamps,
            "symbol": [symbol] * row_count,
            "open": [100.0] * row_count,
            "high": [101.0] * row_count,
            "low": [99.0] * row_count,
            "close": [100.5] * row_count,
            "volume": [1000.0] * row_count,
            "trade_count": [100] * row_count,
            "vwap": [100.25] * row_count,
            "source": ["alpaca"] * row_count,
            "feed": ["iex"] * row_count,
        }
    )


def test_yearly_chunks_cover_development_window() -> None:
    chunks = build_yearly_development_chunks(
        sample_window()
    )

    assert [chunk.label for chunk in chunks] == [
        "2020",
        "2021",
        "2022",
        "2023",
        "2024",
        "2025",
    ]

    assert chunks[0].start == pd.Timestamp(
        "2020-01-02T00:00:00Z"
    )

    assert chunks[-1].end_exclusive == pd.Timestamp(
        "2026-01-01T00:00:00Z"
    )

    for previous, following in zip(
        chunks,
        chunks[1:],
    ):
        assert previous.end_exclusive == following.start


def test_chunks_are_combined_and_sorted() -> None:
    frames = [
        make_bars(
            symbol="SPY",
            timestamps=["2021-01-04T14:30:00Z"],
        ),
        make_bars(
            symbol="QQQ",
            timestamps=["2020-01-02T14:30:00Z"],
        ),
        make_bars(
            symbol="IWM",
            timestamps=["2020-01-02T14:30:00Z"],
        ),
    ]

    result = combine_canonical_bar_chunks(
        frames,
        window=sample_window(),
        expected_symbols=["SPY", "QQQ", "IWM"],
    )

    assert result["symbol"].tolist() == [
        "IWM",
        "QQQ",
        "SPY",
    ]

    assert set(result["symbol"]) == {
        "SPY",
        "QQQ",
        "IWM",
    }


def test_duplicate_symbol_timestamp_is_rejected() -> None:
    duplicate = make_bars(
        symbol="SPY",
        timestamps=[
            "2020-01-02T14:30:00Z",
            "2020-01-02T14:30:00Z",
        ],
    )

    frames = [
        duplicate,
        make_bars(
            symbol="QQQ",
            timestamps=["2020-01-02T14:30:00Z"],
        ),
        make_bars(
            symbol="IWM",
            timestamps=["2020-01-02T14:30:00Z"],
        ),
    ]

    with pytest.raises(
        DevelopmentDatasetError,
        match="Duplicate symbol/timestamp",
    ):
        combine_canonical_bar_chunks(
            frames,
            window=sample_window(),
            expected_symbols=["SPY", "QQQ", "IWM"],
        )


def test_missing_expected_symbol_is_rejected() -> None:
    frames = [
        make_bars(
            symbol="SPY",
            timestamps=["2020-01-02T14:30:00Z"],
        ),
        make_bars(
            symbol="QQQ",
            timestamps=["2020-01-02T14:30:00Z"],
        ),
    ]

    with pytest.raises(
        DevelopmentDatasetError,
        match="Missing: \\['IWM'\\]",
    ):
        combine_canonical_bar_chunks(
            frames,
            window=sample_window(),
            expected_symbols=["SPY", "QQQ", "IWM"],
        )


def test_locked_test_observation_is_rejected() -> None:
    frames = [
        make_bars(
            symbol="SPY",
            timestamps=["2026-01-02T14:30:00Z"],
        ),
        make_bars(
            symbol="QQQ",
            timestamps=["2020-01-02T14:30:00Z"],
        ),
        make_bars(
            symbol="IWM",
            timestamps=["2020-01-02T14:30:00Z"],
        ),
    ]

    with pytest.raises(
        DevelopmentDatasetError,
        match="violated the development window",
    ):
        combine_canonical_bar_chunks(
            frames,
            window=sample_window(),
            expected_symbols=["SPY", "QQQ", "IWM"],
        )
