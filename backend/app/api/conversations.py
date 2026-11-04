from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.conversation import Conversation
from backend.app.schemas.conversation import (
    ConversationCreate,
    ConversationRename,
    ConversationResponse,
    ConversationListItem,
)
from backend.app.services.conversation_service import (
    create_conversation,
    get_all_conversations,
    get_conversation_by_id,
    delete_conversation,
    rename_conversation,
)


router = APIRouter()


@router.post(
    "/conversations",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Research History"]
)
def create_new_conversation(
    request: ConversationCreate,
    db: Session = Depends(get_db)
):
    return create_conversation(db=db, title=request.title)


@router.get(
    "/conversations",
    response_model=list[ConversationListItem],
    tags=["Research History"]
)
def list_conversations(db: Session = Depends(get_db)):
    return get_all_conversations(db=db)


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationResponse,
    tags=["Research History"]
)
def read_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    conversation = get_conversation_by_id(
        db=db,
        conversation_id=conversation_id
    )

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found."
        )

    return conversation


@router.patch(
    "/conversations/{conversation_id}",
    response_model=ConversationResponse,
    tags=["Research History"]
)
def update_conversation_title(
    conversation_id: int,
    request: ConversationRename,
    db: Session = Depends(get_db)
):
    conversation = rename_conversation(
        db=db,
        conversation_id=conversation_id,
        title=request.title
    )

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found."
        )

    return conversation


@router.delete(
    "/conversations/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Research History"]
)
def remove_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    deleted = delete_conversation(
        db=db,
        conversation_id=conversation_id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found."
        )

    return None