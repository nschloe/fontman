import fontman


def test_install_remove():
    fontman.cli(["install", "adobe-fonts/source-code-pro"])
    fontman.cli(["list"])
    fontman.cli(["rm", "adobe-fonts/source-code-pro", "--yes"])


def test_list():
    # show empty
    fontman.cli(["list"])

    out = fontman.cli(["rm", "adobe-fonts/source-code-pro", "--yes"])
    assert out == 1


def test_update(monkeypatch):
    # https://stackoverflow.com/a/36377194/353337
    monkeypatch.setattr("builtins.input", lambda _: "y")

    fontman.cli(["install", "ibm/plex==v5.1.3"])
    fontman.cli(["up"])
