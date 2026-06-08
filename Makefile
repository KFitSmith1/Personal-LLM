# Personal LLM — one-word commands. Run `make help` for the list.
# Overlays are composable, e.g.:  make up CADDY=1 TTS=1

COMPOSE := docker compose -f docker-compose.yml
ifdef CADDY
COMPOSE += -f compose.caddy.yml
endif
ifdef N8N
COMPOSE += -f integrations/n8n/compose.n8n.yml
endif
ifdef TTS
COMPOSE += -f integrations/tts/compose.kokoro.yml
endif
ifdef MCPO
COMPOSE += -f integrations/composio/compose.mcpo.yml
endif

.DEFAULT_GOAL := help

.PHONY: help setup up down restart ps logs models caddy tts n8n config demo demo-down backup restore

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

demo: ## Local test on your laptop (no GPU, tiny model) -> http://localhost:3000
	./scripts/demo.sh

demo-down: ## Stop the local test stack (add WIPE=1 to also delete its data)
	docker compose -f docker-compose.test.yml down $(if $(WIPE),-v,)

setup: ## First-time bootstrap (Docker, NVIDIA toolkit, secrets, boot, models)
	./scripts/setup.sh

up: ## Start the stack (flags: CADDY=1 N8N=1 TTS=1 MCPO=1)
	$(COMPOSE) up -d

down: ## Stop and remove containers
	$(COMPOSE) down

restart: ## Restart the stack
	$(COMPOSE) restart

ps: ## Show running services
	$(COMPOSE) ps

logs: ## Tail logs (Ctrl-C to stop)
	$(COMPOSE) logs -f --tail=100

config: ## Validate the (possibly overlaid) compose config
	$(COMPOSE) config -q && echo OK

models: ## Pull models + build the kevin-assistant persona
	./scripts/pull-models.sh

backup: ## Back up data volumes + secrets (MODELS=1 to include models)
	./scripts/backup.sh

restore: ## Restore from a backup folder:  make restore DIR=./backups/...
	./scripts/restore.sh $(DIR)

caddy: ## Start with the HTTPS reverse proxy
	$(MAKE) up CADDY=1

tts: ## Start with Kokoro TTS (audio overviews)
	$(MAKE) up TTS=1

n8n: ## Start with the n8n automation overlay
	$(MAKE) up N8N=1
