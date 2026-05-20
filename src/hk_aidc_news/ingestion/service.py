import httpx
from typing import Dict, List, Optional
from collections.abc import Iterable
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from hk_aidc_news.discovery.schemas import DiscoveryCandidate
from hk_aidc_news.ingestion.extractor import extract_text
from hk_aidc_news.ingestion.prefilter import is_viable_candidate
from hk_aidc_news.models.raw_document import RawDocument
from hk_aidc_news.models.article import Article
from hk_aidc_news.models.source import Source
from dateutil import parser


def fetch_html(url: str, firecrawl_key: Optional[str] = None) -> str:
    try:
        # Note: Data Center Dynamics and similar sites have strict Cloudflare protections
        # Standard httpx calls will fail with 403 Forbidden even with fake User-Agents
        # We use a third-party scraping API (like Firecrawl or ScrapingBee) when available
        # or fall back to more realistic headers.
        
        # Try Firecrawl first if we have the API key
        if firecrawl_key:
            try:
                response = httpx.post(
                    "https://api.firecrawl.dev/v1/scrape",
                    headers={"Authorization": f"Bearer {firecrawl_key}"},
                    json={"url": url, "formats": ["html"]},
                    timeout=30.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", {}).get("html", "")
            except Exception:
                pass # Fall back to direct fetch

        # Direct fetch fallback
        # Add Jina.ai reader as another fallback to bypass Cloudflare
        try:
            jina_response = httpx.get(
                f"https://r.jina.ai/{url}",
                timeout=20.0,
                headers={
                    "Accept": "text/html",
                }
            )
            if jina_response.status_code == 200 and len(jina_response.text) > 100:
                # Wrap it in basic HTML to satisfy BeautifulSoup
                return f"<html><body>{jina_response.text}</body></html>"
        except Exception:
            pass

        # Final direct fetch attempt
        response = httpx.get(
            url,
            timeout=15.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Sec-Ch-Ua": '"Chromium";v="122", "Google Chrome";v="122"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"macOS"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1"
            },
            follow_redirects=True
        )
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching HTML for {url}: {e}")
        return ""

def normalize_candidate(
    candidate: DiscoveryCandidate, raw_html: str
) -> Dict:

    try:
        raw_text = extract_text(raw_html)
    except Exception:
        raw_text = ""

    return {
        "url": candidate.url,
        "canonical_url": candidate.url,
        "title": candidate.title,
        "source_name": candidate.source_name,
        "discovered_via": candidate.discovered_via,
        "raw_html": raw_html,
        "raw_text": raw_text,
        "crawled_at": datetime.now(timezone.utc).isoformat(),
    }


def run_daily_ingestion(
    candidates: Iterable,
    db_session: Optional[Session] = None,
    settings: Optional[object] = None,
) -> List[Dict]:
    normalized = []
    firecrawl_key = getattr(settings, "firecrawl_api_key", None) if settings else None
    
    for candidate in candidates:
        try:
            html_content = fetch_html(candidate.url, firecrawl_key=firecrawl_key)
            doc = normalize_candidate(candidate, html_content)
            normalized.append(doc)
        except Exception:
            # Ensure it doesn't crash the pipeline but continue processing the rest
            continue

    viable = [doc for doc in normalized if is_viable_candidate(doc)]
    
    final_docs = []
    if db_session:
        for doc in viable:
            try:
                with db_session.begin_nested():
                    existing = db_session.query(RawDocument).filter_by(canonical_url=doc["canonical_url"]).first()
                    if not existing:
                        rd = RawDocument(
                            url=doc["url"],
                            canonical_url=doc["canonical_url"],
                            title=doc["title"],
                            source_name=doc["source_name"],
                            discovered_via=doc["discovered_via"],
                            raw_html=doc["raw_html"],
                            raw_text=doc["raw_text"],
                            crawled_at=doc["crawled_at"],
                        )
                        db_session.add(rd)
                        db_session.flush()
                        doc["id"] = rd.id
                        
                        # Create corresponding Article
                        source = db_session.query(Source).filter_by(name=doc["source_name"]).first()
                        source_id = source.id if source else None
                        
                        try:
                            published_at = parser.parse(doc["crawled_at"])
                        except Exception:
                            published_at = datetime.now(timezone.utc)
                            
                        article = Article(
                            raw_document_id=rd.id,
                            title=doc["title"],
                            url=doc["url"],
                            source_id=source_id,
                            published_at=published_at
                        )
                        db_session.add(article)
                        db_session.flush()
                        doc["article_id"] = article.id
                        final_docs.append(doc)
                    else:
                        doc["id"] = existing.id
                        article = db_session.query(Article).filter_by(raw_document_id=existing.id).first()
                        if article:
                            doc["article_id"] = article.id
                        else:
                            # Fallback if article doesn't exist for some reason
                            source = db_session.query(Source).filter_by(name=doc["source_name"]).first()
                            try:
                                published_at = parser.parse(doc["crawled_at"])
                            except Exception:
                                published_at = datetime.now(timezone.utc)
                            article = Article(
                                raw_document_id=existing.id,
                                title=doc["title"],
                                url=doc["url"],
                                source_id=source.id if source else None,
                                published_at=published_at
                            )
                            db_session.add(article)
                            db_session.flush()
                            doc["article_id"] = article.id
                            final_docs.append(doc)
            except Exception as e:
                continue
    else:
        final_docs = viable
                
    return final_docs
