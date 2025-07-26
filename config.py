# configurations# config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Authentication
    AUTH_TOKEN = os.getenv("AUTH_TOKEN")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/query_system")
    
    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # ChromaDB
    CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
    
    # Server
    PORT = int(os.getenv("PORT", 8000))
    
    # Validation
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required_vars = ["AUTH_TOKEN", "DATABASE_URL"]
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Validate configuration on import
Config.validate()