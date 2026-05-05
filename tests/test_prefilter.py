from hk_aidc_news.ingestion.prefilter import is_viable_candidate

def test_prefilter_rejects_short_content() -> None:
    assert not is_viable_candidate({"raw_text": "Too short", "url": "https://example.com/a"})
    assert is_viable_candidate({"raw_text": "This is a sufficiently long article about AI data centers. " * 10, "url": "https://example.com/a"})

def test_prefilter_language_detection() -> None:
    # English text
    assert is_viable_candidate({
        "raw_text": "Hong Kong's new artificial intelligence data center cluster is expanding rapidly, driving demand for GPU compute power.",
        "url": "https://example.com/a"
    })
    # Chinese text
    assert is_viable_candidate({
        "raw_text": "香港的新人工智能数据中心集群正在迅速扩张，这推动了对GPU计算能力的需求。此举将极大地改变亚洲的计算格局。",
        "url": "https://example.com/b"
    })
    # Spanish text (should be rejected)
    assert not is_viable_candidate({
        "raw_text": "El nuevo clúster de centros de datos de inteligencia artificial de Hong Kong se está expandiendo rápidamente, impulsando la demanda.",
        "url": "https://example.com/c"
    })

def test_prefilter_domain_allowlist() -> None:
    valid_text = "This is a sufficiently long article about AI data centers. " * 10
    assert not is_viable_candidate({
        "raw_text": valid_text,
        "url": "https://spam-seo-farm.com/article"
    })
    assert is_viable_candidate({
        "raw_text": valid_text,
        "url": "https://research.hktdc.com/article"
    })

def test_prefilter_keyword_gates() -> None:
    # Contains relevant keywords
    assert is_viable_candidate({
        "raw_text": "A new data center campus is being built to host 10000 GPUs for artificial intelligence workloads. " * 5,
        "url": "https://example.com/a"
    })
    # Sufficient length but irrelevant topic
    assert not is_viable_candidate({
        "raw_text": "The local bakery just announced their new line of strawberry cakes and pastries. It is expected to be very delicious. " * 10,
        "url": "https://example.com/b"
    })
