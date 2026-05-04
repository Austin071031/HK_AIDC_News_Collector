def cluster_articles(articles: list[dict]) -> list[dict]:
    grouped: dict[str, dict] = {}

    for article in articles:
        key = article.get("semantic_key") or article["canonical_url"]
        bucket = grouped.setdefault(
            key,
            {
                "cluster_id": key,
                "headline": article["title"],
                "items": [],
            },
        )
        bucket["items"].append(article)

    return list(grouped.values())
