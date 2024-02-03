VERSION=$(shell grep ^version pyproject.toml | gawk -F"[= ]" '{print $$NF}' | tr -d '"')
NAME=$(shell grep ^name pyproject.toml | gawk -F"[= ]" '{print $$NF}' | tr -d '"')

.PHONY: all name version lint git_tag

all: requirements.txt requirements-dev.txt lint sync

tag:
	git tag -a v$(VERSION) -m " auto-tagged"

version: pyproject.toml
	echo $(VERSION)

name: pyproject.toml
	echo $(NAME)

requirements.txt: poetry.lock
	poetry export -f requirements.txt --without-hashes \
		--without dev --output requirements.txt

requirements-dev.txt: poetry.lock
	poetry export -f requirements.txt --without-hashes \
		--only dev --output requirements-dev.txt

poetry.lock: pyproject.toml
	poetry lock --no-update

lint: poetry.lock src tests
	isort src tests
	black src tests
	flake8 src tests
	mypy src tests

sync: poetry.lock
	poetry install --sync --no-root