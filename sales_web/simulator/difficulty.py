DIFFICULTIES = {

    "easy": {
        "name": "Easy",
        "behavior": """
Beginner salesperson. Be cooperative and raise simple, manageable objections.
Give credit when they give a reasonable answer instead of digging further.
"""
    },

    "medium": {
        "name": "Medium",
        "behavior": """
Intermediate salesperson. Raise realistic objections and challenge unsupported claims once.
Expect normal buyer resistance, not constant pressure.
"""
    },

    "hard": {
        "name": "Hard",
        "behavior": """
Experienced salesperson — challenge strongly. Reject vague answers and demand evidence,
justification, and business value. Don't agree quickly or let weak claims slide.
"""
    },
}


def get_difficulty(difficulty):

    return DIFFICULTIES.get(
        difficulty,
        DIFFICULTIES["medium"],
    )


def get_difficulty_behavior(difficulty):

    return get_difficulty(
        difficulty
    )["behavior"]