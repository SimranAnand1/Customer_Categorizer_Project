import os
import sys
import pickle
from io import StringIO
from typing import Union, List
from src.logger import logging
from pandas import DataFrame, read_csv
from src.exception import CustomerException


class SimpleStorageService:
    def __init__(self):
        logging.info("S3 is disabled. Using local storage instead.")

    def s3_key_path_available(self, bucket_name, s3_key) -> bool:
        local_path = os.path.join("local_storage", bucket_name, s3_key)
        return os.path.exists(local_path)

    @staticmethod
    def read_object(object_name: str, decode: bool = True, make_readable: bool = False) -> Union[StringIO, str]:
        logging.info("Reading object from local storage")
        try:
            with open(object_name, "rb") as f:
                content = f.read()
                if decode:
                    content = content.decode()
            return StringIO(content) if make_readable else content
        except Exception as e:
            raise CustomerException(e, sys)

    def get_file_object(self, filename: str, bucket_name: str) -> Union[List[object], object]:
        local_path = os.path.join("local_storage", bucket_name, filename)
        if os.path.exists(local_path):
            return local_path
        else:
            raise CustomerException(f"File {filename} not found in local storage", sys)

    def load_model(self, model_name: str, bucket_name: str, model_dir: str = None) -> object:
        logging.info("Loading model from local storage")
        try:
            local_path = os.path.join("local_storage", bucket_name, model_name)
            with open(local_path, "rb") as f:
                model = pickle.load(f)
            return model
        except Exception as e:
            raise CustomerException(str(e), sys)

    def create_folder(self, folder_name: str, bucket_name: str) -> None:
        local_path = os.path.join("local_storage", bucket_name, folder_name)
        os.makedirs(local_path, exist_ok=True)

    def upload_file(self, from_filename: str, to_filename: str, bucket_name: str, remove: bool = True):
        logging.info("Saving file to local storage")
        try:
            os.makedirs(os.path.join("local_storage", bucket_name), exist_ok=True)
            dest_path = os.path.join("local_storage", bucket_name, to_filename)
            os.rename(from_filename, dest_path)
            if remove:
                os.remove(from_filename)
        except Exception as e:
            raise CustomerException(e, sys)

    def upload_df_as_csv(self, data_frame: DataFrame, local_filename: str, bucket_filename: str, bucket_name: str) -> None:
        logging.info("Saving DataFrame as CSV to local storage")
        try:
            os.makedirs(os.path.join("local_storage", bucket_name), exist_ok=True)
            local_path = os.path.join("local_storage", bucket_name, bucket_filename)
            data_frame.to_csv(local_path, index=False, header=True)
        except Exception as e:
            raise CustomerException(e, sys)

    def get_df_from_object(self, object_: object) -> DataFrame:
        logging.info("Reading DataFrame from local file")
        try:
            return read_csv(object_, na_values="na")
        except Exception as e:
            raise CustomerException(e, sys)

    def read_csv(self, filename: str, bucket_name: str) -> DataFrame:
        logging.info("Reading CSV from local storage")
        try:
            local_path = os.path.join("local_storage", bucket_name, filename)
            return read_csv(local_path, na_values="na")
        except Exception as e:
            raise CustomerException(e, sys)
