import asyncio
from ragas import SingleTurnSample
from ragas.llms import llm_factory
from evals.harnes import load_data, run_generator_node
from langchain_nvidia import ChatNVIDIA
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from ragas.metrics.collections import FactualCorrectness, Faithfulness

# LLM aur Embeddings setup
llm = llm_factory(model=ChatNVIDIA())
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

async def run():
    samples = []
    data = load_data(file_path="evals/goldens/correctness_goldens.json")

    for d in data:
        # 1. Agar run_generator_node async hai toh await lagana zarouri hai
        res = await run_generator_node(query=d['inputs']['user_input'])
        
        # Maan lijiye res ek dictionary hai jisme response aur retrieved content dono hain:
        # jaise: {"response": "...", "retrieved_content": [...]}
        response_text = res.get("response", str(res))
        retrieved_docs = res.get("retrieved_content", [])

        samples.append(SingleTurnSample(
            user_input=d['inputs']['user_input'],
            # 2. Reference me ground truth answer hona chahiye (apne json ke structure ke mutabiq change karein)
            reference=d['outputs']['expected_output'], 
            response=response_text,
            # 3. Faithfulness ke liye retrieved_contexts dena zarouri hai
            retrieved_contexts=retrieved_docs 
        ))

    # Metrics initialization
    correct_ness = FactualCorrectness(llm=llm)
    faithfull_ness = Faithfulness(llm=llm)

    # Async scoring
    c_score = await correct_ness.ascore(samples)
    f_score = await faithfull_ness.ascore(samples)

    print("Factual Correctness Score:", c_score)
    print("Faithfulness Score:", f_score)

if __name__ == "__main__":
    asyncio.run(run())