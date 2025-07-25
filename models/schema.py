# models/schemas.py
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from models.database import Base
from datetime import datetime
import uuid

class Document(Base):
    __tablename__ = "documents"
    
    doc_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(Text, nullable=False, unique=True)
    file_type = Column(String(10))
    processed_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default='pending')
    metadata = Column(String)  # Using String instead of JSONB for simplicity
    
    clauses = relationship("Clause", back_populates="document")

class Clause(Base):
    __tablename__ = "clauses"
    
    clause_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doc_id = Column(UUID(as_uuid=True), ForeignKey('documents.doc_id', ondelete='CASCADE'), nullable=False)
    text = Column(Text, nullable=False)
    section_title = Column(Text)
    page_number = Column(Integer)
    char_position_start = Column(Integer)
    char_position_end = Column(Integer)
    clause_type = Column(String(50))
    domain_category = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    document = relationship("Document", back_populates="clauses")
    # Note: Remove embedding relationship if not using pgvector

class QueryLog(Base):
    __tablename__ = "query_logs"
    
    query_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question = Column(Text, nullable=False)
    user_token = Column(String(255))
    processed_at = Column(DateTime, default=datetime.utcnow)
    response_time_ms = Column(Integer)
    total_tokens = Column(Integer)

class QueryResult(Base):
    __tablename__ = "query_results"
    
    result_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id = Column(UUID(as_uuid=True), ForeignKey('query_logs.query_id', ondelete='CASCADE'), nullable=False)
    clause_id = Column(UUID(as_uuid=True), ForeignKey('clauses.clause_id', ondelete='SET NULL'))
    similarity_score = Column(Numeric(precision=5, scale=4))
    extracted_answer = Column(Text)
    explanation = Column(Text)
    confidence_score = Column(Numeric(precision=5, scale=4))

class APICache(Base):
    __tablename__ = "api_cache"
    
    cache_key = Column(String(255), primary_key=True)
    cache_data = Column(Text)  # Store as JSON string
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)