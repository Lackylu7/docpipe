from pathlib import Path

from docpipe.pipeline import discover_files
from docpipe.synthetic import generate_synthetic_dataset


def test_generate_synthetic_dataset_writes_requested_file_count(tmp_path: Path) -> None:
    summary = generate_synthetic_dataset(tmp_path, file_count=24, seed=3)

    files = discover_files(tmp_path)
    assert summary.file_count == 24
    assert len(files) == 24
    assert len(summary.categories) >= 8
    assert any(path.suffix == ".csv" for path in files)
    assert any(path.suffix == ".html" for path in files)
    assert any(path.suffix == ".json" for path in files)


def test_generate_synthetic_dataset_is_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"

    generate_synthetic_dataset(first, file_count=10, seed=11)
    generate_synthetic_dataset(second, file_count=10, seed=11)

    first_files = sorted(path.relative_to(first).as_posix() for path in discover_files(first))
    second_files = sorted(path.relative_to(second).as_posix() for path in discover_files(second))
    assert first_files == second_files
