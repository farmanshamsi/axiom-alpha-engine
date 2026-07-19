import pandas as pd
import pytest

from cqf_al.data.local_store import (
    ImmutableStoreError,
    LocalParquetStore,
)


def sample_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                ["2025-12-15T14:30:00Z"],
                utc=True,
            ),
            "symbol": ["SPY"],
            "close": [680.5],
        }
    )


def test_write_and_read_parquet(tmp_path) -> None:
    store = LocalParquetStore(
        data_root=tmp_path / "raw",
        metadata_root=tmp_path / "metadata",
    )

    artifact = store.write(
        sample_frame(),
        dataset_kind="bars",
        dataset_id="spy_test",
        metadata={"provider": "test"},
    )

    assert artifact.data_path.exists()
    assert artifact.manifest_path.exists()
    assert len(artifact.sha256) == 64

    result = store.read(
        dataset_kind="bars",
        dataset_id="spy_test",
    )

    assert len(result) == 1
    assert result.loc[0, "symbol"] == "SPY"


def test_immutable_write_rejects_duplicate(tmp_path) -> None:
    store = LocalParquetStore(
        data_root=tmp_path / "raw",
        metadata_root=tmp_path / "metadata",
    )

    arguments = {
        "dataset_kind": "bars",
        "dataset_id": "spy_test",
        "metadata": {"provider": "test"},
    }

    store.write(sample_frame(), **arguments)

    with pytest.raises(ImmutableStoreError):
        store.write(sample_frame(), **arguments)
