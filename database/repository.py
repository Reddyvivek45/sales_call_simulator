import uuid
import json
from datetime import datetime

from database.connection import SessionLocal

from database.models import (
    SalesSession,
    Message,
    SessionAnalysis,
)


class SalesRepository:

    # ========================================================
    # CREATE SESSION
    # ========================================================

    def create_session(
        self,
        client_name,
        product_name,
        personality,
        difficulty,
        focus_area,
        session_length,
        mode,
        topic_state,
        user_id,
    ):

        db = SessionLocal()

        try:

            session_id = str(
                uuid.uuid4()
            )

            session = SalesSession(

                id=session_id,

                client_name=client_name,

                product_name=product_name,

                personality=personality,

                difficulty=difficulty,

                focus_area=focus_area,

                session_length=session_length,

                mode=mode,

                topic_state=topic_state,
                user_id=user_id, 

                status="active",

            )

            db.add(session)

            db.commit()

            return session_id

        finally:

            db.close()

    # ========================================================
    # GET SESSION
    # ========================================================

    def get_session(
        self,
        session_id,
    ):

        db = SessionLocal()

        try:

            session = (
                db.query(SalesSession)
                .filter(
                    SalesSession.id
                    == session_id
                )
                .first()
            )

            if not session:
                return None

            return {

                "id": session.id,

                "client_name":
                    session.client_name,

                "product_name":
                    session.product_name,

                "personality":
                    session.personality,

                "difficulty":
                    session.difficulty,

                "focus_area":
                    session.focus_area,

                "session_length":
                    session.session_length,

                "user_id": session.user_id,

                "started_at":
                    session.started_at.isoformat(),

                "ended_at":
                    session.ended_at.isoformat()
                    if session.ended_at
                    else None,

                "status":
                    session.status,
                
                "mode":session.mode,
                "topic_state": session.topic_state,

            }

        finally:

            db.close()


    # ========================================================
    # GET SESSION PERSONALITY
    # ========================================================

    def get_session_personality(
        self,
        session_id,
    ):

        db = SessionLocal()

        try:

            session = (
                db.query(SalesSession)
                .filter(
                    SalesSession.id
                    == session_id
                )
                .first()
            )

            if not session:
                return "skeptical"

            return (
                session.personality
                or "skeptical"
            )

        finally:

            db.close()



    # ========================================================
    # ADD MESSAGE
    # ========================================================

    def add_message(
        self,
        session_id,
        role,
        content,
    ):

        db = SessionLocal()

        try:

            message = Message(
                id=str(uuid.uuid4()),
                session_id=session_id,
                role=role,
                content=content,
            )

            db.add(message)
            db.commit()

        finally:

            db.close()


    # ========================================================
    # GET MESSAGES
    # ========================================================

    def get_messages(
        self,
        session_id,
        limit=None,
    ):

        db = SessionLocal()

        try:

            query = (
                db.query(Message)
                .filter(
                    Message.session_id
                    == session_id
                )
                .order_by(
                    Message.created_at.desc()
                )
            )

            if limit:

                query = query.limit(
                    limit
                )

            messages = query.all()

            messages.reverse()

            return [
                {
                    "role": message.role,
                    "content": message.content,
                }
                for message in messages
            ]

        finally:

            db.close()


    # ========================================================
    # GET RECENT SESSIONS
    # ========================================================

    def get_recent_sessions(
        self,
        user_id, 
        client_name="KLM Fashion Mall",
        limit=20,
    ):

        db = SessionLocal()

        try:

            sessions = (
                db.query(SalesSession)
                .filter(
                    SalesSession.client_name== client_name,
                    SalesSession.user_id == user_id, 
                )
                .order_by(
                    SalesSession.started_at.desc()
                )
                .limit(limit)
                .all()
            )

            output = []

            for session in sessions:

                first_message = (
                    db.query(Message)
                    .filter(
                        Message.session_id
                        == session.id,

                        Message.role
                        == "user",
                    )
                    .order_by(
                        Message.created_at.asc()
                    )
                    .first()
                )

                if first_message:

                    title = (
                        first_message.content
                        .strip()
                    )

                    if len(title) > 55:

                        title = (
                            title[:55].rstrip()
                            + "..."
                        )

                else:

                    title = (
                        "New conversation"
                    )

                output.append({

                    "id":
                        session.id,

                    "client_name":
                        session.client_name,

                    "product_name":
                        session.product_name,

                    "personality":
                        session.personality
                        or "skeptical",

                    "title":
                        title,

                    "started_at":
                        session.started_at.isoformat(),

                    "status":
                        session.status,

                })

            return output

        finally:

            db.close()

    def get_active_sessions(
        self,
        user_id,
        client_name="KLM Fashion Mall",
        limit=50,
    ):

        db = SessionLocal()

        try:

            sessions = (
                db.query(SalesSession)
                .filter(
                    SalesSession.client_name ==client_name,
                    SalesSession.user_id == user_id,

                    SalesSession.status =="active",
                )
                .order_by(
                    SalesSession.started_at.desc()
                )
                .limit(limit)
                .all()
            )

            return [

                {
                    "id": session.id,

                    "client_name":
                        session.client_name,

                    "product_name":
                        session.product_name,

                    "personality":
                        session.personality,

                    "difficulty":
                        session.difficulty,

                    "focus_area":
                        session.focus_area,

                    "session_length":
                        session.session_length,

                    "started_at":
                        session.started_at.isoformat(),

                    "status":
                        session.status,

                    "mode": session.mode,
                }

                for session in sessions

            ]

        finally:

            db.close()
    

    # ========================================================
    # CREATE SESSION ANALYSIS
    # ========================================================

    def create_session_analysis(
        self,
        session_id,
        overall_score,
        analysis_json,
    ):

        db = SessionLocal()

        try:

            analysis = SessionAnalysis(
                id=str(uuid.uuid4()),
                session_id=session_id,
                overall_score=str(overall_score),
                analysis_json=analysis_json,
            )

            db.add(analysis)
            db.commit()

            return analysis.id

        finally:
            db.close()


    # ========================================================
    # GET SESSION ANALYSIS
    # ========================================================

    def get_session_analysis(
        self,
        session_id,
    ):

        db = SessionLocal()

        try:

            analysis = (
                db.query(SessionAnalysis)
                .filter(
                    SessionAnalysis.session_id == session_id
                )
                .first()
            )

            if not analysis:
                return None

            return {
                "id": analysis.id,
                "session_id": analysis.session_id,
                "overall_score": float(
                    analysis.overall_score
                ),
                "analysis_json": analysis.analysis_json,
                "created_at": (
                    analysis.created_at.isoformat()
                ),
            }

        finally:
            db.close()
    # ========================================================
