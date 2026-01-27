import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("API_TOKEN")
if not token:
    raise RuntimeError("API_TOKEN is not set in environment/.env")

class Headers:
    basic = {"app-id": token}
