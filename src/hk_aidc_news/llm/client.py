from openai import AsyncOpenAI

from hk_aidc_news.llm.schemas import EnrichmentResult


class OpenAiCompatibleLlmClient:
    def __init__(
        self, api_key: str, model: str, base_url: str | None = None
    ) -> None:
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    async def enrich(self, title: str, body: str, language: str) -> EnrichmentResult:
        prompt = (
            "Classify and summarize this article in JSON. "
            f"Language: {language}\nTitle: {title}\nBody: {body[:4000]}"
        )
        response = await self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format=EnrichmentResult,
        )
        if not response.choices or not response.choices[0].message.parsed:
            raise ValueError("Failed to parse response")
        return response.choices[0].message.parsed
