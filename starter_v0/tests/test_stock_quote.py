import pytest
from tools import TOOL_FUNCTIONS

quote = TOOL_FUNCTIONS["stock_quote"]


def test_sample_quote_is_explicitly_not_live():
    result = quote(" aapl ")
    assert result["symbol"] == "AAPL"
    assert result["is_demo"] is True
    assert result["source"] == "static_demo"
    assert result["as_of"] is None


@pytest.mark.parametrize("symbol", [None, 123, [], "", "   "])
def test_invalid_symbol_returns_error_without_raising(symbol):
    result = quote(symbol)
    assert "error" in result
    assert "price" not in result


def test_unknown_symbol_does_not_invent_price():
    result = quote("UNKNOWN")
    assert result["error"] == "UnsupportedSymbol"
    assert "price" not in result
