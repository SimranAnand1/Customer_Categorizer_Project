import json
import sys
from typing import Tuple, Union
import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

from pandas import DataFrame
from src.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from src.entity.config_entity import DataValidationConfig
from src.exception import CustomerException
from src.logger import logging
from src.utils.main_utils import MainUtils, write_yaml_file


class DataValidation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact, 
                 data_validation_config: DataValidationConfig):
        
        self.data_ingestion_artifact = data_ingestion_artifact
        self.data_validation_config = data_validation_config
        self.utils = MainUtils()
        self._schema_config = self.utils.read_schema_config_file()

    def validate_schema_columns(self, dataframe: DataFrame) -> bool:
        """
        Validate if the dataframe has the correct number of columns based on schema.
        """
        try:
            expected_columns = self._schema_config["columns"]
            status = len(dataframe.columns) == len(expected_columns)
            logging.info(f"Schema validation status: {status}")
            return status

        except Exception as e:
            raise CustomerException(e, sys) from e

    def validate_dataset_schema_columns(self, train_set: DataFrame, test_set: DataFrame) -> Tuple[bool, bool]:
        """
        Validate schema for both train and test datasets.
        """
        try:
            logging.info("Validating schema columns for train and test sets.")
            train_schema_status = self.validate_schema_columns(train_set)
            test_schema_status = self.validate_schema_columns(test_set)
            return train_schema_status, test_schema_status

        except Exception as e:
            raise CustomerException(e, sys) from e

    def detect_dataset_drift(self, reference_df: DataFrame, current_df: DataFrame) -> bool:
        """
        Detect dataset drift between reference and current dataset.
        """
        try:
            logging.info("Running dataset drift detection using Evidently.")

            # Generate drift report
            data_drift_profile = Report(metrics=[DataDriftPreset()])
            data_drift_profile.run(reference_data=reference_df, current_data=current_df)
            report_json = data_drift_profile.json()

            # Convert JSON string to dictionary
            json_report = json.loads(report_json)
            write_yaml_file(file_path=self.data_validation_config.drift_report_file_path, content=json_report)

            # Debugging: Print structure of the JSON report
            logging.info(f"Top-level keys: {list(json_report.keys())}")

            # Print first few entries of 'metrics' for debugging
            if "metrics" in json_report and isinstance(json_report["metrics"], list):
                logging.info(f"First few metric entries: {json_report['metrics'][:2]}")

            # Locate dataset drift info
            drift_status = False
            for metric in json_report.get("metrics", []):
                if metric.get("metric") == "DatasetDriftMetric":
                    drift_status = metric["result"].get("dataset_drift", False)
                    break  # Stop searching once found

            if drift_status is None:
                raise KeyError("Key 'dataset_drift' not found in JSON report.")

            logging.info(f"Dataset drift detected: {drift_status}")
            return drift_status

        except KeyError as e:
            logging.error(f"Missing key in JSON report: {e}")
            raise CustomerException(f"Missing key in JSON report: {e}", sys) from e
        except Exception as e:
            raise CustomerException(e, sys) from e

    @staticmethod
    def read_data(file_path: str) -> DataFrame:
        """
        Read CSV data from file.
        """
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise CustomerException(e, sys)

    def initiate_data_validation(self) -> DataValidationArtifact:
        """
        Initiate data validation process.
        """
        try:
            logging.info("Starting data validation process.")

            # Load train and test datasets
            train_df = self.read_data(self.data_ingestion_artifact.trained_file_path)
            test_df = self.read_data(self.data_ingestion_artifact.test_file_path)

            # Validate schema columns
            schema_train_col_status, schema_test_col_status = self.validate_dataset_schema_columns(train_df, test_df)

            # Detect dataset drift
            drift_status = self.detect_dataset_drift(train_df, test_df)

            # Validation status check
            validation_status = schema_train_col_status and schema_test_col_status and not drift_status

            logging.info(f"Validation status: {validation_status}")

            # Create and return artifact
            return DataValidationArtifact(
                validation_status=validation_status,
                valid_train_file_path=self.data_ingestion_artifact.trained_file_path,
                valid_test_file_path=self.data_ingestion_artifact.test_file_path,
                invalid_train_file_path=self.data_validation_config.invalid_train_file_path,
                invalid_test_file_path=self.data_validation_config.invalid_test_file_path,
                drift_report_file_path=self.data_validation_config.drift_report_file_path
            )

        except Exception as e:
            raise CustomerException(e, sys)
