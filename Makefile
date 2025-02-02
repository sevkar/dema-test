init:
	pip install uv
	uv sync --frozen

lint:
	pre-commit run --all-files

local_run:
	cp .env.example .env
	docker compose up -d --wait
	uv run alembic upgrade head
	uv run src/main.py