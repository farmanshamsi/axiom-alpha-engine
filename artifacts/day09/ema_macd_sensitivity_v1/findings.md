# Day 9 Findings — EMA/MACD Sensitivity

## Scope

This report evaluates the predeclared 108-configuration SPY 15-minute
development grid only. It is parameter sensitivity, not parameter
optimisation. The locked final period from 2026-01-02 through 2026-06-30
was not accessed.

The grid varies only the fast EMA window, slow EMA window, MACD signal-line
window and normalised-histogram neutral band. Signal construction,
one-bar-delayed position timing, overnight carry and the one-basis-point
turnover-cost convention remain unchanged from Day 8.

## Development evidence

- Configurations with positive cumulative net return: 3 of 108.
- Configurations with a positive model-implied break-even cost: 23 of 108.
- Median total turnover across the grid: 3975.0 turnover units.
- Day 8 baseline net cumulative return: -31.2823%.
- Day 8 baseline net Sharpe: -0.3181.

The highest isolated development net Sharpe occurred at `f016_s032_m012_b0p00050` with a value of 0.292. This cell is reported diagnostically and is not selected as a final parameter.

The highest median neighbouring development net Sharpe occurred around `f016_s032_m012_b0p00025` at 0.061; its own net Sharpe was -0.003. This is neighbourhood evidence, not a parameter-selection decision.

## Interpretation constraints

These results are development-only sensitivity evidence.
They do not establish alpha, statistical superiority, robustness,
deployability, realised execution costs or final parameter validity.

A broad coherent neighbourhood is stronger evidence than an isolated
high-performing cell, but even a stable development plateau must later
pass walk-forward evaluation, explicit anti-overfitting controls and the
separately locked final test.

No parameter was selected using locked-period information.
