"""Command-line contracts for the Day 14 feasibility runner."""

from __future__ import annotations

import inspect
from pathlib import Path

import pandas as pd

import scripts.run_day14_cointegration_feasibility as runner


def test_runner_interface_and_default_output_are_frozen() -> None:
    assert runner.DEFAULT_ARTIFACT_DIRECTORY == Path(
        "artifacts/day14"
    )

    assert tuple(
        inspect.signature(
            runner.main
        ).parameters
    ) == ("argv",)


def test_runner_uses_frozen_development_boundaries() -> None:
    window = runner._development_window()

    assert window.development_start == pd.Timestamp(
        "2020-01-02",
        tz="UTC",
    )
    assert (
        window.development_end_exclusive
        == pd.Timestamp(
            "2026-01-01",
            tz="UTC",
        )
    )
    assert window.final_test_start == pd.Timestamp(
        "2026-01-02",
        tz="UTC",
    )
    assert (
        window.final_test_end_exclusive
        == pd.Timestamp(
            "2026-07-01",
            tz="UTC",
        )
    )
