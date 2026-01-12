import requests
from typing import Any

PERPLEXITY_ENDPOINT = "https://api.perplexity.ai/chat/completions"


class PerplexitySearchError(RuntimeError):
    pass


def perplexity_retrieve(
    api_key: str,
    model: str,
    query: str,
    recency: str = "month",
    max_sources: int = 5
) -> dict[str, Any]:
    """
    Uses Perplexity Sonar (web-grounded) as the *retrieval* layer.
    We instruct Perplexity to return JSON so we can run our own RAG synthesis step afterward.
    """
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    system = (
        "You are a web research assistant. Return ONLY valid JSON with keys: "
        "sources (list of {title,url,snippet}), and evidence (string). "
        "Keep evidence concise but information-dense."
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": query},
        ],
        "temperature": 0.2,
        "search_recency_filter": recency,
    }

    resp = requests.post(PERPLEXITY_ENDPOINT, headers=headers, json=payload, timeout=60)
    if resp.status_code != 200:
        raise PerplexitySearchError(f"Perplexity API error {resp.status_code}: {resp.text}")

    data = resp.json()

    # OpenAI-compatible structure; content is in choices[0].message.content
    content = data["choices"][0]["message"]["content"]
    # content should be JSON as instructed; parsing is done in rag_pipeline for resilience.
    return {"raw_content": content, "raw": data, "max_sources": max_sources}
