import os
import requests
from dotenv import load_dotenv
from pathlib import Path

KEY_FILE = Path(__file__).resolve().parent / "key.env"
load_dotenv(KEY_FILE)

api_key = os.getenv("GOOGLE_TRANSLATE_API_KEY")
if api_key is None:
    print(f"Warning: key not found")

URL = "https://translation.googleapis.com/language/translate/v2"


def translate(text, target, source=None):
    text  = text.strip()

    if text == "":
        print("No text was provided")
        return None

    query = {
    "q": text,
    "target": target,
    "format": "text"
    }   

    if source is not None:
        query["source"] = source

    try:
        response = requests.post(URL, params={"key": api_key}, json=query, timeout=10)
    except requests.RequestException as error:      # no internet, timeout, etc.
        print(f"Translate: request failed: {error}")
        return None

    if response.status_code != 200:
        print(f"Google returned {response.status_code}: {response.text}")
        return None

    return response.json()["data"]["translations"][0]["translatedText"]


if __name__ == "__main__":

    print(translate("Hola, ¿cómo estás?", "fr", "es"))

