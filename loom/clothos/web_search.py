"""
Internet Web Search & Content Extraction Engine (`loom/clothos/web_search.py`).

Reverse-engineered and adapted from OpenClaw's web-search and Sovereign Cluster Google Search Grounding:
- Google Search Grounding Engine (via Gemini 2.5 Flash API with google_search tool):
  Performs real-time web search across Google's live index, providing citations, links, and grounded facts.
- Clean Webpage Extractor:
  Fetches target URLs, strips boilerplate/navigation/scripts, and converts content into clean Markdown.
- Multi-provider fallback:
  Supports Brave Search API or DuckDuckGo if configured.
"""

from __future__ import annotations

import html
import json
import logging
import os
import re
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

logger = logging.getLogger("loom.clothos.web_search")

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


def clean_html_to_markdown(raw_html: str, max_chars: int = 15000) -> str:
    """Strips scripts, styles, navigations, and converts body content into clean readable Markdown."""
    text = re.sub(r'<(script|style|nav|header|footer|aside)[^>]*>.*?</\1>', ' ', raw_html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<!--.*?-->', ' ', text, flags=re.DOTALL)
    text = re.sub(r'<h[1-2][^>]*>(.*?)</h[1-2]>', r'\n\n# \1\n\n', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<h[3-6][^>]*>(.*?)</h[3-6]>', r'\n\n## \1\n\n', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<a\s+(?:[^>]*?\s+)?href=["\'](https?://[^"\']+)["\'][^>]*>(.*?)</a>', r'[\2](\1)', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<li[^>]*>(.*?)</li>', r'\n* \1', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</p>', '\n\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = html.unescape(text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    clean = text.strip()
    return clean[:max_chars] + ("\n\n... [Content truncated]" if len(clean) > max_chars else "")


def search_gemini_google_grounding(query: str, api_key: str) -> Dict[str, Any]:
    """Live Google Web Search via Gemini 2.5 Flash Grounding (Native Google Search)."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": f"Search the live web and provide an up-to-date answer with citations: {query}"}]}],
        "tools": [{"google_search": {}}],
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )

    with urllib.request.urlopen(req, timeout=18) as r:
        if r.status != 200:
            raise RuntimeError(f"Gemini API returned status {r.status}")
        data = json.loads(r.read().decode("utf-8"))

    cand = data.get("candidates", [{}])[0]
    content = cand.get("content", {}).get("parts", [{}])[0].get("text", "")
    grounding = cand.get("groundingMetadata", {})
    chunks = grounding.get("groundingChunks", [])
    
    sources = []
    for c in chunks:
        web = c.get("web", {})
        if web.get("uri"):
            sources.append({
                "title": web.get("title", ""),
                "url": web.get("uri", ""),
            })

    return {
        "success": True,
        "provider": "Google Search Grounding (Gemini 2.5)",
        "query": query,
        "summary": content,
        "sources": sources,
    }


def search_brave(query: str, api_key: str, max_results: int = 8) -> Dict[str, Any]:
    """Brave Search API search."""
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://api.search.brave.com/res/v1/web/search?q={encoded_query}&count={max_results}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "X-Subscription-Token": api_key,
            "User-Agent": DEFAULT_USER_AGENT,
        },
    )
    with urllib.request.urlopen(req, timeout=8) as r:
        data = json.loads(r.read().decode("utf-8"))
        results = []
        for item in data.get("web", {}).get("results", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("description", ""),
            })
    return {
        "success": bool(results),
        "provider": "Brave Search API",
        "query": query,
        "summary": "\n".join([f"- [{r['title']}]({r['url']}): {r['snippet']}" for r in results]),
        "sources": results,
    }


def search_internet(query: str, max_results: int = 8) -> Dict[str, Any]:
    """Unified master search dispatcher: uses Google Search Grounding if API key present, else Brave."""
    gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if gemini_key:
        try:
            return search_gemini_google_grounding(query, gemini_key)
        except Exception as exc:
            logger.warning(f"Google Search Grounding failed, falling back: {exc}")

    brave_key = os.environ.get("BRAVE_API_KEY")
    if brave_key:
        try:
            return search_brave(query, brave_key, max_results)
        except Exception as exc:
            logger.warning(f"Brave Search failed: {exc}")

    return {
        "success": False,
        "query": query,
        "error": "No web search provider succeeded. Set GEMINI_API_KEY or BRAVE_API_KEY for live internet search.",
    }


def fetch_webpage(url: str, max_chars: int = 15000, render_js: bool = False) -> Dict[str, Any]:
    """Fetches a live webpage and extracts clean, readable Markdown text.
    
    If render_js=True or if the initial HTML response indicates a client-side SPA,
    automatically leverages the vendored Playwright Chromium browser.
    """
    if render_js:
        try:
            from loom.clothos.sovereign_runtime import ClothOSSovereignRuntime
            rt = ClothOSSovereignRuntime.get_instance()
            res = rt.fetch_page_rendered(url=url, max_chars=max_chars)
            if res.get("success"):
                return {
                    "success": True,
                    "url": url,
                    "status_code": 200,
                    "content_length": res.get("content_length", 0),
                    "markdown": res.get("text", ""),
                    "renderer": "Playwright Headless Chromium"
                }
        except Exception:
            pass

    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            raw_html = r.read().decode("utf-8", errors="ignore")
            content_md = clean_html_to_markdown(raw_html, max_chars=max_chars)
            # If SPA detected with near-empty text, fallback to headless browser
            if len(content_md.strip()) < 150 and not render_js:
                try:
                    from loom.clothos.sovereign_runtime import ClothOSSovereignRuntime
                    rt = ClothOSSovereignRuntime.get_instance()
                    b_res = rt.fetch_page_rendered(url=url, max_chars=max_chars)
                    if b_res.get("success") and len(b_res.get("text", "")) > len(content_md):
                        return {
                            "success": True,
                            "url": url,
                            "status_code": r.status,
                            "content_length": b_res.get("content_length", 0),
                            "markdown": b_res.get("text", ""),
                            "renderer": "Playwright Headless Chromium (SPA Fallback)"
                        }
                except Exception:
                    pass

            return {
                "success": True,
                "url": url,
                "status_code": r.status,
                "content_length": len(content_md),
                "markdown": content_md,
            }
    except Exception as exc:
        # Final fallback to headless browser on HTTP/TLS errors
        try:
            from loom.clothos.sovereign_runtime import ClothOSSovereignRuntime
            rt = ClothOSSovereignRuntime.get_instance()
            b_res = rt.fetch_page_rendered(url=url, max_chars=max_chars)
            if b_res.get("success"):
                return {
                    "success": True,
                    "url": url,
                    "status_code": 200,
                    "content_length": b_res.get("content_length", 0),
                    "markdown": b_res.get("text", ""),
                    "renderer": "Playwright Headless Chromium (Error Recovery)"
                }
        except Exception:
            pass

        return {
            "success": False,
            "url": url,
            "error": str(exc),
        }
