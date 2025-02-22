import sys
import shutil
import os

from src.entity.artifact_entity import ModelPusherArtifact, ModelTrainerArtifact
from src.entity.config_entity import ModelPusherConfig
from src.exception import CustomerException
from src.logger import logging
from src.ml.model.s3_estimator import CustomerClusterEstimator  # Updated to local storage
from dataclasses import dataclass
from src.constant import prediction_pipeline

from src.constant.training_pipeline import *

class ModelPusher:
    def __init__(
        self,
        model_trainer_artifact: ModelTrainerArtifact,
        model_pusher_config: ModelPusherConfig,
    ):
        self.model_trainer_artifact = model_trainer_artifact
        self.model_pusher_config = model_pusher_config
        self.local_estimator = CustomerClusterEstimator(model_path=model_pusher_config.local_model_path)

    def initiate_model_pusher(self) -> ModelPusherArtifact:
        logging.info("Entered initiate_model_pusher method of ModelPusher class")

        try:
            logging.info("Saving model locally instead of uploading to S3")
            self.local_estimator.save_model(
                from_file="model.pkl"
            )

            model_pusher_artifact = ModelPusherArtifact(
                local_model_path=self.model_pusher_config.local_model_path,
            )
            logging.info("Model successfully saved locally")
            logging.info(f"Model pusher artifact: [{model_pusher_artifact}]")
            logging.info("Exited initiate_model_pusher method of ModelPusher class")

            return model_pusher_artifact

        except Exception as e:
            raise CustomerException(e, sys) from e
