"""
Helper: aapki API key par kaunse Gemini models available hain, wo dikhata hai.

    python list_models.py

Kaam ka tab hota hai jab "404 model not found" error aaye -- Google purane
models ko retire kar deta hai, to yahan se naya naam uthakar src/config.py
me daal do.
"""

from google import genai

from src.config import get_api_key


def main() -> None:
    client = genai.Client(api_key=get_api_key())
    models = list(client.models.list())

    print("=== EMBEDDING models (embedContent) ===")
    for m in models:
        if "embedContent" in (getattr(m, "supported_actions", None) or []):
            print("  ", m.name)

    print("\n=== CHAT models (generateContent) ===")
    for m in models:
        if "generateContent" in (getattr(m, "supported_actions", None) or []):
            print("  ", m.name)


if __name__ == "__main__":
    main()
