# Enhanced Telco Dataset Generator with Text Data


# Telco Customer Churn – Synthetic Dataset with Data Drift

 [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

 [![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)


## Synthetic dataset for working through the full MLOps cycle:

- training churn classification models

- monitoring data drift / concept drift

- automated retraining

- shadow datasets, A/B testing models, etc.

 

 **Does not contain any real customer records** – completely generated programmatically.

 

### Source of inspiration

 The structure and statistical distributions are based on a public dataset:

 **Telco Customer Churn**

 https://www.kaggle.com/datasets/blastchar/telco-customer-churn

 Original license: CC BY-NC-SA 4.0

 

## This repository does not contain or distribute the original dataset.
 

### Synthetic Data Features

- 100,000+ records

- Period: 2023-01-01 → 2024-12-31

- Gradual conceptual drift (Fiber optic growth, Electronic check decline, churn decline, etc.)

- `RecordDate` column for time analysis

- Realistic dependencies between features (like in the real world)

 

## How to generate a dataset


## 1. Clone the repository

```sh
 git clone https://github.com/<your repo>/telco-churn-mlops-synthetic.git
```
```sh
 cd telco-churn-mlops-synthetic
```
 

## 2. Create a virtual environment and install dependencies

```sh
 python -m venv venv
```
```sh
 source venv/bin/activate # Windows: venv\\Scripts\\activate
```
```sh
 pip install -r requirements.txt
```
 

## 3. Generate a dataset with Hydra & DVC

### Running with Default Configuration
```sh
python src/generate_dataset_ext.py
```

### Runtime Overrides via Hydra
You can override any parameter in `config/config.yaml` directly from the CLI:
```sh
# Override samples and conversations
python src/generate_dataset_ext.py generation.samples=20000 generation.conv_samples=3000

# Override drift & pricing parameters
python src/generate_dataset_ext.py drift.fiber_growth_rate=0.35 pricing.base_charge=25.0

# Base generator with Hydra override
python src/generate_dataset.py generation.samples=50000
```

### DVC Pipeline & Reproducibility
The data generation stage and its parameter dependencies from `config/config.yaml` are tracked with DVC (`dvc.yaml`):

```sh
# Check parameter diffs
dvc params diff

# Reproduce pipeline (re-runs when config.yaml or src/ files change)
dvc repro

# Run DVC experiment with parameter override
dvc exp run -S config/config.yaml:generation.samples=20000
```

## 📊 What will you get?
```
data/
├── telco_customers.csv           # Tabular customer churn data with drift
├── support_conversations.csv     # Synthesized support dialogues
├── knowledge_base.csv            # Knowledge base documents (CSV)
└── knowledge_base.json           # Knowledge base documents (JSON)
```

# Recommendations for using make

- `make help` — see all available commands
- `make install` — create venv and install dependencies
- `make generate-ext` — generate extended dataset using Hydra
- `make dvc-repro` — reproduce pipeline using DVC
- `make dvc-params` — view parameter diffs tracked by DVC
- `make dvc-exp` — run DVC experiment
- `make explore` — open JupyterLab
- `make lint` — check style with ruff and black
- `make format` — auto-format code
- `make clean-data` — remove generated datasets


# 1. Data generation (as before)
```sh
make docker-up
```
# or
```sh
docker compose up -d generator
```

# 2. Launch Jupyter
```sh
make jupyter-up
```

# 3. Let's look at the logs → there will be a link and a token
```sh
make jupyter-logs
```

# Example of output in the logs:

 http://127.0.0.1:8888/lab?token=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 4. Stop Jupyter

```sh
make jupyter-down
```

If you want to launch Jupyter without docker-compose (one-time)
Add another target to the Makefile (alternative):
makefilejupyter-standalone: ​​## Run Jupyter in a single container without compose
```sh
	docker run -d \
		--name temp-jupyter \
		-p 8888:8888 \
		-v $(PWD)/notebooks:/home/jovyan/work \
		-v $(PWD)/data:/home/jovyan/data:ro \
		-e JUPYTER_ENABLE_LAB=yes \
		-e JUPYTER_TOKEN=secret123 \
		quay.io/jupyter/scipy-notebook:latest
```

jupyter-standalone-stop: ## Зупинити та видалити standalone Jupyter

```sh
	docker stop temp-jupyter && docker rm temp-jupyter 
```    
