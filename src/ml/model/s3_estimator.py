import sys
import os
import pickle
from pandas import DataFrame
from src.exception import CustomerException
from src.ml.model.estimator import CustomerSegmentationModel
from src.constant import prediction_pipeline

from src.constant.training_pipeline import *


class CustomerClusterEstimator:
    """
    This class is used to save and retrieve the model locally and perform predictions.
    """

    def __init__(self, model_path=MODEL_FILE_NAME):
        """
        :param model_path: Local file path for storing the model.
        """
        self.model_path = model_path
        print("Model path: {}".format(model_path))
        self.loaded_model: CustomerSegmentationModel = None

    def is_model_present(self) -> bool:
        """Check if the model file exists locally."""
        return os.path.exists(self.model_path)

    def load_model(self) -> CustomerSegmentationModel:
        """
        Load the model from local storage.
        :return: Loaded model object.
        """
        try:
            if not self.is_model_present():
                raise FileNotFoundError(f"Model file not found at {self.model_path}")

            with open(self.model_path, "rb") as model_file:
                self.loaded_model = pickle.load(model_file)

            return self.loaded_model

        except Exception as e:
            raise CustomerException(e, sys) from e

    def save_model(self, from_file: str, remove: bool = False) -> None:
        """
        Save the model locally.
        :param from_file: Local system model path.
        :param remove: If True, removes the source model after saving.
        """
        try:
            print("Model path: {}".format(self.model_path))
            print("File path: {}".format(from_file))
            print("----------------------------------------------------------------")
            os.makedirs(os.path.dirname("model.pkl"), exist_ok=True)
            shutil.copy(from_file, "model.pkl")

            if remove:
                os.remove(from_file)

        except Exception as e:
            raise CustomerException(e, sys) from e

    def predict(self, dataframe: DataFrame):
        """
        Perform predictions using the locally loaded model.
        :param dataframe: Input data as a pandas DataFrame.
        :return: Predictions.
        """
        try:
            if self.loaded_model is None:
                self.loaded_model = self.load_model()
            return self.loaded_model.predict(dataframe)
        except Exception as e:
            raise CustomerException(e, sys) from e
