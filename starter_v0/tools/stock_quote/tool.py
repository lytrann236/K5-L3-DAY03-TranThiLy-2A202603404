from typing import Any, Dict

def stock_quote(symbol: str) -> Dict[str, Any]:
    if not symbol:
        return {"error": "Stock symbol is required"}

    symbol_clean = symbol.upper().strip()
    mock_data = {
        "AAPL": {"price": 225.5, "currency": "USD", "change": "+1.2%"},
        "NVDA": {"price": 130.2, "currency": "USD", "change": "+3.5%"},
        "VHM": {"price": 42500, "currency": "VND", "change": "-0.5%"},
    }
    data = mock_data.get(symbol_clean, {"price": 100.0, "currency": "USD", "change": "0.0%"})
    return {
        "symbol": symbol_clean,
        "price": data["price"],
        "currency": data["currency"],
        "change": data["change"],
        "status": "success"
    }

