# ============================================================
# TOPIC TAXONOMY
# ============================================================
#
# Fixed, ordered list of things the buyer should probe during
# a pitch. Each topic has multiple "angles" — different ways
# to ask about the same underlying concern, used when the
# rep's first answer doesn't address it.
#
# ============================================================

MAX_ATTEMPTS_PER_TOPIC = 2


TOPIC_SEQUENCE = [

    {
        "id": "existing_system_comparison",
        "label": "Why FIREAI vs. existing CCTV/fire safety",
        "keywords": [
            "already have", "existing", "cctv",
            "conventional", "different",
        ],
        "angles": [
            "why FIREAI is needed when CCTV and conventional "
            "fire safety already exist",

            "what specific gap or blind spot the current setup "
            "has that FIREAI would close",

            "a concrete scenario where the existing system "
            "might have missed something",
        ],
    },

    {
        "id": "detection_accuracy_speed",
        "label": "Detection accuracy and response speed",
        "keywords": [
            "accuracy", "false positive", "speed",
            "response time", "detect",
        ],
        "angles": [
            "how accurate the detection actually is",
            "how fast it reacts compared to a person noticing smoke or fire",
            "how it handles false alarms on a crowded retail floor",
        ],
    },

    {
        "id": "integration_installation",
        "label": "Integration and install disruption",
        "keywords": [
            "integrate", "install", "disruption",
            "downtime", "setup",
        ],
        "angles": [
            "whether install would disrupt store operations",
            "how it plugs into the CCTV they already have",
            "how long rollout at one branch would actually take",
        ],
    },

    {
        "id": "multi_branch_scalability",
        "label": "Rollout across multiple branches",
        "keywords": [
            "branches", "scale", "multiple stores",
            "rollout", "locations",
        ],
        "angles": [
            "how this scales across all branches, not just one",
            "whether cost or setup changes at higher branch counts",
            "what a phased rollout across locations looks like",
        ],
    },

    {
        "id": "cost_roi",
        "label": "Pricing and ROI",
        "keywords": [
            "cost", "price", "roi", "budget", "pricing",
        ],
        "angles": [
            "what this actually costs",
            "how cost compares to the risk of a fire incident",
            "what kind of return makes sense given a budget-conscious retailer",
        ],
    },

    {
        "id": "proof_case_studies",
        "label": "Proof it works in retail, not just factories",
        "keywords": [
            "case study", "proof", "deployed",
            "track record", "retail",
        ],
        "angles": [
            "whether there's proof this works specifically in retail",
            "any other retail client references",
            "what results other deployments have actually shown",
        ],
    },

]