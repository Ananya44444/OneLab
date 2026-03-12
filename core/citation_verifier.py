from __future__ import annotations

import re

from core.ai_service import SharedAIService


def verify_against_sources(
    response_text: str,
    ai_service: SharedAIService,
) -> list[dict]:
    """
    For each sentence in the tutor response, attempt to retrieve a
    matching chunk from the user's indexed document collection.

    Returns a list of dicts:
        sentence      – the original sentence
        source_found  – True if a matching chunk exists in ChromaDB
        source_excerpt – first 100 chars of the matching chunk, or None
    """
    sentences = re.split(r"(?<=[.!?])\s+", response_text.strip())
    results: list[dict] = []

    for sent in sentences:
        # Skip very short fragments (transitions, conjunctions, etc.)
        if len(sent) < 25:
            results.append(
                {
                    "sentence": sent,
                    "source_found": True,
                    "source_excerpt": None,
                }
            )
            continue

        retrieval = ai_service.retrieve(sent, n=1)

        if retrieval.documents:
            results.append(
                {
                    "sentence": sent,
                    "source_found": True,
                    "source_excerpt": retrieval.documents[0][:100],
                }
            )
        else:
            results.append(
                {
                    "sentence": sent,
                    "source_found": False,
                    "source_excerpt": None,
                }
            )

    return results
