# services/db_service.py
from models.database import get_db
from models.schemas import Document, Clause, QueryLog, QueryResult, APICache
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
import uuid
import json

class AsyncDatabaseService:
    @staticmethod
    async def create_document(db: AsyncSession, url: str, file_type: str = None, metadata: dict = None):
        """Create a new document record"""
        document = Document(
            url=url,
            file_type=file_type,
            metadata=json.dumps(metadata) if metadata else None,
            status='pending'
        )
        db.add(document)
        await db.commit()
        await db.refresh(document)
        return document

    @staticmethod
    async def update_document_status(db: Session, doc_id: str, status: str):
        """Update document processing status"""
        document = db.query(Document).filter(Document.doc_id == doc_id).first()
        if document:
            document.status = status
            document.processed_at = datetime.utcnow()
            db.commit()
            db.refresh(document)
        return document

    @staticmethod
    async def create_clause(db: Session, clause_data: dict):
        """Create a new clause record"""
        clause = Clause(**clause_data)
        db.add(clause)
        db.commit()
        db.refresh(clause)
        return clause

    @staticmethod
    async def log_query(db: Session, question: str, token: str, response_time: int = None, tokens_used: int = None):
        """Log a query for evaluation"""
        query_log = QueryLog(
            question=question,
            user_token=token,
            response_time_ms=response_time,
            total_tokens=tokens_used,
            processed_at=datetime.utcnow()
        )
        db.add(query_log)
        db.commit()
        db.refresh(query_log)
        return query_log

    @staticmethod
    async def log_query_result(db: Session, query_id: str, clause_id: str = None, 
                             similarity: float = None, answer: str = None, 
                             explanation: str = None, confidence: float = None,
                             matched_text: str = None):
        """Log query result for evaluation"""
        query_result = QueryResult(
            query_id=query_id,
            clause_id=clause_id,
            similarity_score=similarity,
            extracted_answer=answer,
            explanation=explanation,
            confidence_score=confidence,
            matched_clause_text=matched_text
        )
        db.add(query_result)
        db.commit()
        db.refresh(query_result)
        return query_result

    @staticmethod
    async def get_cached_result(db: Session, cache_key: str):
        """Get cached result if not expired"""
        cache_entry = db.query(APICache).filter(APICache.cache_key == cache_key).first()
        if cache_entry and datetime.utcnow() < cache_entry.expires_at:
            return json.loads(cache_entry.cache_data)
        return None

    @staticmethod
    async def set_cached_result(db: Session, cache_key: str, data: dict, ttl_seconds: int = 3600):
        """Set cached result with TTL"""
        expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        
        # Try to update existing cache
        cache_entry = db.query(APICache).filter(APICache.cache_key == cache_key).first()
        if cache_entry:
            cache_entry.cache_data = json.dumps(data)
            cache_entry.expires_at = expires_at
        else:
            # Create new cache entry
            cache_entry = APICache(
                cache_key=cache_key,
                cache_data=json.dumps(data),
                expires_at=expires_at
            )
            db.add(cache_entry)
        
        db.commit()
        return cache_entry

    @staticmethod
    async def get_document_clauses(db: Session, doc_id: str):
        """Get all clauses for a document"""
        return db.query(Clause).filter(Clause.doc_id == doc_id).all()

    @staticmethod
    async def get_recent_queries(db: Session, limit: int = 100):
        """Get recent query logs for monitoring"""
        return db.query(QueryLog).order_by(desc(QueryLog.processed_at)).limit(limit).all()