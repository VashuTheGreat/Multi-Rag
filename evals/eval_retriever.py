import asyncio
from ragas import SingleTurnSample
from ragas.llms import llm_factory
from evals.harnes import load_data, run_retriever_node
from langchain_nvidia import ChatNVIDIA
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from ragas.metrics.collections import ContextPrecision, ContextRecall

# LLM aur Embeddings setup
llm = llm_factory(model=ChatNVIDIA())
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

async def run():
    samples = []
    data = load_data(file_path="evals/goldens/retriever_goldens.json")

    for d in data:
        # 1. await lagana zaroori hai agar function async hai
        res = await run_retriever_node(query=d['inputs']['user_input'])
        
        # Maan lijiye run_retriever_node ek list of strings return karta hai (retrieved docs)
        # Agar res dictionary hai (jaise {"retrieved_content": [...]}), toh res.get(...) use karein.
        retrieved_docs = res if isinstance(res, list) else res.get("retrieved_content", [])

        samples.append(SingleTurnSample(
            user_input=d['inputs']['user_input'],
            # 2. Retrieved documents jo aapke model ne nikaale
            retrieved_contexts=retrieved_docs,
            # 3. Ground truth reference contexts jo aapke JSON me expected hain 
            # (apne JSON ke key ke hisaab se change karein, jaise d['outputs']['expected_contexts'])
            reference_contexts=d['outputs']['expected_contexts'] 
        ))

    # Metrics initialization
    context_recall = ContextRecall(llm=llm)
    context_precision = ContextPrecision(llm=llm)

    # Async scoring
    r_score = await context_recall.ascore(samples)
    p_score = await context_precision.ascore(samples)

    print("Context Recall Score:", r_score)
    print("Context Precision Score:", p_score)

if __name__ == "__main__":
    asyncio.run(run())