import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import string
import pickle
import os
import requests
import fitz
from sklearn.feature_extraction.text import TfidfVectorizer
from config import PERSISTENCE_FILE, PDF_URLS, CHUNK_SIZE, CHUNK_OVERLAP
from tqdm import tqdm
import re

# --- Download NLTK data (only need to do this once) ---
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

def preprocess(text):
    """Cleans, tokenizes, removes stop words, and lemmatizes text."""
    text = re.sub(r'\s+', ' ', text).strip()
    stop_words = set(stopwords.words('english'))
    punct = set(string.punctuation)
    lemmatizer = WordNetLemmatizer()
    tokens = word_tokenize(text.lower())
    filtered_tokens = [
        lemmatizer.lemmatize(word) for word in tokens
        if word.isalpha() and word not in stop_words and word not in punct
    ]
    return filtered_tokens

def download_and_extract_text(url):
    """Downloads a PDF from a URL and extracts its text content."""
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        with fitz.open(stream=response.content, filetype="pdf") as doc:
            text = "".join(page.get_text() for page in doc)
        return text
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return None
    except Exception as e:
        print(f"Error processing PDF from {url}: {e}")
        return None

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Simple text chunking."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks

def make_langchain_compatible(data):
    """Convert existing data format to work with LangChain"""
    # Add any necessary format conversions here
    data['langchain_compatible'] = True
    return data

def initialize_and_preprocess():
    """Enhanced to support LangChain integration"""
    if os.path.exists(PERSISTENCE_FILE):
        print("Loading pre-processed data from disk...")
        with open(PERSISTENCE_FILE, 'rb') as f:
            data = pickle.load(f)
        # Ensure backwards compatibility
        if 'langchain_compatible' not in data:
            print("Updating data format for LangChain compatibility...")
            data = make_langchain_compatible(data)
            # Optionally, save the updated format back to disk
            with open(PERSISTENCE_FILE, 'wb') as f:
                pickle.dump(data, f)
        return data

    print("No pre-processed data found. Starting one-time processing from PDF URLs...")
    documents = []
    chunked_documents = []
    chunk_id_counter = 0

    for url in tqdm(PDF_URLS, desc="Downloading & Parsing PDFs"):
        text = download_and_extract_text(url)
        if text:
            documents.append({'id': url, 'text': text})
            chunks = chunk_text(text)
            for chunk_text_content in chunks:
                chunked_documents.append({
                    'chunk_id': chunk_id_counter,
                    'source_doc_id': url,
                    'text': chunk_text_content
                })
                chunk_id_counter += 1

    if not documents:
        raise ValueError("No documents could be processed. Check URLs and network connection.")

    print("Processing chunked documents for TF-IDF (for cache retrieval)...")
    raw_texts = [doc['text'] for doc in chunked_documents]
    vectorizer = TfidfVectorizer(stop_words='english', lowercase=True, min_df=1)
    tfidf_matrix = vectorizer.fit_transform(raw_texts)

    data_to_persist = {
        "full_documents": documents,
        "chunked_documents": chunked_documents,
        "vectorizer": vectorizer,
        "tfidf_matrix_chunks": tfidf_matrix
    }
    # Add LangChain compatibility flag
    data_to_persist = make_langchain_compatible(data_to_persist)

    print(f"Processing complete. Saving to {PERSISTENCE_FILE}...")
    with open(PERSISTENCE_FILE, 'wb') as f:
        pickle.dump(data_to_persist, f)

    return data_to_persist