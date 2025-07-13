# Makefile for managing the Airflow data pipeline project

# Define the Docker Compose command (you can change this if using 'docker compose' instead of 'docker-compose')
COMPOSE=docker-compose

# --------- Commands ---------

# Up: Starts the Airflow containers in detached mode
# The @ keeps the logs clean
up:
	@echo "Getting docker-compose.yml"
	@curl -LfO 'https://airflow.apache.org/docs/apache-airflow/3.0.2/docker-compose.yaml'
	
	@echo "Appending the data persisting folder to docker-compose.yaml"
	@sed -i '\/plugins:\/opt\/airflow\/plugins/a \    - $${AIRFLOW_PROJ_DIR:-.}/data:/opt/airflow/data' docker-compose.yaml

	@echo "📁 Creating Airflow folders"
	@mkdir -p ./dags ./logs ./plugins ./config
	@echo "AIRFLOW_UID=$$(id -u)" > .env

	@echo "Initializing Airflow"
	@docker compose up airflow-init

	@echo "🚀 Starting Airflow container..."
	@docker compose up

# Down: Stops and removes containers and orphaned services.
down:
	@echo "🛑 Stopping Airflow containers..."
	@docker compose down --volumes --remove-orphans

#Give permissions to folders and create them if they do not exist
permissions:
	@echo "Creating initial folders"
	@mkdir -p dags/src dags/utils logs plugins config data
	@echo "Setting permissions to folders"
	@sudo chown -R $$(id -u):$$(id -g) dags logs plugins config #It gives permissions to the folders

# Creates virtual env
virtual_env:
	@echo "🐍 Creating virtual environment..."
	@python3 -m venv .venv
	@echo "✅ Virtual environment created in .venv"

	@echo ""
	@echo "💡 To activate the virtual environment, run:"
	@echo "   source .venv/bin/activate"

requirements:
	@echo "📦 Installing dependencies from requirements.txt..."
	@.venv/bin/pip install --upgrade pip -q
	@.venv/bin/pip install -r requirements.txt -q
	@echo "✅ Dependencies installed"
	
# unit test (Make sure virtual env is active)
unit_tests:
	@echo "🧪 Running unit tests..."
	@PYTHONPATH=./dags coverage run -m unittest discover -s tests/
	
format:
	@echo "[INFO] Formatting all python files..."
	@echo "[INFO] Running black..."
	@black ./dags/src
	@echo "[INFO] Running isort..."
	@isort ./dags/src

check:
	@echo "[INFO] Checking all python files..."
	@echo "[INFO] Running black..."
	@black -q --check ./dags/src 
	@echo "[INFO] Running isort..."
	@isort -q --check ./dags/src

