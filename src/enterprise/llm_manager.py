import os
import json
import requests
from pathlib import Path
from typing import Optional

DEFAULT_MODELS = Path(__file__).parents[1] / '..' / 'config' / 'models.json.example'

class LLMManager:
    """Unified LLM manager with adapters for deepseek, anthropic, openai and a mock fallback.

    Configuration via environment variables:
      - LLM_PROVIDER: 'deepseek' | 'anthropic' | 'openai' | 'local' (default: deepseek)
      - LLM_API_KEY: provider API key
      - DEEPSEEK_API_BASE: base URL for DeepSeek API (default: https://api.deepseek.example/v1/generate)
      - OPENAI_API_BASE / ANTHROPIC_API_BASE: optional custom endpoints

    The manager will return mock responses when no API key is provided to keep endpoints usable in dev.
    """

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = Path(config_path) if config_path else DEFAULT_MODELS
        self._models = self._load()
        self.provider = os.getenv("LLM_PROVIDER", "deepseek").lower()

    def _load(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"models": [], "availableModels": []}

    def list_models(self):
        # Return models declared in config as default
        return self._models.get("models", [])

    def test_connection(self):
        key = os.getenv("LLM_API_KEY", "")
        if not key:
            return {"ok": False, "reason": "no api key", "provider": self.provider}
        # Lightweight provider-specific check could be added here
        return {"ok": True, "provider": self.provider, "models_count": len(self.list_models())}

    def generate(self, model_id: str, prompt: str, max_tokens: int = 800):
        """Generate text using the configured provider. Returns a dict with 'model_id' and 'output'.

        If no API key is configured, a deterministic mock response is returned to avoid hard failures in dev.
        """
        key = os.getenv("LLM_API_KEY", "")

        # Mock fallback when no key present
        if not key:
            return {"model_id": model_id, "output": f"[mock:{self.provider}] {prompt}"}

        if self.provider == 'deepseek':
            return self._call_deepseek(model_id, prompt, key, max_tokens)
        if self.provider == 'anthropic':
            return self._call_anthropic(model_id, prompt, key, max_tokens)
        if self.provider == 'openai':
            return self._call_openai(model_id, prompt, key, max_tokens)
        # local or unknown provider => mock
        return {"model_id": model_id, "output": f"[local-mock] {prompt}"}

    def _call_deepseek(self, model_id, prompt, key, max_tokens):
        endpoint = os.getenv('DEEPSEEK_API_BASE', 'https://api.deepseek.example/v1/generate')
        headers = {
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json',
        }
        payload = {
            'model': model_id,
            'prompt': prompt,
            'max_tokens': max_tokens,
        }
        resp = requests.post(endpoint, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        # DeepSeek response format may vary; try common fields
        if isinstance(data, dict):
            if 'output' in data:
                output = data['output']
            elif 'text' in data:
                output = data['text']
            else:
                # Try choices style
                output = (data.get('choices') or [{}])[0].get('text')
        else:
            output = str(data)
        return {"model_id": model_id, "output": output}

    def _call_anthropic(self, model_id, prompt, key, max_tokens):
        # Minimal example using HTTP; recommend using official SDK for production
        base = os.getenv('ANTHROPIC_API_BASE', 'https://api.anthropic.com')
        url = f"{base}/v1/complete"
        headers = {'x-api-key': key, 'Content-Type': 'application/json'}
        payload = {'model': model_id, 'prompt': prompt, 'max_tokens': max_tokens}
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        output = data.get('completion') or (data.get('choices') or [{}])[0].get('text')
        return {"model_id": model_id, "output": output}

    def _call_openai(self, model_id, prompt, key, max_tokens):
        base = os.getenv('OPENAI_API_BASE', 'https://api.openai.com')
        url = f"{base}/v1/completions"
        headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}
        payload = {'model': model_id, 'prompt': prompt, 'max_tokens': max_tokens}
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        output = (data.get('choices') or [{}])[0].get('text')
        return {"model_id": model_id, "output": output}
