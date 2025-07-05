import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ OPENAI_API_KEY not found!")
    exit(1)

print(f"Loaded OPENAI_API_KEY: {api_key[:4]}...{api_key[-4:]}")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

try:
    resp = requests.get("https://api.openai.com/v1/models", headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    print("✅ API key is valid. Models available:")
    for model in data.get("data", [])[:5]:
        print("-", model.get("id"))
except Exception as e:
    print(f"❌ API request failed: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print("Response:", e.response.text) 