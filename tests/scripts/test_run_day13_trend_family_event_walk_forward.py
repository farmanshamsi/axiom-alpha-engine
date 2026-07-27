"""Contracts for the canonical Day 13 report runner."""

from __future__ import annotations

import importlib
import inspect
from pathlib import Path
from types import SimpleNamespace
from typing import cast

import pandas as pd
import pytest

import scripts.run_day11_trend_walk_forward as day11_runner
import scripts.run_day13_trend_family_event_walk_forward as runner


class SyntheticStageFailure(Exception):
    """One deliberate mocked pipeline-stage failure."""


def make_loaded_bars() -> pd.DataFrame:
    """Return compact synthetic development-only loader output."""

    return pd.DataFrame(
        {
            "timestamp": [
                pd.Timestamp(
                    "2025-12-31 "
                    "14:30:00+00:00"
                ),
            ],
            "symbol": [
                "SPY",
            ],
            "close": [
                100.0,
            ],
        }
    )


def install_success_pipeline(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> tuple[
    list[str],
    list[pd.DataFrame],
    list[object],
]:
    """Install deterministic no-I/O runner dependencies."""

    calls: list[str] = []
    core_inputs: list[
        pd.DataFrame
    ] = []
    writer_inputs: list[
        object
    ] = []
    bars = make_loaded_bars()
    results = object()
    report = object()

    def root_spy() -> Path:
        calls.append("resolve_paths")

        return tmp_path

    def loader_spy() -> object:
        calls.append("load_development")

        return SimpleNamespace(
            bars=bars.copy(deep=True),
            audit=object(),
        )

    def core_spy(
        supplied: pd.DataFrame,
    ) -> object:
        calls.append("orchestrate")
        core_inputs.append(
            supplied.copy(deep=True)
        )

        return results

    def report_spy(
        supplied: object,
    ) -> object:
        calls.append("build_report")
        assert supplied is results

        return report

    def writer_spy(
        supplied: object,
        output_directory: str | Path,
        *,
        overwrite: bool = False,
    ) -> tuple[Path, ...]:
        calls.append("write_artifacts")
        assert supplied is report
        writer_inputs.append(
            (
                supplied,
                Path(output_directory),
                overwrite,
            )
        )

        return tuple(
            Path(output_directory) / name
            for name in runner
            .APPROVED_DAY13_ARTIFACT_NAMES
        )

    monkeypatch.setattr(
        runner,
        "find_project_root",
        root_spy,
    )
    monkeypatch.setattr(
        runner,
        "load_canonical_day11_input",
        loader_spy,
    )
    monkeypatch.setattr(
        runner,
        "run_trend_family_event_walk_forward",
        core_spy,
    )
    monkeypatch.setattr(
        runner,
        "build_day13_event_walk_forward_report",
        report_spy,
    )
    monkeypatch.setattr(
        runner,
        "write_day13_event_walk_forward_artifacts",
        writer_spy,
    )

    return (
        calls,
        core_inputs,
        writer_inputs,
    )


def test_runner_import_is_safe_and_creates_nothing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Importing the module must not load data, execute, or write output."""

    monkeypatch.chdir(tmp_path)
    importlib.reload(runner)

    assert callable(runner.main)
    assert callable(
        runner.load_canonical_day11_input
    )
    assert callable(
        runner
        .run_trend_family_event_walk_forward
    )
    assert callable(
        runner
        .build_day13_event_walk_forward_report
    )
    assert callable(
        runner
        .write_day13_event_walk_forward_artifacts
    )
    assert not Path(
        "artifacts/day13"
    ).exists()


def test_runner_interface_paths_and_guard_are_frozen() -> None:
    """Match recent main conventions and exact repository-relative paths."""

    signature = inspect.signature(
        runner.main
    )
    source = Path(
        runner.__file__
    ).read_text(encoding="utf-8")

    assert tuple(
        signature.parameters
    ) == ("argv",)
    assert runner.DEFAULT_ARTIFACT_DIRECTORY == Path(
        "artifacts/day13"
    )
    assert (
        runner.CANONICAL_DATASET_RELATIVE_PATH
        == day11_runner
        .CANONICAL_DATASET_RELATIVE_PATH
    )
    assert "if __name__ == \"__main__\":" in source
    assert "main()" in source


def test_runner_source_reuses_locked_public_interfaces_only() -> None:
    """Forbid strategy math, tuning, and a parallel data-path contract."""

    source = Path(
        runner.__file__
    ).read_text(
        encoding="utf-8"
    ).lower()

    for required in (
        "samplewindow",
        "load_canonical_day11_input",
        "run_trend_family_event_walk_forward",
        "build_day13_event_walk_forward_report",
        "write_day13_event_walk_forward_artifacts",
    ):
        assert required in source

    for forbidden in (
        "build_trend_ratio_strategy",
        "build_ema_macd_strategy",
        "_run_event_replay_core",
        "parameter_grid",
        "winner",
        "ranking",
        "day07",
        "day09",
        "artifacts/day11",
        "artifacts/day12",
    ):
        assert forbidden not in source


def test_runner_call_order_and_single_core_invocation(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Freeze the canonical load, core, report, write, and summary order."""

    (
        calls,
        core_inputs,
        _,
    ) = install_success_pipeline(
        monkeypatch,
        tmp_path,
    )
    runner.main([])

    assert calls == [
        "resolve_paths",
        "load_development",
        "orchestrate",
        "build_report",
        "write_artifacts",
    ]
    assert len(core_inputs) == 1


def test_runner_passes_complete_immutable_development_frame(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Pass one unchanged DataFrame with no strategy or fold arguments."""

    original = make_loaded_bars()
    captured: list[
        pd.DataFrame
    ] = []

    monkeypatch.setattr(
        runner,
        "find_project_root",
        lambda: tmp_path,
    )
    monkeypatch.setattr(
        runner,
        "load_canonical_day11_input",
        lambda: SimpleNamespace(
            bars=original,
            audit=object(),
        ),
    )

    def core_spy(
        bars: pd.DataFrame,
    ) -> object:
        captured.append(
            bars.copy(deep=True)
        )

        return object()

    monkeypatch.setattr(
        runner,
        "run_trend_family_event_walk_forward",
        core_spy,
    )
    monkeypatch.setattr(
        runner,
        "build_day13_event_walk_forward_report",
        lambda results: object(),
    )
    monkeypatch.setattr(
        runner,
        "write_day13_event_walk_forward_artifacts",
        lambda report, output_directory, overwrite=False: (),
    )

    runner.main([])

    assert len(captured) == 1
    pd.testing.assert_frame_equal(
        captured[0],
        original,
    )
    pd.testing.assert_frame_equal(
        original,
        make_loaded_bars(),
    )


def test_runner_uses_day13_output_and_neutral_console_summary(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Report compact counts without naming a preferred strategy."""

    (
        _,
        _,
        writer_inputs,
    ) = install_success_pipeline(
        monkeypatch,
        tmp_path,
    )
    runner.main([])
    output = capsys.readouterr().out.lower()

    assert len(writer_inputs) == 1
    assert cast(
        tuple[object, Path, bool],
        writer_inputs[0],
    )[1] == (
        tmp_path
        / runner.DEFAULT_ARTIFACT_DIRECTORY
    )

    for statement in (
        "day 13",
        "strategies: 2",
        "folds: 4",
        "replay runs: 8",
        "test observations:",
        "parity comparisons: 64",
        "parity passed:",
        "artifacts/day13",
    ):
        assert statement in output

    for forbidden in (
        "winner",
        "preferred",
        "best strategy",
    ):
        assert forbidden not in output


def test_loaded_locked_period_row_never_reaches_core(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Revalidate loader output so a locked-period row cannot execute."""

    locked = make_loaded_bars()
    locked.loc[
        0,
        "timestamp",
    ] = pd.Timestamp(
        "2026-01-02 "
        "14:30:00+00:00"
    )
    core_called = False

    monkeypatch.setattr(
        runner,
        "find_project_root",
        lambda: tmp_path,
    )
    monkeypatch.setattr(
        runner,
        "load_canonical_day11_input",
        lambda: SimpleNamespace(
            bars=locked,
            audit=object(),
        ),
    )

    def core_spy(
        bars: pd.DataFrame,
    ) -> object:
        nonlocal core_called
        core_called = True

        return object()

    monkeypatch.setattr(
        runner,
        "run_trend_family_event_walk_forward",
        core_spy,
    )
    runner.main([])

    assert core_called is False


@pytest.mark.parametrize(
    "failure_stage",
    (
        "loader",
        "orchestration",
        "report",
        "writer",
    ),
)
def test_pipeline_failures_stop_later_stages_and_success_output(
    failure_stage: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Surface each pipeline failure without suppression or success text."""

    calls: list[str] = []

    def maybe_fail(
        stage: str,
        value: object,
    ) -> object:
        calls.append(stage)

        if stage == failure_stage:
            raise SyntheticStageFailure(
                f"synthetic {stage} failure"
            )

        return value

    monkeypatch.setattr(
        runner,
        "find_project_root",
        lambda: tmp_path,
    )
    monkeypatch.setattr(
        runner,
        "load_canonical_day11_input",
        lambda: maybe_fail(
            "loader",
            SimpleNamespace(
                bars=make_loaded_bars(),
                audit=object(),
            ),
        ),
    )
    monkeypatch.setattr(
        runner,
        "run_trend_family_event_walk_forward",
        lambda bars: maybe_fail(
            "orchestration",
            object(),
        ),
    )
    monkeypatch.setattr(
        runner,
        "build_day13_event_walk_forward_report",
        lambda results: maybe_fail(
            "report",
            object(),
        ),
    )
    monkeypatch.setattr(
        runner,
        "write_day13_event_walk_forward_artifacts",
        lambda report, output_directory, overwrite=False: maybe_fail(
            "writer",
            (),
        ),
    )

    with pytest.raises(
        SyntheticStageFailure,
        match=failure_stage,
    ):
        runner.main([])

    output = capsys.readouterr().out.lower()
    assert "passed" not in output
    assert calls[-1] == failure_stage


def test_repeated_mocked_runs_supply_identical_report_and_writer_inputs(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Require deterministic dependency inputs across repeated runs."""

    reports: list[
        object
    ] = []
    writes: list[
        tuple[object, Path, bool]
    ] = []
    bars = make_loaded_bars()
    results = object()

    monkeypatch.setattr(
        runner,
        "find_project_root",
        lambda: tmp_path,
    )
    monkeypatch.setattr(
        runner,
        "load_canonical_day11_input",
        lambda: SimpleNamespace(
            bars=bars.copy(deep=True),
            audit=object(),
        ),
    )
    monkeypatch.setattr(
        runner,
        "run_trend_family_event_walk_forward",
        lambda supplied: results,
    )

    def report_spy(
        supplied: object,
    ) -> object:
        reports.append(supplied)

        return (
            "deterministic-report"
        )

    def writer_spy(
        report: object,
        output_directory: str | Path,
        *,
        overwrite: bool = False,
    ) -> tuple[Path, ...]:
        writes.append(
            (
                report,
                Path(output_directory),
                overwrite,
            )
        )

        return ()

    monkeypatch.setattr(
        runner,
        "build_day13_event_walk_forward_report",
        report_spy,
    )
    monkeypatch.setattr(
        runner,
        "write_day13_event_walk_forward_artifacts",
        writer_spy,
    )

    runner.main([])
    runner.main([])

    assert reports == [
        results,
        results,
    ]
    assert writes[0] == writes[1]
