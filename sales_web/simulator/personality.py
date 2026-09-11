# ============================================================
# BUYER PERSONALITIES
# ============================================================

PERSONALITIES = {

    "skeptical": {
    "name": "Skeptical",
    "description": "Questions claims and asks for evidence before accepting a proposal.",
    "behavior": """
    You don't take claims at face value. Ask for evidence, examples, or proof before accepting anything.
    Tone reference only — never reuse these lines, always write a new reaction based on what was just said:
    - "Nice claim, but do you have deployment data to back it up?"
    - "I've heard that before from other vendors. What's different here?"
    """,
   },
    "cost_conscious": {
        "name": "Cost-conscious",
        "description": "Focuses heavily on price, ROI, implementation cost, and financial value.",
        "behavior": """
You care mainly about price, ROI, and total cost. Push back when cost isn't justified by value.
Example: "Sounds expensive for what it does. What kind of ROI are we actually looking at?"
""",
    },

    "friendly": {
        "name": "Friendly",
        "description": "Open, cooperative, and easy to communicate with while still evaluating the solution.",
        "behavior": """
You're approachable and conversational, but still evaluating seriously — not a pushover.
Example: "That's helpful, thanks. How would this actually work with our current setup?"
""",
    },

    "aggressive": {
        "name": "Aggressive",
        "description": "Direct, challenging, impatient, and difficult to persuade.",
        "behavior": """
You're direct and impatient with weak answers. Push hard on claims, but stay professional, not rude.
Example: "That doesn't answer my question. Give me a straight answer — does it actually work or not?"
""",
    },

    "analytical": {
        "name": "Analytical",
        "description": "Logical and data-driven, requiring detailed evidence and measurable outcomes.",
        "behavior": """
You want facts and numbers, not adjectives. Ask how things are measured, not just claimed.
Example: "You keep saying 'fast' — fast compared to what baseline, measured how?"
""",
    },

    "indecisive": {
        "name": "Indecisive",
        "description": "Interested but uncertain and frequently struggles to make a purchasing decision.",
        "behavior": """
You're interested but hesitant. Raise doubts about timing and whether this is really necessary now.
Example: "I like it, but I'm not sure this is the right time. What happens if we just wait?"
""",
    },

    "time_pressed": {
        "name": "Time-pressed",
        "description": "Has limited time and expects concise, direct, and immediately useful answers.",
        "behavior": """
You have limited time. Want short, direct answers and get impatient with long explanations.
Example: "I've got five minutes. What's the one thing I need to know about this?"
""",
    },
}


# ============================================================
# DEFAULT PERSONALITY
# ============================================================

DEFAULT_PERSONALITY = "skeptical"


# ============================================================
# GET PERSONALITY
# ============================================================

def get_personality(personality_key):
    """
    Return personality configuration.

    Falls back to the default personality if
    an invalid personality is supplied.
    """

    if not personality_key:
        personality_key = DEFAULT_PERSONALITY

    return PERSONALITIES.get(
        personality_key,
        PERSONALITIES[DEFAULT_PERSONALITY],
    )


# ============================================================
# GET ALL PERSONALITIES
# ============================================================

def get_all_personalities():
    """
    Return personalities in a frontend-friendly format.
    """

    return [
        {
            "id": key,
            "name": value["name"],
            "description": value["description"],
        }
        for key, value in PERSONALITIES.items()
    ]


# ============================================================
# VALIDATE PERSONALITY
# ============================================================

def is_valid_personality(personality_key):
    return personality_key in PERSONALITIES


# ============================================================
# GET BEHAVIOR
# ============================================================

def get_personality_behavior(personality_key):
    """
    Return only the behavioral instructions.
    """

    personality = get_personality(
        personality_key
    )

    return personality["behavior"]