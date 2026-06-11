import pytest

from AI import agent


def test_mistral_model_config_is_default_response_model():
    assert agent.DEFAULT_RESPONSE_MODEL_KEY == "MISTRAL_LARGE"
    assert agent.MODELS[agent.DEFAULT_RESPONSE_MODEL_KEY].name == "mistral-large-latest"
    assert agent.MODELS[agent.DEFAULT_RESPONSE_MODEL_KEY].provider == "mistral"


def test_mistral_provider_uses_direct_api(monkeypatch):
    captured = {}

    class FakeAsyncOpenAI:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setenv("MISTRAL_API_KEY", "test-mistral-key")
    monkeypatch.setattr(agent, "AsyncOpenAI", FakeAsyncOpenAI)

    llm = agent.Agent(agent.MODELS["MISTRAL_LARGE"], "system prompt")

    assert llm.model == "mistral-large-latest"
    assert llm.provider == "mistral"
    assert captured == {
        "api_key": "test-mistral-key",
        "base_url": "https://api.mistral.ai/v1",
    }


def test_mistral_provider_requires_mistral_api_key(monkeypatch):
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)

    with pytest.raises(ValueError, match="MISTRAL_API_KEY"):
        agent.Agent(agent.MODELS["MISTRAL_LARGE"], "system prompt")
