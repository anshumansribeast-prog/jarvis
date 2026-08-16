"""Web and local AI knowledge lookups."""

from __future__ import annotations

import requests

from ansux.config import settings
from ansux.core import memory

_STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "do", "does", "did",
    "give", "me", "tell", "for", "of", "to", "good", "some", "please",
    "what", "who", "how", "why", "when", "where", "and", "in", "on",
    "at", "it", "you", "i", "about", "your", "my", "today", "today's",
}


def _looks_related(query: str, topic: str) -> bool:
    query_words = {w for w in query.lower().split() if len(w) > 2 and w not in _STOPWORDS}
    topic_words = set(topic.lower().replace("(", " ").replace(")", " ").split())
    return bool(query_words & topic_words)


def duckduckgo_answer(query: str) -> str | None:
    try:
        resp = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
            timeout=5,
        )
        data = resp.json()
    except requests.RequestException:
        return None

    text = data.get("AbstractText")
    heading = data.get("Heading")
    if text and heading and not _looks_related(query, heading):
        text = None
    if not text and data.get("RelatedTopics"):
        first = data["RelatedTopics"][0]
        if isinstance(first, dict):
            text = first.get("Text")
    return text or None


def wikipedia_answer(query: str) -> str | None:
    try:
        search = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": 1,
                "format": "json",
            },
            headers=settings.WIKI_HEADERS,
            timeout=5,
        )
        hits = search.json().get("query", {}).get("search", [])
        if not hits:
            return None
        title = hits[0]["title"]
        if not _looks_related(query, title):
            return None
        summary = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(title)}",
            headers=settings.WIKI_HEADERS,
            timeout=5,
        )
        data = summary.json()
    except (requests.RequestException, IndexError, ValueError):
        return None
    return data.get("extract") or None


def web_answer(query: str) -> str | None:
    return duckduckgo_answer(query) or wikipedia_answer(query)


def ask_ollama(query: str) -> str | None:
    facts = memory.all_facts()
    system_prompt = settings.OLLAMA_SYSTEM_PROMPT
    if facts:
        system_prompt += " Known facts about the user: " + "; ".join(
            f"their {k} is {v}" for k, v in facts.items()
        ) + "."
    projects = memory.project_facts()
    if projects:
        system_prompt += f" {settings.USER_NAME}'s coding projects: " + " ".join(
            f"{name} - {desc}" for name, desc in projects.items()
        )
    try:
        resp = requests.post(
            settings.OLLAMA_URL,
            json={
                "model": settings.OLLAMA_MODEL,
                "prompt": query,
                "system": system_prompt,
                "stream": False,
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json().get("response", "").strip() or None
    except (requests.RequestException, ValueError):
        return None
