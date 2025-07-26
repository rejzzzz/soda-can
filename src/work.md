## Project Overview

The **Soda-Can** project is a Cache-Augmented Generation (CAG) system that implements an intelligent document retrieval and question-answering system. The system processes PDF documents, creates searchable indexes, and uses hybrid retrieval methods combined with Google's Gemini AI model to provide contextual answers to user queries.

## File Structure and Components

### Core Files

#### main.py
**Purpose**: Main entry point for the CAG application

**Key Functions**:
- Checks for cache existence and prompts user to build if missing
- Initializes the CAG engine
- Provides interactive command-line interface for user queries
- Handles graceful error management and user input validation

**Dependencies**: cag_engine.py, cache_builder.py

**Usage Flow**:
1. Verifies cache file exists or offers to build it
2. Initializes CAG engine with pre-processed data
3. Enters interactive loop for user questions
4. Processes queries and displays AI-generated answers

---

#### cag_engine.py
**Purpose**: Core orchestration engine that coordinates retrieval and response generation

**Key Components**:
- **CAGEngine Class**: Main engine class that manages the entire pipeline
- **retrieve_relevant_cache()**: Implements hybrid retrieval using LangChain ensemble methods
- **generate_answer()**: Coordinates retrieval and LLM response generation
- **_fallback_retrieval()**: Backup retrieval method for error scenarios

**Key Features**:
- Integrates hybrid retrieval (BM25 + TF-IDF)
- Maps chunk IDs to cache entries for efficient lookup
- Handles error scenarios with fallback mechanisms
- Coordinates between retrieval and LLM interface components

**Dependencies**: retriever.py, data_processor.py, cache_builder.py, llm_interface.py

---

#### retriever.py
**Purpose**: Implements sophisticated document retrieval using hybrid search methods

**Key Classes**:

**TFIDFRetriever (BaseRetriever)**:
- Custom LangChain-compatible retriever
- Uses existing TF-IDF vectorizer and matrix
- Implements cosine similarity scoring
- Returns top-k relevant documents based on query similarity

**CAGHybridRetriever**:
- Orchestrates ensemble retrieval combining BM25 and TF-IDF
- Converts processed data to LangChain document format
- Configurable weighting between retrieval methods (default: 60% BM25, 40% TF-IDF)
- Integrates with existing preprocessing pipeline

**Technical Implementation**:
- Uses scikit-learn for TF-IDF vectorization
- Leverages LangChain's BM25Retriever and EnsembleRetriever
- Maintains metadata including chunk IDs and source document IDs
- Supports configurable result limits and scoring thresholds

---

#### data_processor.py
**Purpose**: Handles document downloading, processing, and text preprocessing

**Key Functions**:

**preprocess(text)**:
- Tokenizes and cleans text using NLTK
- Removes stop words and punctuation
- Applies lemmatization for word normalization
- Returns processed token list

**download_and_extract_text(url)**:
- Downloads PDF files from provided URLs
- Uses PyMuPDF (fitz) for text extraction
- Implements robust error handling and timeouts
- Returns extracted text content

**chunk_text(text, chunk_size, overlap)**:
- Splits documents into overlapping chunks
- Configurable chunk size and overlap parameters
- Maintains context continuity across chunks

**initialize_and_preprocess()**:
- Main processing pipeline entry point
- Handles data persistence using pickle
- Creates TF-IDF vectorizer and document matrices
- Ensures LangChain compatibility
- Implements incremental processing with progress tracking

**Data Persistence**:
- Saves processed data to avoid recomputation
- Includes backwards compatibility checks
- Stores vectorizers, document chunks, and TF-IDF matrices

---

#### cache_builder.py
**Purpose**: Creates and manages pre-computed cache for faster retrieval

**Key Functions**:

**build_cache()**:
- Processes all document chunks into cache entries
- Creates searchable text snippets (limited to 500 characters)
- Stores chunk metadata including IDs and source references
- Saves cache data using pickle serialization

**load_cache()**:
- Loads pre-built cache from disk
- Handles missing cache files gracefully
- Returns cache data structure for engine consumption

**Cache Structure**:
Each cache entry contains:
- `chunk_id`: Unique identifier for the text chunk
- `source_doc_id`: Reference to original document
- `text_snippet`: Truncated text content for quick access

---

#### llm_interface.py
**Purpose**: Manages communication with Google's Gemini AI model

**Key Functions**:

