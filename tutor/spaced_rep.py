from datetime import date, timedelta


def sm2_update(concept_node, quality: int) -> None:
    """
    Apply the SM-2 algorithm and persist the result to the database.

    quality 0-5:
        0-2  failed recall    -> reset interval, mark struggling
        3-5  successful recall -> extend interval, update easiness factor
    """
    quality = max(0, min(5, quality))

    if quality >= 3:
        if concept_node.interval <= 1:
            concept_node.interval = 6
        else:
            concept_node.interval = round(
                concept_node.interval * concept_node.easiness
            )
        concept_node.easiness = max(
            1.3,
            concept_node.easiness
            + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)),
        )
    else:
        concept_node.interval = 1
        concept_node.struggling = True

    concept_node.due_date = date.today() + timedelta(
        days=concept_node.interval
    )
    concept_node.save(
        update_fields=["easiness", "interval", "due_date", "struggling"]
    )
