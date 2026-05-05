from hk_aidc_news.clustering.service import cluster_articles

def test_cluster_articles_merges_same_semantic_key() -> None:
    articles = [
        {
            "canonical_url": "https://example.com/a",
            "title": "A",
            "semantic_key": "event-1",
        },
        {
            "canonical_url": "https://example.cn/a",
            "title": "A zh",
            "semantic_key": "event-1",
        },
        {
            "canonical_url": "https://example.com/b",
            "title": "B",
            "semantic_key": "event-2",
        },
    ]

    clusters = cluster_articles(articles)

    assert len(clusters) == 2
    assert len(clusters[0]["items"]) == 2

def test_cluster_articles_merges_fuzzy_title_and_entities() -> None:
    articles = [
        {
            "canonical_url": "https://example.com/a",
            "title": "OpenAI announces GPT-5 release date",
            "semantic_key": "event-1",
            "entities": ["OpenAI", "GPT-5"],
        },
        {
            "canonical_url": "https://example.com/b",
            "title": "OpenAI to announce GPT-5 release date soon",
            "semantic_key": "event-unknown",
            "entities": ["OpenAI", "Sam Altman"],
        },
        {
            "canonical_url": "https://example.com/c",
            "title": "Different topic completely",
            "semantic_key": "event-3",
            "entities": ["Apple"],
        },
    ]

    clusters = cluster_articles(articles)

    assert len(clusters) == 2
    # The first two should merge because titles are similar and share "OpenAI"
    # Event-1 should have 2 items
    assert len(clusters[0]["items"]) == 2
    assert clusters[0]["cluster_key"] == "event-1"
    assert len(clusters[1]["items"]) == 1
