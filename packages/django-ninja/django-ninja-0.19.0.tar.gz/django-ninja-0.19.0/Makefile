.PHONY: help docs
.DEFAULT_GOAL := help

help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	flit install --deps develop --symlink

lint: ## Run code linters
	black --check ninja tests
	isort --check ninja tests
	flake8 ninja tests
	mypy ninja

fmt format: ## Run code formatters
	black ninja tests
	isort ninja tests

test: ## Run tests
	pytest .

test-cov: ## Run tests with coverage
	pytest --cov=ninja --cov-report term-missing tests
