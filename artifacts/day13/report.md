# Day 13 — Event-Driven Trend-Family Walk-Forward

## 1. Scope and frozen protocol

This is development data only: SPY only, 15-minute bars only, using the
frozen Trend Ratio and EMA/MACD baselines over four fixed expanding folds.
There was no tuning, no ranking, and no winner selection. No 2026 data was
accessed, and this evidence is not final locked-period performance.

## 2. Scientific question

The study asks whether the frozen event-driven executions reproduce the
independent vectorised walk-forward reference through chronological test
folds without carrying execution or accounting state across fold boundaries.

## 3. Fold definitions

Training expands from 2020 through the year before each test year.
Training history warms indicators, while each evaluation contains one complete
calendar-year test fold.

| strategy | fold_id | train_observations | test_observations | train_sessions | test_sessions | evaluation_start | evaluation_end_exclusive | initial_position | initial_equity | parity_passed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| trend_ratio | wf_2022 | 13094 | 6514 | 505 | 251 | 2022-01-03T14:30:00+00:00 | 2022-12-30T21:00:00+00:00 | 0 | 1 | True |
| trend_ratio | wf_2023 | 19608 | 6476 | 756 | 250 | 2023-01-03T14:30:00+00:00 | 2023-12-29T21:00:00+00:00 | 0 | 1 | True |
| trend_ratio | wf_2024 | 26084 | 6516 | 1006 | 252 | 2024-01-02T14:30:00+00:00 | 2024-12-31T21:00:00+00:00 | 0 | 1 | True |
| trend_ratio | wf_2025 | 32600 | 6464 | 1258 | 250 | 2025-01-02T14:30:00+00:00 | 2025-12-31T21:00:00+00:00 | 0 | 1 | True |
| ema_macd | wf_2022 | 13094 | 6514 | 505 | 251 | 2022-01-03T14:30:00+00:00 | 2022-12-30T21:00:00+00:00 | 0 | 1 | True |
| ema_macd | wf_2023 | 19608 | 6476 | 756 | 250 | 2023-01-03T14:30:00+00:00 | 2023-12-29T21:00:00+00:00 | 0 | 1 | True |
| ema_macd | wf_2024 | 26084 | 6516 | 1006 | 252 | 2024-01-02T14:30:00+00:00 | 2024-12-31T21:00:00+00:00 | 0 | 1 | True |
| ema_macd | wf_2025 | 32600 | 6464 | 1258 | 250 | 2025-01-02T14:30:00+00:00 | 2025-12-31T21:00:00+00:00 | 0 | 1 | True |

## 4. Event-driven replay and warm-up design

Execution events are test-only. Signals are formed on completed bars and use
a one-observation execution delay. Ordinary sessions within a fold preserve
state; training observations supply feature history but never execution
records.

## 5. Fold-boundary reset and leakage controls

Every fold starts from a neutral position. Pending execution state is cleared
at every fold start, and equity reset to 1.0 is enforced. These diagnostics
demonstrate no training P&L leakage and no fold-boundary position leakage.

| strategy | fold_id | initial_previous_position | initial_position | initial_position_eligible | initial_turnover | initial_transaction_cost | initial_previous_equity | initial_cash_balance | initial_holdings_value | initial_ending_equity | initial_fill_executed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| trend_ratio | wf_2022 | 0 | 0 | False | 0 | 0 | 1 | 1 | 0 | 1 | False |
| trend_ratio | wf_2023 | 0 | 0 | False | 0 | 0 | 1 | 1 | 0 | 1 | False |
| trend_ratio | wf_2024 | 0 | 0 | False | 0 | 0 | 1 | 1 | 0 | 1 | False |
| trend_ratio | wf_2025 | 0 | 0 | False | 0 | 0 | 1 | 1 | 0 | 1 | False |
| ema_macd | wf_2022 | 0 | 0 | False | 0 | 0 | 1 | 1 | 0 | 1 | False |
| ema_macd | wf_2023 | 0 | 0 | False | 0 | 0 | 1 | 1 | 0 | 1 | False |
| ema_macd | wf_2024 | 0 | 0 | False | 0 | 0 | 1 | 1 | 0 | 1 | False |
| ema_macd | wf_2025 | 0 | 0 | False | 0 | 0 | 1 | 1 | 0 | 1 | False |

## 6. Event counts and execution diagnostics

| strategy | fold_id | market_bar_events | signal_events | order_events | fill_events | portfolio_snapshots | total_events |
| --- | --- | --- | --- | --- | --- | --- | --- |
| trend_ratio | wf_2022 | 6514 | 6514 | 456 | 456 | 6514 | 20454 |
| trend_ratio | wf_2023 | 6476 | 6476 | 462 | 462 | 6476 | 20352 |
| trend_ratio | wf_2024 | 6516 | 6516 | 448 | 448 | 6516 | 20444 |
| trend_ratio | wf_2025 | 6464 | 6464 | 452 | 452 | 6464 | 20296 |
| ema_macd | wf_2022 | 6514 | 6514 | 805 | 805 | 6514 | 21152 |
| ema_macd | wf_2023 | 6476 | 6476 | 540 | 540 | 6476 | 20508 |
| ema_macd | wf_2024 | 6516 | 6516 | 415 | 415 | 6516 | 20378 |
| ema_macd | wf_2025 | 6464 | 6464 | 521 | 521 | 6464 | 20434 |

## 7. Vectorised/event-driven parity

All eight comparisons remain visible for every run, including any observed
failure, mismatch count, and maximum absolute difference.

