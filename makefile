pre-commit:
	pre-commit install 
	pre-commit run --all-files

check:
	uv run ruff check && uv run pyright

deps:
	# Using uv, install all Python dependencies needed for local development and spin up necessary docker services
	uv sync --all-groups --all-packages

push_merged_gpkg:
	oras push ghcr.io/internetofwater/geoconnex-mainstem-lookup-gpkg:latest merged.gpkg:application/octet-stream --username internetofwater --password $(GITHUB_TOKEN) --annotation 'org.opencontainers.image.source=https://github.com/internetofwater/geoconnex-mainstem-lookup'

pull_merged_gpkg:
	oras pull ghcr.io/internetofwater/geoconnex-mainstem-lookup-gpkg:latest merged.gpkg