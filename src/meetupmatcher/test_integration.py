from pathlib import Path

import pytest

from meetupmatcher.main import main
from meetupmatcher.util.compat_resource import resources


def get_test_pairs() -> list[tuple[Path, Path]]:
    test_files_dir = Path(resources.files("meetupmatcher.test_data"))  # type: ignore
    test_files: list[Path] = sorted(
        f for f in test_files_dir.iterdir() if f.is_file() and f.name.endswith(".csv")
    )
    expect_files: list[Path] = sorted(
        f
        for f in test_files_dir.iterdir()
        if f.is_file() and f.name.endswith(".txt") and f.name.startswith("out_")
    )
    return list(zip(test_files, expect_files))


@pytest.mark.parametrize("inpt,outpt", get_test_pairs())
def test_integration(inpt: Path, outpt: Path, capsys):
    main(["--dry-run", "--seed", "0", str(inpt)])
    captured = capsys.readouterr()
    expected = outpt.read_text()
    assert captured.out == expected
