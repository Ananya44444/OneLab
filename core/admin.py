from django.contrib import admin

from .models import ConceptNode, LearnerEdge


@admin.register(ConceptNode)
class ConceptNodeAdmin(admin.ModelAdmin):
    list_display = (
        "user", "concept_id", "mastery", "struggling",
        "interval", "due_date", "last_seen",
    )
    list_filter = ("struggling", "concept_id")
    search_fields = ("user__username", "concept_id")


@admin.register(LearnerEdge)
class LearnerEdgeAdmin(admin.ModelAdmin):
    list_display = ("user", "source", "target", "edge_type", "confidence")
    list_filter = ("edge_type",)
    search_fields = ("user__username",)
