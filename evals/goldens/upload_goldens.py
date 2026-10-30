from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
from langsmith import Client
from evals.harnes import load_data

# ============== Constants ===================
GOLDENS_DIR = Path(__file__).resolve().parent

client = Client()

for dataset_path in sorted(GOLDENS_DIR.glob("*.json")):
    dataset_name = dataset_path.stem
    if client.has_dataset(dataset_name=dataset_name):
        print(f"Dataset already exists, skipping: {dataset_name}")
        continue

    examples = load_data(file_path=str(dataset_path))
    dataset = client.create_dataset(
        dataset_name,
        description=f"Golden evaluation dataset from {dataset_path.name}",
    )
    client.create_examples(dataset_id=dataset.id, examples=examples)
    print(f"Uploaded {len(examples)} examples to {dataset_name}")

