VERSION=$(shell grep ^version pyproject.toml | gawk -F"[= ]" '{print $$NF}' | tr -d '"')
NAME=$(shell grep ^name pyproject.toml | gawk -F"[= ]" '{print $$NF}' | tr -d '"')
DIR:=${CURDIR}

.PHONY: all name version lint git_tag

all: lint build

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
	isort src tests extras
	black src tests extras
	flake8 src tests extras
	$(DIR)/scripts/dmypy.sh src tests extras

sync: poetry.lock
	poetry install --sync --no-root

build: sync
	poetry build

render:
	helm template chart-instance k8s/defaultchart | yq -C | less -R