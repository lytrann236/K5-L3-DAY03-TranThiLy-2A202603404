---
name: stock_quote
track: bonus
kind: local_knowledge
provider: static_demo
requires_env: []
inputs: [symbol]
outputs: [symbol, price, currency, change, status, is_demo, source, as_of, message]
side_effect: false
---
# stock_quote
Returns static sample quotes for AAPL, NVDA, and VHM for a lab demonstration.
This tool does not fetch current market data and requires no API key.
Use only for explicitly requested demo/sample data. Always show the demo label.
Empty or non-string input returns an error dict. Unknown symbols return
UnsupportedSymbol without an invented price. Successful results set is_demo=true,
source=static_demo, and as_of=null because no live price timestamp is available.
