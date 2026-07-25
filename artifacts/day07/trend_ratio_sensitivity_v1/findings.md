# Day 7 Findings — Trend-Ratio Sensitivity

## Scope

This report covers the predeclared 36-configuration SPY 15-minute development grid only. The locked 2026-01-02 through 2026-06-30 period was not accessed.

## Development evidence

- Configurations with positive cumulative net return: 14 of 36.
- Configurations with a positive model-implied break-even cost: 31 of 36.
- Median total turnover across the grid: 1846.0 turnover units.

The highest isolated net Sharpe occurred at `s008_l096_d0p0005` with net Sharpe 0.277. This is an in-sample diagnostic, not a selected final parameter.

The highest median neighbouring net Sharpe occurred around `s008_l096_d0p0020` at 0.218; its own net Sharpe was 0.206.

## Interpretation constraints

The results are development-only sensitivity evidence. They do not establish alpha, statistical superiority, robustness, deployability, realised execution costs, or final parameter validity. An isolated high-performing cell should be treated as weaker evidence than a coherent neighbouring plateau.

## Next evidence gate

Any configuration retained for further study must later pass parameter-stability review, walk-forward evaluation, anti-overfitting controls, and the separately locked final test.
