import json

import pandas as pd
from utils.utils import get_arguments, logger, save_as_parquet

logging = logger()


def read_data(path, logging):

    try:
        df = pd.read_parquet(path)

        logging.info(
            json.dumps(
                {"Observability": f"Successfully loaded '{path}' into a DataFrame."}
            )
        )

        return df

    except Exception as e:
        logging.error(
            json.dumps(
                {"Observability": "An unexpected error occurred", "Error": str(e)}
            )
        )

        return None


def get_aggregated_data(df, logging):
    """
    This function aggregates data by location (country, state and city) by count the type of
    breweries for each one.
    """

    try:
        aggregated_total_breweries = (
            df.groupby(
                ["country", "state", "city", "brewery_type"]
            )  # Group by location
            .size()  # Count the number of rows in each group
            .reset_index(
                name="total_breweries_in_location"
            )  # Name the new count column
        )

        filtered_breweries_df = aggregated_total_breweries[
            aggregated_total_breweries["total_breweries_in_location"] > 0
        ]

        logging.info(
            json.dumps(
                {
                    "Observability": f"Successfully aggregated dataframe by location (country, state and city) by count the type of breweries for each one."
                }
            )
        )

        return filtered_breweries_df

    except Exception as e:
        logging.error(
            json.dumps(
                {"Observability": "An unexpected error occurred", "Error": str(e)}
            )
        )

        return None


if __name__ == "__main__":

    execution_variables = get_arguments(logging)

    silver_path = execution_variables.silver_path
    gold_path = execution_variables.gold_path

    brewery_silver_data = read_data(silver_path, logging)

    filtered_breweries_df = get_aggregated_data(brewery_silver_data, logging)

    save_as_parquet(filtered_breweries_df, gold_path, logging)
