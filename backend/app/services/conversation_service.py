from sqlalchemy.orm import Session

from backend.app.models.conversation import (
    Conversation,
    Message,
    get_current_utc_time
)

def create_conversation(
    db: Session,
    title: str = "New Research"
) -> Conversation:
    """
    Create and save a new research conversation.
    """

    conversation = Conversation(
        title=title
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


def get_all_conversations(
    db: Session
) -> list[Conversation]:
    """
    Retrieve all research conversations,
    ordered by most recently updated.
    """

    return (
        db.query(Conversation)
        .order_by(Conversation.updated_at.desc())
        .all()
    )

def get_conversation_by_id(
    db: Session,
    conversation_id: int
) -> Conversation | None:
    """
    Retrieve a conversation and all its messages
    using its unique ID.
    """

    return (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )

def save_message(
    db: Session,
    conversation_id: int,
    role: str,
    content: str,
    citations: list | None = None,
    evidence: list | None = None,
    insufficient_evidence: bool = False
) -> Message:
    """
    Save a user question or AI response
    to an existing conversation.
    """

    if role not in ["user", "assistant"]:
        raise ValueError("Message role must be user or assistant.")

    conversation = get_conversation_by_id(
        db=db,
        conversation_id=conversation_id
    )

    if conversation is None:
        raise ValueError("Conversation not found.")

    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        citations=citations or [],
        evidence=evidence or [],
        insufficient_evidence=insufficient_evidence
    )

    db.add(message)

    # Update the conversation's last activity time
    conversation.updated_at = get_current_utc_time()

    db.commit()
    db.refresh(message)

    return message

def rename_conversation(
    db: Session,
    conversation_id: int,
    title: str
) -> Conversation | None:
    """
    Rename an existing research conversation.
    """

    conversation = get_conversation_by_id(
        db=db,
        conversation_id=conversation_id
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
    conversation_id: int
) -> bool:
    """
    Delete a research conversation and its messages.
    """

    conversation = get_conversation_by_id(
        db=db,
        conversation_id=conversation_id
    )

    if conversation is None:
        return False

    db.delete(conversation)
    db.commit()

    return True
