cov:
	poetry run pytest --cov-report term-missing --cov-branch --cov=pixi tests/

lint:
	poetry run isort -rc .
	poetry run flake8

tests:
	poetry run pytest
	poetry run isort -rc -c .
	poetry run flake8

.PHONY: lint tests