**get_llm_response_with_cache(query, relevant_cache_entries, context_docs_snippets)**:
- Constructs prompts using retrieved cache entries
- Integrates additional context when available
- Handles API communication with error management
- Uses Gemini 2.5 Flash model with configurable thinking budget

**Prompt Engineering**:
- Structures prompts with clear sections for knowledge and context
- Separates pre-loaded knowledge from additional context
- Provides clear question-answer format
- Implements fallback responses for missing data

**Configuration**:
- Uses environment variables for API key management
- Configurable model parameters and thinking budget
- Robust error handling and response validation

---

#### config.py
**Purpose**: Centralized configuration management for the entire system

**Configuration Categories**:

**File Paths**:
- `PERSISTENCE_FILE`: Location for processed data storage
- `CACHE_FILE`: Location for cache data storage

**Document Sources**:
- `PDF_URLS`: List of PDF URLs to process (currently configured with policy documents)

**Model Configuration**:
- `LLM_MODEL_NAME`: Specifies Gemini 2.5 Flash model
- `GEMINI_API_KEY`: API key loaded from environment variables

**Processing Parameters**:
- `CHUNK_SIZE`: Text chunk size (512 words)
- `CHUNK_OVERLAP`: Overlap between chunks (100 words)
- `RETRIEVAL_METHOD`: Current retrieval strategy

**Hybrid Retrieval Settings**:
- `USE_LANGCHAIN_HYBRID`: Enable/disable hybrid retrieval
- `BM25_WEIGHT`: Weight for BM25 retrieval (0.7)
- `TFIDF_WEIGHT`: Weight for TF-IDF retrieval (0.3)
- `HYBRID_TOP_K`: Number of top results to return (5)

---

### Utility Files

#### docProcess.py
**Purpose**: Specialized document processing utilities for arXiv papers

**Key Functions**:

**get_arxiv_paper_content(search_query, max_results)**:
- Fetches arXiv papers using their API
- Extracts metadata and PDF links
- Supports batch processing of multiple papers

**extract_pdf_content(pdf_url)**:
- Downloads and processes arXiv PDFs
- Handles URL formatting for arXiv links
- Implements robust PDF text extraction

**clean_pdf_text(text)**:
- Removes common PDF artifacts
- Handles page numbers and formatting issues
- Cleans arXiv-specific formatting

**save_to_json(data, filename)**:
- Exports processed papers to JSON format
- Includes timestamp-based naming
- Maintains UTF-8 encoding for international content

---

## System Architecture

### Data Flow

1. **Document Ingestion**: PDF documents are downloaded from configured URLs
2. **Text Processing**: Documents are chunked, cleaned, and vectorized
3. **Cache Generation**: Pre-computed cache entries are created for fast retrieval
4. **Query Processing**: User queries trigger hybrid retrieval combining BM25 and TF-IDF
5. **Response Generation**: Retrieved context is sent to Gemini AI for answer generation

### Key Design Patterns

**Hybrid Retrieval**: Combines statistical (TF-IDF) and probabilistic (BM25) methods for improved relevance

**Cache-Augmented Generation**: Pre-processes documents to reduce real-time computation overhead

**Modular Architecture**: Separates concerns into distinct modules for maintainability

**LangChain Integration**: Leverages LangChain framework for standardized retrieval interfaces

**Configuration Management**: Centralized configuration allows easy system tuning

### Dependencies

**Core Libraries**:
- `langchain-community`: Document retrieval and processing
- `scikit-learn`: TF-IDF vectorization and similarity calculations
- `google.genai`: Gemini AI model interface
- `nltk`: Natural language processing and text preprocessing
- `PyMuPDF (fitz)`: PDF text extraction
- `requests`: HTTP requests for document downloading

**Development Tools**:
- `tqdm`: Progress tracking for long-running operations
- `pickle`: Data serialization and persistence
- `python-dotenv`: Environment variable management

### Error Handling

The system implements comprehensive error handling:
- Network timeouts for PDF downloads
- Missing cache file detection and recovery
- API communication error management
- Graceful degradation with fallback methods
- User input validation and sanitization

### Performance Considerations

- **Caching Strategy**: Pre-computed cache reduces query response time
- **Incremental Processing**: Avoids reprocessing existing data
- **Chunking Optimization**: Balances context preservation with processing efficiency
- **Hybrid Retrieval**: Improves relevance while maintaining speed
- **Memory Management**: Uses disk persistence for large datasets

This documentation provides a comprehensive overview of the Soda-Can project's architecture, components, and functionality. Each module is designed with specific responsibilities while maintaining clear interfaces for integration and extensibility.