import sys

from meetupmatcher.main import main

if sys.version_info >= (3, 9):
    from importlib import resources
else:
    import importlib_resources as resources


def test_integration(capsys):
    with resources.path("meetupmatcher.test_data", "test.csv") as csv_path:
        main(["--dry-run", "--seed", "0", str(csv_path)])
    captured = capsys.readouterr()
    expected = resources.read_text("meetupmatcher.test_data", "out.txt")
    assert captured.out == expected
