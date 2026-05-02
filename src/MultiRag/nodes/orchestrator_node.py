import logging
from utils.asyncHandler import asyncHandler

from src.MultiRag.models.rag_model import State
from src.MultiRag.models.orchestrator_output_model import OrchestratorOutput
from src.MultiRag.llm.llm_loader import llm
from src.MultiRag.prompts.prompt_templates import ORCHESTRATOR_PROMPT
from langchain_core.messages import SystemMessage, HumanMessage

@asyncHandler
async def orchestrator_node(state:State):
    logging.info("Entered in the orchestrator_node")
    logging.info(f"Current messages: {len(state.get('messages', []))} message(s)")

    orchestrator_llm = llm.with_structured_output(OrchestratorOutput, method="tool_call")
    
    user_content = state.get('userContent', [])
    files_info = "\n".join([f"- Name: {c.name}, Path: {c.path}, About: {c.about}" for c in user_content])
    logging.info(f"Files available for orchestration: {len(user_content)}")
    
    system_prompt = ORCHESTRATOR_PROMPT + f"\n\n### Available Files:\n{files_info}\n\nWhen using a worker, you MUST specify the exact 'file_path' and 'file_type' (one of: pdf, txt, docs, png, url) from the list above."
    
    prompt= [SystemMessage(content=system_prompt)]+ state.get('messages', [])
    logging.info("Invoking orchestrator LLM with file context...")

    try:
        response = await orchestrator_llm.ainvoke(prompt)
    except Exception as e:
        logging.error(f"Error in orchestrator ainvoke: {e}")
        response = None

    if response is None:
        logging.info("Structured output failed, attempting manual JSON parsing...")
        raw_res = await llm.ainvoke(prompt)
        import json
        import re
        
        # Extract JSON from potential markdown blocks or raw text
        content = raw_res.content
        logging.info(f"Raw orchestrator response: {content}")
        
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            try:
                json_data = json.loads(json_match.group())
                response = OrchestratorOutput(**json_data)
                logging.info("Successfully parsed JSON manually.")
            except Exception as e:
                logging.error(f"Manual JSON parsing failed: {e}")
        else:
            logging.warning("No JSON block found in orchestrator response. Attempting to construct plan from text...")
            # Fallback: if it's not JSON, maybe it's just text. 
            # We'll default to use_worker=False if we can't be sure, 
            # or try to extract info if it looks like a task.
            if "worker" in content.lower() and "docs/" in content:
                logging.info("Detected worker mention in text, but couldn't parse JSON. This model might need a better prompt.")
                # We could try to extract more, but for now let's just log it.

    logging.info(f"Final plan decided: {response}")
    return {"plan": response}
