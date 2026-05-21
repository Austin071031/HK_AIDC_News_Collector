from urllib.parse import urlparse
import langdetect
from langdetect.lang_detect_exception import LangDetectException
from typing import Dict

BLOCKED_DOMAINS = {"spam-seo-farm.com"}
REQUIRED_KEYWORDS = [
    "data center", "gpu", "ai ", "artificial intelligence", "compute",
    "人工智能", "数据中心", "算力", "llm", "machine learning"
]

def is_viable_candidate(normalized_doc: Dict) -> bool:
    text = normalized_doc.get("raw_text", "")
    url = normalized_doc.get("url", "")
    
    # Length check (lowered threshold to accommodate concise Chinese texts)
    if len(text) < 40:
        return False

    # Domain blocklist
    if url:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        if any(blocked in domain for blocked in BLOCKED_DOMAINS):
            return False

    # Language detection
    try:
        lang = langdetect.detect(text)
        if not lang.startswith("en") and not lang.startswith("zh"):
            return False
    except LangDetectException:
        return False

    # Keyword gates
    text_lower = text.lower()
    # Ensure at least one required keyword is present
    if not any(kw in text_lower for kw in REQUIRED_KEYWORDS):
        return False

    return True
