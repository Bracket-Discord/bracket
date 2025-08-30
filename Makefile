# Include .env if it exists
ifneq (,$(wildcard .env))
	include .env
	export
endif


api-dev:
	uv run --package api uvicorn apps.api.main:app --reload

bot:
	@uv run --package bot python apps/bot/main.py
