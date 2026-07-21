"""Development-only market-data chunking and assembly."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

import pandas as pd

from cqf_al.data.sample_windows import (
    SampleWindow,
    SampleWindowError,
)


class DevelopmentDatasetError(ValueError):
    """Raised when development data cannot be assembled safely."""


@dataclass(frozen=True)
class DevelopmentChunk:
    """One immutable calendar-year development-data request."""

    label: str
    start: pd.Timestamp
    end_exclusive: pd.Timestamp

    def request_bounds(self) -> tuple[datetime, datetime]:
        """Return API-compatible UTC request boundaries."""

        return (
            self.start.to_pydatetime(),
            self.end_exclusive.to_pydatetime(),
        )


def _clean_symbols(symbols: Sequence[str]) -> list[str]:
    """Normalize and validate the development universe."""

    clean = sorted(
        {
            str(symbol).strip().upper()
            for symbol in symbols
            if str(symbol).strip()
        }
    )

    if not clean:
        raise DevelopmentDatasetError(
            "At least one development symbol is required."
        )

    return clean


def build_yearly_development_chunks(
    window: SampleWindow,
) -> list[DevelopmentChunk]:
    """Split the development sample into calendar-year chunks."""

    start_year = window.development_start.year
    final_included_year = (
        window.development_end_exclusive
        - pd.Timedelta(days=1)
    ).year

    chunks: list[DevelopmentChunk] = []

    for year in range(start_year, final_included_year + 1):
        year_start = pd.Timestamp(
            year=year,
            month=1,
            day=1,
            tz="UTC",
        )

        following_year = pd.Timestamp(
            year=year + 1,
            month=1,
            day=1,
            tz="UTC",
        )

        chunk_start = max(
            window.development_start,
            year_start,
        )

        chunk_end = min(
            window.development_end_exclusive,
            following_year,
        )

        if chunk_start >= chunk_end:
            continue

        chunks.append(
            DevelopmentChunk(
                label=str(year),
                start=chunk_start,
                end_exclusive=chunk_end,
            )
        )

    if not chunks:
        raise DevelopmentDatasetError(
            "Development sample produced no calendar-year chunks."
        )

    return chunks


def combine_canonical_bar_chunks(
    frames: Sequence[pd.DataFrame],
    *,
    window: SampleWindow,
    expected_symbols: Sequence[str],
) -> pd.DataFrame:
    """Combine canonical yearly bar chunks with leakage controls."""

    symbols = _clean_symbols(expected_symbols)

    if not frames:
        raise DevelopmentDatasetError(
            "No canonical bar chunks were supplied."
        )

    checked_frames: list[pd.DataFrame] = []

    required_columns = {
        "timestamp",
        "symbol",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "trade_count",
        "vwap",
        "source",
        "feed",
    }

    for index, frame in enumerate(frames):
        if frame.empty:
            raise DevelopmentDatasetError(
                f"Canonical chunk {index} is empty."
            )

        missing = required_columns.difference(frame.columns)

        if missing:
            raise DevelopmentDatasetError(
                f"Canonical chunk {index} is missing columns: "
                f"{sorted(missing)}"
            )

        checked_frames.append(frame.copy())

    combined = pd.concat(
        checked_frames,
        ignore_index=True,
        sort=False,
    )

    try:
        combined = window.validate_development_frame(combined)
    except SampleWindowError as exc:
        raise DevelopmentDatasetError(
            "Combined dataset violated the development window."
        ) from exc

    combined["symbol"] = (
        combined["symbol"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    actual_symbols = set(
        combined["symbol"].dropna().tolist()
    )

    expected_symbol_set = set(symbols)

    missing_symbols = expected_symbol_set.difference(
        actual_symbols
    )

    unexpected_symbols = actual_symbols.difference(
        expected_symbol_set
    )

    if missing_symbols or unexpected_symbols:
        raise DevelopmentDatasetError(
            "Development-universe mismatch. "
            f"Missing: {sorted(missing_symbols)}; "
            f"unexpected: {sorted(unexpected_symbols)}."
        )

    duplicate_mask = combined.duplicated(
        ["symbol", "timestamp"],
        keep=False,
    )

    if duplicate_mask.any():
        duplicate_count = int(duplicate_mask.sum())

        raise DevelopmentDatasetError(
            "Duplicate symbol/timestamp bars detected. "
            f"Affected rows: {duplicate_count}."
        )

    if combined["source"].nunique(dropna=False) != 1:
        raise DevelopmentDatasetError(
            "Combined development bars contain multiple sources."
        )

    if combined["feed"].nunique(dropna=False) != 1:
        raise DevelopmentDatasetError(
            "Combined development bars contain multiple feeds."
        )

    combined = combined.sort_values(
        ["symbol", "timestamp"],
        kind="stable",
    ).reset_index(drop=True)

    for symbol, symbol_frame in combined.groupby(
        "symbol",
        sort=True,
    ):
        if symbol_frame.empty:
            raise DevelopmentDatasetError(
                f"No observations found for {symbol}."
            )

        if not symbol_frame["timestamp"].is_monotonic_increasing:
            raise DevelopmentDatasetError(
                f"Timestamps are not increasing for {symbol}."
            )

    return combined