| strategy | fold_id | comparisons | passed | mismatches | maximum_absolute_difference |
| --- | --- | --- | --- | --- | --- |
| trend_ratio | wf_2022 | 8 | 8 | 0 | 0 |
| trend_ratio | wf_2023 | 8 | 8 | 0 | 0 |
| trend_ratio | wf_2024 | 8 | 8 | 0 | 0 |
| trend_ratio | wf_2025 | 8 | 8 | 0 | 0 |
| ema_macd | wf_2022 | 8 | 8 | 0 | 0 |
| ema_macd | wf_2023 | 8 | 8 | 0 | 0 |
| ema_macd | wf_2024 | 8 | 8 | 0 | 0 |
| ema_macd | wf_2025 | 8 | 8 | 0 | 0 |

## 8. Fold-level gross and net performance

Gross and net evidence is presented neutrally using observed-session
annualisation.

| strategy | fold_id | series | annualization_factor | cumulative_return | annualized_return | annualized_volatility | sharpe_ratio | maximum_drawdown | final_wealth |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| trend_ratio | wf_2022 | gross | 6539.95 | 0.068615 | 0.0688976 | 0.212182 | 0.420204 | -0.160388 | 1.06862 |
| trend_ratio | wf_2022 | net | 6539.95 | 0.0202634 | 0.020345 | 0.212195 | 0.201113 | -0.174537 | 1.02026 |
| trend_ratio | wf_2023 | gross | 6527.81 | 0.0452671 | 0.0456374 | 0.111668 | 0.455469 | -0.0940758 | 1.04527 |
| trend_ratio | wf_2023 | net | 6527.81 | -0.00192727 | -0.00194267 | 0.111684 | 0.0384287 | -0.10454 | 0.998073 |
| trend_ratio | wf_2024 | gross | 6516 | 0.0712078 | 0.0712078 | 0.108752 | 0.686692 | -0.0843288 | 1.07121 |
| trend_ratio | wf_2024 | net | 6516 | 0.0241727 | 0.0241727 | 0.10877 | 0.273781 | -0.0947089 | 1.02417 |
| trend_ratio | wf_2025 | gross | 6515.71 | -0.127866 | -0.12882 | 0.18339 | -0.660246 | -0.233106 | 0.872134 |
| trend_ratio | wf_2025 | net | 6515.71 | -0.166829 | -0.168044 | 0.183406 | -0.911354 | -0.258598 | 0.833171 |
| ema_macd | wf_2022 | gross | 6539.95 | -0.113333 | -0.113758 | 0.172307 | -0.614572 | -0.313576 | 0.886667 |
| ema_macd | wf_2022 | net | 6539.95 | -0.182165 | -0.18282 | 0.172341 | -1.08516 | -0.340034 | 0.817835 |
| ema_macd | wf_2023 | gross | 6527.81 | 0.0747704 | 0.0753906 | 0.0770624 | 0.981714 | -0.0697326 | 1.07477 |
| ema_macd | wf_2023 | net | 6527.81 | 0.0182706 | 0.0184181 | 0.077085 | 0.275297 | -0.0807398 | 1.01827 |
| ema_macd | wf_2024 | gross | 6516 | -0.0130407 | -0.0130407 | 0.0753662 | -0.136259 | -0.0621416 | 0.986959 |
| ema_macd | wf_2024 | net | 6516 | -0.0532577 | -0.0532577 | 0.0753876 | -0.688034 | -0.0721899 | 0.946742 |
| ema_macd | wf_2025 | gross | 6515.71 | -0.176509 | -0.177788 | 0.143574 | -1.29145 | -0.230304 | 0.823491 |
| ema_macd | wf_2025 | net | 6515.71 | -0.218565 | -0.220105 | 0.1437 | -1.65788 | -0.244055 | 0.781435 |

## 9. Aggregate walk-forward evidence

Chronological out-of-sample aggregation concatenates the four independently
reset return streams. Aggregate metrics are recomputed rather than averaged;
portfolio and pending-order state are not linked between folds.

| strategy | series | folds | observations | sessions | annualization_factor | cumulative_return | annualized_return | annualized_volatility | sharpe_ratio | maximum_drawdown | final_wealth |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| trend_ratio | gross | 4 | 25970 | 1003 | 6524.87 | 0.0435318 | 0.0107633 | 0.160397 | 0.146962 | -0.233106 | 1.04353 |
| trend_ratio | net | 4 | 25970 | 1003 | 6524.87 | -0.131075 | -0.0346841 | 0.160412 | -0.139834 | -0.291621 | 0.868925 |
| ema_macd | gross | 4 | 25970 | 1003 | 6524.87 | -0.225477 | -0.0621784 | 0.124398 | -0.453702 | -0.361365 | 0.774523 |
| ema_macd | net | 4 | 25970 | 1003 | 6524.87 | -0.383896 | -0.114576 | 0.124453 | -0.915402 | -0.459931 | 0.616104 |

## 10. Interpretation and limitations

The evidence covers two frozen strategies, SPY, 15-minute bars, four
development-period folds, normalized-notional fills, and the existing cost
model. It does not establish locked-period performance, deployability,
market-impact behavior, partial-fill behavior, or live-broker readiness.

## 11. Reproducibility and manifest

The exact table schemas, row order, reset diagnostics, parity evidence, and
artifact SHA-256 hashes are recorded in `manifest.json`. The evidence
files are `fold_summary.csv`, `event_counts.csv`,
`position_diagnostics.csv`, `performance.csv`,
`vectorized_parity.csv`, and `aggregate_summary.csv`.

## 12. Day 13 conclusion

Day 13 acceptance concerns deterministic orchestration, fold isolation,
accounting integrity, and transparent parity diagnostics. Performance signs
and magnitudes are descriptive research outcomes.
