from langchain_aws import ChatBedrockConverse
from langchain_groq import ChatGroq
from src.MultiRag.constants import LLM_MODEL_ID,LLM_REGION,MODEL_NAME
import logging
llm = ChatBedrockConverse(
    model_id=LLM_MODEL_ID,
    region_name=LLM_REGION
)

# llm=ChatGroq(
#     model=MODEL_NAME
# )
# logging.info(f"LLM initialized with model_id={LLM_MODEL_ID}, region_name={LLM_REGION}")
logging.info(f"LLM initialized with model_name:{MODEL_NAME}")