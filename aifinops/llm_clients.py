import os
from typing import Literal, Optional

import httpx

Provider = Literal["xai", "openai", "gemini", "anthropic"]

class LLMClient:
    def __init__(self, provider: Provider):
        self.provider = provider

    async def _post_json(self, url: str, headers: dict, payload: dict) -> str:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            # NOTE: This will vary per provider; keep generic & simple
            # You should adjust once you wire real providers.
            if "choices" in data:
                # OpenAI-style
                return data["choices"][0].get("message", {}).get("content", "")
            if "output_text" in data:
                # Gemini-style (example)
                return data["output_text"]
            if "content" in data and isinstance(data["content"], str):
                return data["content"]
            return str(data)

    async def chat(self, prompt: str, system: Optional[str] = None) -> str:
        if self.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return "[OPENAI_API_KEY missing – cannot call API]"
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}"}
            payload = {
                "model": os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
                "messages": [
                    {"role": "system", "content": system or ""},
                    {"role": "user", "content": prompt},
                ],
            }
            return await self._post_json(url, headers, payload)

        if self.provider == "xai":
            api_key = os.getenv("XAI_API_KEY")
            if not api_key:
                return "[XAI_API_KEY missing – cannot call API]"
            url = "https://api.x.ai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}"}
            payload = {
                "model": os.getenv("XAI_MODEL", "grok-2-latest"),
                "messages": [
                    {"role": "system", "content": system or ""},
                    {"role": "user", "content": prompt},
                ],
            }
            return await self._post_json(url, headers, payload)

        if self.provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                return "[GEMINI_API_KEY missing – cannot call API]"
            # Placeholder; real Gemini endpoint differs
            url = (
                "https://generativelanguage.googleapis.com/v1beta/models/"
                "gemini-1.5-flash:generateContent?key=" + api_key
            )
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [
                    {"parts": [{"text": (system or "") + "\n" + prompt}]}
                ],
            }
            return await self._post_json(url, headers, payload)

        if self.provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                return "[ANTHROPIC_API_KEY missing – cannot call API]"
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            }
            payload = {
                "model": os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}],
                "system": system or "",
            }
            return await self._post_json(url, headers, payload)

        return "[Unknown provider – set LLM_PROVIDER to xai/openai/gemini/anthropic]"
