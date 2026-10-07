# ============================================================
# TOPIC TRACKER
# ============================================================
#
# Drives topic-by-topic probing: retries the current topic
# from a different angle if the rep's answer didn't address
# it, gives up and advances after MAX_ATTEMPTS_PER_TOPIC,
# and produces a prompt instruction for each case.
#
# ============================================================

from .topics import (
    TOPIC_SEQUENCE,
    MAX_ATTEMPTS_PER_TOPIC,
)


class TopicTracker:

    def __init__(
        self,
        sequence=TOPIC_SEQUENCE,
        max_attempts=MAX_ATTEMPTS_PER_TOPIC,
    ):

        self.sequence = sequence
        self.max_attempts = max_attempts

        self._by_id = {
            topic["id"]: topic
            for topic in sequence
        }


    # ========================================================
    # INITIAL STATE
    # ========================================================

    def initial_state(self):

        first_id = self.sequence[0]["id"]

        return {

            "current_topic": first_id,

            "progress": {
                first_id: {
                    "attempts": 1,
                    "status": "probing",
                    "angle_index": 0,
                },
            },

        }


    # ========================================================
    # FIND NEXT UNCOVERED TOPIC
    # ========================================================

    def _next_uncovered(self, progress):

        for topic in self.sequence:

            status = progress.get(
                topic["id"], {}
            ).get("status")

            if status not in ("covered", "skipped"):

                return topic["id"]

        return None


    # ========================================================
    # DID THE ANSWER ADDRESS THE TOPIC
    # ========================================================

    def _addressed(
        self,
        user_message,
        topic,
        retrieved_context,
    ):

        text = user_message.lower()

        keyword_hit = any(
            keyword in text
            for keyword in topic["keywords"]
        )

        chunk_hit = any(
            chunk.get("topic") == topic["id"]
            for chunk in retrieved_context[:3]
        )

        long_enough = (
            len(user_message.strip()) >= 20
        )

        return long_enough and (
            keyword_hit or chunk_hit
        )


    # ========================================================
    # PROCESS ONE TURN
    # ========================================================

    def process_turn(
        self,
        state,
        user_message,
        retrieved_context,
    ):

        current_id = state["current_topic"]

        if current_id is None:

            return state, {"mode": "free_form"}

        topic = self._by_id[current_id]

        entry = state["progress"].setdefault(
            current_id,
            {
                "attempts": 1,
                "status": "probing",
                "angle_index": 0,
            },
        )

        if self._addressed(
            user_message, topic, retrieved_context
        ):

            entry["status"] = "covered"

            return self._advance(
                state, topic, mode="advance"
            )

        entry["attempts"] += 1

        if entry["attempts"] > self.max_attempts:

            entry["status"] = "skipped"

            return self._advance(
                state, topic, mode="skip_and_advance"
            )

        entry["angle_index"] = (
            (entry["angle_index"] + 1)
            % len(topic["angles"])
        )

        return state, {

            "mode": "retry",

            "label": topic["label"],

            "angle": topic["angles"][
                entry["angle_index"]
            ],

            "attempt": entry["attempts"],

        }


    # ========================================================
    # ADVANCE TO NEXT TOPIC
    # ========================================================

    def _advance(
        self,
        state,
        finished_topic,
        mode,
    ):

        next_id = self._next_uncovered(
            state["progress"]
        )

        state["current_topic"] = next_id

        label_key = (
            "covered_label"
            if mode == "advance"
            else "skipped_label"
        )

        if next_id is None:

            return state, {
                "mode": f"{mode}_to_free_form",
                label_key: finished_topic["label"],
            }

        next_topic = self._by_id[next_id]

        state["progress"].setdefault(
            next_id,
            {
                "attempts": 1,
                "status": "probing",
                "angle_index": 0,
            },
        )

        return state, {

            "mode": mode,

            label_key: finished_topic["label"],

            "next_label": next_topic["label"],

            "next_angle": next_topic["angles"][0],

        }


# ============================================================
# BUILD PROMPT INSTRUCTION
# ============================================================

def build_topic_instruction(instruction):

    mode = instruction["mode"]

    if mode == "retry":

        return (
            f"TOPIC FOLLOW-UP:\n"
            f"The rep's last answer didn't clearly address: "
            f"{instruction['label']}.\n"
            f"Ask about it again from a different angle — "
            f"specifically probe: {instruction['angle']}.\n"
            f"Do not repeat your previous question's wording — "
            f"rephrase it as a genuinely curious buyer, not an "
            f"interrogation."
        )

    if mode == "advance":

        return (
            f"TOPIC TRANSITION:\n"
            f"The rep adequately addressed: "
            f"{instruction['covered_label']}.\n"
            f"Move the conversation naturally toward "
            f"{instruction['next_label']}, opening with "
            f"something about {instruction['next_angle']}. "
            f"Don't announce the shift — just pivot like a "
            f"real conversation would."
        )

    if mode == "skip_and_advance":

        return (
            f"TOPIC TRANSITION:\n"
            f"The rep hasn't clearly addressed "
            f"{instruction['skipped_label']} after a couple "
            f"of tries. Let it go without calling it out — "
            f"shift naturally toward {instruction['next_label']}, "
            f"asking about {instruction['next_angle']}."
        )

    if mode in (
        "advance_to_free_form",
        "skip_and_advance_to_free_form",
    ):

        return (
            "TOPIC TRANSITION:\n"
            "All planned topics are covered or set aside. "
            "Continue naturally based on whatever the rep "
            "brings up next — no fixed agenda left."
        )

    return ""