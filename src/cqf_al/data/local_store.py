"""Immutable local Parquet storage with metadata manifests."""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from cqf_al.data.config_loader import (
    load_project_config,
    resolve_data_directories,
)


class ImmutableStoreError(RuntimeError):
    """Raised when an immutable dataset cannot be stored safely."""


@dataclass(frozen=True)
class StoredArtifact:
    """Paths and identifying information for a stored dataset."""

    data_path: Path
    manifest_path: Path
    sha256: str
    row_count: int


def _safe_component(value: str) -> str:
    """Validate a safe directory or filename component."""

    if not re.fullmatch(r"[A-Za-z0-9_.-]+", value):
        raise ImmutableStoreError(
            f"Unsafe storage identifier: {value!r}"
        )

    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


class LocalParquetStore:
    """Write immutable Parquet data and JSON provenance manifests."""

    def __init__(
        self,
        *,
        data_root: Path,
        metadata_root: Path,
        allow_overwrite: bool = False,
    ) -> None:
        self.data_root = Path(data_root)
        self.metadata_root = Path(metadata_root)
        self.allow_overwrite = allow_overwrite

    @classmethod
    def from_project_config(
        cls,
        config: dict[str, Any] | None = None,
    ) -> "LocalParquetStore":
        project_config = config or load_project_config()
        directories = resolve_data_directories(project_config)

        return cls(
            data_root=directories["raw"],
            metadata_root=directories["metadata"],
            allow_overwrite=project_config["data"][
                "allow_raw_overwrite"
            ],
        )

    def write(
        self,
        frame: pd.DataFrame,
        *,
        dataset_kind: str,
        dataset_id: str,
        metadata: dict[str, Any],
    ) -> StoredArtifact:
        """Store a dataset exactly once unless overwrite is enabled."""

        if frame.empty:
            raise ImmutableStoreError("Cannot store an empty dataset.")

        kind = _safe_component(dataset_kind)
        identifier = _safe_component(dataset_id)

        data_directory = self.data_root / kind
        metadata_directory = self.metadata_root / kind

        data_directory.mkdir(parents=True, exist_ok=True)
        metadata_directory.mkdir(parents=True, exist_ok=True)

        data_path = data_directory / f"{identifier}.parquet"
        manifest_path = metadata_directory / f"{identifier}.json"

        if not self.allow_overwrite:
            existing = [
                path
                for path in (data_path, manifest_path)
                if path.exists()
            ]

            if existing:
                raise ImmutableStoreError(
                    "Immutable dataset already exists: "
                    + ", ".join(str(path) for path in existing)
                )

        temporary_data = data_path.with_suffix(".parquet.tmp")
        temporary_manifest = manifest_path.with_suffix(".json.tmp")

        frame.to_parquet(
            temporary_data,
            index=False,
            engine="pyarrow",
        )

        file_hash = _sha256(temporary_data)

        manifest = {
            "dataset_id": identifier,
            "dataset_kind": kind,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "row_count": int(len(frame)),
            "columns": list(frame.columns),
            "minimum_timestamp": (
                frame["timestamp"].min().isoformat()
                if "timestamp" in frame
                else None
            ),
            "maximum_timestamp": (
                frame["timestamp"].max().isoformat()
                if "timestamp" in frame
                else None
            ),
            "sha256": file_hash,
            "data_path": str(data_path),
            "metadata": metadata,
        }

        with temporary_manifest.open("w", encoding="utf-8") as file:
            json.dump(
                manifest,
                file,
                indent=2,
                sort_keys=True,
                default=str,
            )

        os.replace(temporary_data, data_path)
        os.replace(temporary_manifest, manifest_path)

        return StoredArtifact(
            data_path=data_path,
            manifest_path=manifest_path,
            sha256=file_hash,
            row_count=len(frame),
        )

    def read(
        self,
        *,
        dataset_kind: str,
        dataset_id: str,
    ) -> pd.DataFrame:
        """Read a previously stored immutable dataset."""

        path = (
            self.data_root
            / _safe_component(dataset_kind)
            / f"{_safe_component(dataset_id)}.parquet"
        )

        if not path.exists():
            raise ImmutableStoreError(f"Dataset not found: {path}")

        return pd.read_parquet(path)
