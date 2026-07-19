# Axiom Alpha Engine

## Multi-Strategy Systematic Trading Research & Paper-Execution Platform

Axiom Alpha Engine is a production-minded quantitative trading project combining systematic trend following, statistically validated mean reversion, intraday market-data engineering, market microstructure, walk-forward research, transaction-cost modelling, portfolio risk controls, and Alpaca paper execution.

The project is being developed as the implementation component of the CQF final project:

> **Algorithmic Trading for Trend-Following and Reversion**

The objective is not to produce a collection of isolated notebooks. The objective is to build a reproducible research and execution system in which the same data definitions, signal conventions, risk constraints, and validation rules can be used across historical research and paper trading.

---

## Strategy Architecture

The final system will contain three independently validated strategies:

1. **Price-ratio trend strategy**
2. **EMA/MACD trend strategy**
3. **Cointegration-based mean-reversion strategy**

### Research Universe

| Strategy family | Instruments |
|---|---|
| Trend primary | SPY |
| Trend robustness | QQQ, IWM |
| Mean-reversion candidates | V/MA, XOM/CVX, KO/PEP, HD/LOW, JPM/BAC, GS/MS |

The final pair will not be selected simply because it produces the best in-sample Sharpe ratio. Selection will require statistical, economic, structural, and execution-based evidence.

---

## Mathematical Research Framework

### 1. Price-Ratio Trend Following

The first trend model compares short- and long-horizon estimates of price.

Short-horizon average:

```math
\bar{P}^{(s)}_t
=
\frac{1}{n_s}
\sum_{i=0}^{n_s-1} P_{t-i}
```

Long-horizon average:

```math
\bar{P}^{(l)}_t
=
\frac{1}{n_l}
\sum_{i=0}^{n_l-1} P_{t-i},
\qquad
n_s < n_l
```

Relative trend state:

```math
R_t
=
\frac{\bar{P}^{(s)}_t}
{\bar{P}^{(l)}_t}
-1
```

Volatility-normalized trend state:

```math
Z^{\mathrm{trend}}_t
=
\frac{R_t}{\hat{\sigma}_t}
```

The research will test:

- fixed versus volatility-scaled thresholds;
- long/flat versus long/short positioning;
- time bars versus volume and dollar bars;
- turnover and slippage sensitivity;
- parameter-surface stability;
- out-of-sample persistence across SPY, QQQ, and IWM.

---

### 2. EMA and MACD Trend Following

The second trend strategy is deliberately distinct from the price-ratio model.

An exponential moving average evolves recursively as:

```math
EMA_t
=
\alpha P_t
+
(1-\alpha)EMA_{t-1}
```

The smoothing coefficient is:

```math
\alpha
=
\frac{2}{n+1}
```

The MACD state is:

```math
MACD_t
=
EMA^{(f)}_t
-
EMA^{(s)}_t
```

where \(f\) and \(s\) denote the fast and slow horizons.

The signal line is:

```math
Signal_t
=
EMA^{(m)}(MACD_t)
```

The MACD histogram is:

```math
H_t
=
MACD_t
-
Signal_t
```

First difference of the histogram:

```math
\Delta H_t
=
H_t
-
H_{t-1}
```

Second difference of the histogram:

```math
\Delta^2 H_t
=
\Delta H_t
-
\Delta H_{t-1}
```

Candidate confirmation filters include:

- realized-volatility regimes;
- volume participation;
- higher-timeframe agreement;
- ADX-based directional strength;
- Level-1 spread and quote conditions.

Each additional filter will be evaluated through ablation rather than assumed to add value.

---

### 3. Cointegration-Based Mean Reversion

The mean-reversion component is designed to go beyond a simple Bollinger Band or rolling Z-score strategy.

For two candidate price series \(X_t\) and \(Y_t\), the long-run relationship is estimated as:

```math
Y_t
=
\alpha
+
\beta X_t
+
\varepsilon_t
```

where:

- \(\alpha\) is the intercept;
- \(\beta\) is the hedge ratio;
- \(\varepsilon_t\) is the equilibrium residual.

The central hypothesis is that the two price series may each be non-stationary:

```math
X_t \sim I(1)
```

```math
Y_t \sim I(1)
```

while a linear combination is stationary:

```math
\varepsilon_t
=
Y_t
-
\alpha
-
\beta X_t
\sim I(0)
```

The residual will be evaluated using an Engle-Granger framework with appropriate residual-based inference.

A candidate pair must demonstrate:

- economically defensible linkage;
- both individual price series behaving as \(I(1)\);
- a stationary equilibrium residual;
- a stable and interpretable hedge ratio;
- acceptable structural stability;
- sufficient spread crossings;
- realistic borrow and transaction costs;
- robust out-of-sample behaviour.

#### Error-Correction Model

Short-run changes can be connected to the previous equilibrium deviation through:

