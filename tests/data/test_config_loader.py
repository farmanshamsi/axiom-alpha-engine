from pathlib import Path

from cqf_al.data.config_loader import (
    find_project_root,
    load_project_config,
    resolve_data_directories,
)


def test_project_root_contains_pyproject() -> None:
    root = find_project_root()
    assert (root / "pyproject.toml").exists()


def test_project_config_loads() -> None:
    config = load_project_config()

    assert config["project"]["name"] == "cqf-algorithmic-trading"
    assert config["broker"]["paper"] is True
    assert config["safety"]["allow_live_trading"] is False


def test_data_directories_are_inside_project() -> None:
    root = find_project_root()
    directories = resolve_data_directories()

    for path in directories.values():
        assert isinstance(path, Path)
        assert path.is_relative_to(root)
