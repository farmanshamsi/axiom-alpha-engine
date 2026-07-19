# AL Project Decision Log

## Governance

The frozen AL V1.0 plan remains the canonical baseline.

This repository is the working implementation branch. Any changes caused by
Tutorial III or later CQF instructions must be documented before implementation.

---

## D-001 — Core Broker and Venue

**Decision:** Use Alpaca paper trading for the core project.

**Reasoning:**
- Paper environment is operational.
- Authentication has been tested successfully.
- Market clock and asset-information endpoints work.
- SPY, QQQ, and IWM are active and tradable.
- The architecture can later support additional venue adapters.

**Excluded from core scope:**
- Binance
- Kalshi
- Polymarket
- Real-money trading

These may be discussed as future extensions only.

---

## D-002 — Core Instrument Universe

**Primary trend instrument:** SPY

**Robustness instruments:**
- QQQ
- IWM

**Mean-reversion candidate pairs:**
- V / MA
- XOM / CVX
- KO / PEP
- HD / LOW
- JPM / BAC
- GS / MS

The final pair will not be selected using correlation alone.

Selection requires:
1. Economic rationale
2. Unit-root checks
3. Engle-Granger residual testing
4. Error-correction evidence
5. OU mean-reversion evaluation
6. Rolling stability
7. Cost-adjusted tradeability

---

## D-003 — Trading Session and Timezones

**Trading session:** US regular market hours only

**Exchange timezone:** America/New_York

**Storage timezone:** UTC

**Extended-hours data:** Excluded from the core experiment

---

## D-004 — Sampling Frequencies

**Raw historical bars:** 1 minute

**Primary strategy frequency:** 15 minutes

**Robustness frequencies:**
- 30 minutes
- 60 minutes

**Long-run cointegration estimation:** Daily data where appropriate

**Execution-level pair analysis:** Intraday data after the long-run relationship
passes the statistical gate

---

## D-005 — Sample Design

**Development sample:**
2 January 2020 through 31 December 2025

**Locked final test sample:**
2 January 2026 through 30 June 2026

The locked test period must not be used for:
- strategy selection
- parameter tuning
- pair selection
- transaction-cost calibration
- acceptance-rule design

The project will use rolling walk-forward evaluation before the final test.

---

## D-006 — Positioning Assumptions

**Trend baseline:** Long or flat

**Trend long-short version:** Separate ablation

**Mean-reversion strategy:** One long leg and one short leg

**Maximum gross exposure:** 1.0 times capital

**Leverage:** Not used in the core experiment

**Pair target net exposure:** Approximately zero

---

## D-007 — Event-Bar Analysis

The required non-time-bar comparison will primarily use dollar bars.

If trade-level data is insufficient, volume bars will be used as the documented
fallback.

The benchmark comparison is:

15-minute time bars versus event bars.

Synthetic event bars created from coarse OHLCV data must not be represented as
genuine trade-level event bars.

---

## D-008 — Paper-Trading Safety

The system must:
- use paper mode only
- prevent live-order submission
- maintain a kill switch
- handle rejected and partially filled orders
- reconcile broker positions against internal positions
- record all order-state transitions

No real-money order is permitted in the core project.

---

## D-009 — Alpaca Access Test

The following tests passed on 19 July 2026:

- Paper authentication
- Active account status
- Account information retrieval
- Historical market-data script
- Latest market-data script
- Market clock retrieval
- SPY eligibility
- QQQ eligibility
- IWM eligibility

SPY, QQQ, and IWM were reported as:
- active
- tradable
- shortable
- easy to borrow
- fractionable

These properties must be checked again at execution time because broker
eligibility can change.

---

## D-010 — Tutorial III Governance

The project may begin before Tutorial III.

After Tutorial III:
1. Extract new instructions.
2. Compare them against the frozen V1.0 baseline.
3. Classify changes as mandatory, recommended, optional, or irrelevant.
4. Update the working plan only after documenting the delta.

## 2026-07-20 — Day 03 Data Architecture

### Decision

Use Alpaca as the primary provider for US equity bars, quotes, and trades. Store all normalized timestamps in UTC and convert to America/New_York only for session analysis and reporting.

### Storage

Raw and processed market data are stored locally as Parquet files. Raw datasets are immutable by default. Each stored dataset has a JSON provenance manifest and SHA-256 file hash.

### Bar hierarchy

- Raw research frequency: 1 minute
- Primary strategy frequency: 15 minutes
- Robustness frequencies: 30 and 60 minutes

The project will build strategy bars internally rather than relying exclusively on provider-generated aggregated bars.

### Microstructure

Historical Level-1 quotes and individual trades will support:

- quoted spread
- relative spread
- bid/ask imbalance
- microprice
- trade-flow analysis
- slippage and execution-cost modelling

Microstructure variables will initially act as filters and execution diagnostics rather than independent alpha strategies.

### Data governance

The final January–June 2026 test period remains locked. Day 03 pipeline testing used 15 December 2025, which belongs to the development period.
