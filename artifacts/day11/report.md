# Day 11 — Trend-Family Walk-Forward Validation

## 1. Title and scope

Day 11 evaluates SPY at the primary 15-minute frequency using development
data only. The 2026 locked final-test period was not accessed.

## 2. Scientific purpose

The purpose is to test the temporal stability of the two frozen trend-family
baselines through chronological out-of-sample folds. Day 11 does not tune,
rank, optimise or select parameters, does not use a Day 7 or Day 9
sensitivity winner, and has no profitability gate.

## 3. Locked scope

- Symbol: SPY only.
- Frequency: 15-minute bars only.
- Sample: development observations through 2025-12-31 only.
- Strategies: frozen Day 6 Trend Ratio and frozen Day 8 EMA/MACD baselines.
- Parameter selection and sensitivity-result consultation: none.
- Profitability as an acceptance condition: explicitly excluded.

## 4. Fold design

- `wf_2022`: train 2020-01-02 through 2021-12-31; test calendar year 2022.
- `wf_2023`: train 2020-01-02 through 2022-12-31; test calendar year 2023.
- `wf_2024`: train 2020-01-02 through 2023-12-31; test calendar year 2024.
- `wf_2025`: train 2020-01-02 through 2024-12-31; test calendar year 2025.

Training windows expand from one fixed origin and test years do not overlap.

## 5. Leakage controls

Whole trading sessions define every partition.
Training history is available only to warm indicators.
Training returns, turnover, costs and drawdowns are excluded from test metrics.
Each test fold resets position and delayed execution state to neutral.
The existing one-observation execution delay remains active within the fold.
Train and test sessions never overlap.

Purge and embargo are both zero sessions. They are unnecessary here because
the strategies are fixed rather than fitted in each fold, labels do not span
the boundary, test years do not overlap, execution is delayed by one
observation, and test accounting is reset and isolated. The 2026 locked period
was not accessed.

## 6. Frozen configurations

| strategy | configuration_id | parameters |
| --- | --- | --- |
| Trend Ratio | trend_ratio_day06_baseline_v1 | {"cost_bps_per_turnover": 1.0, "long_window": 32, "neutral_band": 0.001, "price_column": "close", "return_column": "close_to_close_simple_return", "short_window": 8} |
| EMA/MACD | ema_macd_day08_baseline_v1 | {"cost_bps_per_turnover": 1.0, "fast_window": 12, "neutral_band": 0.0005, "price_column": "close", "return_column": "close_to_close_simple_return", "signal_window": 9, "slow_window": 26} |

## 7. Dataset audit

- Canonical loader input: `data/processed/bars/spy_qqq_iwm_15min_2020-01-02_2025-12-31_sip_v3_development_canonical.parquet`.
- Dataset identifier: `spy_qqq_iwm_15min_2020-01-02_2025-12-31_sip_v3_development_canonical`.
- Full canonical development rows: 117192.
- SPY rows: 39064.
- SPY sessions: 1508.
- Minimum timestamp: 2020-01-02T14:30:00+00:00.
- Maximum timestamp: 2025-12-31T20:45:00+00:00.
- Development window confirmed: 2020-01-02 through 2025-12-31.

## 8. Per-fold results

All performance columns below use test observations only. Net returns already
include the frozen one-basis-point turnover cost. The compact public engine
does not serialize a competing reconstructed gross-return series or per-bar
training data; turnover is retained to document cost intensity.

### Trend Ratio

| fold_id | train_start_timestamp | train_end_timestamp | test_start_timestamp | test_end_timestamp | train_sessions | test_sessions | test_observations | annualization_factor | initial_test_position | initial_test_turnover | warmup_observations | active_observations | cumulative_return | annualized_return | annualized_volatility | sharpe_ratio | maximum_drawdown | turnover | trade_count | average_exposure | long_exposure | short_exposure | flat_exposure |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| wf_2022 | 2020-01-02T14:30:00+00:00 | 2021-12-31T20:45:00+00:00 | 2022-01-03T14:30:00+00:00 | 2022-12-30T20:45:00+00:00 | 505 | 251 | 6514 | 6539.9522 | 0 | 0.0000 | 1 | 6513 | 0.0203 | 0.0203 | 0.2122 | 0.2011 | -0.1745 | 463.0000 | 456 | 86.5039 | 41.4095 | 45.0944 | 13.4961 |
| wf_2023 | 2020-01-02T14:30:00+00:00 | 2022-12-30T20:45:00+00:00 | 2023-01-03T14:30:00+00:00 | 2023-12-29T20:45:00+00:00 | 756 | 250 | 6476 | 6527.8080 | 0 | 0.0000 | 1 | 6475 | -0.0019 | -0.0019 | 0.1117 | 0.0384 | -0.1045 | 462.0000 | 462 | 76.4633 | 44.0154 | 32.4479 | 23.5367 |
| wf_2024 | 2020-01-02T14:30:00+00:00 | 2023-12-29T20:45:00+00:00 | 2024-01-02T14:30:00+00:00 | 2024-12-31T20:45:00+00:00 | 1006 | 252 | 6516 | 6516.0000 | 0 | 0.0000 | 1 | 6515 | 0.0242 | 0.0242 | 0.1088 | 0.2738 | -0.0947 | 449.0000 | 448 | 71.4045 | 41.9954 | 29.4091 | 28.5955 |
| wf_2025 | 2020-01-02T14:30:00+00:00 | 2024-12-31T20:45:00+00:00 | 2025-01-02T14:30:00+00:00 | 2025-12-31T20:45:00+00:00 | 1258 | 250 | 6464 | 6515.7120 | 0 | 0.0000 | 1 | 6463 | -0.1668 | -0.1680 | 0.1834 | -0.9114 | -0.2586 | 457.0000 | 452 | 74.9652 | 44.2983 | 30.6669 | 25.0348 |

