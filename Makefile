.PHONY: test test_flake test_cli

test: test_flake test_cli

test_flake:
	flake8 salmonberry.py --max-line-length=88

test_cli:
	pytest tests/cli

test_cli_loop:
	tdd 'make test_cli'
