"""OpenAI LLM service client."""
import json
import urllib.error
import urllib.request

from spendsense.config import settings


class LLMService:
    """
    Client for OpenAI API interactions.
    
    Usage:
        llm = LLMService()
        response = llm.ask("What category is this: Kroger grocery store?")
    """

    def __init__(self):
        self.api_key = settings.openai_api_key
        self.model = settings.OPENAI_MODEL
        self.base_url = settings.OPENAI_BASE_URL
        self.timeout = settings.OPENAI_TIMEOUT

    def ask(self, prompt: str, system_prompt: str | None = None) -> str:
        """
        Send a prompt to the LLM and return the response.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt (defaults to concise assistant)
        
        Returns:
            The model's response text
        
        Raises:
            RuntimeError: If the API call fails
        """
        if system_prompt is None:
            system_prompt = "Follow instructions exactly. Keep outputs concise."
        
        payload = {
            "model": self.model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": system_prompt},
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
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"OpenAI API error: {e.code}") from e
        except urllib.error.URLError as e:
            raise RuntimeError(f"Request failed: {e}") from e
