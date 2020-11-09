lint:
	poetry run black .
	poetry run isort .

tests:
	poetry run pytest --cov-report term-missing --cov-branch --cov=. tests/
	poetry run black --check .
	poetry run isort -c .
	poetry run flake8 .

.PHONY: lint tests
