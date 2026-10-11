"""Tier 4 NLP — natural-language Impression generation.

Generates the radiologist "Impression" narrative from the structured tier
outputs. Uses an LLM (OpenAI) when a key is configured — this is the NLP
component — and falls back to a deterministic template when it isn't, so the
pipeline always produces a report.
"""
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_SYSTEM_PROMPT = (
    "You are a consultant radiologist writing ONLY the 'Impression' section of a "
    "mammography report. Write 2-4 concise, formal clinical sentences that "
    "synthesise the provided findings: describe the lesion's morphology, state the "
    "assigned BI-RADS category and what it implies, incorporate the predicted ER "
    "status and its treatment implication, and end with the recommended next step. "
    "Do not invent data not provided. Do not add headings, bullet points, or a "
    "disclaimer — return the impression paragraph only."
)


def generate_impression_nlp(context: str, fallback: str) -> tuple[str, str]:
    """Return (impression_text, generator_name).

    Tries the LLM first (the NLP component); returns `fallback` (a deterministic
    template built by the caller) on any failure or when no key is configured.
    """
    if settings.rag_key_configured:
        try:
            from langchain_openai import ChatOpenAI

            llm = ChatOpenAI(
                model=settings.RAG_LLM_MODEL,
                temperature=0.2,
                api_key=settings.OPENAI_API_KEY,
                timeout=30,
            )
            msg = llm.invoke([("system", _SYSTEM_PROMPT), ("human", context)])
            text = (msg.content or "").strip()
            if text:
                return text, f"nlp-{settings.RAG_LLM_MODEL}"
        except Exception as exc:  # noqa: BLE001
            logger.warning("NLP impression generation failed, using template: %s", exc)

    return fallback, "template"
