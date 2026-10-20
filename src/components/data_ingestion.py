from src.utils.asyncHandler import asyncHandler
import logging
import os

from src.entity.config_entity import DataIngestionConfig, RetreiverConfig
from src.entity.artifact_entity import DataTransformationArtifact, DataIngestionArtifact
from src.retrievers.create_retreivers import Retreiver
from src.constants import INGESTION_STRATEGY_NAME
from src.retrievers.strategies.ingestion_strategy import get_ingestion_strategy

class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig, data_ingestion_artifact: DataIngestionArtifact):
        self.data_ingestion_artifact = data_ingestion_artifact
        self.data_ingestion_config = data_ingestion_config

        retreiver_config = RetreiverConfig(
            vector_store_path=self.data_transformation_config.vector_store_path
        )
        self.retreiver = Retreiver(retreiver_config=retreiver_config)

    @asyncHandler
    async def initiate_data_transformation(self) -> DataTransformationArtifact:
        logging.info("Initiating data transformation...")

        # Use Strategy Pattern for loosely coupled ingestion techniques
        strategy = get_ingestion_strategy(INGESTION_STRATEGY_NAME)

        # The strategy handles parsing AND saving to its respective native vector store
        # to avoid costly O(n) document conversions.
        vector_store_path = await strategy.execute(
            file_path=self.data_ingestion_artifact.ingested_file_path,
            retriever=self.retreiver
        )

        logging.info("Data transformation completed successfully.")
        return DataTransformationArtifact(vector_store_path=vector_store_path)
