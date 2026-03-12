from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from core.models import ConceptNode


class Command(BaseCommand):
    help = "Seeds default concept nodes for a demo user."

    def handle(self, *args, **options):
        User = get_user_model()
        user, _ = User.objects.get_or_create(username="demo_learner")

        concepts = [
            "neural networks",
            "backpropagation",
            "attention mechanism",
            "RAG pipelines",
        ]

        for concept in concepts:
            ConceptNode.objects.get_or_create(
                user=user,
                concept_id=concept,
                defaults={"mastery": 0.3, "struggling": True},
            )

        self.stdout.write(
            self.style.SUCCESS("Seed concepts created for demo_learner")
        )
