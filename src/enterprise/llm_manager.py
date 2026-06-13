import os
import json
from typing import Optional
from pathlib import Path

DEFAULT_MODELS = Path(__file__).parents[1] / ".." / "config" / "models.json.example"

class LLMManager:
    def __init__(self, config_path: Optional[Path]=None):
        self.config_path = config_path or DEFAULT_MODELS
        self._models = self._load()
        self.provider = os.getenv("LLM_PROVIDER", "anthropic")

    def _load(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"models": [], "availableModels": []}

    def list_models(self):
        return self._models.get("models", [])

    def test_connection(self):
        # Demo: check API key presence
        key = os.getenv("LLM_API_KEY", "")
        return {"provider": self.provider, "key_present": bool(key), "models_count": len(self.list_models())}

    def generate(self, model_id: str, prompt: str):
        # Example lightweight wrapper; real implementation uses provider SDKs
        if self.provider == "anthropic":
            key = os.getenv("LLM_API_KEY")
            if not key:
                raise RuntimeError("Missing LLM_API_KEY")
            # Placeholder: return prompt echo
            return {"model_id": model_id, "output": f"[Anthropic mock] {prompt}"}
        elif self.provider == "openai":
            key = os.getenv("LLM_API_KEY")
            if not key:
                raise RuntimeError("Missing LLM_API_KEY")
            return {"model_id": model_id, "output": f"[OpenAI mock] {prompt}"}
        else:
            return {"model_id": model_id, "output": f"[Local mock] {prompt}"}
