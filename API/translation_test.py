import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ("GOOGLE_TRANSLATE_API_KEY")

query = {
    "q": input("text to translate: "),
    "target": input("Enter target language (en,es,pt): "),
    "format": "text"
}

response = requests.post("https://translation.googleapis.com/language/translate/v2", params={"key": api_key}, json=query, timeout=10)

print(response.status_code)
print(response.json()["data"]["translations"][0]["translatedText"])
