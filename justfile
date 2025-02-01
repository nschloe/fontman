version := `python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])"`

default:
	@echo "\"just publish\"?"

publish: release

release:
	@if [ "$(git rev-parse --abbrev-ref HEAD)" != "main" ]; then exit 1; fi
	gh release create {{version}}

clean:
	@find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
	@rm -rf src/*.egg-info/ build/ dist/ .tox/ htmlcov/

format:
	black src/ tests/
	ruff check src/ tests/ --fix
	blacken-docs README.md

lint:
	pre-commit run --all

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
		adobe-fonts/source-serif \
		source-foundry/Hack \
		arrowtype/recursive \
		uswds/public-sans

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
		adobe-fonts/source-serif \
		source-foundry/Hack \
		arrowtype/recursive \
		uswds/public-sans
