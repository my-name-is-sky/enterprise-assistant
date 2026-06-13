# DeepSeek / LLM integration guide

This document explains how the repository integrates with LLM providers and how to configure and test them.

Supported providers
- deepseek (recommended for your environment)
- anthropic (example HTTP adapter; prefer vendor SDKs in production)
- openai (example HTTP adapter)
- local (mock)

Environment variables
- LLM_PROVIDER: deepseek | anthropic | openai | local  (default: deepseek)
- LLM_API_KEY: The API key for the chosen provider. If not set, llm endpoints will return a mock response for development.
- DEEPSEEK_API_BASE: Optional. Base URL for DeepSeek's generate endpoint. Default: https://api.deepseek.example/v1/generate
- ANTHROPIC_API_BASE, OPENAI_API_BASE: Optional custom endpoints for other providers.

How to add the API key to GitHub Secrets (recommended)
1. Go to your repository on GitHub -> Settings -> Secrets and variables -> Actions -> New repository secret
2. Add a secret named LLM_API_KEY with the value of your key.
3. Optionally add a repository variable LLM_PROVIDER set to "deepseek".

Local testing (without adding Secrets)
1. Export the provider and key locally:
   export LLM_PROVIDER=deepseek
   export LLM_API_KEY="<your_key>"
   # optionally override base URL
   export DEEPSEEK_API_BASE="https://api.deepseek.example/v1/generate"

2. Start the API server (see README for project startup)
   uvicorn src.api.app:app --reload --port 8000

3. Call the generate endpoint (replace <API_TOKEN> with your admin token from scripts/init_db_and_token.py):
   curl -X POST http://127.0.0.1:8000/llm/generate \
     -H "Content-Type: application/json" \
     -H "X-API-TOKEN: <API_TOKEN>" \
     -d '{"model_id":"deepseek-model-1","prompt":"Summarize last week's sales emails."}'

Behavior notes
- When LLM_API_KEY is not present, generate will return a deterministic mock response to simplify development and testing.
- The adapter implementations in this repo are minimal HTTP wrappers. For production use, replace with official SDKs (Anthropic/OpenAI) or follow DeepSeek's recommended client.

Security
- Never commit API keys to the repository.
- Always use GitHub Secrets for Actions and environment variables for local testing.
