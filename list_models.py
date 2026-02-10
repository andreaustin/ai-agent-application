from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("API Key not found in .env")
else:
    client = genai.Client(api_key=api_key)
    print("Listing available models...")
    try:
        for model in client.models.list():
            print(f"- {model.name}")
    except Exception as e:
        print(f"Error: {e}")
