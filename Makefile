.PHONY: check
check: ## Run code quality tools.
	@echo "🚀 Linting code: Running pre-commit"
	@pre-commit run -a
	@echo "🚀 Static type checking: Running mypy"
	@mypy

.PHONY: test
test: ## Test the code with pytest
	@echo "🚀 Testing code: Running pytest"
	@pytest -v --cov --cov-config=pyproject.toml