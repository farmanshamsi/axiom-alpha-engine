# Day 15 — Strategy Diversification Feasibility

## 1. Objective and scope

This development-only study measures return-stream diversification across six
frozen strategy sleeves. Statistical diversification, economic performance,
and portfolio allocation are distinct questions: this phase addresses only
the first.

Low correlation does not automatically create alpha.
No profitability improvement is claimed.

## 2. Frozen six-sleeve universe

| Sleeve | Strategy | Symbol | Configuration |
|---|---|---|---|
| trend_ratio_spy | trend_ratio | SPY | trend_ratio_day06_baseline_v1 |
| trend_ratio_qqq | trend_ratio | QQQ | trend_ratio_day06_baseline_v1 |
| trend_ratio_iwm | trend_ratio | IWM | trend_ratio_day06_baseline_v1 |
| ema_macd_spy | ema_macd | SPY | ema_macd_day08_baseline_v1 |
| ema_macd_qqq | ema_macd | QQQ | ema_macd_day08_baseline_v1 |
| ema_macd_iwm | ema_macd | IWM | ema_macd_day08_baseline_v1 |

Each strategy uses its frozen Day 10 configuration.
No strategy was ranked or removed.

## 3. Data and alignment protocol

The source frequency is 15 minutes and the permitted development dates are
2020-01-02 through 2025-12-31. Existing net strategy returns include the
frozen transaction-cost convention and preserve position[t] = signal[t-1].
Intraday simple net returns are compounded within each session as
product(1 + intraday net return) - 1. The six session series are aligned on
exact common session dates. Forward filling, backward filling, interpolation,
or asynchronous calendar matching is not used.

The locked January–June 2026 period was not accessed.

## 4. Mathematical diagnostics

Pearson correlations are calculated for all 15 unique unordered sleeve pairs.
Correlation eigenvalues are evaluated in descending order; first-principal-
component share and entropy effective rank describe concentration. Covariance
uses ordinary sample covariance with ddof=1, without repair or shrinkage.
Positive-semidefinite status uses the frozen numerical tolerance.
Equal weights of 1/6 are used only as a neutral diagnostic.
They are not a portfolio allocation.

## 5. Predeclared thresholds

- Sleeve variance must exceed 9.9999999999999998e-17.
- PSD eigenvalues may not be below -9.9999999999999998e-13.
- Every fold requires at least 252 training sessions and
  100 test sessions.
- Maximum training absolute correlation may not exceed
  0.95.
- Median training effective rank must be at least
  2.00.
- Median training PC1 share may not exceed
  0.80.
- Median realised test equal-weight diversification ratio must be strictly
  greater than 1.00.

## 6. Full-sample descriptive evidence

- Aligned sessions: 1508
- Minimum pair correlation: 0.021378
  (trend_ratio_iwm / ema_macd_spy)
- Maximum pair correlation: 0.818743
  (ema_macd_spy / ema_macd_qqq)
- Maximum absolute correlation:
  0.818743
- First-PC share: 0.424795
- Entropy effective rank: 3.758647
- Equal-weight diversification ratio:
  1.547310
- Correlation PSD: Yes
- Covariance PSD: Yes

These statistics describe dependence; they do not establish economic
performance.

## 7. Training and realised test-fold evidence

| Fold | Sample | Sessions | Max abs. correlation | PC1 share | Effective rank | Equal-weight DR |
|---|---|---:|---:|---:|---:|---:|
| wf_2022 | train | 505 | 0.813156 | 0.403030 | 3.869139 | 1.656130 |
| wf_2022 | test | 251 | 0.860023 | 0.512183 | 3.312817 | 1.394146 |
| wf_2023 | train | 756 | 0.802058 | 0.414364 | 3.745722 | 1.559956 |
| wf_2023 | test | 250 | 0.786685 | 0.477832 | 4.227459 | 1.482917 |
| wf_2024 | train | 1006 | 0.791866 | 0.418296 | 3.840077 | 1.554204 |
| wf_2024 | test | 252 | 0.828720 | 0.398085 | 4.071273 | 1.743606 |
| wf_2025 | train | 1258 | 0.791080 | 0.410238 | 3.880016 | 1.570816 |
| wf_2025 | test | 250 | 0.914693 | 0.492770 | 3.136587 | 1.431683 |

Training evidence is computed independently of future test rows. Realised test
diversification is descriptive and is not an outperformance claim.

## 8. Gate-by-gate feasibility conclusion

| Gate | Outcome |
|---|---:|
| Finite sleeve returns | Pass |
| Exact common-session alignment | Pass |
| Non-degenerate sleeve variance | Pass |
| Minimum training sessions | Pass |
| Minimum test sessions | Pass |
| Training absolute-correlation ceiling | Pass |
| Median training effective-rank floor | Pass |
| Median training PC1-share ceiling | Pass |
| Correlation PSD status | Pass |
| Covariance PSD status | Pass |
| Median realised test diversification-ratio floor | Pass |

The recorded ensemble_feasible outcome is **true**. The frozen
sleeves exhibit sufficient return-stream diversification under the
predeclared correlation, eigenstructure, covariance, and walk-forward gates.
A false feasibility outcome is valid and is retained without changing the
sleeve universe.

## 9. Limitations and next-stage restrictions

This phase does not test alpha creation, economic utility, capacity, market
impact, or profitability improvement. Equal weights are diagnostic only.
No portfolio weights were optimised.
No leverage was used, and no allocation decision is provided.
Subsequent economic-performance or allocation work
must remain separate and must not use the locked period without explicit
authorization.
