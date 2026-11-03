import copy
import json
import os
import time
import uuid

import requests
from dotenv import load_dotenv

load_dotenv()

from src.core.logger import logger

URL = os.getenv("EVAL_CHAT_URL", "http://localhost:7860/api/v1/chat")
REQUEST_TIMEOUT = float(os.getenv("EVAL_REQUEST_TIMEOUT", "120"))
DELAY = float(os.getenv("EVAL_REQUEST_DELAY", "10"))

def _context_text(context) -> str:
    if isinstance(context, str):
        return context
    if isinstance(context, dict):
        return str(context.get("page_content") or context.get("content") or "")
    return str(getattr(context, "page_content", context))


def run_pipeline(golden_dataset: dict) -> dict:
    """Populate RAG samples by querying the local chat API."""
    golden_dataset = copy.deepcopy(golden_dataset)
    rag_samples = golden_dataset.get("rag_samples") or []
    logger.info("Starting evaluation data collection", sample_count=len(rag_samples), url=URL)

    for index, sample in enumerate(rag_samples, start=1):
        question = sample.get("question")
        if not isinstance(question, str) or not question.strip():
            raise ValueError(f"RAG sample {sample.get('id', index)} has no valid question.")

        thread_id = str(uuid.uuid4())
        payload = {
            "message": question,
            "thread_id": thread_id,
            "stream": False,
        }

        logger.info(
            "Collecting evaluation sample",
            sample_id=sample.get("id", index),
            progress=f"{index}/{len(rag_samples)}",
            thread_id=thread_id,
        )
        try:
            response = requests.post(URL, json=payload, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            result = response.json()
        except (requests.RequestException, ValueError) as exc:
            logger.error(
                "Evaluation sample request failed",
                sample_id=sample.get("id", index),
                error=str(exc),
            )
            raise RuntimeError(
                f"Could not collect evaluation sample {sample.get('id', index)}: {exc}"
            ) from exc

        if not result.get("success"):
            raise RuntimeError(f"Chat API did not complete sample {sample.get('id', index)} successfully.")

        data = result.get("data") or {}
        contexts = data.get("retreived_content") or data.get("retrieved_content") or []
        sample["actual_response"] = result.get("response") or ""
        sample["actual_contexts"] = [text for item in contexts if (text := _context_text(item))]
        logger.info(
            "Evaluation sample collected",
            sample_id=sample.get("id", index),
            context_count=len(sample["actual_contexts"]),
        )

        if index < len(rag_samples) and DELAY > 0:
            time.sleep(DELAY)

    logger.info("Evaluation data collection complete", sample_count=len(rag_samples))
    return golden_dataset


def save_dict(golden_dataset: dict, file_path: str):
    """Save the populated golden dataset as JSON."""
    os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(golden_dataset, f, indent=4)
    logger.info("Evaluation dataset saved", path=file_path)


def load_dataset(file_path: str) -> dict:
    """Load a golden dataset from JSON."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)