from __future__ import annotations

import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from meetupmatcher.main import main
from meetupmatcher.util.compat_resource import resources
from meetupmatcher.util.log import logger

test_files_dir = Path(resources.files("meetupmatcher.test_data"))  # type: ignore


def get_test_pairs() -> list[tuple[Path, Path, Path]]:
    test_files: list[Path] = sorted(
        f
        for f in test_files_dir.iterdir()
        if f.is_file() and f.name.endswith(".csv") and not f.name.startswith("_")
    )
    config_files: list[Path] = sorted(
        f
        for f in test_files_dir.iterdir()
        if f.is_file() and f.name.endswith(".yaml") and not f.name.startswith("_")
    )
    expect_files: list[Path] = sorted(
        f
        for f in test_files_dir.iterdir()
        if f.name.endswith(".txt") and not f.name.startswith("_")
    )
    return list(zip(test_files, config_files, expect_files))


def _build_command(
    inpt: Path, config: Path | None, additional_args: list[str] | None = None
):
    if additional_args is None:
        additional_args = []
    command = [
        "--dry-run",
        "--seed",
        "0",
        str(inpt),
    ]
    if config is not None:
        command.extend(["--config", str(config)])
    command.extend(additional_args)
    return command


def _run_command(command: list[str]):
    runner = CliRunner(mix_stderr=False)
    return runner.invoke(
        main,
        command,
        catch_exceptions=False,
    )


def _test_expected_output(
    inpt: Path,
    config: Path | None,
    outpt: Path,
    additional_args: list[str] | None = None,
):
    if additional_args is None:
        additional_args = []
    command = _build_command(inpt, config, additional_args)
    result = _run_command(command)
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
        outpt=tfd / "default.txt",
        additional_args=["--templates", str(template_dir)],
    )


def test_unspecified_config():
    tfd = test_files_dir
    _test_expected_output(
        inpt=tfd / "default.csv",
        config=None,
        outpt=tfd / "default.txt",
    )


if __name__ == "__main__":
    os.environ["MEETUPMATCHER_TESTING"] = "True"
    # Update all test outputs
    test_pairs = get_test_pairs()
    logger.info(f"Updating {test_pairs} test outputs")
    for csv, config, out in test_pairs:
        logger.info((csv, config, out))
        command = _build_command(csv, config)
        logger.info(" ".join(command))
        result = _run_command(command)
        logger.info(f"Writing to {out}")
        out.write_text(result.output)
