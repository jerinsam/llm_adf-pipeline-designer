import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    
    USE_PERPLEXITY = os.getenv('USE_PERPLEXITY', 'false').lower() == 'true'
    PERPLEXITY_URL = os.getenv('PERPLEXITY_URL', 'https://api.perplexity.ai/chat/completions')
    PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
    PERPLEXITY_MODEL = os.getenv('PERPLEXITY_MODEL', 'sonar-pro')

    # USE_OLLAMA = os.getenv('USE_OLLAMA', 'false').lower() == 'true'
    # OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434/api/generate')
    # OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'mistral')