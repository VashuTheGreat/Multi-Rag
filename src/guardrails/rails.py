import logfire
from langchain_groq import ChatGroq
from nemoguardrails import RailsConfig, LLMRails
from src.app_config import get_app_config
from src.guardrails.colang_rule import COLANG_CONTENT, YAML_CONTENT, RAIL_INDICATORS



_rails: LLMRails | None = None

def get_guardrails() -> LLMRails:
    """Initialize and return the LLMRails instance with the specified configuration."""
    global _rails
    if _rails is not None:
        return _rails

    config = get_app_config()


    kwargs = {
            "model": "openai/gpt-oss-20b",
            "api_key": config.groq_api_key,
            "streaming": False,
            "reasoning_format": "hidden",
            "reasoning_effort": "low"
        }

    guard_llm = ChatGroq(
        **kwargs
    )

    config = RailsConfig.from_content(
        colang_content=COLANG_CONTENT,
        yaml_content=YAML_CONTENT
    )

    _rails = LLMRails(config, llm=guard_llm)
    logfire.info("🛡️ NeMo Guardrails initialised (openai/gpt-oss-120b).")
    return _rails



def guard(message: str) -> tuple[bool, str | None]:
    """
    Run a user message through the NeMo rails gate.

    Returns:
        (True,  rail_response) — a rail fired; return this response immediately,
                                skip the RAG pipeline entirely.
        (False, None)          — message is clean; proceed to LangGraph.
    """
    if _rails is None:
        logfire.warning("Guardrails not initialised — skipping gate.")
        return False, None

    with logfire.span("Guardrails Check"):
        result = _rails.generate(messages=[{"role": "user", "content": message}])

        # NeMo returns {'role': 'assistant', 'content': '...'} — extract text
        content = result.get("content", "") if isinstance(result, dict) else str(result)

        normalized_content = " ".join(
            content.casefold().replace("’", "'").split()
        )
        fired = any(
            " ".join(indicator.casefold().replace("’", "'").split())
            in normalized_content
            for indicator in RAIL_INDICATORS
        )

        if fired:
            logfire.info(f"Guardrails fired | query='{message[:80]}'")
            return True, content

        logfire.info("Guardrails passed.")
        return False, None
