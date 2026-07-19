import pandas as pd

from cqf_al.data.alpaca_microstructure import (
    AlpacaMicrostructureProvider,
)


class FakeResponse:
    def __init__(self, frame: pd.DataFrame) -> None:
        self.df = frame


class FakeClient:
    def __init__(
        self,
        quotes: pd.DataFrame,
        trades: pd.DataFrame,
    ) -> None:
        self.quotes = quotes
        self.trades = trades

    def get_stock_quotes(self, request):
        return FakeResponse(self.quotes)

    def get_stock_trades(self, request):
        return FakeResponse(self.trades)


def make_provider() -> AlpacaMicrostructureProvider:
    quote_index = pd.MultiIndex.from_tuples(
        [
            (
                "SPY",
                pd.Timestamp(
                    "2025-12-15T14:30:00Z"
                ),
            )
        ],
        names=["symbol", "timestamp"],
    )

    trade_index = pd.MultiIndex.from_tuples(
        [
            (
                "SPY",
                pd.Timestamp(
                    "2025-12-15T14:30:00Z"
                ),
            )
        ],
        names=["symbol", "timestamp"],
    )

    quotes = pd.DataFrame(
        {
            "bid_price": [679.49],
            "bid_size": [100],
            "ask_price": [679.50],
            "ask_size": [200],
        },
        index=quote_index,
    )

    trades = pd.DataFrame(
        {
            "price": [679.50],
            "size": [50],
            "exchange": ["V"],
            "conditions": [["@" ]],
            "tape": ["C"],
        },
        index=trade_index,
    )

    return AlpacaMicrostructureProvider(
        config={
            "broker": {
                "stock_data_feed": "iex",
            }
        },
        client=FakeClient(quotes, trades),
    )


def test_fetch_quotes() -> None:
    provider = make_provider()

    result = provider.fetch_quotes(
        symbols=["SPY"],
        start="2025-12-15T14:30:00Z",
        end="2025-12-15T14:31:00Z",
    )

    assert len(result) == 1
    assert result.loc[0, "symbol"] == "SPY"
    assert result.loc[0, "bid_price"] == 679.49
    assert result.loc[0, "ask_price"] == 679.50


def test_fetch_trades() -> None:
    provider = make_provider()

    result = provider.fetch_trades(
        symbols=["SPY"],
        start="2025-12-15T14:30:00Z",
        end="2025-12-15T14:31:00Z",
    )

    assert len(result) == 1
    assert result.loc[0, "symbol"] == "SPY"
    assert result.loc[0, "price"] == 679.50
    assert result.loc[0, "size"] == 50
