# api/models.py
from pydantic import BaseModel
from typing import List, Optional, Union

class QueryRequest(BaseModel):
    documents: Union[str, List[str]]
    questions: List[str]

class AnswerResponse(BaseModel):
    question: str
    answer: str
    confidence: Optional[float] = 0.0
    source_clauses: Optional[List[str]] = []
    explanation: Optional[str] = ""

class QueryResponse(BaseModel):
    answers: List[AnswerResponse]