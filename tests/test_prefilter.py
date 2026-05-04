from hk_aidc_news.ingestion.prefilter import is_viable_candidate

def test_prefilter_rejects_short_content() -> None:
    assert not is_viable_candidate({"raw_text": "Too short"})
    assert is_viable_candidate({"raw_text": "This is a sufficiently long article about AI data centers. " * 10})
