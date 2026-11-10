from copy import deepcopy

import pytest

from tools import TOOL_FUNCTIONS


deduplicate = TOOL_FUNCTIONS["deduplicate"]


def test_duplicates_keep_first_item_and_do_not_mutate_input():
    items = [
        {"url": " https://example.com/a ", "title": "First", "score": 1},
        {"url": "https://example.com/b", "title": "Second"},
        {"url": "https://example.com/a", "title": "Duplicate"},
    ]
    original = deepcopy(items)
    result = deduplicate(items)
    assert result == {
        "tool": "deduplicate",
        "items": [{**items[0], "url": "https://example.com/a"}, items[1]],
        "input_count": 3, "item_count": 2, "removed_count": 1,
    }
    assert items == original


def test_distinct_query_strings_and_fragments_are_preserved():
    items = [{"url": url} for url in [
        "https://example.com/a", "https://example.com/a?x=1",
        "https://example.com/a#section", "https://example.com/a/",
    ]]
    result = deduplicate(items)
    assert result["items"] == items
    assert result["removed_count"] == 0


def test_empty_list_is_valid():
    result = deduplicate([])
    assert result["items"] == []
    assert result["input_count"] == result["item_count"] == result["removed_count"] == 0


@pytest.mark.parametrize("items", [None, "bad", {}, [None], [{}],
    [{"url": ""}], [{"url": 42}], [{"url": "ftp://example.com/a"}],
    [{"url": "https://"}], [{"url": "http://[bad"}],
    [{"url": "https://example.com"}, {"url": " "}],
])
def test_invalid_input_returns_error_without_partial_results(items):
    result = deduplicate(items)
    assert result["error"] == "ValueError"
    assert result["message"]
    assert "items" not in result
