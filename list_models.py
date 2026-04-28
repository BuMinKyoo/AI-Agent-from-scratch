import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

print(f"{'Model Name':<50} | Supported Actions")
print("-" * 90)
for m in client.models.list():
    print(f"{m.name:<50} | {m.supported_actions}")
