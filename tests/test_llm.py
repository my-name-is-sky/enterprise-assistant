import os
from src.enterprise.llm_manager import LLMManager


def test_mock_when_no_key():
    os.environ.pop('LLM_API_KEY', None)
    os.environ['LLM_PROVIDER'] = 'deepseek'
    mgr = LLMManager()
    out = mgr.generate('test-model', 'Hello world')
    assert 'mock' in out['output']


def test_list_models_returns_list():
    mgr = LLMManager()
    assert isinstance(mgr.list_models(), list)
