.PHONY: dev test lint eval up down migrate
test:    ; uv run pytest -m "not integration and not eval"
lint:    ; uv run ruff check . && uv run ruff format --check .
eval:    ; uv run python -m evals.run
up:      ; docker compose up -d
down:    ; docker compose down
migrate: ; uv run alembic upgrade head
