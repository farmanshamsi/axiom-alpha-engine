"""Alpaca historical market-data adapter."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Any

import pandas as pd
from alpaca.data.enums import Adjustment, DataFeed
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit

from cqf_al.data.config_loader import (
    load_alpaca_credentials,
    load_project_config,
)
from cqf_al.data.schemas import normalize_bars


class AlpacaDataError(RuntimeError):
    """Raised when Alpaca data cannot be retrieved or normalized."""


def _as_utc_datetime(value: str | datetime | pd.Timestamp) -> datetime:
    """Convert a datetime-like value to a timezone-aware UTC datetime."""

    timestamp = pd.Timestamp(value)

    if timestamp.tzinfo is None:
        timestamp = timestamp.tz_localize("UTC")
    else:
        timestamp = timestamp.tz_convert("UTC")

    return timestamp.to_pydatetime()


def _resolve_feed(feed_name: str) -> DataFeed:
    """Convert the configured feed name to Alpaca's enum."""

    feeds = {
        "iex": DataFeed.IEX,
        "sip": DataFeed.SIP,
    }

    try:
        return feeds[feed_name.lower()]
    except KeyError as exc:
        raise AlpacaDataError(
            f"Unsupported Alpaca stock feed: {feed_name!r}. "
            f"Supported feeds: {sorted(feeds)}"
        ) from exc


class AlpacaBarProvider:
    """Provider-independent adapter around Alpaca historical stock bars."""

    def __init__(
        self,
        *,
        config: dict[str, Any] | None = None,
        client: StockHistoricalDataClient | Any | None = None,
    ) -> None:
        self.config = config or load_project_config()

        feed_name = self.config["broker"].get("stock_data_feed", "iex")
        self.feed = _resolve_feed(feed_name)

        if client is None:
            credentials = load_alpaca_credentials(self.config)
            client = StockHistoricalDataClient(
                api_key=credentials.api_key,
                secret_key=credentials.secret_key,
            )

        self.client = client

    def fetch_bars(
        self,
        *,
        symbols: Sequence[str],
        start: str | datetime | pd.Timestamp,
        end: str | datetime | pd.Timestamp,
        timeframe_minutes: int = 1,
    ) -> pd.DataFrame:
        """Fetch and normalize historical equity bars."""

        clean_symbols = sorted(
            {
                symbol.strip().upper()
                for symbol in symbols
                if symbol.strip()
            }
        )

        if not clean_symbols:
            raise AlpacaDataError("At least one symbol is required.")

        if timeframe_minutes <= 0:
            raise AlpacaDataError(
                "timeframe_minutes must be a positive integer."
            )

        start_utc = _as_utc_datetime(start)
        end_utc = _as_utc_datetime(end)

        if start_utc >= end_utc:
            raise AlpacaDataError("Start time must precede end time.")

        request = StockBarsRequest(
            symbol_or_symbols=clean_symbols,
            timeframe=TimeFrame(
                timeframe_minutes,
                TimeFrameUnit.Minute,
            ),
            start=start_utc,
            end=end_utc,
            adjustment=Adjustment.ALL,
            feed=self.feed,
        )

        try:
            response = self.client.get_stock_bars(request)
        except Exception as exc:
            raise AlpacaDataError(
                "Alpaca historical-bar request failed."
            ) from exc

        try:
            frame = response.df.copy()
        except AttributeError as exc:
            raise AlpacaDataError(
                "Alpaca response did not expose a DataFrame."
            ) from exc

        if frame.empty:
            raise AlpacaDataError(
                "Alpaca returned no bars for the requested interval."
            )

        frame = frame.reset_index()

        return normalize_bars(
            frame,
            source="alpaca",
            feed=self.feed.value,
        )
