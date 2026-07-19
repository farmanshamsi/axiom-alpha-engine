"""Alpaca historical quote and trade data adapter."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Any

import pandas as pd
from alpaca.data.enums import DataFeed
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import (
    StockQuotesRequest,
    StockTradesRequest,
)

from cqf_al.data.config_loader import (
    load_alpaca_credentials,
    load_project_config,
)
from cqf_al.data.schemas import (
    normalize_quotes,
    normalize_trades,
)


class AlpacaMicrostructureError(RuntimeError):
    """Raised when Alpaca quote or trade data cannot be retrieved."""


def _as_utc_datetime(
    value: str | datetime | pd.Timestamp,
) -> datetime:
    timestamp = pd.Timestamp(value)

    if timestamp.tzinfo is None:
        timestamp = timestamp.tz_localize("UTC")
    else:
        timestamp = timestamp.tz_convert("UTC")

    return timestamp.to_pydatetime()


def _resolve_feed(feed_name: str) -> DataFeed:
    feeds = {
        "iex": DataFeed.IEX,
        "sip": DataFeed.SIP,
    }

    try:
        return feeds[feed_name.lower()]
    except KeyError as exc:
        raise AlpacaMicrostructureError(
            f"Unsupported Alpaca feed: {feed_name!r}"
        ) from exc


class AlpacaMicrostructureProvider:
    """Fetch normalized historical quotes and trades."""

    def __init__(
        self,
        *,
        config: dict[str, Any] | None = None,
        client: StockHistoricalDataClient | Any | None = None,
    ) -> None:
        self.config = config or load_project_config()

        feed_name = self.config["broker"].get(
            "stock_data_feed",
            "iex",
        )
        self.feed = _resolve_feed(feed_name)

        if client is None:
            credentials = load_alpaca_credentials(self.config)

            client = StockHistoricalDataClient(
                api_key=credentials.api_key,
                secret_key=credentials.secret_key,
            )

        self.client = client

    @staticmethod
    def _clean_symbols(
        symbols: Sequence[str],
    ) -> list[str]:
        clean = sorted(
            {
                symbol.strip().upper()
                for symbol in symbols
                if symbol.strip()
            }
        )

        if not clean:
            raise AlpacaMicrostructureError(
                "At least one symbol is required."
            )

        return clean

    def fetch_quotes(
        self,
        *,
        symbols: Sequence[str],
        start: str | datetime | pd.Timestamp,
        end: str | datetime | pd.Timestamp,
    ) -> pd.DataFrame:
        """Fetch historical Level-1 bid and ask quotes."""

        start_utc = _as_utc_datetime(start)
        end_utc = _as_utc_datetime(end)

        if start_utc >= end_utc:
            raise AlpacaMicrostructureError(
                "Start time must precede end time."
            )

        request = StockQuotesRequest(
            symbol_or_symbols=self._clean_symbols(symbols),
            start=start_utc,
            end=end_utc,
            feed=self.feed,
        )

        try:
            response = self.client.get_stock_quotes(request)
            frame = response.df.copy().reset_index()
        except Exception as exc:
            raise AlpacaMicrostructureError(
                "Alpaca historical quote request failed."
            ) from exc

        if frame.empty:
            raise AlpacaMicrostructureError(
                "Alpaca returned no quotes."
            )

        return normalize_quotes(
            frame,
            source="alpaca",
            feed=self.feed.value,
        )

    def fetch_trades(
        self,
        *,
        symbols: Sequence[str],
        start: str | datetime | pd.Timestamp,
        end: str | datetime | pd.Timestamp,
    ) -> pd.DataFrame:
        """Fetch historical individual trades."""

        start_utc = _as_utc_datetime(start)
        end_utc = _as_utc_datetime(end)

        if start_utc >= end_utc:
            raise AlpacaMicrostructureError(
                "Start time must precede end time."
            )

        request = StockTradesRequest(
            symbol_or_symbols=self._clean_symbols(symbols),
            start=start_utc,
            end=end_utc,
            feed=self.feed,
        )

        try:
            response = self.client.get_stock_trades(request)
            frame = response.df.copy().reset_index()
        except Exception as exc:
            raise AlpacaMicrostructureError(
                "Alpaca historical trade request failed."
            ) from exc

        if frame.empty:
            raise AlpacaMicrostructureError(
                "Alpaca returned no trades."
            )

        return normalize_trades(
            frame,
            source="alpaca",
            feed=self.feed.value,
        )