### EMA/MACD

| fold_id | train_start_timestamp | train_end_timestamp | test_start_timestamp | test_end_timestamp | train_sessions | test_sessions | test_observations | annualization_factor | initial_test_position | initial_test_turnover | warmup_observations | active_observations | cumulative_return | annualized_return | annualized_volatility | sharpe_ratio | maximum_drawdown | turnover | trade_count | average_exposure | long_exposure | short_exposure | flat_exposure |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| wf_2022 | 2020-01-02T14:30:00+00:00 | 2021-12-31T20:45:00+00:00 | 2022-01-03T14:30:00+00:00 | 2022-12-30T20:45:00+00:00 | 505 | 251 | 6514 | 6539.9522 | 0 | 0.0000 | 1 | 6513 | -0.1822 | -0.1828 | 0.1723 | -1.0852 | -0.3400 | 808.0000 | 805 | 51.5124 | 25.2725 | 26.2398 | 48.4876 |
| wf_2023 | 2020-01-02T14:30:00+00:00 | 2022-12-30T20:45:00+00:00 | 2023-01-03T14:30:00+00:00 | 2023-12-29T20:45:00+00:00 | 756 | 250 | 6476 | 6527.8080 | 0 | 0.0000 | 1 | 6475 | 0.0183 | 0.0184 | 0.0771 | 0.2753 | -0.0807 | 540.0000 | 540 | 29.4363 | 15.1042 | 14.3320 | 70.5637 |
| wf_2024 | 2020-01-02T14:30:00+00:00 | 2023-12-29T20:45:00+00:00 | 2024-01-02T14:30:00+00:00 | 2024-12-31T20:45:00+00:00 | 1006 | 252 | 6516 | 6516.0000 | 0 | 0.0000 | 1 | 6515 | -0.0533 | -0.0533 | 0.0754 | -0.6880 | -0.0722 | 416.0000 | 415 | 22.9470 | 12.0645 | 10.8826 | 77.0530 |
| wf_2025 | 2020-01-02T14:30:00+00:00 | 2024-12-31T20:45:00+00:00 | 2025-01-02T14:30:00+00:00 | 2025-12-31T20:45:00+00:00 | 1258 | 250 | 6464 | 6515.7120 | 0 | 0.0000 | 1 | 6463 | -0.2186 | -0.2201 | 0.1437 | -1.6579 | -0.2441 | 524.0000 | 521 | 30.3419 | 15.4727 | 14.8693 | 69.6581 |

## 9. Aggregate out-of-sample results

These metrics are recomputed from the chronologically concatenated test
observations from 2022 through 2025. Fold Sharpe ratios and drawdowns are not
averaged.

| strategy | configuration_id | folds | test_sessions | test_observations | annualization_factor | cumulative_return | annualized_return | annualized_volatility | sharpe_ratio | maximum_drawdown | turnover | trade_count | average_exposure | long_exposure | short_exposure | flat_exposure |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| trend_ratio | trend_ratio_day06_baseline_v1 | 4 | 1003 | 25970 | 6524.8654 | -0.1311 | -0.0347 | 0.1604 | -0.1398 | -0.2916 | 1831.0000 | 1818 | 77.3396 | 42.9254 | 34.4142 | 22.6604 |
| ema_macd | ema_macd_day08_baseline_v1 | 4 | 1003 | 25970 | 6524.8654 | -0.3839 | -0.1146 | 0.1245 | -0.9154 | -0.4599 | 2288.0000 | 2281 | 33.5708 | 16.9837 | 16.5871 | 66.4292 |

## 10. Stability interpretation

Trend Ratio had 2 positive net-return folds out of four; fold net returns ranged from -0.1668 to 0.0242. Total out-of-sample turnover was 1831.0, and the most negative fold drawdown was -0.2586.

EMA/MACD had 1 positive net-return folds out of four; fold net returns ranged from -0.2186 to 0.0183. Total out-of-sample turnover was 2288.0, and the most negative fold drawdown was -0.3400.

Variation across calendar years shows that neither frozen rule has uniform
temporal behaviour. Net performance reflects the same frozen transaction-cost
assumption in every fold. Turnover therefore provides descriptive evidence
about cost pressure, while the fold and aggregate drawdowns document different
loss paths.
These comparisons do not declare a winning strategy.
The report does not select either strategy for deployment.

## 11. Acceptance criteria

Day 11 passes on chronological integrity, absence of leakage, deterministic
output, correct fold resets, frozen configurations, valid test-only accounting,
reproducibility and full test coverage.
Profitability is not an acceptance condition.
Negative returns or Sharpe-like ratios remain valid research outcomes.

## 12. Limitations and next step

Evidence is limited to SPY, 15-minute bars, four calendar-year test folds, two
frozen trend-family baselines and the development period. It does not establish
locked-period performance, deployability, market-impact tolerance or parameter
superiority. Any later locked evaluation must remain separate and must not
feed back into configuration choice.
