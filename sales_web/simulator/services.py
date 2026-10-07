import time

import json

from config import MAX_HISTORY_MESSAGES

from .topic_tracker import (TopicTracker,build_topic_instruction,)

from rag.retriever import Retriever

from persona.system_prompt import (
    build_system_prompt,
)

from persona.prompt_builder import (
    build_messages,
)

from llm.client import get_llm_client

from database.repository import (
    SalesRepository,
)

from .personality import (
    is_valid_personality,
    get_personality,
    get_all_personalities,
    get_personality_behavior,
)
from .difficulty import (
    get_difficulty_behavior,
)

from .focus_area import (
    get_focus_area_behavior,
)
from .analyzer import SessionAnalyzer

CLIENT_NAME = "KLM Fashion Mall"
PRODUCT_NAME = "FIREAI"


class SalesSimulatorService:

    def __init__(self):

        self.retriever = Retriever()

        self.llm = get_llm_client()

        self.repository = SalesRepository()

        self.analyzer = SessionAnalyzer()
        self.topic_tracker = TopicTracker() 
        self.system_prompt = (build_system_prompt())



    # ====================================================
    # PERSONALITIES
    # ====================================================

    def get_personalities(self):

        return get_all_personalities()

    # ====================================================
    # CREATE SESSION
    # ====================================================
    

    def create_session(
        self,
        personality,
        difficulty,
        focus_area,
        session_length,
        mode,
    ):

        if not is_valid_personality(
            personality
        ):
            raise ValueError(
                f"Invalid personality: {personality}"
            )

        valid_difficulties = {
            "easy",
            "medium",
            "hard",
        }

        if difficulty not in valid_difficulties:

            raise ValueError(
                "Invalid difficulty."
            )

        valid_lengths = {
            "quick",
            "full",
        }

        if session_length not in valid_lengths:

            raise ValueError(
                "Invalid session length."
            )

        if focus_area == "":
            focus_area = None

        initial_topic_state = json.dumps(self.topic_tracker.initial_state())                                         



        valid_modes = {"chat", "simulation"}
        if mode not in valid_modes:                   
           raise ValueError("Invalid mode.")   

        session_id =self.repository.create_session(

                client_name=CLIENT_NAME,

                product_name=PRODUCT_NAME,

                personality=personality,

                difficulty=difficulty,

                focus_area=focus_area,

                topic_state=initial_topic_state,

                session_length=session_length,

                mode=mode,
            )

        opening_message = (
            "Thanks for taking the meeting. "
            "Before we go too far, we already have CCTV "
            "and conventional fire-safety systems in place. "
            "Why exactly would KLM need FIREAI?"
        )

        self.repository.add_message(
            session_id=session_id,
            role="assistant",
            content=opening_message,
        )

        personality_data =get_personality(personality)

        return {

            "session_id":
                session_id,

            "personality":
                personality,

            "personality_name":
                personality_data["name"],

            "difficulty":
                difficulty,

            "focus_area":
                focus_area,

            "session_length":
                session_length,

            "opening_message":
                opening_message,
            "mode": mode,  

        }
    def get_active_sessions(self, limit=50):

        return self.repository.get_active_sessions(
            client_name=CLIENT_NAME,
            limit=limit,
        )

    # ====================================================
    # GET SESSION
    # ====================================================

    def get_session(
        self,
        session_id,
    ):

        return self.repository.get_session(
            session_id
        )

    # ====================================================
    # GET HISTORY
    # ====================================================

    def get_history(
        self,
        session_id,
    ):

        return self.repository.get_messages(
            session_id=session_id,
            limit=None,
        )

    # ====================================================
    # GET RECENT SESSIONS
    # ====================================================

    def get_recent_sessions(
        self,
        limit=20,
    ):

        return self.repository.get_recent_sessions(
            client_name=CLIENT_NAME,
            limit=limit,
        )

    # ====================================================
    # DASHBOARD DATA
    # ====================================================

    def get_dashboard_data(self):

        return self.repository.get_dashboard_data(client_name=CLIENT_NAME)

    # ====================================================
    # CHAT STREAM
    # ====================================================

    def chat_stream(
        self,
        session_id,
        user_message,
    ):

        # ------------------------------------------------
        # Get session
        # ------------------------------------------------

        session = self.repository.get_session(
            session_id
        )

        if not session:

            yield {
                "type": "error",
                "content": "Session not found.",
            }

            return

        # ------------------------------------------------
        # Check session status
        # ------------------------------------------------

        if session["status"] != "active":

            yield {
                "type": "error",
                "content": (
                    "This training session "
                    "is already completed."
                ),
            }

            return

        # ------------------------------------------------
        # Get personality from database
        # ------------------------------------------------

        personality = session["personality"]
        difficulty = session["difficulty"]
        focus_area = session["focus_area"]

        if not personality:

            yield {
                "type": "error",
                "content": (
                    "This session does not have "
                    "a buyer personality."
                ),
            }

            return

        # ------------------------------------------------
        # Validate personality
        # ------------------------------------------------

        if not is_valid_personality(
            personality
        ):

            yield {
                "type": "error",
                "content": (
                    "Invalid session personality."
                ),
            }

            return

        # ------------------------------------------------
        # Get personality behavior
        # ------------------------------------------------

        personality_behavior = (
            get_personality_behavior(
                personality
            )
        )
        difficulty_behavior = (
            get_difficulty_behavior(difficulty)
        )

        focus_area_behavior = (
            get_focus_area_behavior(focus_area)
        )

        # ------------------------------------------------
        # Save user message
        # ------------------------------------------------

        self.repository.add_message(
            session_id=session_id,
            role="user",
            content=user_message,
        )

        # ------------------------------------------------
        # RAG
        # ------------------------------------------------

        rag_start = time.time()

        retrieved_context = (
            self.retriever.search(
                user_message
            )
        )

        rag_time = (
            time.time() - rag_start
        )
        topic_state = json.loads(
            session.get("topic_state") or "{}"
        )

        if not topic_state:
            topic_state = self.topic_tracker.initial_state()

        topic_state, topic_instruction_data = (
            self.topic_tracker.process_turn(
                topic_state,
                user_message,
                retrieved_context,
            )
        )

        self.repository.update_topic_state(
            session_id=session_id,
            topic_state_json=json.dumps(topic_state),
        )

        topic_instruction = build_topic_instruction(
            topic_instruction_data
        )

        # ------------------------------------------------
        # Get recent conversation history
        # ------------------------------------------------

        recent_history = (
            self.repository.get_messages(
                session_id=session_id,
                limit=MAX_HISTORY_MESSAGES + 1,
            )
        )

        # Remove the current user message
        # because it is passed separately to build_messages.

        if recent_history:

            recent_history = (
                recent_history[:-1]
            )

        # ------------------------------------------------
        # Build final system prompt
        # ------------------------------------------------
        #
        # Base buyer behavior
        # +
        # selected personality behavior
        #
        # Personality remains fixed because it comes
        # from the database session.
        #

        final_system_prompt = (
            self.system_prompt
                )

        # ------------------------------------------------
        # Build LLM messages
        # ------------------------------------------------

        prompt_start = time.time()

        messages = build_messages(
            system_prompt=final_system_prompt,
            history=recent_history,
            retrieved_context=retrieved_context,
            user_message=user_message,
            personality_behavior=personality_behavior,
            difficulty_behavior=difficulty_behavior,
            focus_behavior=focus_area_behavior,
            topic_instruction=topic_instruction,

        )

        prompt_time = (
            time.time() - prompt_start
        )

        # ------------------------------------------------
        # Debug
        # ------------------------------------------------
        print("=" * 60)
        print(messages)
        print("=" * 60)


        print("=" * 60)
        print("PROMPT DEBUG")
        print("=" * 60)

        print(
            f"Personality        : "
            f"{personality}"
        )

        print(
            f"Messages           : "
            f"{len(messages)}"
        )

        print(
            f"RAG time           : "
            f"{rag_time:.3f}s"
        )

        print(
            f"Prompt time        : "
            f"{prompt_time:.3f}s"
        )

      
        # ------------------------------------------------
        # Stream response
        # ------------------------------------------------

        answer = ""

        llm_start = time.time()

        first_token_time = None

        try:

            for token in self.llm.chat_stream(
                messages
            ):

                if first_token_time is None:

                    first_token_time = (
                        time.time()
                    )

                    print(
                        "FIRST TOKEN      : "
                        f"{first_token_time - llm_start:.3f}s"
                    )

                answer += token

                yield {
                    "type": "token",
                    "content": token,
                }

            # ------------------------------------------------
            # Save complete assistant response
            # ------------------------------------------------

            self.repository.add_message(
                session_id=session_id,
                role="assistant",
                content=answer,
            )

            llm_time = (
                time.time() - llm_start
            )

            print(
                "LLM TIME         : "
                f"{llm_time:.3f}s"
            )

            yield {
                "type": "done",
                "content": "",
            }

        except Exception as e:

            print(
                f"LLM ERROR: {e}"
            )

            yield {
                "type": "error",
                "content": str(e),
            }

            return
    def analyze_session(
        self,
        session_id,
    ):

        return self.analyzer.analyze(
            session_id
        )
    def get_session_analysis(
        self,
        session_id,
    ):

        analysis = (
            self.repository
            .get_session_analysis(
                session_id
            )
        )

        if not analysis:
            return None

        return json.loads(
            analysis["analysis_json"]
    )
    # ====================================================
    # GET HISTORY SESSIONS  
    # ====================================================


    def get_history_sessions(self,client_name=CLIENT_NAME,):

        return self.repository.get_history_sessions(client_name=client_name,)
    
    # ====================================================
    # END SESSION
    # ====================================================

    def end_session(
        self,
        session_id,
    ):

        self.repository.end_session(
            session_id
        )