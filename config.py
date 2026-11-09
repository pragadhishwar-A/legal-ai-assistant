# config.py
# Central place for all configurable settings, loaded from .env

import os
from dotenv import load_dotenv

load_dotenv()  # reads the .env file into the environment

LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "10"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))
RETRIEVAL_K = int(os.getenv("RETRIEVAL_K", "4"))