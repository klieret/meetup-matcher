from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from meetupmatcher.main import main
from meetupmatcher.util.compat_resource import resources

test_files_dir = Path(resources.files("meetupmatcher.test_data"))  # type: ignore


def get_test_pairs() -> list[tuple[Path, Path, Path]]:
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


def _test_expected_output(
    inpt: Path, config: Path, outpt: Path, additional_args: list[str] | None = None
):
    if additional_args is None:
        additional_args = []
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        main,
        [
            "--dry-run",
            "--seed",
            "0",
            str(inpt),
            "--config",
            str(config),
            *additional_args,
        ],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert result.output == outpt.read_text()


@pytest.mark.parametrize("inpt,config,outpt", get_test_pairs())
def test_expected_output(inpt: Path, config: Path, outpt: Path):
    _test_expected_output(inpt=inpt, config=config, outpt=outpt)


def test_specified_template_dir():
    tfd = test_files_dir
    template_dir = Path(resources.files("meetupmatcher.templates"))  # type: ignore
    _test_expected_output(
        inpt=tfd / "default.csv",
        config=tfd / "default.yaml",
        outpt=tfd / "out_default.txt",
        additional_args=["--templates", str(template_dir)],
    )
