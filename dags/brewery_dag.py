from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "start_date": datetime.today(),
    "retries": 2,
    "retry_delay": timedelta(minutes=5),  # Wait 5 minutes between retries
    "email_on_failure": True,
    "email": ["rodrigo_amandio2008@hotmail.com"],
}

with DAG(
    "brewery_etl_with_params",
    default_args=default_args,
    schedule="0 23 * * *",  # Runs everyday at 08p.m Brazil time
    catchup=False,
    tags=["brewery", "daily"],
    params={
        "url_api": "https://api.openbrewerydb.org/v1/breweries",
        "raw_final_path": "/opt/airflow/data/teste_bees/raw_data/",
        "raw_file_name": "teste_bees_rodrigo_amandio",
        "silver_path": "/opt/airflow/data/teste_bees/silver_data/",
        "gold_path": "/opt/airflow/data/teste_bees/gold_data/",
    },
) as dag:

    # Pass params to the script via CLI args using Jinja templating
    extract = BashOperator(
        task_id="extract_data",
        bash_command=(
            "PYTHONPATH=/opt/airflow/dags "  # It makes sure that dags folder is the root for Python
            "python3 /opt/airflow/dags/src/extract_data.py "
            "--url_api {{ params.url_api }} "
            "--raw_final_path {{ params.raw_final_path }} "  # Leave empty spaces at the end
            "--raw_file_name {{ params.raw_file_name }}"
        ),
    )

    transform = BashOperator(
        task_id="data_transformation",
        bash_command=(
            "PYTHONPATH=/opt/airflow/dags "
            "python3 /opt/airflow/dags/src/transformation.py "
            "--raw_final_path {{ params.raw_final_path }} "
            "--raw_file_name {{ params.raw_file_name }} "
            "--silver_path {{ params.silver_path }}"
        ),
    )

    aggregate = BashOperator(
        task_id="data_aggregation",
        bash_command=(
            "PYTHONPATH=/opt/airflow/dags "
            "python3 /opt/airflow/dags/src/aggregation.py "
            "--silver_path {{ params.silver_path }} "
            "--gold_path {{ params.gold_path }}"
        ),
    )

    extract >> transform >> aggregate
