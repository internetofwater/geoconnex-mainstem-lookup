pre-commit:
	pre-commit install 
	pre-commit run --all-files

check:
	uv run ruff check && uv run pyright

deps:
	# Using uv, install all Python dependencies needed for local development and spin up necessary docker services
	uv sync --all-groups --all-packages