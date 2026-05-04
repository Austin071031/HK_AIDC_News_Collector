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
