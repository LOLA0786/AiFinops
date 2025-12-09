from __future__ import annotations

import httpx
import os
from typing import Optional, Dict, Any, Generator

class LLMClient:
    """
    Universal LLM client with OpenAI streaming support.
    """

    def __init__(self, provider: str):
        self.provider = provider

        # OpenAI
        self.openai_url = "https://api.openai.com/v1/chat/completions"
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

        # xAI (fallback)
        self.xai_url = "https://api.x.ai/v1/completions"
        self.xai_key = os.getenv("XAI_API_KEY")
        self.xai_model = os.getenv("XAI_MODEL", "grok-2-latest")

        # Claude (optional)
        self.claude_key = os.getenv("ANTHROPIC_API_KEY")
        self.claude_model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

        # Gemini
        self.gemini_key = os.getenv("GEMINI_API_KEY")

    async def chat(self, user_prompt: str, system: Optional[str] = None) -> str:
        if self.provider == "openai":
            return await self._chat_openai(user_prompt, system)
        if self.provider == "xai":
            return await self._chat_xai(user_prompt, system)
        if self.provider == "anthropic":
            return await self._chat_claude(user_prompt, system)
        raise ValueError(f"Unknown provider: {self.provider}")

    async def _post_json(self, url: str, headers: Dict[str, str], data: Dict[str, Any]) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, json=data, headers=headers)
            resp.raise_for_status()
            return resp.json()

    #
    # OpenAI chat (non-stream)
    #
    async def _chat_openai(self, user_prompt: str, system: Optional[str]):
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json",
        }
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": user_prompt})
        payload = {
            "model": self.openai_model,
            "messages": messages,
            "temperature": 0.3,
        }
        js = await self._post_json(self.openai_url, headers, payload)
        return js["choices"][0]["message"]["content"]

    #
    # OpenAI streaming (generator) - synchronous generator using httpx streaming
    #
    def stream_openai_chat(self, user_prompt: str, system: Optional[str] = None) -> Generator[str, None, None]:
        """
        Yields incremental text chunks from the OpenAI streaming API.
        Use in synchronous code (Streamlit) like:
          for chunk in client.stream_openai_chat(prompt, system): ...
        """
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json",
        }
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": user_prompt})
        payload = {
            "model": self.openai_model,
            "messages": messages,
            "temperature": 0.3,
            "stream": True
        }

        # Use httpx synchronous client streaming
        with httpx.Client(timeout=120.0) as client:
            with client.stream("POST", self.openai_url, json=payload, headers=headers) as resp:
                if resp.status_code >= 400:
                    text = resp.text
                    yield f"[ERROR] {text}"
                    return
                # OpenAI streams lines starting with "data: "
                for line in resp.iter_lines():
                    if not line:
                        continue
                    try:
                        s = line.decode("utf-8") if isinstance(line, bytes) else str(line)
                    except Exception:
                        s = str(line)
                    if s.startswith("data: "):
                        data = s[len("data: "):].strip()
                        if data == "[DONE]":
                            break
                        try:
                            import json
                            js = json.loads(data)
                            # choices -> delta -> content
                            delta = js.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content")
                            if content:
                                yield content
                        except Exception:
                            # non-json chunk
                            yield s
                    else:
                        # fallback: yield raw
                        yield s

    #
    # xAI simple completions fallback
    #
    async def _chat_xai(self, user_prompt: str, system: Optional[str]):
        headers = {"Authorization": f"Bearer {self.xai_key}", "Content-Type": "application/json"}
        full_prompt = (f"System: {system}\n\n" if system else "") + f"User: {user_prompt}"
        payload = {"model": self.xai_model, "prompt": full_prompt, "temperature": 0.3}
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(self.xai_url, json=payload, headers=headers)
            resp.raise_for_status()
            js = resp.json()
            return js.get("text", str(js))

    #
    # Claude (placeholder)
    #
    async def _chat_claude(self, user_prompt: str, system: Optional[str]):
        raise NotImplementedError("Claude support not implemented in this client.")
