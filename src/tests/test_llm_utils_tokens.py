import sys
import os
import pytest
from unittest.mock import Mock, patch, MagicMock

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.llm_utils import query_llm_with_tokens, get_clean_llm_response_with_tokens
from core.models import TokenUsage, LLMResponse


@pytest.fixture
def mock_config():
    config_mock = MagicMock()
    config_mock.__contains__ = Mock(return_value=True)
    config_mock.__getitem__ = Mock(side_effect=lambda key: {
        "DEFAULT": {
            "url": "http://localhost:11434",
            "model": "mistral:latest"
        },
        "Ollama": {
            "provider": "ollama",
            "endpoint": "/api/generate"
        }
    }[key])
    config_mock.sections = Mock(return_value=["Ollama"])
    return config_mock


@pytest.fixture
def mock_litellm_response():
    response = Mock()
    response.choices = [Mock()]
    response.choices[0].message.content = "This is a test response"

    response.usage = Mock()
    response.usage.prompt_tokens = 10
    response.usage.completion_tokens = 20
    response.usage.total_tokens = 30

    return response


@pytest.fixture
def mock_litellm_response_no_usage():
    response = Mock()
    response.choices = [Mock()]
    response.choices[0].message.content = "Response without usage"
    response.usage = None
    return response


def test_query_llm_with_tokens_success(mock_config, mock_litellm_response):
    with patch('litellm.completion', return_value=mock_litellm_response):
        content, token_usage = query_llm_with_tokens("test prompt", "Ollama", mock_config)

        assert content == "This is a test response"
        assert token_usage is not None
        assert token_usage.input_tokens == 10
        assert token_usage.output_tokens == 20
        assert token_usage.total_tokens == 30


def test_query_llm_with_tokens_no_usage(mock_config, mock_litellm_response_no_usage):
    with patch('litellm.completion', return_value=mock_litellm_response_no_usage):
        content, token_usage = query_llm_with_tokens("test prompt", "Ollama", mock_config)

        assert content == "Response without usage"
        assert token_usage is None


def test_query_llm_with_tokens_no_active_llm(mock_config):
    content, token_usage = query_llm_with_tokens("test prompt", None, mock_config)

    assert content is None
    assert token_usage is None


def test_query_llm_with_tokens_llm_not_in_config(mock_config):
    config_mock = MagicMock()
    config_mock.__contains__ = Mock(return_value=False)

    content, token_usage = query_llm_with_tokens("test prompt", "NonExistent", config_mock)

    assert content is None
    assert token_usage is None


def test_query_llm_with_tokens_api_error(mock_config):
    with patch('litellm.completion', side_effect=Exception("API Error")):
        content, token_usage = query_llm_with_tokens("test prompt", "Ollama", mock_config)

        assert content is None
        assert token_usage is None


def test_get_clean_llm_response_with_tokens_success(mock_config, mock_litellm_response):
    with patch('core.llm_utils.load_config', return_value=mock_config):
        with patch('core.llm_utils.get_active_llm_from_config', return_value="Ollama"):
            with patch('litellm.completion', return_value=mock_litellm_response):
                response = get_clean_llm_response_with_tokens("test prompt")

                assert isinstance(response, LLMResponse)
                assert response.content == "This is a test response"
                assert response.token_usage is not None
                assert response.token_usage.input_tokens == 10
                assert response.token_usage.output_tokens == 20
                assert response.token_usage.total_tokens == 30


def test_get_clean_llm_response_with_tokens_no_active_llm(mock_config):
    with patch('core.llm_utils.load_config', return_value=mock_config):
        with patch('core.llm_utils.get_active_llm_from_config', return_value=None):
            response = get_clean_llm_response_with_tokens("test prompt")

            assert isinstance(response, LLMResponse)
            assert response.content == "Error: No active Local LLM found"
            assert response.token_usage is None


def test_get_clean_llm_response_with_tokens_query_failure(mock_config):
    with patch('core.llm_utils.load_config', return_value=mock_config):
        with patch('core.llm_utils.get_active_llm_from_config', return_value="Ollama"):
            with patch('litellm.completion', side_effect=Exception("Error")):
                response = get_clean_llm_response_with_tokens("test prompt")

                assert isinstance(response, LLMResponse)
                assert response.content == "Error: Failed to get a response from the LLM"
                assert response.token_usage is None


def test_token_usage_dataclass_immutability():
    usage = TokenUsage(input_tokens=10, output_tokens=20, total_tokens=30)

    with pytest.raises(AttributeError):
        usage.input_tokens = 100


def test_llm_response_dataclass_immutability():
    usage = TokenUsage(input_tokens=10, output_tokens=20, total_tokens=30)
    response = LLMResponse(content="test", token_usage=usage)

    with pytest.raises(AttributeError):
        response.content = "modified"


def test_llm_response_to_dict():
    usage = TokenUsage(input_tokens=10, output_tokens=20, total_tokens=30)
    response = LLMResponse(content="test content", token_usage=usage)

    result_dict = response.to_dict()

    assert result_dict["content"] == "test content"
    assert "token_usage" in result_dict
    assert result_dict["token_usage"]["input_tokens"] == 10
    assert result_dict["token_usage"]["output_tokens"] == 20
    assert result_dict["token_usage"]["total_tokens"] == 30


def test_llm_response_to_dict_no_usage():
    response = LLMResponse(content="test content", token_usage=None)

    result_dict = response.to_dict()

    assert result_dict["content"] == "test content"
    assert "token_usage" not in result_dict


def test_token_usage_to_dict():
    usage = TokenUsage(input_tokens=10, output_tokens=20, total_tokens=30)

    result_dict = usage.to_dict()

    assert result_dict["input_tokens"] == 10
    assert result_dict["output_tokens"] == 20
    assert result_dict["total_tokens"] == 30
