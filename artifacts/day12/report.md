# Day 12 — Deterministic Trend-Family Event Replay

## 1. Objective and scope

Day 12 validates deterministic historical event replay for SPY 15-minute
development bars from 2020-01-02 through 2025-12-31. It evaluates the frozen
Day 6 Trend Ratio and Day 8 EMA/MACD baselines without parameter selection.

## 2. Frozen constraints

- SPY and 15-minute bars only.
- Development data only; the locked 2026 period was not accessed.
- Frozen configuration identifiers and one basis point per unit turnover.
- No tuning, optimisation, sensitivity-winner use, profitability gate, or
  strategy selection. This report does not select a winner.

| strategy | configuration_id | parameters |
| --- | --- | --- |
| trend_ratio | trend_ratio_day06_baseline_v1 | {"cost_bps_per_turnover": 1.0, "long_window": 32, "neutral_band": 0.001, "price_column": "close", "return_column": "close_to_close_simple_return", "short_window": 8} |
| ema_macd | ema_macd_day08_baseline_v1 | {"cost_bps_per_turnover": 1.0, "fast_window": 12, "neutral_band": 0.0005, "price_column": "close", "return_column": "close_to_close_simple_return", "signal_window": 9, "slow_window": 26} |

## 3. Event model

Each immutable replay record is one of: market bar, signal, target-position
order, fill, or portfolio snapshot. Orders express a normalized target
position in `-1, 0, 1`; they do not model shares or an order book.

## 4. Exact per-bar event ordering

Events are globally sequenced as market bar, optional fill, portfolio
snapshot, signal, and optional target-position order. All events for one bar
precede every event for the next bar. A terminal signal is retained, while an
order that cannot execute inside the replay is omitted.

## 5. One-observation execution delay

The completed-bar target `q_t` becomes executed position `p_(t+1)`. The first
bar starts neutral, so no same-bar signal can earn that bar's return.

## 6. Neutral initial and reset conventions

Every independent replay begins with executed position zero, no pending order,
position eligibility false, turnover and transaction cost zero, and equity
one. State persists across ordinary sessions. No pre-evaluation state or P&L
is carried into an evaluation interval.

## 7. Return-ledger and normalized-notional accounting

For previous equity `E`, executed position `p`, asset return `r`, turnover
`|p-p_prev|`, and fractional cost `c`:

- gross return = `p * r`
- net return = `p * r - c`
- transaction-cost amount = `E * c`
- cash = `E * (1 - p) - E * c`
- holdings = `p * E * (1 + r)`
- ending equity = `E * (1 + p * r - c)`
- cash plus holdings equals ending equity

## 8. Canonical development-data coverage

- Loader path: `data/processed/bars/spy_qqq_iwm_15min_2020-01-02_2025-12-31_sip_v3_development_canonical.parquet`
- Dataset identifier: `spy_qqq_iwm_15min_2020-01-02_2025-12-31_sip_v3_development_canonical`
- Canonical rows before SPY filtering: 117192
- SPY rows: 39064
- SPY sessions: 1508
- Minimum timestamp: 2020-01-02T14:30:00+00:00
- Maximum timestamp: 2025-12-31T20:45:00+00:00

## 9. Results for both frozen strategies

| strategy | symbol | frequency | configuration_id | observations | sessions | start_timestamp | end_timestamp | events | initial_executed_position | initial_position_eligible | initial_turnover | initial_transaction_cost | initial_previous_equity | final_equity | event_sha256 | observation_sha256 | deterministic_replay | input_mutated | locked_2026_accessed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| trend_ratio | SPY | 15min | trend_ratio_day06_baseline_v1 | 39064 | 1508 | 2020-01-02T14:30:00+00:00 | 2025-12-31T20:45:00+00:00 | 122626 | 0 | False | 0.000000 | 0.000000 | 1.000000 | 0.958766 | 4f147e9ff5391f604532ac1106e36cb36f48b6c7a23135c5900970ad184ee92c | 5824f532c867bc55aea8f4a1dc977c705a620b0eb7bcca634d2af8d032921205 | True | False | False |
| ema_macd | SPY | 15min | ema_macd_day08_baseline_v1 | 39064 | 1508 | 2020-01-02T14:30:00+00:00 | 2025-12-31T20:45:00+00:00 | 123798 | 0 | False | 0.000000 | 0.000000 | 1.000000 | 0.687177 | 4bcd8f02f5ce742b342fb6185189fbb69777ee58306daa3844f57260518a7efe | 25e47dc097a0a0db29fac75e5e40db3f20bf83234ef227dc113fa676d7bd8378 | True | False | False |

## 10. Vectorised versus event-driven parity

The vectorised builders were executed independently as validation references;
their execution columns were not replay inputs. Every exact mismatch count and
every numeric maximum absolute difference is reported below.

