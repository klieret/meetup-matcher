from pathlib import Path

import pytest
from click.testing import CliRunner

from meetupmatcher.main import main
from meetupmatcher.util.compat_resource import resources


def get_test_pairs() -> list[tuple[Path, Path, Path]]:
    test_files_dir = Path(resources.files("meetupmatcher.test_data"))  # type: ignore
    test_files: list[Path] = sorted(
        f for f in test_files_dir.iterdir() if f.is_file() and f.name.endswith(".csv")
    )
    config_files: list[Path] = sorted(
        f for f in test_files_dir.iterdir() if f.is_file() and f.name.endswith(".yaml")
    )
    expect_files: list[Path] = sorted(
        f
        for f in test_files_dir.iterdir()
        if f.is_file() and f.name.endswith(".txt") and f.name.startswith("out_")
    )
    return list(zip(test_files, config_files, expect_files))


@pytest.mark.parametrize("inpt,config,outpt", get_test_pairs())
def test_integration(inpt: Path, config: Path, outpt: Path):
    runner = CliRunner()
    result = runner.invoke(
        main, ["--dry-run", "--seed", "0", str(inpt), "--config", str(config)]
    )
    assert result.exit_code == 0
    assert result.output == outpt.read_text()
