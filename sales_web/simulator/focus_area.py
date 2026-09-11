FOCUS_AREAS = {

    "objection_handling": {
        "name": "Objection handling",
        "behavior": """
Focus: Objection Handling. Raise realistic objections and check whether the salesperson
addresses the real concern instead of dodging it. Follow up on weak responses.
"""
    },

    "closing": {
        "name": "Closing",
        "behavior": """
Focus: Closing. Show buying signals when earned, ask about next steps, and raise
final concerns before committing. Don't agree to buy automatically.
"""
    },

    "pricing_negotiation": {
        "name": "Pricing negotiation",
        "behavior": """
Focus: Pricing Negotiation. Push on price, implementation cost, and recurring fees.
Challenge whether the value justifies the cost. Don't accept pricing without justification.
"""
    },

    "rapport_building": {
        "name": "Rapport building",
        "behavior": """
Focus: Rapport Building. Respond well to thoughtful communication and share context
when the salesperson listens well. Avoid hostility unless the personality calls for it.
"""
    },

    "product_knowledge": {
        "name": "Product knowledge",
        "behavior": """
Focus: Product Knowledge. Ask how FIREAI actually works, how it deploys, and how it
differs from existing CCTV/conventional systems. Challenge unsupported technical claims.
"""
    },
}


def get_focus_area(focus_area):

    return FOCUS_AREAS.get(
        focus_area,
        FOCUS_AREAS["objection_handling"],
    )


def get_focus_area_behavior(focus_area):

    return get_focus_area(
        focus_area
    )["behavior"]