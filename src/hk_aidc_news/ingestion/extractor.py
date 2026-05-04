from bs4 import BeautifulSoup


def extract_text(raw_html: str) -> str:
    soup = BeautifulSoup(raw_html, "html.parser")
    return " ".join(soup.get_text(" ", strip=True).split())
