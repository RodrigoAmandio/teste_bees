"""
Obs: This file must start with test_*.py to be discovered by default.
"""

import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from dags.src.aggregation import get_aggregated_data, read_data
from dags.src.extract_data import get_api_data, save_raw_data
from dags.src.transformation import data_transformation, json_to_dataframe


class TestGetAPIData(unittest.TestCase):

    def setUp(self):
        # It serves as mock for some of the unit tests
        self.df = pd.DataFrame([{"id": 1, "name": "Test Brewery"}])
        self.test_path = "fake_path/file.parquet"
        self.logger = MagicMock()

    @patch("dags.src.extract_data.requests.get")
    def test_get_api_data_success(self, mock_get):
        # Setup
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": 1, "name": "Brewery A"}]
        mock_get.return_value = mock_response

        mock_logger = MagicMock()

        # Execute
        result = get_api_data("http://fakeapi.com", mock_logger)

        # Assert
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]["name"], "Brewery A")
        mock_logger.info.assert_called_once()

    @patch("dags.src.extract_data.requests.get")
    def test_get_api_data_failure(self, mock_get):
        # Setup
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        mock_logger = MagicMock()

        # Execute
        result = get_api_data("http://fakeapi.com", mock_logger)

        # Assert
        self.assertEqual(result, 404)
        mock_logger.error.assert_called_once()

    def test_save_raw_data_success(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_name = "test_file"

            # Call the function
            save_raw_data(self.df, tmp_dir, file_name, self.logger)

            # Construct expected file path
            expected_file_path = os.path.join(tmp_dir, f"{file_name}.json")

            # Assertions
            self.assertTrue(os.path.exists(expected_file_path))

            with open(expected_file_path, "r") as f:
                content = json.load(f)
                self.assertEqual(content[0]["name"], "Test Brewery")

            self.logger.info.assert_called_once()
            self.logger.error.assert_not_called()

    def test_json_to_dataframe_success(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_name = "success"
            file_path = os.path.join(tmp_dir, f"{file_name}.json")
            sample_data = [{"id": 1}, {"id": 2}]

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(sample_data, f)

            df = json_to_dataframe(tmp_dir, file_name, self.logger)

            self.assertIsInstance(df, pd.DataFrame)
            self.assertEqual(len(df), 2)
            self.logger.info.assert_called_once()
            self.logger.error.assert_not_called()

    def test_json_decode_error(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_name = "invalid_json"
            file_path = os.path.join(tmp_dir, f"{file_name}.json")

            with open(file_path, "w", encoding="utf-8") as f:
                f.write("{ invalid json }")

            df = json_to_dataframe(tmp_dir, file_name, self.logger)

            self.assertIsNone(df)
            self.logger.error.assert_called_once()
            self.logger.info.assert_not_called()

    def test_unexpected_exception(self):
        # Patch json.load to raise a ValueError
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_name = "raises_error"
            file_path = os.path.join(tmp_dir, f"{file_name}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump({"id": 1}, f)

            with patch("dags.src.transformation.open", side_effect=ValueError("Boom")):
                df = json_to_dataframe(tmp_dir, file_name, self.logger)

                self.assertIsNone(df)
                self.logger.error.assert_called_once()
                self.logger.info.assert_not_called()

    def test_valid_transformation(self):
        # Sample raw input
        raw_data = {
            "address_1": ["123 Main St", None, None, "456 Oak Ave"],
            "street": ["123 Main St", "789 Pine St", None, None],
            "address_2": [None] * 4,
            "address_3": [None] * 4,
            "city": ["New York", None, "Chicago", None],
        }

        df = pd.DataFrame(raw_data)

        transformed_df = data_transformation(df, self.logger)

        # Assertions
        self.assertIsNotNone(transformed_df)
        self.assertIn("address", transformed_df.columns)
        self.assertNotIn("address_1", transformed_df.columns)
        self.assertTrue(all(transformed_df["address"].notna()))
        self.logger.info.assert_called()  # Ensure logging happened

    def test_empty_dataframe(self):
        df = pd.DataFrame()
        transformed_df = data_transformation(df, self.logger)
        self.assertIsNone(transformed_df)
        self.logger.error.assert_called()

    @patch("dags.src.aggregation.pd.read_parquet")
    def test_read_parquet_success(self, mock_read_parquet):
        mock_df = pd.DataFrame({"col": [1, 2, 3]})
        mock_read_parquet.return_value = mock_df

        result = read_data(self.test_path, self.logger)

        self.assertIsNotNone(result)
        pd.testing.assert_frame_equal(result, mock_df)
        self.logger.info.assert_called()
        self.logger.error.assert_not_called()

    @patch(
        "dags.src.aggregation.pd.read_parquet",
        side_effect=FileNotFoundError("file not found"),
    )
    def test_file_not_found(self, mock_read_parquet):
        result = read_data(self.test_path, self.logger)

        self.assertIsNone(result)
        self.logger.error.assert_called()
        error_msg = self.logger.error.call_args[0][0]
        self.assertIn("file not found", error_msg)

    def test_successful_aggregation(self):
        # Sample input DataFrame
        data = {
            "country": ["US", "US", "US", "US"],
            "state": ["CA", "CA", "NY", "NY"],
            "city": ["LA", "LA", "NYC", "NYC"],
            "brewery_type": ["micro", "micro", "nano", "micro"],
        }
        df = pd.DataFrame(data)

        # Run aggregation
        result = get_aggregated_data(df, self.logger)

        # Expected output: counts of breweries grouped by location and type
        expected_data = {
            "country": ["US", "US", "US"],
            "state": ["CA", "NY", "NY"],
            "city": ["LA", "NYC", "NYC"],
            "brewery_type": ["micro", "nano", "micro"],
            "total_breweries_in_location": [2, 1, 1],
        }
        expected_df = pd.DataFrame(expected_data)

        # Check if results are as expected (ignore order of rows)
        pd.testing.assert_frame_equal(
            result.sort_values(by=result.columns.tolist()).reset_index(drop=True),
            expected_df.sort_values(by=expected_df.columns.tolist()).reset_index(
                drop=True
            ),
        )

        self.logger.info.assert_called_once()
        self.logger.error.assert_not_called()


if __name__ == "__main__":
    unittest.main()
