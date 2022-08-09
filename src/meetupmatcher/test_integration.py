from meetupmatcher.main import main
from meetupmatcher.util.compat_resource import resources


def test_integration(capsys):
    with resources.path("meetupmatcher.test_data", "test.csv") as csv_path:
        main(["--dry-run", "--seed", "0", str(csv_path)])
    captured = capsys.readouterr()
    expected = resources.read_text("meetupmatcher.test_data", "out.txt")
    assert captured.out == expected
