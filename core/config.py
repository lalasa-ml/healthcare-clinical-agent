import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Settings:
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_SEARCH_SERVICE_ENDPOINT: str = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT", "")
    AZURE_SEARCH_API_KEY: str = os.getenv("AZURE_SEARCH_API_KEY", "")
    AZURE_AI_PROJECT_CONNECTION_STRING: str = os.getenv("AZURE_AI_PROJECT_CONNECTION_STRING", "")
    AZURE_OPENAI_DEPLOYMENT_NAME: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1-mini")

settings = Settings()