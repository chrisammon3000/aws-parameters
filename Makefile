.PHONY: check
check: ## Run code quality tools.
	@echo "🚀 Linting code: Running pre-commit"
	@pre-commit run -a --show-diff-on-failure
	@echo "🚀 Static type checking: Running mypy"
	@mypy

.PHONY: test
test: ## Test the code with pytest
	@echo "🚀 Testing code: Running pytest"
	@pytest -v --cov --cov-config=pyproject.toml

.PHONY: build
build: clean-build ## Build wheel file using setuptools
	@echo "🚀 Creating wheel file"
	@python3 -m build --sdist --wheel
	@twine check dist/*

.PHONY: clean-build
clean-build: ## clean build artifacts
	@rm -rf dist
	@rm -rf build
	@rm -rf *.egg-info

.PHONY: publish.test
publish.test: build ## publish a release to pypi test repository.
	@echo "🚀 Publishing."
	@twine upload -r testpypi dist/* --verbose

.PHONY: build-and-publish
build-and-publish: build publish ## Build and publish.