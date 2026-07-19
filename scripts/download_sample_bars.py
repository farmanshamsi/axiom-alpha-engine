"""Download and preserve a small development-period Alpaca sample."""

from cqf_al.data.alpaca_provider import AlpacaBarProvider
from cqf_al.data.local_store import LocalParquetStore


def main() -> None:
    symbols = ["SPY"]
    start = "2025-12-15T14:30:00Z"
    end = "2025-12-15T21:00:00Z"

    provider = AlpacaBarProvider()
    store = LocalParquetStore.from_project_config()

    bars = provider.fetch_bars(
        symbols=symbols,
        start=start,
        end=end,
        timeframe_minutes=1,
    )

    artifact = store.write(
        bars,
        dataset_kind="bars",
        dataset_id="spy_1min_2025-12-15_iex",
        metadata={
            "provider": "alpaca",
            "feed": "iex",
            "symbols": symbols,
            "timeframe_minutes": 1,
            "start_utc": start,
            "end_utc": end,
            "purpose": "Day 03 development-period pipeline test",
        },
    )

    print("Rows:", artifact.row_count)
    print("Data:", artifact.data_path)
    print("Manifest:", artifact.manifest_path)
    print("SHA256:", artifact.sha256)


if __name__ == "__main__":
    main()
