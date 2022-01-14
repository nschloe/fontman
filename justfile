version := `python3 -c "from configparser import ConfigParser; p = ConfigParser(); p.read('setup.cfg'); print(p['metadata']['version'])"`
name := `python3 -c "from configparser import ConfigParser; p = ConfigParser(); p.read('setup.cfg'); print(p['metadata']['name'])"`


default:
	@echo "\"just publish\"?"

# tag:
# 	@if [ "$(git rev-parse --abbrev-ref HEAD)" != "main" ]; then exit 1; fi
# 	curl -H "Authorization: token `cat ~/.github-access-token`" -d '{"tag_name": "{{version}}"}' https://api.github.com/repos/nschloe/{{name}}/releases

upload: clean
	@if [ "$(git rev-parse --abbrev-ref HEAD)" != "main" ]; then exit 1; fi
	flit publish

publish: tag upload

clean:
	@find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
	@rm -rf src/*.egg-info/ build/ dist/ .tox/

format:
	isort .
	black .
	blacken-docs README.md

lint:
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
