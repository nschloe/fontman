import fontman


def test_install_remove():
    fontman.cli(["install", "adobe-fonts/source-code-pro"])
    fontman.cli(["rm", "adobe-fonts/source-code-pro", "--yes"])


def test_list():
    fontman.cli(["list"])


def test_update():
    fontman.cli(["up"])
