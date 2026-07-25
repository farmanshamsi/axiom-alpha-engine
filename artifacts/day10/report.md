# Day 10 Trend-Family Robustness

## 1. Objective

Evaluate whether the two frozen trend-family baselines retain coherent
behaviour across SPY, QQQ and IWM at 15-, 30- and 60-minute frequencies.
Profitability was not an acceptance criterion.

## 2. Frozen experimental design

The experiment contains exactly 18 runs: two strategies, three symbols and
three frequencies. Annualisation factors are 6,552 for 15-minute bars, 3,276
for 30-minute bars and 1,764 for 60-minute bars. All comparisons are
descriptive and no run was removed because its return or Sharpe was negative.

## 3. Data and aggregation contract

The source is the canonical 117,192-row development dataset from 2020-01-02
through 2025-12-31. Aggregation remained inside symbol and trading-session
boundaries. 60-minute partial closing bars were retained.
The 2026 locked test period was not accessed.

## 4. Strategy configuration lock

Trend Ratio uses the Day 6 baseline configuration `trend_ratio_day06_baseline_v1`.
EMA/MACD uses the Day 8 baseline configuration `ema_macd_day08_baseline_v1`.
No Day 9 best configuration was selected.
Fixed-bar parameters imply longer clock-time horizons at lower frequencies;
the windows were not converted into time-equivalent alternatives.

## 5. Cross-asset results

| strategy | symbol | mean_annualized_return | mean_sharpe_ratio | worst_maximum_drawdown | mean_turnover |
| --- | --- | --- | --- | --- | --- |
| trend_ratio | SPY | -0.0103 | 0.0421 | -0.4236 | 1640.3333 |
| trend_ratio | QQQ | -0.0197 | 0.0293 | -0.4945 | 1652.3333 |
| trend_ratio | IWM | -0.0427 | -0.0396 | -0.5853 | 1719.6667 |
| ema_macd | SPY | -0.0157 | -0.0248 | -0.4559 | 2294.3333 |
| ema_macd | QQQ | -0.0031 | 0.0649 | -0.4351 | 2718.3333 |
| ema_macd | IWM | -0.0497 | -0.1239 | -0.6119 | 2865.6667 |

## 6. Cross-frequency results

| strategy | frequency | mean_annualized_return | mean_sharpe_ratio | worst_maximum_drawdown | mean_turnover |
| --- | --- | --- | --- | --- | --- |
| trend_ratio | 15min | -0.0305 | -0.0093 | -0.5776 | 2791.0000 |
| trend_ratio | 30min | 0.0025 | 0.1190 | -0.5290 | 1425.6667 |
| trend_ratio | 60min | -0.0447 | -0.0779 | -0.5853 | 795.6667 |
| ema_macd | 15min | -0.0913 | -0.4017 | -0.6119 | 4020.0000 |
| ema_macd | 30min | 0.0066 | 0.1292 | -0.3996 | 2427.3333 |
| ema_macd | 60min | 0.0161 | 0.1886 | -0.4151 | 1431.0000 |

## 7. Economic-coherence assessment

Each strategy-symbol-frequency run was retained regardless of economic sign.
The assessment compares direction, drawdown, turnover and exposure with each
strategy's SPY 15-minute reference.
The rules below are diagnostic rules, not performance acceptance criteria.

- Permanently flat: flat exposure at least 99.5%.
- Near-permanent direction: long or short exposure at least 95.0%.
- Zero trades: no position-changing bars.
- Undefined Sharpe: zero return volatility under the project convention.
- Extreme turnover change: ratio below 0.25 or above 4.00.
- Sign reversal: return or Sharpe sign differs from the strategy reference.
- Materially larger drawdown: drawdown worsens by at least 0.10.
- Low active count: active observations below 20% of observations.

## 8. Degenerate-behaviour flags

| diagnostic_flag | flagged_runs |
| --- | --- |
| permanently_flat | 0 |
| near_permanent_long | 0 |
| near_permanent_short | 0 |
| zero_trades | 0 |
| undefined_sharpe | 0 |
| extreme_turnover_change | 0 |
| return_sign_reversal | 6 |
| sharpe_sign_reversal | 10 |
| materially_larger_drawdown | 7 |
| low_active_observation_count | 0 |

Flags identify cases for investigation; they do not reject or rank
configurations.

## 9. Limitations

These results omit locked-period evidence, execution slippage beyond the
frozen turnover-cost assumption, market impact and walk-forward parameter
re-estimation. Lower-frequency results also mix full bars with the retained
half-hour session-close bar in the 60-minute series.

## 10. Day 10 conclusion

This report provides development-sample robustness evidence, not locked-test results.
It documents cross-asset and cross-frequency behaviour without
optimising, selecting or accepting configurations based on profitability.
