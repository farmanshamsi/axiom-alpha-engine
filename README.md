# CQF Algorithmic Trading Final Project

Research and engineering implementation for the CQF final project:

**Algorithmic Trading for Trend-Following and Reversion**

## Core scope

- Two distinct trend-following strategies
- One statistically validated mean-reversion strategy
- SPY as the primary trend instrument
- QQQ and IWM as robustness instruments
- Alpaca paper trading
- Intraday time bars and event bars
- Walk-forward and out-of-sample validation
- Transaction costs, execution controls, and broker reconciliation

## Safety

This project is configured for paper trading only.

API credentials are stored locally in `.env` and must never be committed.

## Day 03 — Market Data Pipeline

Implemented a provider-independent historical market-data pipeline with:

- Alpaca historical OHLCV bar acquisition
- Historical Level-1 quote acquisition
- Historical trade acquisition
- UTC timestamp normalization
- Normalized bar, quote, and trade schemas
- OHLC consistency validation
- Duplicate and missing-bar detection
- Immutable Parquet storage
- SHA-256 provenance manifests
- 1-minute to 15-, 30-, and 60-minute resampling
- Weighted VWAP aggregation
- Paper-mode credential and configuration validation
- Automated tests with mocked Alpaca clients

### Initial pipeline validation

A full SPY regular trading session for 15 December 2025 was downloaded through the Alpaca IEX feed.

- Raw 1-minute rows: 390
- Missing bars: 0
- Duplicate timestamps: 0
- Missing values: 0
- 15-minute bars: 26
- 30-minute bars: 13
- 60-minute bars: 7

Raw and processed market data are intentionally excluded from Git. Dataset provenance is recorded through local JSON manifests and SHA-256 hashes.
