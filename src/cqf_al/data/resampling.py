"""Time-bar construction from normalized one-minute OHLCV data."""

from __future__ import annotations

import pandas as pd

from cqf_al.data.schemas import normalize_bars
from cqf_al.data.validators import assert_valid_bars


class ResamplingError(ValueError):
    """Raised when market bars cannot be resampled safely."""


def resample_bars(
    frame: pd.DataFrame,
    *,
    timeframe_minutes: int,
) -> pd.DataFrame:
    """Aggregate one-minute bars into larger regular time bars."""

    if timeframe_minutes <= 1:
        raise ResamplingError(
            "timeframe_minutes must be greater than one."
        )

    assert_valid_bars(frame, expected_minutes=1)

    if frame["source"].nunique() != 1:
        raise ResamplingError(
            "Input frame must contain exactly one data source."
        )

    if frame["feed"].nunique() != 1:
        raise ResamplingError(
            "Input frame must contain exactly one market-data feed."
        )

    source = str(frame["source"].iloc[0])
    feed = str(frame["feed"].iloc[0])

    pieces: list[pd.DataFrame] = []
    rule = f"{timeframe_minutes}min"

    for symbol, symbol_frame in frame.groupby("symbol", sort=True):
        working = (
            symbol_frame
            .sort_values("timestamp")
            .set_index("timestamp")
            .copy()
        )

        working["_vwap_notional"] = (
            working["vwap"].fillna(working["close"])
            * working["volume"]
        )

        resampler = working.resample(
            rule,
            label="left",
            closed="left",
            origin="start_day",
            offset="30min",
        )

        result = resampler.agg(
            {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
                "trade_count": "sum",
                "_vwap_notional": "sum",
            }
        )

        result = result.dropna(
            subset=["open", "high", "low", "close"]
        )

        result["vwap"] = (
            result["_vwap_notional"]
            / result["volume"].replace(0, pd.NA)
        )

        result["symbol"] = symbol
        result = result.drop(columns="_vwap_notional")
        result = result.reset_index()

        pieces.append(result)

    if not pieces:
        raise ResamplingError("Resampling produced no bars.")

    combined = pd.concat(pieces, ignore_index=True)

    normalized = normalize_bars(
        combined,
        source=source,
        feed=feed,
    )

    assert_valid_bars(
        normalized,
        expected_minutes=timeframe_minutes,
    )

    return normalized
