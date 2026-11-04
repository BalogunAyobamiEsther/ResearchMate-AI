from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=2000
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=10
    )
    conversation_id: int | None = Field(
        default=None,
        ge=1
    )


class Citation(BaseModel):
    source_id: str
    document_id: str
    filename: str
    page_number: int


class Evidence(BaseModel):
    source_id: str
    chunk_id: str
    document_id: str
    filename: str
    page_number: int
    text: str


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    evidence: list[Evidence]
    insufficient_evidence: bool
    conversation_id: int | None = None


class LLMResponse(BaseModel):
    answer: str
    insufficient_evidence: bool