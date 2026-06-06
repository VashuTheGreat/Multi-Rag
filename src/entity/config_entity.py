from dataclasses import dataclass, field
import uuid

from src.constants import *
import os
from typing import List
import time

BASE_FOLDER_NAME=f"artifacts/{time.time()}"


@dataclass
class DataIngestionConfig:
    input_file_path: str
    save_file_path: str = field(default=None)

    def __post_init__(self):
        if self.save_file_path is None:
            # Generate a random UUID for the ingested file name
            random_name = f"{uuid.uuid4()}.pdf"
            self.save_file_path = os.path.join(BASE_FOLDER_NAME, INGESTION_FOLDER_NAME, random_name)

@dataclass
class ContentEmbedderConfig:
    data_ingestion_configs:List[DataIngestionConfig]

@dataclass
class DataTransformationConfig:
    vector_store_path: str = field(default=None)

    def __post_init__(self):
        if self.vector_store_path is None:
            self.vector_store_path = os.path.join(BASE_FOLDER_NAME, "transformation", "vector_store")

@dataclass
class ContentTransformationConfig:
    data_transformation_configs: List[DataTransformationConfig]


@dataclass
class RetreiverConfig:
    vector_store_path: str = field(default=None)
    k: int = 5
    ensemble_weights: List[float] = field(default_factory=lambda: [0.7, 0.3])
    partition_strategy: str = "hi_res"
    max_characters: int = 3000
    new_after_n_chars: int = 2400
    combine_text_under_n_chars: int = 50

    def __post_init__(self):
        if self.vector_store_path is None:
            self.vector_store_path = os.path.join(BASE_FOLDER_NAME, "transformation", "vector_store")