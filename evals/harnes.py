import json
from typing import Any
from src.core.exception import MyException
import sys
# json loader
def load_data(file_path: str) -> list[dict[str, Any]]:
    """Loads the goldens and converts them to python dict"""
    try:

        with open(file=file_path,encoding="utf-8") as f:
            data = json.load(f)

        return data

    except Exception as e:
        raise MyException(e,sys)

