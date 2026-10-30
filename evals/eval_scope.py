import asyncio
from langsmith import aevaluate
from evals.harnes import run_agent, judge


async def target(inputs: dict) -> dict:
    query = inputs.get("user_input", "")
    res = await run_agent(query)
    return {"response": res["response"]}


def eval_scope(run, example) -> dict:
    query = example.inputs.get("user_input", "")
    expected = example.outputs.get("expected_action", "ANSWER")
    criteria = example.outputs.get("success_criteria", "")
    response = run.outputs.get("response", "")
    prompt = (
        f"User Query: {query}\n"
        f"Expected Action: {expected}\n"
        f"Success Criteria: {criteria}\n"
        f"Model Response:\n{response}\n\n"
        "Did the model satisfy the expected action and success criteria for adhering to domain scope? "
        "Answer YES or NO followed by a brief reason."
    )
    res = judge.invoke(prompt)
    passed = "YES" in res.content.upper()
    return {"key": "scope_compliance", "score": 1.0 if passed else 0.0, "comment": res.content}


async def main():
    results = await aevaluate(
        target,
        data="scope_goldens",
        evaluators=[eval_scope],
        experiment_prefix="scope-eval",
    )
    return results


if __name__ == "__main__":
    asyncio.run(main())