```math
\Delta Y_t
=
c
+
\lambda \varepsilon_{t-1}
+
\sum_i \phi_i \Delta Y_{t-i}
+
\sum_j \psi_j \Delta X_{t-j}
+
u_t
```

The coefficient \(\lambda\) measures the speed and direction of adjustment toward the long-run equilibrium.

#### Ornstein-Uhlenbeck Representation

When supported by the residual dynamics, the spread will also be modelled as an Ornstein-Uhlenbeck process:

```math
d\varepsilon_t
=
\kappa(\mu-\varepsilon_t)\,dt
+
\sigma\,dW_t
```

where:

- \(\mu\) is the long-run spread mean;
- \(\kappa\) is the mean-reversion speed;
- \(\sigma\) is the diffusion volatility;
- \(W_t\) is Brownian motion.

The theoretical half-life is:

```math
t_{1/2}
=
\frac{\ln 2}{\kappa}
```

The equilibrium standard deviation is:

```math
\sigma_{\mathrm{eq}}
=
\frac{\sigma}
{\sqrt{2\kappa}}
```

A normalized spread state can then be written as:

```math
Z_t
=
\frac{\varepsilon_t-\mu}
{\sigma_{\mathrm{eq}}}
```

Entry and exit thresholds will be selected through walk-forward analysis after transaction costs rather than through one globally optimized threshold.

The project will compare:

- both regression directions;
- static and rolling hedge ratios;
- alternative deterministic terms;
- Engle-Granger and Johansen/VECM evidence;
- theoretical and empirical half-life;
- theoretical and empirical crossing frequency;
- raw and cost-adjusted performance.

---

## Market-Data Engineering

The current implementation includes a reusable historical market-data pipeline with:

- Alpaca OHLCV acquisition;
- historical Level-1 quote acquisition;
- historical trade acquisition;
- UTC timestamp normalization;
- normalized bar, quote, and trade schemas;
- OHLC consistency checks;
- duplicate detection;
- missing-bar detection;
- immutable Parquet storage;
- JSON provenance manifests;
- SHA-256 dataset hashes;
- 15-, 30-, and 60-minute resampling;
- volume-weighted VWAP aggregation;
- secure credential loading;
- mocked unit tests for external API behaviour.

### Verified Initial Result

A complete SPY regular session for 15 December 2025 was acquired from the Alpaca IEX feed.

| Validation item | Result |
|---|---:|
| Raw one-minute bars | 390 |
| Missing internal bars | 0 |
| Duplicate symbol/timestamp rows | 0 |
| Missing values | 0 |
| Fifteen-minute bars | 26 |
| Thirty-minute bars | 13 |
| Sixty-minute bars | 7 |

The 390 one-minute observations correspond to the complete 6.5-hour regular US equity session.

Raw and processed market data are excluded from Git. Each local dataset is associated with provenance metadata containing the provider, feed, request interval, schema, timestamp range, row count, SHA-256 hash, and transformation details.

---

## Market Microstructure Layer

Historical Level-1 quotes and trades will support execution and market-quality features.

### Quoted Spread

```math
Spread_t
=
Ask_t
-
Bid_t
```

### Relative Spread

```math
RelativeSpread_t
=
\frac{Ask_t-Bid_t}
{\frac{Ask_t+Bid_t}{2}}
```

### Quote Imbalance

```math
QI_t
=
\frac{BidSize_t-AskSize_t}
{BidSize_t+AskSize_t}
```

### Microprice

```math
Microprice_t
=
\frac{
Ask_t \cdot BidSize_t
+
Bid_t \cdot AskSize_t
}{
BidSize_t+AskSize_t
}
```

The microstructure layer will initially be used as:

- a spread filter;
- an execution-quality filter;
- an entry-confirmation layer;
- a slippage diagnostic;
- a paper-trading monitoring tool.

It will not be treated as independent alpha unless controlled ablation demonstrates robust incremental value.

---

## Research Validation

The project separates development, walk-forward analysis, and the locked final-test interval.

| Period | Purpose |
|---|---|
| 2020-01-02 to 2025-12-31 | Development and walk-forward research |
| 2026-01-02 to 2026-06-30 | Locked final test |

The final-test period must not be used for indicator selection, pair selection, threshold optimization, cost calibration, or model redesign.

Planned statistical evaluation includes:

- annualized return and volatility;
- Sharpe and Sortino ratios;
- maximum drawdown and Calmar ratio;
- turnover and cost attribution;
- hit rate and payoff ratio;
- long/short attribution;
- rolling beta and factor exposure;
- Value at Risk and Expected Shortfall;
- information coefficient and information ratio;
- HAC/Newey-West-adjusted inference;
- AIC and BIC where appropriate;
- Deflated Sharpe Ratio;
- block-bootstrap confidence intervals;
- parameter-sensitivity surfaces;
- multiple-testing awareness;
- walk-forward and final out-of-sample performance.

