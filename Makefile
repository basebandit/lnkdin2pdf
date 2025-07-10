.PHONY: setup-dev-env

setup-dev-env:
	@echo "✅ Installing dev dependencies with uv..."
	uv sync --all-groups

	@echo "✅ Installing pre-commit hooks..."
	pre-commit install
	pre-commit install --hook-type commit-msg

	@echo "✅ Writing commit-msg hook manually..."
	@printf '#!/bin/sh\nuv run cz check --commit-msg-file "$$1"\n' > .git/hooks/commit-msg
	@chmod +x .git/hooks/commit-msg

	@echo "✅ Dev environment is ready!"
