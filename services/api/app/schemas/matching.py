from enum import Enum

from pydantic import BaseModel


class MatchStatus(str, Enum):
    EXACT_MATCH = "EXACT_MATCH"
    HARMLESS_VARIANT = "HARMLESS_VARIANT"
    CONFLICT = "CONFLICT"


class DocumentMatchResult(BaseModel):
    left_document_id: str
    right_document_id: str
    field_name: str
    similarity: float | None = None
    match_status: MatchStatus
    reasoning: str