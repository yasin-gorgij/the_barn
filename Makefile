.PHONY: install
install:
	uv sync

.PHONY: collectstatic
collectstatic:
	uv run manage.py collectstatic --noinput

.PHONY: check
check:
	uv run manage.py check

.PHONY: format
format:
	uv run reorder-python-imports --py313-plus
	uv run ruff format

.PHONY: lint
lint: format
	uv run ruff check --select I --fix --show-fixes

.PHONY: migrate
migrate: format
	uv run manage.py migrate

.PHONY: migrations
migrations:
	uv run manage.py makemigrations

.PHONY: push
push:
	git push -u origin main

.PHONY: run
run:
	uv run manage.py runserver

.PHONY: shell
shell:
	uv run manage.py shell

.PHONY: superuser
superuser:
	uv run manage.py createsuperuser

.PHONY: test
test: format
	uv run pytest
