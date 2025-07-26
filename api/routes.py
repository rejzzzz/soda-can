# api/routes.py
from fastapi import APIRouter, Header, HTTPException, Depends
from api.models import QueryRequest, QueryResponse
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

router = APIRouter()

# Load token from environment
EXPECTED_TOKEN = os.getenv("AUTH_TOKEN")

# Validate that token is set
if not EXPECTED_TOKEN:
    raise ValueError("AUTH_TOKEN not found in environment variables")

def verify_auth_token(authorization: str = Header(None)):
    """Dependency to verify authorization token from environment"""
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header is missing"
        )
    
    # Check if token format is correct (Bearer <token>)
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization format. Use: Bearer <token>"
        )
    
    # Extract token
    token = authorization.split("Bearer ", 1)[1].strip()
    
    # Verify token against environment variable
    if token != EXPECTED_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization token"
        )
    
    return token

@router.post("/hackrx/run", response_model=QueryResponse)
async def process_hackrx_query(
    request: QueryRequest, 
    authorization: str = Depends(verify_auth_token)
):
    """
    Main endpoint for hackathon evaluation
    Expected format:
    POST /api/v1/hackrx/run
    Authorization: Bearer <token_from_env>
    """
    start_time = time.perf_counter()
    
    try:
        # Validate request format
        validate_request_format(request)
        
        # TODO: Integrate with ML processing pipeline
        # This is where you'll call your document processing and query answering logic
        # response = await process_documents_and_queries(request.documents, request.questions)
        
        # Placeholder response - replace with actual processing
        response = QueryResponse(answers=[])
        
        # Log processing time
        end_time = time.perf_counter()
        processing_time_ms = int((end_time - start_time) * 1000)
        
        # TODO: Log to database
        # await log_query_processing(request, response, processing_time_ms)
        
        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

def validate_request_format(request: QueryRequest):
    """Validate request format matches hackathon requirements"""
    # Handle both string and list for documents
    documents = request.documents
    if isinstance(documents, str):
        documents = [documents]
    
    # Validate document URLs
    for doc_url in documents:
        if not isinstance(doc_url, str):
            raise ValueError("Document URLs must be strings")
        if not doc_url.startswith(("http://", "https://")):
            raise ValueError(f"Invalid document URL: {doc_url}")
    
    # Validate questions
    if not isinstance(request.questions, list):
        raise ValueError("Questions must be a list")
    
    if not request.questions:
        raise ValueError("Questions list cannot be empty")
    
    for question in request.questions:
        if not isinstance(question, str) or not question.strip():
            raise ValueError("All questions must be non-empty strings")

# Keep your existing endpoint for testing (optional)
@router.post("/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    authorization: str = Depends(verify_auth_token)
):
    """Legacy endpoint - same functionality as /hackrx/run"""
    return await process_hackrx_query(request, authorization)