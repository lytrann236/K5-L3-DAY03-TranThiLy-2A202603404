from typing import Any, Dict

def stock_quote(symbol: str) -> Dict[str, Any]:
    if not isinstance(symbol, str) or not symbol.strip():
        return {"error": "Stock symbol is required"}

    symbol_clean = symbol.upper().strip()
    mock_data = {
        "AAPL": {"price": 225.5, "currency": "USD", "change": "+1.2%"},
        "NVDA": {"price": 130.2, "currency": "USD", "change": "+3.5%"},
        "VHM": {"price": 42500, "currency": "VND", "change": "-0.5%"},
    }
    data = mock_data.get(symbol_clean)
    if data is None:
        return {"tool": "stock_quote", "error": "UnsupportedSymbol", "symbol": symbol_clean,
                "message": "No demo data for this symbol. Supported: AAPL, NVDA, VHM.", "is_demo": True}
    return {
        "symbol": symbol_clean,
        "price": data["price"],
        "currency": data["currency"],
        "change": data["change"],
        "status": "success",
        "is_demo": True, "source": "static_demo", "as_of": None,
        "message": "Static sample data for the lab; not a current market quote."
    }

