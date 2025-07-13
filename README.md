# 🧪 Brewery ETL Pipeline with Airflow

This repository contains a complete ELT pipeline for processing data from the Open Brewery DB API using Apache Airflow. It follows the **Medallion architecture** (Raw → Silver → Gold) and is orchestrated through Airflow running in Docker.

---

## 🚀 Project Overview

This ETL process performs:

1. **Extraction** of brewery data from a public API
2. **Transformation** into a clean silver dataset
3. **Aggregation** of metrics by location for gold-level analysis
4. **Persistence** of all data in JSON and Parquet formats under a local `/data` folder, mounted to the Airflow container

The pipeline is containerized using Docker and all common operations are automated via a `Makefile`.

---

## ⚙️ Environment Setup

> Ensure [Docker Desktop](https://www.docker.com/products/docker-desktop/) is installed and running before continuing.

### 🧰 Main Setup Commands

All setup commands are available in the `Makefile`. Run them from your terminal in the project root:

```bash
make permissions
```

- Creates the necessary folders: dags/, logs/, plugins/, config/, and data/

- Sets permissions if needed


```bash
make up
```

- Downloads and runs the official Apache Airflow docker-compose.yaml

- Ensures the data/ volume is mounted via sed

- Starts all required services (scheduler, webserver, etc.)


## Airflow Access
**URL**: http://localhost:8080

**Username**: airflow

**Password**: airflow

## Volumes & Persistence
These folders on your host are mapped to the Airflow container:

```yaml
volumes:
  - ${AIRFLOW_PROJ_DIR:-.}/dags:/opt/airflow/dags
  - ${AIRFLOW_PROJ_DIR:-.}/logs:/opt/airflow/logs
  - ${AIRFLOW_PROJ_DIR:-.}/config:/opt/airflow/config
  - ${AIRFLOW_PROJ_DIR:-.}/plugins:/opt/airflow/plugins
  - ${AIRFLOW_PROJ_DIR:-.}/data:/opt/airflow/data
```

- Changes to these directories in the container will reflect on your local machine and vice versa.

## Virtual Environment (for development)
Used to run unit tests and format Python files locally.

```bash
make virtual_env
source .venv/bin/activate
make requirements
```

- **make virtual_env**: Creates a virtual environment in .venv/

- **source .venv/bin/activate**: Activates the environment

- **make requirements**: Installs project dependencies from requirements.txt


## Code Quality & Formatting
Before pushing code, ensure it follows consistent formatting:

```bash
make format
```
Runs:

- **black**: Auto-formatter

- **isort**: Organizes import statements

```bash
make unit_tests
```

Runs unit tests in tests/test_functions.py

```bash
make check
```

Used in CI to validate formatting and test execution.


## Unit Testing & Coverage
To check your tests with coverage:

```bash
coverage run -m unittest discover tests/
coverage report -m
```

## Shutting Down
To stop the Airflow containers when you're done:

```bash
make down
```

## Project Structure

```graphql

├── .github/
    ├── workflows
        └── unit-test.yml # CI workflow
├── config/               # Configs if needed
├── dags/                 # All DAG definitions and ETL scripts
│   ├── src/              # Python modules for extract, transform, load
│   └── brewery_dag.py    # Main Airflow DAG
├── data/                 # Data folder (mounted inside the container)
│   ├── raw_data/
│   ├── silver_data/
│   └── gold_data/
├── logs/                 # Airflow logs
├── plugins/              # Custom Airflow plugins (if any)
├── tests/                # Unit test folder
│   └── test_functions.py
├── .env                  # Airflow ENV
├── .gitignore            # Declare what folders/files will be ignored
├── docker-compose.yaml  # Airflow infrastructure
├── Makefile              # Automates all key commands
└── README.md             # This file
├── requirements.txt      # Python dependency file

```

## Additional Notes
- **Timezone**: DAG schedules use UTC. Daily runs are configured at 23:00 UTC (8:00 PM Brazil time).

- **Retries & Resilience**: Python scripts include try/except handling. Airflow DAGs can be configured with retries if needed (see retries, retry_delay).

- **Parametrized DAG**: DAG parameters are passed via params={} and injected into BashOperator scripts via Jinja ({{ params.xyz }}). The required parameters are:
    - **raw_final_path**  
    - **raw_file_name**
    - **url_api**
    - **silver_path**
    - **gold_path**

- **Monitoring / Logging**: All Python scripts include structured logging for observability in Airflow logs. Messages that start with "Observability" can be mapped and then integrated with a visualazation tool like Datadog or Grafana

- **Testing**: Modular design allows each Python function to be tested in isolation.

## Repository Patterns and Data Quality
To maintain consistency and ensure code quality, this repository uses a CI pipeline to enforce naming conventions for commits and branches. See the desired commit patters:

<type>: <description>

Where <type> is one of the following:

- feat – New feature
- fix – Bug fix
- docs – Documentation changes
- chore – Maintenance tasks
- refactor – Code refactoring that doesn't affect behavior
- test – Adding or updating tests
- build – Build system changes
- ci – Continuous Integration configuration
- perf – Performance improvements
- revert – Revert a previous commit

**Example**: feat: add retry logic to ETL pipeline

## Branch Naming Convention
All branches for new features or improvements must begin with **feature/**. Example: feature/add-transformation-logging.

These conventions are enforced in CI using GitHub Actions, ensuring code hygiene across contributors.

## Unit tests with CI

It also checks for code formatting and unit tests, the same used with make format and make unit_tests commands.