| strategy | comparison | comparison_type | row_count | maximum_absolute_difference | mismatch_count | tolerance | passed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| trend_ratio | target_position | exact | 39064 | 0.000000 | 0 | 0.000000 | True |
| trend_ratio | signal_available | exact | 39064 | 0.000000 | 0 | 0.000000 | True |
| trend_ratio | executed_position | exact | 39064 | 0.000000 | 0 | 0.000000 | True |
| trend_ratio | position_eligible | exact | 39064 | 0.000000 | 0 | 0.000000 | True |
| trend_ratio | turnover | numeric | 39064 | 0.000000 | 0 | 0.000000 | True |
| trend_ratio | transaction_cost | numeric | 39064 | 0.000000 | 0 | 0.000000 | True |
| trend_ratio | gross_strategy_return | numeric | 39064 | 0.000000 | 0 | 0.000000 | True |
| trend_ratio | net_strategy_return | numeric | 39064 | 0.000000 | 0 | 0.000000 | True |
| ema_macd | target_position | exact | 39064 | 0.000000 | 0 | 0.000000 | True |
| ema_macd | signal_available | exact | 39064 | 0.000000 | 0 | 0.000000 | True |
| ema_macd | executed_position | exact | 39064 | 0.000000 | 0 | 0.000000 | True |
| ema_macd | position_eligible | exact | 39064 | 0.000000 | 0 | 0.000000 | True |
| ema_macd | turnover | numeric | 39064 | 0.000000 | 0 | 0.000000 | True |
| ema_macd | transaction_cost | numeric | 39064 | 0.000000 | 0 | 0.000000 | True |
| ema_macd | gross_strategy_return | numeric | 39064 | 0.000000 | 0 | 0.000000 | True |
| ema_macd | net_strategy_return | numeric | 39064 | 0.000000 | 0 | 0.000000 | True |

## 11. Event counts by type

| strategy | event_type | count |
| --- | --- | --- |
| trend_ratio | MarketBarEvent | 39064 |
| trend_ratio | SignalEvent | 39064 |
| trend_ratio | TargetPositionOrderEvent | 2717 |
| trend_ratio | FillEvent | 2717 |
| trend_ratio | PortfolioSnapshot | 39064 |
| ema_macd | MarketBarEvent | 39064 |
| ema_macd | SignalEvent | 39064 |
| ema_macd | TargetPositionOrderEvent | 3303 |
| ema_macd | FillEvent | 3303 |
| ema_macd | PortfolioSnapshot | 39064 |

## 12. Position, turnover, and cost diagnostics

| strategy | long_bars | neutral_bars | short_bars | entries | exits | direct_reversals | position_changes | total_turnover | total_fractional_transaction_cost | total_transaction_cost_amount | final_equity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| trend_ratio | 17283 | 8945 | 12836 | 1346 | 1345 | 26 | 2717 | 2743.000000 | 0.274300 | 0.314494 | 0.958766 |
| ema_macd | 6748 | 25733 | 6583 | 1644 | 1644 | 15 | 3303 | 3318.000000 | 0.331800 | 0.310485 | 0.687177 |

## 13. Gross and net performance

Shared performance utilities calculate both series with annualisation factor
6552. Net final equity reconciles bar for bar to
the shared wealth index.

| strategy | series | observations | annualization_factor | cumulative_return | annualized_return | annualized_volatility | sharpe_ratio | maximum_drawdown | final_equity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| trend_ratio | gross | 39064 | 6552 | 0.261377 | 0.039715 | 0.190884 | 0.299866 | -0.233106 | 1.261377 |
| trend_ratio | net | 39064 | 6552 | -0.041234 | -0.007038 | 0.190895 | 0.058842 | -0.298225 | 0.958766 |
| ema_macd | gross | 39064 | 6552 | -0.042394 | -0.007239 | 0.158103 | 0.033768 | -0.356633 | 0.957606 |
| ema_macd | net | 39064 | 6552 | -0.312823 | -0.060985 | 0.158147 | -0.318136 | -0.455928 | 0.687177 |

## 14. Determinism and no-mutation validation

Repeated public replay produces identical immutable events, ledgers, and
shared metrics. Input frames are copied and remain unchanged. Event and
observation SHA-256 digests provide compact evidence without exporting the
full event stream.

## 15. Limitations

This replay has no partial fills, no order-book model, no latency model,
no concurrency, and no live broker. It performs no tuning.
There is no 2026 evaluation.
Normalized positions abstract from shares, borrowing constraints, market
impact, and venue-specific execution.

## 16. Day 12 conclusion

Both frozen baselines pass the deterministic event-ordering, delayed-execution,
accounting, development-window, and vectorised-parity integrity gates.
Profitability is not an acceptance criterion, and neither strategy is selected
for deployment.
