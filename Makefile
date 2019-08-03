cov:
	poetry run pytest --cov-report term-missing --cov-branch --cov=pixi tests/

lint:
	poetry run isort -rc pixi
	poetry run flake8 pixi

tests:
	poetry run pytest
	poetry run isort -rc -c .
	poetry run flake8

.PHONY: lint tests
