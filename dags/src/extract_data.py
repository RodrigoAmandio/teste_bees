import json
import os

import pandas as pd
import requests
from utils.utils import get_arguments, logger

logging = logger()


def get_api_data(url_api, logging):
    """
    This function is responsible for retrieving data from the brewery's API. It also has a logging tool to collect information
    about both successful and unsuccessful execution attempts.

    Args:
        url_api (str): The API endpoint.
        logging: Logging tool for observability (Monitoring).

    Returns:
        For succesful execution, returns a JSON file with required data.
        For unsuccessful execution, returns the status_code for an error
    """

    response = requests.get(url_api)

    if response.status_code == 200:
        breweries = response.json()
        logging.info(
            json.dumps(
                {
                    "Observability": "API data successfully retrieved",
                    "StatusCode": response.status_code,
                }
            )
        )

        return breweries

    else:
        logging.error(
            json.dumps(
                {
                    "Observability": "Unexpected error when retrieving API data",
                    "Error": response.text,
                    "StatusCode": response.status_code,
                }
            )
        )

        return response.status_code


def save_raw_data(df, path, file_name, logging):
    """
    This function is responsible saving raw data in a desired final path

    Args:
        df: Pandas dataframe
        path (str): The path where the file will be saved
        file_name (str): Name of the final file
        logging: Logging tool for observability (Monitoring)

    Returns:
        Returns a log message for both successful and unsuccessful execution attempts.
    """

    os.makedirs(path, exist_ok=True)
    file_path = os.path.join(path, f"{file_name}.json")

    try:
        df.to_json(
            file_path, orient="records", lines=False
        )  # Save as an array of objects

        logging.info(
            json.dumps(
                {"Observability": "Raw data succesfully saved", "Path": file_path}
            )
        )

    except Exception as e:
        logging.error(
            json.dumps(
                {
                    "Observability": "Unexpected error when saving raw data",
                    "Error": str(e),
                }
            )
        )


if __name__ == "__main__":

    execution_variables = get_arguments(logging)

    url_api = execution_variables.url_api
    folder_path = execution_variables.raw_final_path
    file_name = execution_variables.raw_file_name

    breweries = get_api_data(url_api, logging)

    if breweries != 404:

        df_breweries = pd.DataFrame(breweries)

        save_raw_data(df_breweries, folder_path, file_name, logging)
