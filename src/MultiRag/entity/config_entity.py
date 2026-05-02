from dataclasses import dataclass



@dataclass
class ContentEmbedderConfig:
    file_path: str
    vector_store_path: str
    file_types: str = "pdf"