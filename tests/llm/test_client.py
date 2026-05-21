import pytest
from unittest.mock import AsyncMock, patch

from hk_aidc_news.llm.client import OpenAiCompatibleLlmClient
from hk_aidc_news.llm.schemas import EnrichmentResult

@pytest.mark.asyncio
async def test_llm_client_calls_openai():
    mock_response = AsyncMock()
    mock_response.choices = [AsyncMock()]
    mock_response.choices[0].message.content = EnrichmentResult(
        relevance="direct",
        confidence=0.9,
        rationale="test",
        tags=["tag1"],
        entities=["entity1"],
        summary="summary",
        key_points=["kp1"],
        extracted_content="content",
        semantic_key="key"
    ).model_dump_json()

    with patch("hk_aidc_news.llm.client.AsyncOpenAI") as mock_openai:
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        client = OpenAiCompatibleLlmClient(api_key="test_key", model="test-model")
        result = await client.enrich(title="Test", body="Body", language="en")
        
        assert result.relevance == "direct"
        assert result.confidence == 0.9
        
        mock_client.chat.completions.create.assert_called_once()
        _, kwargs = mock_client.chat.completions.create.call_args
        assert kwargs["model"] == "test-model"
        assert kwargs["response_format"] == {"type": "json_object"}
        assert "messages" in kwargs
