import json
import os

import numpy as np
import pandas as pd
from utils.utils import get_arguments, logger, save_as_parquet

logging = logger()


def json_to_dataframe(path, file_name, logging):
    """
    Reads a JSON file and converts its content into a pandas DataFrame.

    Args:
        path (str): The path to the raw JSON file.
        file_name (str): The name of the raw JSON file.
        logging: Logging tool for observability (Monitoring)

    Returns:
        pandas.DataFrame or None: A DataFrame if successful, None otherwise.
    """

    os.makedirs(path, exist_ok=True)
    file_path = os.path.join(path, f"{file_name}.json")

    try:
        # Read the JSON file
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Convert the JSON data to a pandas DataFrame
        df = pd.json_normalize(data)

        logging.info(
            json.dumps(
                {
                    "Observability": f"Successfully loaded '{file_path}' into a DataFrame."
                }
            )
        )

        return df

    except FileNotFoundError:
        logging.error(
            json.dumps(
                {
                    "Observability": f"Error - The file '{file_path}' was not found.",
                    "Path": file_path,
                }
            )
        )

        return None

    except json.JSONDecodeError:
        logging.error(
            json.dumps(
                {
                    "Observability": f"Error - Could not decode JSON from '{file_path}'. Check if it's a valid JSON file."
                }
            )
        )

        return None

    except Exception as e:
        logging.error(
            json.dumps(
                {"Observability": "An unexpected error occurred", "Error": str(e)}
            )
        )

        return None


def data_transformation(df, logging):
    """
    Apply transformations in raw data for silver layer

    df: Dataframe with raw data

    logging: Logging tool for observability (Monitoring)
    """
    try:
        # Treating address in just one column
        conditions = [
            (df["address_1"].isna()) & (df["street"].isna()),  # Condition 1
            (df["address_1"] == df["street"])
            & (~df["address_1"].isna())
            & (~df["street"].isna()),  # Condition 2
            (df["address_1"] != df["street"])
            & (df["address_1"].isna())
            & (~df["street"].isna()),  # Condition 3
            (df["address_1"] != df["street"])
            & (~df["address_1"].isna())
            & (df["street"].isna()),  # Condition 4
        ]

        choices = [
            "address not informed",  # Response for condition 1
            df["address_1"],  # Response for condition 2
            df["street"],  # Response for condition 3
            df["address_1"],  # Response for condition 4
        ]

        df["address"] = np.select(conditions, choices)

        # Deleting unused columns
        final_df = df.drop(
            columns=["address_1", "address_2", "address_3", "street"], inplace=False
        )

        # Treating NaN and None throughout columns
        for column in final_df.columns:
            final_df[[column]] = final_df[[column]].fillna(f"{column} not informed")

        # Casting everything to string
        for column in final_df.columns:
            final_df[[column]] = final_df[[column]].astype(str)

        logging.info(
            json.dumps(
                {
                    "Observability": f"Successfully transformed raw_data for silver layer."
                }
            )
        )

        return final_df

    except Exception as e:
        logging.error(
            json.dumps(
                {"Observability": "An unexpected error occurred", "Error": str(e)}
            )
        )

        return None


if __name__ == "__main__":

    execution_variables = get_arguments(logging)

    path = execution_variables.raw_final_path
    file_name = execution_variables.raw_file_name
    silver_path = execution_variables.silver_path

    brewery_df = json_to_dataframe(path, file_name, logging)

    final_brewery_df = data_transformation(brewery_df, logging)

    save_as_parquet(final_brewery_df, silver_path, logging)
