import sys
import types

# --- PATCH START: Fix ragas missing langchain_community.chat_models.vertexai import error ---
try:
    import langchain_community.chat_models.vertexai
except ImportError:
    vertexai_mock = types.ModuleType("langchain_community.chat_models.vertexai")
    vertexai_mock.ChatVertexAI = type("ChatVertexAI", (object,), {})
    sys.modules["langchain_community.chat_models.vertexai"] = vertexai_mock
# --- PATCH END ---

from dotenv import load_dotenv
load_dotenv()
import os
import asyncio
import time
import pandas as pd
from openai import AsyncOpenAI
from src.core.logger import logger

from ragas.llms import llm_factory
from ragas.embeddings import HuggingFaceEmbeddings
from ragas.metrics.collections import (
    Faithfulness,
    AnswerRelevancy,
    ContextPrecision,
    ContextRecall,
    AnswerCorrectness,
)

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
JUDGE_MODEL = "qwen/qwen3.8-27b"
COOLDOWN = 5  # Simple rate-limit pause


# def _build_judge():
#     logger.info(
#         "Configuring evaluation judge",
#         provider="nvidia",
#         model="minimaxai/minimax-m3.1-flash",
#         api_key_configured=bool(os.getenv("NVIDIA_API_KEY")),
#     )
#     async_client = AsyncOpenAI(
#         api_key=os.getenv("NVIDIA_API_KEY"),
#         base_url="https://integrate.api.nvidia.com/v1"
#     )
#     # Added max_tokens to prevent IncompleteOutputException length limits
#     judge_llm = llm_factory(
#         "minimaxai/minimax-m3.1-flash", 
#         provider="openai", 
#         client=async_client,
#         max_tokens=8192
#     )
    
#     embeddings = HuggingFaceEmbeddings(model="sentence-transformers/all-MiniLM-L6-v2", use_api=False)
#     return judge_llm, embeddings


def _build_judge():
    logger.info(
        "Configuring evaluation judge",
        provider="ollama",
        model="llama3",  # Ya jo model aapne pull kiya ho (e.g., "qwen2.5", "mistral")
    )
    
    # Ollama ka local OpenAI-compatible endpoint
    async_client = AsyncOpenAI(
        api_key="ba3d454424674024ac30f25fe7b548a9.6rEuskvmK7hK8n6-AVZBXIQh",  # Ollama ko real API key ki zaroorat nahi hoti
        base_url="http://localhost:11434/v1"
    )
    
    # Ollama par pull kiya hua model name yahan pass karein
    judge_llm = llm_factory(
        "gemma4:31b-cloud",  # Yahan apna local Ollama model name dein (jaise "llama3" ya "qwen2.5")
        provider="openai", 
        client=async_client,
        max_tokens=8192
    )

    embeddings = HuggingFaceEmbeddings(model="sentence-transformers/all-MiniLM-L6-v2", use_api=False)
    return judge_llm, embeddings

def _score_df(metric_key: str, samples: list, scores) -> pd.DataFrame:
    rows = []
    for s, r in zip(samples, scores):
        # Handle cases where score might be None or failed
        val = 0.0
        if r is not None:
            try:
                val = round(float(getattr(r, "value", r)), 3)
            except Exception:
                val = 0.0
        rows.append({"question": s["question"], metric_key: val})
    return pd.DataFrame(rows)


