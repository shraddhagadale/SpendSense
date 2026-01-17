import json
from pathlib import Path
import urllib.error
import urllib.request


class LLMAssistant:

    def __init__(self):
        key_path = Path(__file__).resolve().parent / "secrets" / "openai_api_key.txt"
        if not key_path.exists():
            raise RuntimeError("Missing OpenAI API key. Put it in secrets/openai_api_key.txt")
        self.api_key = key_path.read_text(encoding="utf-8").strip()
        self.model = "gpt-4o-mini"
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def ask(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": "Follow instructions exactly. Keep outputs concise."},
                {"role": "user", "content": prompt},
            ],
        }

        req = urllib.request.Request(
            self.base_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"OpenAI API error: {e.code}") from e
        except urllib.error.URLError as e:
            raise RuntimeError(f"Request failed: {e}") from e


if __name__ == "__main__":
    assistant = LLMAssistant()
    categories = ["Grocery","Food", "Transport", "Entertainment", 
    "Digital Services","Rent", "Utilities", "Shopping","Health","Others"]
    prompt = (
        "You are a finance expert in categorizing expenses.\n"
        "Given a transaction description and amount, select exactly ONE category from this list:\n"
        f"{categories}\n\n"
        "Return only the category name (exactly as written in the list).\n\n"
        "Description: Uber ride\n"
        "Amount: 12.50\n"
        "Category:"
    )
    print(assistant.ask(prompt))