# GET DASHBOARD DATA
# ========================================================

    def get_dashboard_data(
        self,
        user_id,
        client_name="KLM Fashion Mall",
    ):
        db = SessionLocal()

        try:

            # ------------------------------------------------
            # GET COMPLETED SESSIONS
            # ------------------------------------------------

            completed_sessions = (
                db.query(SalesSession)
                .filter(
                    SalesSession.client_name == client_name,
                    SalesSession.status == "completed",
                    SalesSession.user_id == user_id,
                )
                .order_by(
                    SalesSession.started_at.asc()
                )
                .all()
            )

            # ------------------------------------------------
            # GET ANALYZED SESSIONS
            # ------------------------------------------------

            analyzed_sessions = (
                db.query(
                    SalesSession,
                    SessionAnalysis,
                )
                .join(
                    SessionAnalysis,
                    SessionAnalysis.session_id
                    == SalesSession.id,
                )
                .filter(
                    SalesSession.client_name == client_name,
                    SalesSession.user_id == user_id,
                    SalesSession.status == "completed",
                )
                .order_by(
                    SalesSession.started_at.asc()
                )
                .all()
            )

            # ------------------------------------------------
            # NO ANALYSIS AVAILABLE
            # ------------------------------------------------

            if not analyzed_sessions:

                return {
                    "average_score": None,

                    "sessions_completed": len(
                        completed_sessions
                    ),

                    "best_score": None,

                    "score_progress": {
                        "labels": [],
                        "scores": [],
                    },

                    "skill_performance": {
                        "labels": [
                            "Product Knowledge",
                            "Needs Discovery",
                            "Objection Handling",
                            "Value Selling",
                            "Communication",
                            "Closing",
                        ],
                        "scores": [],
                    },
                }

            # ------------------------------------------------
            # SCORE PROGRESS
            # ------------------------------------------------

            score_progress_labels = []
            score_progress_scores = []

            scores = []

            for index, (
                session,
                analysis,
            ) in enumerate(
                analyzed_sessions,
                start=1,
            ):

                score = float(
                    analysis.overall_score
                )

                scores.append(score)

                score_progress_labels.append(
                    f"Session {index}"
                )

                score_progress_scores.append(
                    score
                )

            # ------------------------------------------------
            # DASHBOARD STATISTICS
            # ------------------------------------------------

            average_score = round(
                sum(scores) / len(scores),
                1,
            )

            best_score = round(
                max(scores),
                1,
            )

            # ------------------------------------------------
            # SKILL PERFORMANCE
            # AVERAGE OF LAST 6 ANALYZED SESSIONS
            # ------------------------------------------------

            recent_sessions = analyzed_sessions[-6:]

            skill_keys = [
                "product_knowledge",
                "needs_discovery",
                "objection_handling",
                "value_selling",
                "communication",
                "closing",
            ]

            skill_labels = [
                "Product Knowledge",
                "Needs Discovery",
                "Objection Handling",
                "Value Selling",
                "Communication",
                "Closing",
            ]

            skill_totals = {
                key: 0.0
                for key in skill_keys
            }

            skill_counts = {
                key: 0
                for key in skill_keys
            }

            # -----------------------------------------------
            # COLLECT SKILL SCORES
            # -----------------------------------------------

            for (
                session,
                analysis,
            ) in recent_sessions:

                try:

                    analysis_data = json.loads(
                        analysis.analysis_json
                    )

                except (
                    json.JSONDecodeError,
                    TypeError,
                ):

                    continue

                session_scores = (
                    analysis_data.get(
                        "scores",
                        {},
                    )
                )

                for key in skill_keys:

                    value = session_scores.get(
                        key
                    )

                    if value is not None:

                        skill_totals[key] += float(
                            value
                        )

                        skill_counts[key] += 1

            # -----------------------------------------------
            # CALCULATE AVERAGE FOR EACH SKILL
            # -----------------------------------------------

            skill_averages = []

            for key in skill_keys:

                if skill_counts[key] > 0:

                    average = (
                        skill_totals[key]
                        / skill_counts[key]
                    )

                else:

                    average = 0

                skill_averages.append(
                    round(
                        average,
                        1,
                    )
                )

            # -----------------------------------------------
            # FINAL SKILL PERFORMANCE
            # -----------------------------------------------

            skill_performance = {

                "labels": skill_labels,

                "scores": skill_averages,
            }

            # ------------------------------------------------
            # FINAL DASHBOARD DATA
            # ------------------------------------------------

            return {

                "average_score":
                    average_score,

                "sessions_completed":
                    len(completed_sessions),

                "best_score":
                    best_score,

                "score_progress": {

                    "labels":
                        score_progress_labels,

                    "scores":
                        score_progress_scores,
                },

                "skill_performance":
                    skill_performance,
            }

        finally:

            db.close()

    # ========================================================
    # GET HISTORY SESSIONS
    # ========================================================
    
    def get_history_sessions(
        self,
        user_id,
        client_name="KLM Fashion Mall",
    ):

        db = SessionLocal()

        try:

            sessions = (
                db.query(
                    SalesSession,
                    SessionAnalysis,
                )
                .outerjoin(
                    SessionAnalysis,
                    SessionAnalysis.session_id
                    == SalesSession.id,
                )
                .filter(
                    SalesSession.client_name == client_name,
                    SalesSession.user_id == user_id,
                    SalesSession.status == "completed",
                )
                .order_by(
                    SalesSession.started_at.desc()
                )
                .all()
            )

            history = []

            for session, analysis in sessions:

                history.append({
                    "id": session.id,
                    "product_name": session.product_name,
                    "personality": session.personality,
                    "difficulty": session.difficulty,
                    "focus_area": session.focus_area,
                    "session_length": session.session_length,
                    "started_at": session.started_at,
                    "ended_at": session.ended_at,

                    "analysis_status": (
                        "analysed"
                        if analysis
                        else "pending"
                    ),

                    "score": (
                        float(analysis.overall_score)
                        if analysis
                        else None
                    ),
                })

            return history

        finally:
            db.close()

    # ========================================================
# UPDATE TOPIC STATE
# ========================================================

    def update_topic_state(
        self,
        session_id,
        topic_state_json,
    ):

        db = SessionLocal()

        try:

            session = (
                db.query(SalesSession)
                .filter(SalesSession.id == session_id)
                .first()
            )

            if session:

                session.topic_state = topic_state_json

                db.commit()

        finally:

            db.close()

    # ========================================================
    # END SESSION
    # ========================================================

    def end_session(
        self,
        session_id,
    ):

        db = SessionLocal()

        try:

            session = (
                db.query(SalesSession)
                .filter(
                    SalesSession.id
                    == session_id
                )
                .first()
            )

            if session:

                session.status = (
                    "completed"
                )

                session.ended_at = (
                    datetime.utcnow()
                )

                db.commit()

        finally:

            db.close()
    