async def run_all_metrics(golden_dataset: dict, status_cb=None) -> dict:
    judge_llm, embeddings = _build_judge()
    samples = golden_dataset.get("rag_samples", [])

    if not samples:
        logger.error("Evaluation dataset is empty or missing rag_samples")
        raise ValueError("Dataset is empty or missing 'rag_samples'.")

    logger.info("Starting Ragas evaluation", sample_count=len(samples))
    results = {}

    async def run_metric(name, metric_instance, inputs_builder):
        started_at = time.perf_counter()
        logger.info("Starting evaluation metric", metric=name, sample_count=len(samples))
        if status_cb:
            status_cb(f"Running {name}...")
        
        scores = []
        # Process sample by sample so an error in one doesn't crash the whole run
        for idx, s in enumerate(samples):
            single_input = [inputs_builder(s)]
            try:
                # abatch_score for a single item list
                res = await metric_instance.abatch_score(single_input)
                if res and len(res) > 0:
                    scores.append(res[0])
                else:
                    scores.append(0.0)
            except Exception as exc:
                logger.error(
                    "Sample evaluation failed, skipping sample",
                    metric=name,
                    sample_index=idx,
                    error=str(exc),
                )
                # Append a fallback/default score object or value so length matches
                class FallbackScore:
                    value = 0.0
                scores.append(FallbackScore())

        key = name.lower().replace(" ", "_")
        results[key] = _score_df(key, samples, scores)
        logger.info(
            "Evaluation metric completed",
            metric=name,
            sample_count=len(samples),
            elapsed_seconds=round(time.perf_counter() - started_at, 2),
        )
        await asyncio.sleep(COOLDOWN)

    logger.info("Evaluation Faithfulness")
    # 1. Faithfulness
    await run_metric(
        "Faithfulness",
        Faithfulness(llm=judge_llm),
        lambda s: {"user_input": s["question"], "response": s["actual_response"], "retrieved_contexts": s["actual_contexts"]}
    )

    logger.info("Evaluation Answer Relevancy")
    # 2. Answer Relevancy
    await run_metric(
        "Answer Relevancy",
        AnswerRelevancy(llm=judge_llm, embeddings=embeddings),
        lambda s: {"user_input": s["question"], "response": s["actual_response"]}
    )

    logger.info("Evaluation Context Precision")
    # 3. Context Precision
    await run_metric(
        "Context Precision",
        ContextPrecision(llm=judge_llm),
        lambda s: {"user_input": s["question"], "reference": s["reference"], "retrieved_contexts": s["actual_contexts"]}
    )

    logger.info("Evaluation Context Recall")
    # 4. Context Recall
    await run_metric(
        "Context Recall",
        ContextRecall(llm=judge_llm),
        lambda s: {"user_input": s["question"], "reference": s["reference"], "retrieved_contexts": s["actual_contexts"]}
    )

    logger.info("Evaluation Answer Correctness")
    # 5. Answer Correctness
    await run_metric(
        "Answer Correctness",
        AnswerCorrectness(llm=judge_llm, embeddings=embeddings),
        lambda s: {"user_input": s["question"], "response": s["actual_response"], "reference": s["reference"]}
    )

    if status_cb:
        status_cb("Evaluation complete!")

    logger.info("Ragas evaluation completed", metric_count=len(results))
    return results


if __name__ == "__main__":
    import json
    import sys
    from evals.harness import run_pipeline, save_dict, load_dataset

    if len(sys.argv) != 2:
        print("Usage: python metrics.py <path_to_golden_dataset.json>")
        sys.exit(1)

    dataset_path = sys.argv[1]
    logger.info("Loading evaluation dataset", path=dataset_path)
    if not os.path.exists(dataset_path):
        logger.info("Evaluation dataset not found; collecting it from the chat API", path=dataset_path)
        print(f"File not found: {dataset_path}")
        print("Creating dataset file...")
        dataset = run_pipeline(load_dataset("evals/goldens/golden_dataset.json"))
        save_dict(dataset, dataset_path)

    with open(dataset_path, "r") as f:
        golden_dataset = json.load(f)
    logger.info(
        "Evaluation dataset loaded",
        path=dataset_path,
        sample_count=len(golden_dataset.get("rag_samples", [])),
    )

    # Run evaluations safely
    try:
        results = asyncio.run(run_all_metrics(golden_dataset))
    except Exception as e:
        logger.error("Critical error during evaluation run", error=str(e))
        results = {}

    os.makedirs("evals/results", exist_ok=True)
    i = 0
    while os.path.exists(f"evals/results/metrics_results_{i}.json"):
        i += 1
    output_path = f"evals/results/metrics_results_{i}.json"
    
    # Save whatever results were collected even if some samples failed
    if results:
        with open(output_path, "w") as f:
            json.dump({k: v.to_dict(orient="records") for k, v in results.items()}, f, indent=4)
        logger.info("Evaluation results saved", path=output_path, metric_count=len(results))
        print(f"Evaluation results saved to {output_path}")
    else:
        print("No evaluation results were generated to save.")