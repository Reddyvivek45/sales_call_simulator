import uuid
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

                "started_at":
                    session.started_at.isoformat(),

                "ended_at":
                    session.ended_at.isoformat()
                    if session.ended_at
                    else None,

                "status":
                    session.status,

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
        client_name="KLM Fashion Mall",
        limit=20,
    ):

        db = SessionLocal()

        try:

            sessions = (
                db.query(SalesSession)
                .filter(
                    SalesSession.client_name
                    == client_name
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
        client_name="KLM Fashion Mall",
        limit=50,
    ):

        db = SessionLocal()

        try:

            sessions = (
                db.query(SalesSession)
                .filter(
                    SalesSession.client_name ==
                    client_name,

                    SalesSession.status ==
                    "active",
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
                }

                for session in sessions

            ]

        finally:

            db.close()
    

# ========================================================
# CREATE SESSION ANALYSIS
# ========================================================

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
    