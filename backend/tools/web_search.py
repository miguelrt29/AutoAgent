"""Tool that performs web searches using the DDGS library."""

from ddgs import DDGS


def web_search(query: str, max_results: int = 5) -> dict:
    """Search the web via DuckDuckGo and return titles with links."""
    max_results = int(max_results)

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

        if not results:
            return {"success": False, "result": f"No results found for '{query}'."}

        formatted = f"Search results for '{query}':\n\n"
        for i, r in enumerate(results, 1):
            title = r.get("title", "")
            body = r.get("body", "")
            link = r.get("href", "")
            snippet = f"{body[:120]}{'...' if len(body) > 120 else ''}" if body else ""
            formatted += f"{i}. {title}\n   {snippet}\n   {link}\n\n"

        return {"success": True, "result": formatted}

    except Exception as e:
        return {"success": False, "result": f"Search error: {str(e)}"}
