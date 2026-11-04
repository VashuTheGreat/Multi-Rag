"""
Guardrails binary evaluation.
Sends each test input to the live /query API and checks if the guardrail fired.
Classifies each result as TP / TN / FP / FN and computes precision + recall.
"""


import time
import copy
import json
import requests
import logfire

API_URL = "http://localhost:7860/api/v1/chat"


def _is_blocked(events) -> bool:
    for line in events:
        if isinstance(line, bytes):
            line = line.decode("utf-8")
        if not line.startswith("data:"):
            continue

        try:
            event = json.loads(line[5:].strip())
        except json.JSONDecodeError:
            continue

        if event.get("type") == "blocked":
            return True
        if (
            event.get("type") == "node_flow"
            and event.get("node") == "guardrail"
            and event.get("status") == "blocked"
        ):
            return True

    return False


def run_guardrails_eval(guardrails_samples: dict) -> list:
    """
    Runs each guardrails test case against the live API.
    Adds actual_blocked and result (TP/TN/FP/FN) to each sample in place.
    Returns the enriched list.
    """
    samples = copy.deepcopy(guardrails_samples)
    n = len(samples)

    with logfire.span("🛡️ Eval — Guardrails Tests", total=n):
        for i, sample in enumerate(samples):
            
            with logfire.span(
                f"🛡️ Test {sample['id']}",
                input_text=sample["input"][:80],
                expected_blocked=sample["expected_blocked"],
            ):
                try:
                    with requests.post(
                        API_URL,
                        json={
                            "message": sample["input"],
                            "thread_id": f"guardrail_eval_{i}",
                            "stream": True,
                        },
                        timeout=30,
                        stream=True,
                    ) as resp:
                        resp.raise_for_status()
                        blocked = _is_blocked(resp.iter_lines(decode_unicode=True))

                except requests.exceptions.ConnectionError:
                    logfire.error("❌ Cannot reach FastAPI — is the app running on :8000?")
                    blocked = False

                except Exception as e:
                    logfire.error(f"❌ Guardrails test error: {e}")
                    blocked = False

                expected = sample["expected_blocked"]
                sample["actual_blocked"] = blocked

                if expected and blocked:
                    sample["result"] = "TP"
                elif expected and not blocked:
                    sample["result"] = "FN"
                elif not expected and not blocked:
                    sample["result"] = "TN"
                else:
                    sample["result"] = "FP"

                logfire.info(
                    f"🛡️ {sample['result']}",
                    expected_blocked=expected,
                    actual_blocked=blocked,
                    input_preview=sample["input"][:60],
                )

            time.sleep(2)

    return samples


def compute_guardrails_metrics(results: list) -> dict:
    tp = sum(1 for r in results if r["result"] == "TP")
    tn = sum(1 for r in results if r["result"] == "TN")
    fp = sum(1 for r in results if r["result"] == "FP")
    fn = sum(1 for r in results if r["result"] == "FN")

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    accuracy  = (tp + tn) / len(results) if results else 0.0

    return {
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "accuracy": round(accuracy, 3),
        "total": len(results),
        "correct": tp + tn,
    }



if __name__ == "__main__":
    import sys
    import os

    if len(sys.argv) < 2:
        print("Usage: python evals/guardrails_eval.py <guardrails_samples.json>")
        sys.exit(1)

    input_file = sys.argv[1]
    with open(input_file, "r") as f:
        dataset = json.load(f)

    guardrails_samples = dataset["guardrails_samples"]

    results = run_guardrails_eval(guardrails_samples)
    metrics = compute_guardrails_metrics(results)

    print("\nGuardrails Evaluation Metrics:")
    for k, v in metrics.items():
        print(f"{k}: {v}")

    # Optionally save results to a file
    i =0
    while os.path.exists(f"evals/results/guardrails_eval_results_{i}.json"):
        i += 1
    output_file = f"evals/results/guardrails_eval_results_{i}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed results saved to {output_file}")
