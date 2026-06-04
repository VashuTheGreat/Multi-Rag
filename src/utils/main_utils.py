import yaml
import os

def load_yaml(file_path: str):
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r") as f:
        return yaml.safe_load(f) or {}

def write_yaml(file_path: str, data: dict, mode: str = "w"):
    if mode == "a":
        existing_data = load_yaml(file_path)
        if isinstance(existing_data, dict) and isinstance(data, dict):
            # If we are appending to a specific list within the dict
            for key, value in data.items():
                if key in existing_data and isinstance(existing_data[key], list) and isinstance(value, list):
                    existing_data[key].extend(value)
                else:
                    existing_data[key] = value
            data = existing_data
        elif isinstance(existing_data, list) and isinstance(data, list):
            existing_data.extend(data)
            data = existing_data
            
    with open(file_path, "w") as f:
        yaml.dump(data, f)

