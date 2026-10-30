import asyncio
import sys
from evals import (
    eval_generator,
    eval_retriever,
    eval_faithfulness,
    eval_scope,
    eval_toxicity,
    security,
)

EVALS = {
    "retriever": eval_retriever.main,
    "correctness": eval_generator.main,
    "faithfulness": eval_faithfulness.main,
    "leakage": security.main,
    "scope": eval_scope.main,
    "toxicity": eval_toxicity.main,
}


async def main():
    targets = sys.argv[1:] if len(sys.argv) > 1 else list(EVALS.keys())
    print(f"🚀 Running evaluations for: {', '.join(targets)}")

    for name in targets:
        if name not in EVALS:
            print(f"⚠️ Unknown evaluation: {name}. Available: {list(EVALS.keys())}")
            continue
        print(f"\n==========================================")
        print(f"▶️ Starting evaluation: {name}")
        print(f"==========================================")
        try:
            res = await EVALS[name]()
            print(f"✅ Finished {name}: {res}")
        except Exception as e:
            print(f"❌ Error during {name}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
