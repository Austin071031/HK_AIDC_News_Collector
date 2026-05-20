from typing import Optional
from openai import AsyncOpenAI
from hk_aidc_news.llm.schemas import EnrichmentResult

class OpenAiCompatibleLlmClient:
    def __init__(
        self, api_key: str, model: str, base_url: Optional[str] = None
    ) -> None:
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    async def enrich(self, title: str, body: str, language: str) -> EnrichmentResult:
        prompt = (
            "Classify and summarize this article in JSON. "
            "Ensure the summary is formatted as a concise list of bullet points, rather than a single paragraph. "
            f"Language: {language}\nTitle: {title}\nBody: {body[:4000]}"
            f"\n\nThe JSON must follow this schema: {EnrichmentResult.model_json_schema()}"
        )
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        if not response.choices or not response.choices[0].message.content:
            raise ValueError("Failed to parse response")
        return EnrichmentResult.model_validate_json(response.choices[0].message.content)
