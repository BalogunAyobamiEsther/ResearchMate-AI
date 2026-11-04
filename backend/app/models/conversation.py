from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


def get_current_utc_time():
    """Return the current UTC time."""
    return datetime.now(timezone.utc)


class Conversation(Base):
    """
    Database model for a research conversation.
    """

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(
        String(255),
        nullable=False,
        default="New Research"
    )

    created_at = Column(
        DateTime(timezone=True),
        default=get_current_utc_time,
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=get_current_utc_time,
        onupdate=get_current_utc_time,
        nullable=False
    )

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at"
    )


class Message(Base):
    """
    Database model for individual conversation messages.
    """

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)

    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    role = Column(
        String(20),
        nullable=False
    )

    content = Column(
        Text,
        nullable=False
    )

    citations = Column(
        JSON,
        nullable=True,
        default=list
    )

    evidence = Column(
        JSON,
        nullable=True,
        default=list
    )

    insufficient_evidence = Column(
        Boolean,
        nullable=False,
        default=False
    )

    created_at = Column(
        DateTime(timezone=True),
        default=get_current_utc_time,
        nullable=False
    )

    conversation = relationship(
        "Conversation",
        back_populates="messages"
    )