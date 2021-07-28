import fontman


def test_install_remove(monkeypatch):
    fontman.cli(["install", "adobe-fonts/source-code-pro"])
    fontman.cli(["list"])

    # remove and abort
    # https://stackoverflow.com/a/36377194/353337
    monkeypatch.setattr("builtins.input", lambda _: "n")
    out = fontman.cli(["rm", "adobe-fonts/source-code-pro"])
    assert out == 1

    # actually remove
    monkeypatch.setattr("builtins.input", lambda _: "y")
    out = fontman.cli(["rm", "adobe-fonts/source-code-pro"])
    assert out == 0


def test_list(monkeypatch):
    # show empty
    fontman.cli(["list"])

    monkeypatch.setattr("builtins.input", lambda _: "y")
    out = fontman.cli(["rm", "adobe-fonts/source-code-pro"])
    assert out == 1


def test_update(monkeypatch):
    # nothing to update
    out = fontman.cli(["up"])
    assert out == 0

    # install an outdated version of something
    fontman.cli(["install", "ibm/plex==v5.1.3"])

    # request update and abort
    monkeypatch.setattr("builtins.input", lambda _: "n")
    out = fontman.cli(["up"])
    assert out == 1

    # actually update
    monkeypatch.setattr("builtins.input", lambda _: "y")
    out = fontman.cli(["up"])
    assert out == 0
