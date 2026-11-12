
import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.session import get_session_id, require_trusted_origin
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.services.rag_service import answer_research_question
from backend.app.services.conversation_service import (
    create_conversation,
    get_conversation_by_id,
    save_message,
)


logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/chat/query",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    tags=["Chat"],
    dependencies=[Depends(require_trusted_origin)],
)
def query_research_assistant(
    request: ChatRequest,
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id),
):
    """
    Submit a research question, generate an evidence-grounded answer,
    and save both messages to the session's Research History.
    """

    # Reuse an existing conversation or create a new one.
    if request.conversation_id is None:
        title = request.question.strip()[:60]

        if len(request.question.strip()) > 60:
            title += "..."

        conversation = create_conversation(
            db=db,
            title=title,
            owner_session_id=session_id,
        )

        conversation_id = conversation.id

    else:
        # Retrieve the conversation only if this session owns it.
        conversation = get_conversation_by_id(
            db=db,
            conversation_id=request.conversation_id,
            owner_session_id=session_id,
        )

        if conversation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found.",
            )

        conversation_id = conversation.id

    try:
        # Save the user's question.
        save_message(
            db=db,
            conversation_id=conversation_id,
            owner_session_id=session_id,
            role="user",
            content=request.question,
        )

        # Generate the answer using session-scoped RAG retrieval.
        result = answer_research_question(
            question=request.question,
            owner_session_id=session_id,
            top_k=request.top_k,
        )

        # Save the assistant's response and supporting information.
        save_message(
            db=db,
            conversation_id=conversation_id,
            owner_session_id=session_id,
            role="assistant",
            content=result["answer"],
            citations=result["citations"],
            evidence=result["evidence"],
            insufficient_evidence=result["insufficient_evidence"],
        )

        # Return the answer together with its conversation ID.
        result["conversation_id"] = conversation_id

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    except Exception as error:
        logger.exception("Research assistant query failed")

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The research assistant could not generate an answer.",
        ) from error
