import json
from typing import Any
from openai import OpenAI

from web_search import perplexity_retrieve
from config import Settings


class RAGError(RuntimeError):
    pass


def _robust_json_loads(s: str) -> dict[str, Any]:
    """
    Tries to parse JSON even if the model wraps it in markdown fences.
    """
    s = s.strip()
    if s.startswith("```"):
        # Remove the first and last fence blocks loosely
        s = s.strip("`").strip()
        if s.lower().startswith("json"):
            s = s[4:].strip()
    return json.loads(s)


def _chunk_text(text: str, chunk_size: int = 900, overlap: int = 120) -> list[str]:
    text = text.strip()
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end])
        start = max(end - overlap, end)
    return chunks


def answer_with_web_rag(
    question: str,
    shape_context: dict[str, Any],
    recency: str,
    max_sources: int,
    settings: Settings
) -> dict[str, Any]:
    """
    Web-RAG pipeline:
      1) Retrieve web-grounded evidence & sources via Perplexity (no user URLs needed).
      2) Chunk/organize evidence.
      3) Synthesize final answer via OpenAI.
    """
    # ---- Retrieval (Perplexity) ----
    retrieval_query = (
        f"{question}\n\n"
        f"Context (user's current shape spec): {json.dumps(shape_context)}\n\n"
        "Prefer authoritative math/education sources when possible."
    )

    retrieved = perplexity_retrieve(
        api_key=settings.perplexity_api_key,
        model=settings.perplexity_model,
        query=retrieval_query,
        recency=recency,
        max_sources=max_sources
    )

    try:
        parsed = _robust_json_loads(retrieved["raw_content"])
    except Exception:
        # fallback: if Perplexity didn't follow JSON, still pass raw content as evidence
        parsed = {
            "sources": [],
            "evidence": retrieved["raw_content"]
        }

    sources = (parsed.get("sources", []) or [])[:max_sources]
    evidence = parsed.get("evidence", "") or ""

    chunks = _chunk_text(evidence)
    if not chunks:
        chunks = [evidence[:1200]] if evidence else []

    # ---- Synthesis (OpenAI) ----
    client = OpenAI(api_key=settings.openai_api_key)

    sources_block = "\n".join(
        [
            f"[{i+1}] {s.get('title','(source)')} — {s.get('url','')}\nSnippet: {s.get('snippet','')}"
            for i, s in enumerate(sources)
        ]
    ) if sources else "(No sources parsed; answer may be less grounded.)"

    evidence_block = "\n\n---\n\n".join([f"Chunk {i+1}:\n{c}" for i, c in enumerate(chunks[:6])])

    prompt = f"""
You are a precise geometry tutor.
Use the evidence chunks and sources below to answer the user's question.
If you use a fact from a source, cite it with [1], [2], etc.
Keep it clear and interview-demo friendly.

USER QUESTION:
{question}

SOURCES:
{sources_block}

EVIDENCE:
{evidence_block}
""".strip()

    resp = client.responses.create(
        model=settings.openai_model,
        input=prompt
    )

    return {
        "answer": resp.output_text,
        "sources": sources
    }
