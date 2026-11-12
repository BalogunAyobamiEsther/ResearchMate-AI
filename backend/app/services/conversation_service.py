
from sqlalchemy.orm import Session

from backend.app.models.conversation import (
    Conversation,
    Message,
    get_current_utc_time,
)


def create_conversation(
    db: Session,
    owner_session_id: str,
    title: str = "New Research",
) -> Conversation:
    """
    Create a conversation owned by a specific browser session.
    """

    conversation = Conversation(
        title=title,
        owner_session_id=owner_session_id,
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


def get_all_conversations(
    db: Session,
    owner_session_id: str,
) -> list[Conversation]:
    """
    Retrieve only conversations belonging to a browser session,
    ordered by most recently updated.
    """

    return (
        db.query(Conversation)
        .filter(Conversation.owner_session_id == owner_session_id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )


def get_conversation_by_id(
    db: Session,
    conversation_id: int,
    owner_session_id: str,
) -> Conversation | None:
    """
    Retrieve a conversation only if it belongs to the given session.
    """

    return (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.owner_session_id == owner_session_id,
        )
        .first()
    )


def save_message(
    db: Session,
    conversation_id: int,
    owner_session_id: str,
    role: str,
    content: str,
    citations: list | None = None,
    evidence: list | None = None,
    insufficient_evidence: bool = False,
) -> Message:
    """
    Save a message only to a conversation owned by the given session.
    """

    if role not in ["user", "assistant"]:
        raise ValueError("Message role must be user or assistant.")

    conversation = get_conversation_by_id(
        db=db,
        conversation_id=conversation_id,
        owner_session_id=owner_session_id,
    )

    if conversation is None:
        raise ValueError("Conversation not found.")

    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        citations=citations or [],
        evidence=evidence or [],
        insufficient_evidence=insufficient_evidence,
    )

    db.add(message)

    # Update the conversation's last activity time.
    conversation.updated_at = get_current_utc_time()

    db.commit()
    db.refresh(message)

    return message


def rename_conversation(
    db: Session,
    conversation_id: int,
    owner_session_id: str,
    title: str,
) -> Conversation | None:
    """
    Rename a conversation only if it belongs to the given session.
    """

    conversation = get_conversation_by_id(
        db=db,
        conversation_id=conversation_id,
        owner_session_id=owner_session_id,
    )

    if conversation is None:
        return None

    conversation.title = title.strip()
    conversation.updated_at = get_current_utc_time()

    db.commit()
    db.refresh(conversation)

    return conversation


def delete_conversation(
    db: Session,
    conversation_id: int,
    owner_session_id: str,
) -> bool:
    """
    Delete a conversation only if it belongs to the given session.
    """

    conversation = get_conversation_by_id(
        db=db,
        conversation_id=conversation_id,
        owner_session_id=owner_session_id,
    )

    if conversation is None:
        return False

    db.delete(conversation)
    db.commit()

    return True
