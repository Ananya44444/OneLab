from __future__ import annotations

import uuid

import fitz
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from core.ai_service import SharedAIService

from .models import Document


def chunk_text(text: str, size: int = 400, overlap: int = 80) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end == len(text):
            break
        start = max(0, end - overlap)
    return chunks


def extract_pdf_text(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = [page.get_text("text") for page in doc]
    return "\n".join(pages)


@require_http_methods(["GET", "POST"])
def upload_view(request):
    documents = Document.objects.order_by("-uploaded_at")[:20]

    if request.method == "GET":
        return render(
            request,
            "research/upload.html",
            {"documents": documents},
        )

    pdf_file = request.FILES.get("pdf")
    if not pdf_file:
        return JsonResponse({"error": "Please upload a PDF file."}, status=400)

    title = pdf_file.name
    record = Document.objects.create(title=title, status="processing")

    User = get_user_model()
    user, _ = User.objects.get_or_create(username="demo_learner")
    ai_service = SharedAIService(user_id=user.id)

    try:
        text = extract_pdf_text(pdf_file.read())
        chunks = chunk_text(text)

        for i, chunk in enumerate(chunks):
            ai_service.embed_and_store(
                text=chunk,
                metadata={
                    "id": str(uuid.uuid4()),
                    "source": title,
                    "chunk_index": i,
                },
            )

        summary_prompt = [
            {
                "role": "user",
                "content": (
                    "Summarize the following paper content "
                    "in exactly 3 sentences:\n\n"
                    f"{text[:5000]}"
                ),
            }
        ]
        summary = ai_service.ask_llm(summary_prompt, context=text[:3000])

        record.status = "processed"
        record.save(update_fields=["status"])

        return JsonResponse(
            {
                "title": title,
                "summary": summary,
                "chunks_indexed": len(chunks),
                "status": record.status,
            }
        )
    except Exception as exc:
        record.status = "failed"
        record.save(update_fields=["status"])
        return JsonResponse({"error": str(exc)}, status=500)
