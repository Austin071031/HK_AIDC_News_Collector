import pytest
from unittest.mock import AsyncMock, patch

from hk_aidc_news.llm.client import OpenAiCompatibleLlmClient
from hk_aidc_news.llm.schemas import EnrichmentResult

@pytest.mark.asyncio
async def test_llm_client_calls_openai():
    client = OpenAiCompatibleLlmClient(api_key="test_key", model="test-model")
    
    mock_response = AsyncMock()
    mock_response.choices = [AsyncMock()]
    mock_response.choices[0].message.parsed = EnrichmentResult(
        relevance="direct",
        confidence=0.9,
        rationale="test",
        tags=["tag1"],
        entities=["entity1"],
        summary="summary",
        semantic_key="key"
    )
    
    with patch("openai.resources.beta.chat.completions.AsyncCompletions.parse", new_callable=AsyncMock) as mock_parse:
        mock_parse.return_value = mock_response
        
        result = await client.enrich(title="Test", body="Body", language="en")
        
        assert result.relevance == "direct"
        assert result.confidence == 0.9
        
        mock_parse.assert_called_once()
        _, kwargs = mock_parse.call_args
        assert kwargs["model"] == "test-model"
        assert kwargs["response_format"] == EnrichmentResult
        assert "messages" in kwargs
