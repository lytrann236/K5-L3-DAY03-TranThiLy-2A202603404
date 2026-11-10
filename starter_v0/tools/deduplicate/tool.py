from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit


def deduplicate_items(items: list[dict[str, Any]]) -> dict[str, Any]:
    """Keep the first item for each exact URL after trimming whitespace."""
    try:
        if not isinstance(items, list):
            raise ValueError("items must be a list of objects")
        unique: list[dict[str, Any]] = []
        seen: set[str] = set()
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                raise ValueError(f"items[{index}] must be an object")
            url = item.get("url")
            if not isinstance(url, str) or not url.strip():
                raise ValueError(f"items[{index}].url must be a non-empty HTTP(S) URL")
            url = url.strip()
            parsed = urlsplit(url)
            if parsed.scheme not in ("http", "https") or not parsed.hostname:
                raise ValueError(f"items[{index}].url must be an HTTP(S) URL")
            if url not in seen:
                seen.add(url)
                unique.append({**item, "url": url})
        return {
            "tool": "deduplicate", "items": unique,
            "input_count": len(items), "item_count": len(unique),
            "removed_count": len(items) - len(unique),
        }
    except ValueError as exc:
        return {"tool": "deduplicate", "error": "ValueError", "message": str(exc)}
