from run_eval import normalize_value


def test_normalization_compares_lists_of_objects_without_sorting_dicts():
    first = [{"url": "https://example.com/b"}, {"url": "https://example.com/a"}]
    assert normalize_value(first) == normalize_value(list(reversed(first)))
    assert normalize_value(first) != normalize_value(first[:1])
