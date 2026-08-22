# ──────────────────────────────────────────────────────────────────────────────
# Makefile для проєкту telco-churn-mlops-synthetic
# ──────────────────────────────────────────────────────────────────────────────

.PHONY: help install dev install-dev generate generate-ext explore lint format clean clean-data dvc-repro dvc-params dvc-exp docker-build docker-run docker-up docker-down

# ──────────────────────────────────────────────────────────────────────────────
# Основні команди
# ──────────────────────────────────────────────────────────────────────────────

help: ## Показати цю довідку
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Створити віртуальне середовище та встановити основні залежності
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip
	. .venv/bin/activate && pip install -r requirements.txt

dev: install-dev ## Встановити залежності для розробки (ruff, black, jupyter тощо)
install-dev:
	. .venv/bin/activate && pip install -r requirements-dev.txt
	. .venv/bin/activate && pre-commit install

generate: ## Згенерувати базовий датасет через Hydra
	. .venv/bin/activate 2>/dev/null || true; python3 src/generate_dataset.py generation.samples=50000

generate-ext: ## Згенерувати розширений датасет через Hydra (табличні + conversations + knowledge base)
	. .venv/bin/activate 2>/dev/null || true; python3 src/generate_dataset_ext.py

explore: ## Запустити JupyterLab для дослідження даних
	. .venv/bin/activate 2>/dev/null || true; jupyter lab notebooks/

lint: ## Перевірити код стилем (ruff + black --check)
	. .venv/bin/activate 2>/dev/null || true; ruff check src/ notebooks/
	. .venv/bin/activate 2>/dev/null || true; black --check src/ notebooks/

format: ## Автоматично відформатувати код (black + ruff --fix)
	. .venv/bin/activate 2>/dev/null || true; black src/ notebooks/
	. .venv/bin/activate 2>/dev/null || true; ruff check --fix src/ notebooks/

# ──────────────────────────────────────────────────────────────────────────────
# DVC Pipeline та Experiment команди
# ──────────────────────────────────────────────────────────────────────────────

dvc-repro: ## Відтворити DVC пайплайн генерації даних
	PATH=".venv/bin:$$PATH" dvc repro

dvc-params: ## Переглянути відмінності параметрів у конфігурації через DVC
	PATH=".venv/bin:$$PATH" dvc params diff

dvc-exp: ## Запустити DVC experiment з можливістю перевизначення конфігу
	PATH=".venv/bin:$$PATH" dvc exp run

clean: ## Видалити тимчасові файли, venv, кеш
	rm -rf .venv venv
	rm -rf __pycache__ *.pyc *.pyo .pytest_cache .ruff_cache
	rm -rf notebooks/.ipynb_checkpoints

clean-data: ## Видалити всі згенеровані дані
	rm -rf data/*.csv data/*.json

# ──────────────────────────────────────────────────────────────────────────────
# Docker команди
# ──────────────────────────────────────────────────────────────────────────────

docker-build: ## Зібрати Docker-образ
	docker build -t telco-churn-generator:latest .

docker-run: ## Запустити генерацію всередині контейнера з параметрами Hydra
	docker run --rm \
		-v $(PWD)/data:/app/data \
		-v $(PWD)/config:/app/config \
		telco-churn-generator:latest \
		python src/generate_dataset_ext.py generation.samples=30000 generation.conv_samples=5000

docker-up: ## Запустити docker-compose
	docker compose up --build

docker-down: ## Зупинити та видалити контейнери
	docker compose down

# ──────────────────────────────────────────────────────────────────────────────
# Приклади використання з параметрами Hydra
# ──────────────────────────────────────────────────────────────────────────────

generate-small: ## Швидка генерація невеликого датасету для тестів
	. .venv/bin/activate 2>/dev/null || true; python3 src/generate_dataset_ext.py generation.samples=10000 generation.conv_samples=1500

generate-demo: ## Генерація для демо на занятті (~30–50 тис. рядків)
	. .venv/bin/activate 2>/dev/null || true; python3 src/generate_dataset_ext.py generation.samples=40000 generation.conv_samples=6000

# ──────────────────────────────────────────────────────────────────────────────
# Jupyter Notebook / Lab в Docker
# ──────────────────────────────────────────────────────────────────────────────

jupyter-up: ## Запустити JupyterLab у контейнері (порт 8888)
	docker compose up -d jupyter

jupyter-down: ## Зупинити Jupyter контейнер
	docker compose down jupyter

jupyter-logs: ## Показати логи Jupyter (корисний для отримання token)
	docker compose logs -f jupyter

jupyter-build: ## Перебудувати Jupyter
	docker compose build jupyter

jupyter-bash: ## Зайти в bash всередину запущеного Jupyter контейнера
	docker compose exec jupyter bash

jupyter-clean: ## Видалити Jupyter контейнер та образ
	docker compose down jupyter --rmi local