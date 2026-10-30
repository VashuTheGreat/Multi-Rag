import asyncio
from ragas import SingleTurnSample
from ragas.llms import llm_factory
from evals.harnes import load_data, run_agent  # run_agent import kiya
from langchain_nvidia import ChatNVIDIA
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from ragas.metrics.collections import FactualCorrectness, Faithfulness, ResponseRelevance

# LLM aur Embeddings setup
llm = llm_factory(model=ChatNVIDIA())
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

async def run():
    samples = []
    # Apne test/eval dataset ka path dein
    data = load_data(file_path="evals/goldens/agent_goldens.json")

    for d in data:
        # 1. Poora agent pipeline run karein (await ke sath)
        res = await run_agent(query=d['inputs']['user_input'])
        
        # run_agent ke output dictionary se response aur retrieved content nikalna
        response_text = res.get("response", "")
        retrieved_docs = res.get("retrieved_content", [])

        samples.append(SingleTurnSample(
            user_input=d['inputs']['user_input'],
            response=response_text,
            retrieved_contexts=retrieved_docs,
            # Ground truth reference answer (JSON structure ke hisaab se key change kar sakte hain)
            reference=d['outputs']['expected_output']
        ))

    # Metrics setup (Aap apni zaroorat ke hisaab se metrics rakh sakte hain)
    factual_correctness = FactualCorrectness(llm=llm)
    faithfulness = Faithfulness(llm=llm)
    response_relevance = ResponseRelevance(llm=llm)

    # Async scoring
    fc_score = await factual_correctness.ascore(samples)
    f_score = await faithfulness.ascore(samples)
    rr_score = await response_relevance.ascore(samples)

    print("Factual Correctness:", fc_score)
    print("Faithfulness:", f_score)
    print("Response Relevance:", rr_score)

if __name__ == "__main__":
    asyncio.run(run())