A high in-sample Sharpe ratio will not be treated as sufficient evidence of a valid strategy.

---

## Transaction-Cost and Execution Model

A simple initial slippage model is:

```math
c_t
=
\frac{\text{slippage bps}}{10{,}000}
\left|
\Delta w_t
\right|
```

where \(\Delta w_t\) represents the portfolio weight traded.

Planned execution analysis includes:

- quoted half-spread;
- slippage scenarios;
- turnover sensitivity;
- borrow costs;
- legging risk in pair trades;
- partial fills;
- rejected and cancelled orders;
- stale orders;
- execution delay;
- paper-fill versus market-price comparison.

---

## Portfolio and Risk Layer

After standalone validation, strategies may be combined using:

- equal allocation;
- inverse-volatility allocation;
- minimum-variance allocation;
- constrained cost-aware optimization.

Full-investment constraint:

```math
\sum_i w_i
=
1
```

Single-position concentration constraint:

```math
|w_i|
\leq
w_{\max}
```

Gross-exposure constraint:

```math
\sum_i |w_i|
\leq
G_{\max}
```

The portfolio layer will include covariance conditioning, shrinkage, solver-feasibility checks, turnover control, and deterministic fallbacks.

---

## Execution Architecture

```text
Historical and live market data
        ↓
Validation and normalization
        ↓
Immutable local storage
        ↓
Time bars and event bars
        ↓
Features and indicators
        ↓
Strategy signals
        ↓
Target positions
        ↓
Portfolio risk and allocation
        ↓
Execution adapter
        ↓
Order-state management
        ↓
Broker reconciliation
        ↓
Monitoring and reporting
```

Planned execution controls include:

- Alpaca REST and WebSocket connectivity;
- paper-only safeguards;
- stale-feed detection;
- reconnect and resubscribe logic;
- idempotent order handling;
- duplicate update protection;
- partial-fill handling;
- rejected and cancelled orders;
- account, position, and order reconciliation;
- exposure limits;
- kill switches;
- scheduled operation;
- Docker-based reproducibility.

---

## Current Status

### Completed

- Repository and package structure
- Paper-trading safety configuration
- Secure local credential handling
- Alpaca historical bar adapter
- Alpaca quote and trade adapters
- Normalized market-data schemas
- Immutable Parquet storage
- Dataset manifests and SHA-256 hashes
- Missing-bar, duplicate, and OHLC validation
- Fifteen-, thirty-, and sixty-minute resampling
- Automated unit tests
- Initial SPY pipeline validation

### In Development

- Resumable multi-symbol historical acquisition
- Dataset catalogue
- External data reconciliation
- Event-bar construction
- Trend indicators and signals
- Pair screening and cointegration testing
- ECM and OU estimation
- Transaction-cost engine
- Walk-forward backtesting
- Portfolio allocation
- Alpaca paper-execution adapter
- Broker reconciliation and monitoring

---

## Repository Structure

```text
axiom-alpha-engine/
├── config/
│   └── base.yaml
├── docs/
│   └── DECISIONS.md
├── scripts/
│   ├── download_sample_bars.py
│   ├── download_sample_microstructure.py
│   └── process_sample_bars.py
├── src/
│   └── cqf_al/
│       └── data/
│           ├── alpaca_microstructure.py
│           ├── alpaca_provider.py
│           ├── config_loader.py
│           ├── local_store.py
│           ├── resampling.py
│           ├── schemas.py
│           └── validators.py
├── tests/
│   └── data/
├── .gitignore
├── pyproject.toml
└── README.md
```

---

## Installation

Python 3.11 is used for development.

```bash
git clone https://github.com/farmanshamsi/axiom-alpha-engine.git
cd axiom-alpha-engine

python -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Create a local `.env` file:

```text
ALPACA_API_KEY=your_paper_api_key
ALPACA_SECRET_KEY=your_paper_secret_key
```

The `.env` file is excluded from Git and must never be committed.

Run the test suite:

```bash
python -m pytest
```

---

## Safety

This repository is configured for **paper trading only**.

Current safeguards include:

- live trading disabled;
- paper mode required;
- manual order confirmation required;
- kill-switch support;
- credentials stored outside source control;
- raw market data excluded from Git;
- locked final-test period;
- immutable raw-data storage.

No component should be considered ready for live capital without further validation, operational testing, independent review, and explicit removal of paper-only restrictions.

---

## Research Philosophy

The project follows five principles:

1. **Statistical evidence before trading logic**
2. **Out-of-sample performance before optimization claims**
3. **Transaction costs before headline returns**
4. **Reproducibility before complexity**
5. **Execution realism before live deployment**

The intended result is not simply a profitable backtest. It is a transparent quantitative research and execution system whose assumptions, data, mathematics, software behaviour, and limitations can be inspected and challenged.
