from fastapi import APIRouter, HTTPException, status

from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.services.rag_service import answer_research_question


router = APIRouter()


@router.post(
    "/chat/query",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    tags=["Chat"]
)
def query_research_assistant(request: ChatRequest):
    """
    Submit a research question and receive an evidence-grounded answer.
    """
    try:
        result = answer_research_question(
            question=request.question,
            top_k=request.top_k
        )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The research assistant could not generate an answer."
        ) from error