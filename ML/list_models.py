import os
from google import genai
from dotenv import load_dotenv

backend_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Backend API', '.env')
load_dotenv(backend_env_path)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
for model in client.models.list():
    if "flash" in model.name:
        print(model.name)
