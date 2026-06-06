from dataclasses import dataclass


@dataclass
class RetrievalArtifact:
    retreivar: object

@dataclass
class DataIngestionArtifact:
    ingested_file_path:str

@dataclass
class DataTransformationArtifact:
    vector_store_path: str

@dataclass
class ContentEmbedderArtifact:
    data_ingestion_artifacts: list[DataIngestionArtifact]

@dataclass
class ContentTransformedArtifact:
    data_transformation_artifacts: list[DataTransformationArtifact]
    