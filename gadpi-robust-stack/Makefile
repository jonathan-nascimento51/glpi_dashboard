.PHONY: dev fe be lint typecheck test storybook ci precommit-install
dev:
	@$(MAKE) -j2 be fe
fe:
	cd frontend && npm run dev || echo "Configure seu script dev no package.json"
be:
	cd backend && uvicorn app.main:app --reload
lint:
	cd backend && ruff check . && black --check . && mypy . || true
	cd frontend && npx eslint .
typecheck:
	cd frontend && npx tsc --noEmit
test:
	cd backend && pytest
	cd frontend && npx vitest run
storybook:
	cd frontend && npm run storybook
ci: lint typecheck test
precommit-install:
	pre-commit install