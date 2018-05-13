.PHONY: test test_flake test_cli test_unit

test: test_pytest test_flake

test_flake:
	flake8 salmonberry.py --max-line-length=88

test_pytest:
	python3 -m pytest tests/

test_cli:
	python3 -m pytest tests/cli

test_unit:
	python3 -m pytest tests/unit

test_cli_loop:
	tdd 'make test_cli'

test_loop:
	tdd 'make test'
