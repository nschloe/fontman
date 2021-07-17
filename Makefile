VERSION=$(shell python3 -c "from configparser import ConfigParser; p = ConfigParser(); p.read('setup.cfg'); print(p['metadata']['version'])")

default:
	@echo "\"make publish\"?"

# https://packaging.python.org/distributing/#id72
upload:
	# Make sure we're on the main branch
	@if [ "$(shell git rev-parse --abbrev-ref HEAD)" != "main" ]; then exit 1; fi
	rm -f dist/*
	# python3 setup.py sdist bdist_wheel
	# https://stackoverflow.com/a/58756491/353337
	python3 -m build --sdist --wheel .
	twine upload dist/*

tag:
	@if [ "$(shell git rev-parse --abbrev-ref HEAD)" != "main" ]; then exit 1; fi
	# Always create a github "release"; this automatically creates a Git tag, too.
	curl -H "Authorization: token `cat $(HOME)/.github-access-token`" -d '{"tag_name": "v$(VERSION)"}' https://api.github.com/repos/nschloe/fontman/releases

publish: tag upload

clean:
	@find . | grep -E "(__pycache__|\.pyc|\.pyo$\)" | xargs rm -rf
	@rm -rf *.egg-info/ build/ dist/ MANIFEST .pytest_cache/

format:
	isort .
	black .
	blacken-docs README.md

lint:
	isort --check .
	black --check .
	flake8 .

install:
	@fontman install \
		-t ~/.github-access-token \
		microsoft/cascadia-code \
		be5invis/Iosevka \
		i-tu/Hasklig \
		adobe-fonts/source-code-pro \
		rsms/inter \
		googlefonts/roboto \
		tonsky/FiraCode \
		JetBrains/JetBrainsMono \
		larsenwork/monoid \
		IBM/plex \
		belluzj/fantasque-sans \
		madmalik/mononoki \
		adobe-fonts/source-sans \
		adobe-fonts/source-serif

remove:
	@fontman rm \
		microsoft/cascadia-code \
		be5invis/Iosevka \
		i-tu/Hasklig \
		adobe-fonts/source-code-pro \
		rsms/inter \
		googlefonts/roboto \
		tonsky/FiraCode \
		JetBrains/JetBrainsMono \
		larsenwork/monoid \
		IBM/plex \
		belluzj/fantasque-sans \
		madmalik/mononoki \
		adobe-fonts/source-sans \
		adobe-fonts/source-serif
