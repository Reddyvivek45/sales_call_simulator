from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey,
)

from sqlalchemy.orm import declarative_base


Base = declarative_base()


class SalesSession(Base):

    __tablename__ = "sales_sessions"

    id = Column(
        String(36),
        primary_key=True
    )

    client_name = Column(
        String(255),
        nullable=False
    )

    product_name = Column(
        String(255),
        nullable=False
    )

    personality = Column(
        String(200),
        nullable=False
    )

    difficulty = Column(
        String(50),
        nullable=False
    )

    focus_area = Column(
        String(100),
        nullable=True
    )

    session_length = Column(
        String(20),
        nullable=False,
        default="quick"
    )

    started_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    ended_at = Column(
        DateTime,
        nullable=True
    )

    status = Column(
        String(50),
        default="active",
        nullable=False
    )


class Message(Base):

    __tablename__ = "messages"

    id = Column(
        String(36),
        primary_key=True,
    )

    session_id = Column(
        String(36),
        ForeignKey(
            "sales_sessions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    role = Column(
        String(20),
        nullable=False,
    )

    content = Column(
        Text,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


# ============================================================
# SESSION ANALYSIS
# ============================================================

class SessionAnalysis(Base):

    __tablename__ = "session_analysis"

    id = Column(
        String(36),
        primary_key=True,
    )

    session_id = Column(
        String(36),
        ForeignKey(
            "sales_sessions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
    )

    overall_score = Column(
        String(10),
        nullable=False,
    )

    analysis_json = Column(
        Text,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )