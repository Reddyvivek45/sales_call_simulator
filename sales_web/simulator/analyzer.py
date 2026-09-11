import json
import re

from database.repository import SalesRepository
from llm.session_analyzer_client import (
    SessionAnalyzerOllamaClient,
)


class SessionAnalyzer:

    # ========================================================
    # SCORE WEIGHTS
    # ========================================================

    WEIGHTS = {

        "product_knowledge": 0.20,

        "needs_discovery": 0.20,

        "objection_handling": 0.20,

        "value_selling": 0.20,

        "communication": 0.10,

        "closing": 0.10,

    }

    # ========================================================
    # INITIALIZE
    # ========================================================

    def __init__(self):

        self.repository = (
            SalesRepository()
        )

        self.llm = (
            SessionAnalyzerOllamaClient()
        )

    # ========================================================
    # MAIN ANALYSIS
    # ========================================================

    def analyze(self, session_id):

        # ----------------------------------------------------
        # GET SESSION
        # ----------------------------------------------------

        session = (
            self.repository
            .get_session(session_id)
        )

        if not session:

            raise ValueError(
                "Session not found."
            )

        # ----------------------------------------------------
        # ONLY COMPLETED SESSIONS
        # ----------------------------------------------------

        if session["status"] != "completed":

            raise ValueError(
                "Only completed sessions can be analyzed."
            )

        # ----------------------------------------------------
        # CHECK EXISTING ANALYSIS
        # ----------------------------------------------------

        existing = (
            self.repository
            .get_session_analysis(
                session_id
            )
        )

        if existing:

            return json.loads(
                existing["analysis_json"]
            )

        # ----------------------------------------------------
        # GET FULL TRANSCRIPT
        # ----------------------------------------------------

        messages = (
            self.repository
            .get_messages(
                session_id=session_id,
                limit=None,
            )
        )

        if not messages:

            raise ValueError(
                "No conversation found for this session."
            )

        # ----------------------------------------------------
        # OBJECTIVE METRICS
        # ----------------------------------------------------

        objective_metrics = (
            self._calculate_objective_metrics(
                messages
            )
        )

        # ----------------------------------------------------
        # TRANSCRIPT
        # ----------------------------------------------------

        transcript = (
            self._build_transcript(
                messages
            )
        )

        # ----------------------------------------------------
        # LLM EVALUATION
        # ----------------------------------------------------

        llm_result = (
            self._evaluate_with_llm(
                session=session,
                transcript=transcript,
                metrics=objective_metrics,
            )
        )

        # ----------------------------------------------------
        # FINAL SCORE
        # ----------------------------------------------------

        scores = llm_result["scores"]

        overall_score = (
            self._calculate_overall_score(
                scores
            )
        )

        # ----------------------------------------------------
        # FINAL RESULT
        # ----------------------------------------------------

        result = {

            "overall_score":
                overall_score,

            "scores":
                scores,

            "objective_metrics":
                objective_metrics,

            "strengths":
                llm_result.get(
                    "strengths",
                    [],
                ),

            "weaknesses":
                llm_result.get(
                    "weaknesses",
                    [],
                ),

            "recommendations":
                llm_result.get(
                    "recommendations",
                    [],
                ),

            "evidence":
                llm_result.get(
                    "evidence",
                    [],
                ),

            "summary":
                llm_result.get(
                    "summary",
                    "",
                ),
        }

        # ----------------------------------------------------
        # SAVE ANALYSIS
        # ----------------------------------------------------

        self.repository.create_session_analysis(

            session_id=session_id,

            overall_score=overall_score,

            analysis_json=json.dumps(
                result,
                ensure_ascii=False,
            ),

        )

        return result

    # ========================================================
    # OBJECTIVE METRICS
    # ========================================================

    def _calculate_objective_metrics(
        self,
        messages,
    ):

        salesperson_messages = [
            message
            for message in messages
            if message["role"] == "user"
        ]

        buyer_messages = [
            message
            for message in messages
            if message["role"] == "assistant"
        ]

        salesperson_text = " ".join(
            message["content"]
            for message in salesperson_messages
        )

        text_lower = (
            salesperson_text.lower()
        )

        # ----------------------------------------------------
        # QUESTIONS
        # ----------------------------------------------------

        questions_asked = sum(
            message["content"].count("?")
            for message in salesperson_messages
        )

        # ----------------------------------------------------
        # PRICING
        # ----------------------------------------------------

        pricing_keywords = [

            "price",
            "pricing",
            "cost",
            "budget",
            "license",
            "licensing",
            "maintenance",
            "subscription",
            "implementation cost",

        ]

        pricing_discussed = any(
            keyword in text_lower
            for keyword in pricing_keywords
        )

        # ----------------------------------------------------
        # VALUE
        # ----------------------------------------------------

        value_keywords = [

            "roi",
            "return on investment",
            "savings",
            "benefit",
            "business value",
            "cost saving",
            "reduce cost",

        ]

        value_discussed = any(
            keyword in text_lower
            for keyword in value_keywords
        )

        # ----------------------------------------------------
        # CLOSING
        # ----------------------------------------------------

        closing_keywords = [

            "pilot",
            "demo",
            "demonstration",
            "poc",
            "proof of concept",
            "next step",
            "schedule",
            "trial",
            "evaluation",
            "deploy",

        ]

        closing_attempt = any(
            keyword in text_lower
            for keyword in closing_keywords
        )

        # ----------------------------------------------------
        # TECHNICAL
        # ----------------------------------------------------

        technical_keywords = [

            "cctv",
            "camera",
            "integration",
            "deployment",
            "api",
            "software",
            "hardware",
            "system",
            "installation",

        ]

        technical_discussed = any(
            keyword in text_lower
            for keyword in technical_keywords
        )

        # ----------------------------------------------------
        # AVERAGE RESPONSE LENGTH
        # ----------------------------------------------------

        if salesperson_messages:

            average_words = (
                sum(
                    len(
                        message["content"].split()
                    )
                    for message in salesperson_messages
                )
                /
                len(salesperson_messages)
            )

        else:

            average_words = 0

        return {

            "total_salesperson_messages":
                len(salesperson_messages),

            "total_buyer_messages":
                len(buyer_messages),

            "questions_asked":
                questions_asked,

            "pricing_discussed":
                pricing_discussed,

            "value_discussed":
                value_discussed,

            "closing_or_next_step_attempt":
                closing_attempt,

            "technical_discussion":
                technical_discussed,

            "average_salesperson_response_words":
                round(
                    average_words,
                    1,
                ),
        }

    # ========================================================
    # TRANSCRIPT
    # ========================================================

    def _build_transcript(
        self,
        messages,
    ):

        lines = []

        for message in messages:

            if message["role"] == "user":

                role = "SALESPERSON"

            else:

                role = "BUYER"

            lines.append(
                f"{role}: {message['content']}"
            )

        return "\n".join(lines)

    # ========================================================
    # LLM EVALUATION
    # ========================================================

    def _evaluate_with_llm(
        self,
        session,
        transcript,
        metrics,
    ):

        prompt = f"""
You are an expert sales training evaluator.

Analyze the completed sales conversation below.

You are evaluating ONLY the salesperson.

==================================================
SESSION
==================================================

Client:
{session["client_name"]}

Product:
{session["product_name"]}

Buyer Personality:
{session["personality"]}

Difficulty:
{session["difficulty"]}

Focus Area:
{session["focus_area"]}

Session Length:
{session["session_length"]}

==================================================
SCORING DIMENSIONS
==================================================

PRODUCT KNOWLEDGE — 20%

Evaluate:
- Product understanding
- Technical understanding
- Accuracy
- Relevant explanations
- Avoidance of unsupported claims

NEEDS DISCOVERY — 20%

Evaluate:
- Quality of discovery questions
- Understanding of KLM's situation
- Understanding of current systems
- Identification of pain points
- Understanding of business needs

OBJECTION HANDLING — 20%

Evaluate:
- Recognition of objections
- Direct response
- Relevance
- Quality of justification
- Ability to handle difficult questions

VALUE SELLING — 20%

Evaluate:
- Business value
- Benefits
- ROI/value justification
- Connection to KLM's needs
- Ability to explain why FIREAI matters

COMMUNICATION — 10%

Evaluate:
- Clarity
- Professionalism
- Conciseness
- Logical explanation
- Directly answering questions

CLOSING — 10%

Evaluate:
- Clear next step
- Pilot/demo/POC
- Moving the sale forward
- Commitment
- Appropriate closing behavior

==================================================
SCORING SCALE
==================================================

90-100 = Excellent
75-89  = Good
60-74  = Average
40-59  = Weak
0-39   = Poor

==================================================
IMPORTANT RULES
==================================================

Do NOT reward keyword usage alone.

For example:

"I don't know the ROI."

contains the word ROI but should NOT receive credit
for value selling.

Evaluate meaning and context.

Do not reward invented facts.

Unsupported claims about:
- prices
- accuracy
- latency
- customers
- ROI figures
- SLA
- technical specifications

should reduce the relevant score.

Buyer personality and difficulty provide context.

Do not automatically penalize the salesperson because
the buyer is aggressive, skeptical, or difficult.

The focus area is particularly important.

==================================================
OBJECTIVE METRICS
==================================================

{json.dumps(metrics, indent=2)}

These metrics are supporting evidence only.

Do not directly convert keyword presence into scores.

==================================================
CONVERSATION
==================================================

{transcript}

==================================================
OUTPUT
==================================================

Return ONLY valid JSON.

Use exactly this structure:

{{
    "scores": {{
        "product_knowledge": 0,
        "needs_discovery": 0,
        "objection_handling": 0,
        "value_selling": 0,
        "communication": 0,
        "closing": 0
    }},

    "strengths": [
        "strength 1",
        "strength 2",
        "strength 3"
    ],

    "weaknesses": [
        "weakness 1",
        "weakness 2",
        "weakness 3"
    ],

    "recommendations": [
        "recommendation 1",
        "recommendation 2",
        "recommendation 3"
    ],

    "evidence": [
        {{
            "category": "needs_discovery",
            "salesperson_statement": "short statement from transcript",
            "assessment": "why this was good or weak"
        }}
    ],

    "summary": "Short overall evaluation."
}}
"""

        messages = [

            {
                "role": "system",
                "content": (
                    "You are a strict and fair "
                    "sales training evaluator. "
                    "Return JSON only."
                ),
            },

            {
                "role": "user",
                "content": prompt,
            },

        ]

        response = (
            self.llm.analyze(
                messages
            )
        )

        return self._parse_llm_json(
            response
        )

    # ========================================================
    # FINAL SCORE
    # ========================================================

    def _calculate_overall_score(
        self,
        scores,
    ):

        total = 0

        for category, weight in (
            self.WEIGHTS.items()
        ):

            score = float(
                scores.get(
                    category,
                    0,
                )
            )

            score = max(
                0,
                min(
                    100,
                    score,
                )
            )

            total += (
                score * weight
            )

        return round(
            total,
            1,
        )

    # ========================================================
    # PARSE LLM JSON
    # ========================================================

    def _parse_llm_json(
        self,
        response,
    ):

        response = response.strip()

        # Remove markdown fences if model
        # ignores JSON-only instruction.

        response = re.sub(
            r"^```json\s*",
            "",
            response,
            flags=re.IGNORECASE,
        )

        response = re.sub(
            r"\s*```$",
            "",
            response,
        )

        start = response.find("{")

        end = response.rfind("}")

        if start == -1 or end == -1:

            raise ValueError(
                "Analyzer LLM did not return valid JSON."
            )

        json_text = response[
            start:end + 1
        ]

        try:

            result = json.loads(
                json_text
            )

        except json.JSONDecodeError as exc:

            raise ValueError(
                f"Invalid analyzer JSON: {exc}"
            )

        # ----------------------------------------------------
        # VALIDATE SCORE OBJECT
        # ----------------------------------------------------

        required_scores = [

            "product_knowledge",

            "needs_discovery",

            "objection_handling",

            "value_selling",

            "communication",

            "closing",

        ]

        if "scores" not in result:

            raise ValueError(
                "Analyzer response does not contain scores."
            )

        for category in required_scores:

            if category not in result["scores"]:

                raise ValueError(
                    f"Missing analyzer score: {category}"
                )

            try:

                score = float(
                    result["scores"][category]
                )

            except (
                TypeError,
                ValueError,
            ):

                raise ValueError(
                    f"Invalid score for {category}"
                )

            result["scores"][category] = round(
                max(
                    0,
                    min(
                        100,
                        score,
                    )
                ),
                1,
            )

        # ----------------------------------------------------
        # DEFAULT LISTS
        # ----------------------------------------------------

        for key in [
            "strengths",
            "weaknesses",
            "recommendations",
            "evidence",
        ]:

            if not isinstance(
                result.get(key),
                list,
            ):

                result[key] = []

        if not isinstance(
            result.get("summary"),
            str,
        ):

            result["summary"] = ""

        return result