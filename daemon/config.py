import os

API_TOKEN = os.getenv("API_TOKEN")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "t", "yes", "y", "1")
