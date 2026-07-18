"""
lilly/web_search.py
Lilly's web search capability via DuckDuckGo Lite.

Why this file exists:
    When Lilly doesn't know something, or when Gigi asks her to learn
    about a topic, she can search the web. We use DuckDuckGo Lite
    because it requires no API key, respects privacy, and returns
    simple HTML we can parse with regex.

Design note:
    We use urllib and regex — both in the standard library.
    No external dependencies. No JavaScript. Pure Python.
"""

import re
import urllib.parse
import urllib.request
from typing import List


def _extract_results(html: str) -> List[tuple]:
    """
    Extract search results from DuckDuckGo Lite HTML.
    DDG Lite wraps actual URLs in redirect links like:
    //duckduckgo.com/l/?uddg=https%3A%2F%2F...
    """
    results = []
    
    # Pattern: <a href="//duckduckgo.com/l/?uddg=ENCODED_URL" ...>TITLE</a>
    # We capture the href and the text between > and </a>
    pattern = r'<a[^>]*href="(//duckduckgo\.com/l/\?uddg=[^"]*)"[^>]*>(.*?)</a>'
    matches = re.findall(pattern, html, re.DOTALL)
    
    for href, title in matches:
        # Clean up title (remove HTML tags, normalize whitespace)
        clean_title = re.sub(r'<[^>]+>', '', title).strip()
        clean_title = re.sub(r'\s+', ' ', clean_title)
        
        # Extract actual URL from the redirect
        # The uddg parameter contains the real URL
        url_match = re.search(r'uddg=([^&"]+)', href)
        if url_match:
            actual_url = urllib.parse.unquote(url_match.group(1))
        else:
            actual_url = href
        
        # Skip navigation links (Next, Previous, etc.)
        if clean_title.lower() in ('next', 'previous', 'more results', ''):
            continue
            
        results.append((clean_title, actual_url))
    
    return results


def search_duckduckgo(query: str, max_results: int = 5) -> List[str]:
    """
    Search DuckDuckGo Lite and return formatted result snippets.
    """
    encoded = urllib.parse.quote_plus(query)
    url = f"https://lite.duckduckgo.com/lite/?q={encoded}"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode("utf-8", errors="replace")
    except Exception as e:
        return [f"Web search failed: {e}"]

    results = _extract_results(html)

    if not results:
        return ["No web results found."]

    formatted = []
    for title, link in results[:max_results]:
        formatted.append(f"{title}: {link}")

    return formatted


def search_and_summarize(query: str, max_results: int = 3) -> str:
    """
    Search the web and format results for Lilly to read.
    """
    results = search_duckduckgo(query, max_results)
    if len(results) == 1 and results[0].startswith("Web search failed"):
        return results[0]

    lines = ["WEB SEARCH RESULTS:", ""]
    for i, result in enumerate(results, 1):
        lines.append(f"{i}. {result}")
    lines.append("")
    lines.append("Use these results to answer the user's question. Cite sources when possible.")
    return "\n".join(lines)
