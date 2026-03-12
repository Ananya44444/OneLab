from __future__ import annotations

import json

from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from core.ai_service import SharedAIService
from core.citation_verifier import verify_against_sources
from core.models import ConceptNode
from tutor.spaced_rep import sm2_update


def _score_delta(message: str) -> float:
    text = message.lower()
    confused_words = [
        "confused",
        "lost",
        "dont understand",
        "don't understand",
        "unclear",
    ]
    engaged_words = ["i think", "my answer", "because", "understand", "got it"]

    if any(word in text for word in confused_words):
        return -0.1
    if any(word in text for word in engaged_words):
        return 0.1
    return 0.02


def _quality_from_delta(delta: float) -> int:
    """Map engagement delta to SM-2 quality score (0-5)."""
    if delta < 0:
        return 1  # failed recall
    if delta > 0.05:
        return 4  # successful recall
    return 3      # bare pass


def chat_page(request):
    User = get_user_model()
    user, _ = User.objects.get_or_create(username="demo_learner")
    concepts = ConceptNode.objects.filter(user=user).order_by("concept_id")
    return render(request, "tutor/chat.html", {"concepts": concepts})


@csrf_exempt
@require_http_methods(["POST"])
def chat_view(request):
    User = get_user_model()
    user, _ = User.objects.get_or_create(username="demo_learner")

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    message = (payload.get("message") or "").strip()
    concept = (payload.get("concept") or "general learning").strip().lower()

    if not message:
        return JsonResponse({"error": "Message is required."}, status=400)

    ai_service = SharedAIService(user_id=user.id)
    retrieval = ai_service.retrieve(message, n=3)
    chunks = (
        "\n\n".join(retrieval.documents)
        if retrieval.documents
        else "No context found."
    )

    tutor_messages = [
        {
            "role": "user",
            "content": (
                f"Student concept focus: {concept}.\n"
                f"Student message: {message}\n\n"
                "You are a tutor, here is context. "
                "Explain to the student clearly, "
                "then ask one follow-up question to test understanding."
            ),
        }
    ]

    response_text = ai_service.ask_llm(messages=tutor_messages, context=chunks)

    concept_node, _ = ConceptNode.objects.get_or_create(
        user=user,
        concept_id=concept,
        defaults={"mastery": 0.3},
    )
    delta = _score_delta(message)
    concept_node.mastery += delta
    concept_node.save()

    sm2_update(concept_node, _quality_from_delta(delta))
    citations = verify_against_sources(response_text, ai_service)

    return JsonResponse(
        {
            "response": response_text,
            "mastery_score": round(concept_node.mastery, 2),
            "concept": concept_node.concept_id,
            "citations": citations,
        }
    )
