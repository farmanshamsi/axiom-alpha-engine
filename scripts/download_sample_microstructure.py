"""Download a small quote and trade sample for Day 03."""

from cqf_al.data.alpaca_microstructure import (
    AlpacaMicrostructureProvider,
)
from cqf_al.data.local_store import LocalParquetStore


def main() -> None:
    symbols = ["SPY"]
    start = "2025-12-15T14:30:00Z"
    end = "2025-12-15T14:31:00Z"

    provider = AlpacaMicrostructureProvider()
    store = LocalParquetStore.from_project_config()

    quotes = provider.fetch_quotes(
        symbols=symbols,
        start=start,
        end=end,
    )

    trades = provider.fetch_trades(
        symbols=symbols,
        start=start,
        end=end,
    )

    quote_artifact = store.write(
        quotes,
        dataset_kind="quotes",
        dataset_id="spy_quotes_2025-12-15_1430_1431_iex",
        metadata={
            "provider": "alpaca",
            "feed": "iex",
            "symbols": symbols,
            "start_utc": start,
            "end_utc": end,
            "purpose": "Day 03 Level-1 quote test",
        },
    )

    trade_artifact = store.write(
        trades,
        dataset_kind="trades",
        dataset_id="spy_trades_2025-12-15_1430_1431_iex",
        metadata={
            "provider": "alpaca",
            "feed": "iex",
            "symbols": symbols,
            "start_utc": start,
            "end_utc": end,
            "purpose": "Day 03 trade data test",
        },
    )

    print("Quote rows:", quote_artifact.row_count)
    print("Quote data:", quote_artifact.data_path)
    print("Quote SHA256:", quote_artifact.sha256)

    print("Trade rows:", trade_artifact.row_count)
    print("Trade data:", trade_artifact.data_path)
    print("Trade SHA256:", trade_artifact.sha256)


if __name__ == "__main__":
    main()
