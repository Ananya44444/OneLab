from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import chromadb
from anthropic import Anthropic
from django.conf import settings
from sentence_transformers import SentenceTransformer


@dataclass
class RetrievalResult:
    documents: list[str]
    metadatas: list[dict[str, Any]]


class SharedAIService:
    """Shared AI utility for embeddings, retrieval, and LLM responses."""

    _embedding_model: SentenceTransformer | None = None

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.collection_name = f"user_{user_id}"
        settings.CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(settings.CHROMA_DIR))
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    @classmethod
    def embedding_model(cls) -> SentenceTransformer:
        if cls._embedding_model is None:
            cls._embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        return cls._embedding_model

    def embed_and_store(self, text: str, metadata: dict[str, Any]) -> None:
        if not text.strip():
            return
        embedding = self.embedding_model().encode(text).tolist()
        doc_id = metadata.get("id") or f"{self.user_id}-{abs(hash(text))}"
        self.collection.add(
            ids=[str(doc_id)],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata],
        )

    def retrieve(self, query: str, n: int = 3) -> RetrievalResult:
        if self.collection.count() == 0:
            return RetrievalResult(documents=[], metadatas=[])

        query_embedding = self.embedding_model().encode(query).tolist()
        result = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n,
            include=["documents", "metadatas"],
        )
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        return RetrievalResult(documents=documents, metadatas=metadatas)

    def ask_llm(self, messages: list[dict[str, str]], context: str) -> str:
        """Calls Anthropic; gracefully falls back if key is unavailable."""
        if not settings.ANTHROPIC_API_KEY:
            return (
                "[LLM disabled: add ANTHROPIC_API_KEY in environment.] "
                f"Context received ({len(context)} chars)."
            )

        client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        final_messages = [
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nConversation:\n{messages}",
            },
        ]

        response = client.messages.create(
            model="claude-haiku-3-5-20251001",
            max_tokens=500,
            system=(
                "You are an adaptive tutor and research assistant. "
                "Ground your answer in the provided context when possible."
            ),
            messages=final_messages,
        )
        chunks = [
            block.text
            for block in response.content
            if hasattr(block, "text")
        ]
        return "\n".join(chunks).strip()

    def stream_response(
        self,
        messages: list[dict[str, str]],
        system: str,
    ):
        """Yields text deltas — use with Django StreamingHttpResponse."""
        if not settings.ANTHROPIC_API_KEY:
            yield "[LLM disabled: add ANTHROPIC_API_KEY in environment.]"
            return

        client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        with client.messages.stream(
            model="claude-haiku-3-5-20251001",
            max_tokens=500,
            system=system,
            messages=messages,
        ) as stream:
            for delta in stream.text_stream:
                yield delta
