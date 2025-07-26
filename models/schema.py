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
    file_type = Column(String(10))  # PDF, DOCX, EMAIL
    processed_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default='pending')  # pending, processed, failed
    metadata = Column(Text)  # Store as JSON string for flexibility
    
    # Relationships
    clauses = relationship("Clause", back_populates="document", cascade="all, delete-orphan")

class Clause(Base):
    __tablename__ = "clauses"
    
    clause_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chromadb_id = Column(String(255), unique=True)  # ChromaDB vector ID for traceability
    doc_id = Column(UUID(as_uuid=True), ForeignKey('documents.doc_id', ondelete='CASCADE'), nullable=False)
    text = Column(Text, nullable=False)
    matched_clause_text = Column(Text)  # Immutable copy for explainability + evaluation reproducibility
    section_title = Column(Text)
    page_number = Column(Integer)
    char_position_start = Column(Integer)
    char_position_end = Column(Integer)
    clause_type = Column(String(50))  # coverage, exclusion, waiting_period, etc.
    domain_category = Column(String(20))  # insurance, legal, hr, compliance
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="clauses")
    query_results = relationship("QueryResult", back_populates="clause")

class QueryLog(Base):
    __tablename__ = "query_logs"
    
    query_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question = Column(Text, nullable=False)
    user_token = Column(String(255))  # For auth tracking
    processed_at = Column(DateTime, default=datetime.utcnow)
    response_time_ms = Column(Integer)  # Essential for latency evaluation
    total_tokens = Column(Integer)  # For token efficiency tracking
    status = Column(String(20), default="completed")  # For batch evaluation tracking
    
    # Relationships
    query_results = relationship("QueryResult", back_populates="query_log", cascade="all, delete-orphan")

class QueryResult(Base):
    __tablename__ = "query_results"
    
    result_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id = Column(UUID(as_uuid=True), ForeignKey('query_logs.query_id', ondelete='CASCADE'), nullable=False)
    clause_id = Column(UUID(as_uuid=True), ForeignKey('clauses.clause_id', ondelete='SET NULL'))
    similarity_score = Column(Numeric(precision=5, scale=4))  # 0.0000 to 1.0000
    extracted_answer = Column(Text)
    explanation = Column(Text)
    confidence_score = Column(Numeric(precision=5, scale=4))
    matched_clause_text = Column(Text)  # Immutable copy for reproducibility
    
    # Relationships
    query_log = relationship("QueryLog", back_populates="query_results")
    clause = relationship("Clause", back_populates="query_results")

class APICache(Base):
    __tablename__ = "api_cache"
    
    cache_key = Column(String(255), primary_key=True)
    cache_data = Column(Text)  # Store as JSON string
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)