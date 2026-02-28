.PHONY: setup run seed test verify load

setup:
	uv sync --extra dev

run:
	uv run uvicorn app.main:app --reload

seed:
	uv run python -m app.seed

test:
	uv run pytest tests/ -v

verify:
	$(MAKE) test

load:
	@echo "Sending 50 requests to /api/users/profile/1 ..."
	@for i in $$(seq 1 50); do \
		curl -s -o /dev/null -w "req $$i: %{http_code} (%{time_total}s)\n" \
			http://localhost:8000/api/users/profile/1; \
	done
