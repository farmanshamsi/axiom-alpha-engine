# Day 14 — Cointegration and OU Feasibility

## 1. Purpose

This study evaluates whether any predeclared ETF pair satisfies the frozen
development-period statistical and OU feasibility gates. It does not define,
simulate or assess a trading strategy.

## 2. Frozen candidate universe

- SPY / QQQ: SPY is Y and QQQ is X
- SPY / IWM: SPY is Y and IWM is X
- QQQ / IWM: QQQ is Y and IWM is X

Reverse orientations were not tested for eligibility.

## 3. Data and alignment contract

Engle–Granger estimation uses daily log session-close prices derived from the
canonical 15-minute development data. Daily observations are joined by exact
session date. Intraday observations are joined by exact timestamp and session.
No forward filling, interpolation or asynchronous matching is permitted.

## 4. Statistical contract

Individual series are assessed for plausible I(1) behaviour using the frozen
ADF level and first-difference specifications. Engle–Granger inference uses an
intercept and Holm correction across the three candidate tests. Hedge-ratio
and expanding-fold stability gates are applied before OU estimation.

## 5. Aggregate diagnostic counts

- Plausibly I(1) symbols: 3 of 3
- Holm-adjusted cointegration passes: 0 of 3
- OU estimations attempted: 0 of 3
- Fully eligible pairs: 0 of 3

## 6. Pair eligibility

| Pair | Eligible | Rejection reasons |
|---|---:|---|
| SPY_QQQ | No | holm_cointegration_failed|fold_stationarity_failed|ou_not_attempted |
| SPY_IWM | No | holm_cointegration_failed|fold_beta_stability_failed|fold_stationarity_failed|ou_not_attempted |
| QQQ_IWM | No | holm_cointegration_failed|fold_beta_stability_failed|fold_stationarity_failed|ou_not_attempted |

## 7. Interpretation boundary

No profitability criterion, transaction-cost criterion, trading threshold,
position rule, pair ranking or winner selection is included in Day 14.
Eligibility is a statistical feasibility outcome only. A result in which no
pair qualifies is valid.

## 8. Locked-period protection

The January–June 2026 final evaluation period was not accessed.

## 9. Conclusion

The evidence records pass/fail outcomes for every predeclared pair without
using returns or profitability to rank the candidates. Any subsequent ECM,
signal, execution or portfolio work remains outside Day 14.
