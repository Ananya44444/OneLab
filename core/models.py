from django.conf import settings
from django.db import models


class ConceptNode(models.Model):
    """Tracks learner mastery and spaced-repetition schedule per concept."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    concept_id = models.CharField(max_length=120)
    label = models.CharField(max_length=200, blank=True)
    mastery = models.FloatField(default=0.0)
    easiness = models.FloatField(default=2.5)       # SM-2 easiness factor
    interval = models.IntegerField(default=1)       # days until next review
    due_date = models.DateField(null=True, blank=True)
    struggling = models.BooleanField(default=False)
    engage_pref = models.JSONField(default=dict)    # interaction signals
    last_seen = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "concept_id")
        ordering = ["concept_id"]

    def save(self, *args, **kwargs):
        # Clamp mastery and derive struggling flag automatically.
        self.mastery = max(0.0, min(1.0, self.mastery))
        self.struggling = self.mastery < 0.4
        if not self.label:
            self.label = self.concept_id.replace("-", " ").title()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.concept_id} ({self.mastery:.2f})"


class LearnerEdge(models.Model):
    """Directed relationship between two concepts in the knowledge graph."""

    EDGE_TYPES = [
        ("mastered", "Mastered"),
        ("struggling-with", "Struggling With"),
        ("has-read", "Has Read"),
        ("requires-prereq", "Requires Prerequisite"),
        ("encountered-tutor", "Encountered in Tutor"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    source = models.ForeignKey(
        ConceptNode,
        on_delete=models.CASCADE,
        related_name="outgoing",
    )
    target = models.ForeignKey(
        ConceptNode,
        on_delete=models.CASCADE,
        related_name="incoming",
    )
    edge_type = models.CharField(max_length=30, choices=EDGE_TYPES)
    confidence = models.FloatField(default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "source", "target", "edge_type")

    def __str__(self):
        return (
            f"{self.source.concept_id} --[{self.edge_type}]-->"
            f" {self.target.concept_id}"
        )
