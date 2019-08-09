cov:
	pytest --cov-report term-missing --cov-branch --cov=pixi tests/

lint:
	isort -rc .
	flake8

tests:
	pytest
	isort -rc -c .
	flake8

.PHONY: cov lint tests
