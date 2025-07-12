import argparse
import json
import logging
import os
import shutil
import subprocess
import sys


def logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    if not logger.handlers:
        logger.addHandler(console_handler)

    return logger


def save_as_parquet(df, path, logger):

    shutil.rmtree(path)

    os.makedirs(path, exist_ok=True)

    # Install pyarrow to save data as parquet
    package_name = "pyarrow"

    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

        logger.info(
            json.dumps({"Observability": f"Successfully installed {package_name}."})
        )

        df.to_parquet(
            path=path,
            engine="pyarrow",
            partition_cols=["country", "state", "city"],
            index=False,
        )

        logger.info(
            json.dumps(
                {"Observability": "Successfully saved data as parquet", "Path": path}
            )
        )

    except Exception as e:
        logger.error(
            json.dumps({"Observability": "An unexpected error occurred", "Error": e})
        )

        sys.exit(1)


def get_arguments(logger):
    parser = argparse.ArgumentParser()
    parser.add_argument("--url_api", required=False, help="API Endpoint")
    parser.add_argument(
        "--raw_final_path", required=False, help="Final path for raw layer"
    )
    parser.add_argument("--raw_file_name", required=False, help="Raw data file name")
    parser.add_argument(
        "--silver_path", required=False, help="Final path for silver layer"
    )
    parser.add_argument("--gold_path", required=False, help="Final path for gold layer")
    args = parser.parse_args()

    logger.info(
        json.dumps(
            {
                "Observability": "Execution variables succesfully created",
                "Args": vars(args),
            }
        )
    )

    return args
