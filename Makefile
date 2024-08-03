VERSION=$(shell grep ^version pyproject.toml | gawk -F"[= ]" '{print $$NF}' | tr -d '"')
NAME=$(shell grep ^name pyproject.toml | gawk -F"[= ]" '{print $$NF}' | tr -d '"')
DIR:=${CURDIR}
EXAMPLE_DIR:=$(DIR)/extras/example_app_pkg
MAKE:=make
src_files:=$(shell find $(DIR) -type f -name '*.py')

.PHONY: all name version lint git_tag shell example-image test docs

all: lint test build

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

shell: poetry.lock
	poetry install --no-root --sync

lint: poetry.lock src tests
	isort src tests extras docs/source
	black src tests extras docs/source
	flake8 src tests extras docs/source
	$(DIR)/scripts/dmypy.sh src tests extras

sync: poetry.lock
	poetry install --sync --no-root

build: sync
	poetry build

render:
	helm template chart-instance k8s/defaultchart | yq -C | less -R

example-image: $(EXAMPLE_DIR)/Dockerfile $(EXAMPLE_DIR)/basichttp.py pyproject.toml
	docker build $(EXAMPLE_DIR) -t python-httpserver:$(VERSION)

kind-load: example-image
	kind load docker-image python-httpserver:$(VERSION) -n deploydocus

test: requirements-dev.txt
	PYTHONPATH=src:extras pytest tests

docs:
	$(MAKE) -C docs html

.PHONY: preview-docs
preview-docs: docs
	python -m http.server 9000 --bind=127.0.0.1 --directory docs/build/html

.PHONY: site
site:
	$(MAKE) -C docs/project_site build

.PHONY: preview-site
preview-site: site
	$(MAKE) -C docs/project_site preview


.PHONY: deploy-site
deploy-site: site
	firebase deploy  --only hosting:deploydocus