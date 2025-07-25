from fastapi import APIRouter
from api.models import QueryRequest, QueryResponse

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    # Placeholder - will integrate with ML components
    return QueryResponse(answers=[])