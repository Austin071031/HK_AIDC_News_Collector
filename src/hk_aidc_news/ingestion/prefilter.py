from urllib.parse import urlparse

import langdetect
from langdetect.lang_detect_exception import LangDetectException

ALLOWED_DOMAINS = {
    "research.hktdc.com",
    "www.scmp.com",
    "36kr.com",
    "www.datacenterdynamics.com",
    "example.com",
}

TOPIC_KEYWORDS = {
    "data center", "data centre", "gpu", "artificial intelligence", "ai", "compute", 
    "数据中心", "人工智能", "算力", "芯片", "服务器"
}

from typing import Dict

import re

def is_viable_candidate(normalized_doc: Dict) -> bool:
    text = normalized_doc.get("raw_text", "")
    url = normalized_doc.get("url", "")
    
    # Length check (lowered threshold to accommodate concise Chinese texts)
    if len(text) < 40:
        return False
        
    # Domain allowlist check
    if url:
        domain = urlparse(url).netloc
        if domain not in ALLOWED_DOMAINS:
            return False

    # Language detection
    try:
        lang = langdetect.detect(text)
        if not lang.startswith("en") and not lang.startswith("zh"):
            return False
    except LangDetectException:
        return False

    # Keyword topic gates
    text_lower = text.lower()
    
    # Check for exact word match for short acronyms like 'ai', otherwise substring match
    has_keyword = False
    for keyword in TOPIC_KEYWORDS:
        if keyword == "ai":
            if re.search(r'\bai\b', text_lower):
                has_keyword = True
                break
        elif keyword in text_lower:
            has_keyword = True
            break
            
    if not has_keyword:
        return False

    return True
