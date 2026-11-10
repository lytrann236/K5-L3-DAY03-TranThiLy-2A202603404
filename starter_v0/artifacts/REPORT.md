# Research Agent ? Report

## Team
- Working branch: nguyenthuyduong
- Provider/model: Gemini / gemini-3.5-flash
- Team membership: to be confirmed by the submitter.

# PH?N A ? Gi?i thi?u agent

## A1. Capabilities
Research assistant for web news, X posts, reading URLs, and formatting digests.
The new deduplicate tool removes repeated URLs from supplied articles without an API key.
UI: Streamlit app.py; local URL http://localhost:8501. Public demo URL: pending deployment. See UI-README.md for launch instructions.

## A2. Tools
| Tool | Purpose | New |
|---|---|---|
| clarify | Ask for missing information or confirmation | No |
| timeline | Read recent posts from a specified account | No |
| social_search | Search social posts by topic | No |
| lookup | Search the web and news | No |
| fetch | Read a specific URL | No |
| format | Format collected items as a digest | No |
| deduplicate | Keep the first item per exact URL after trimming whitespace | Yes |
| send | Telegram delivery; requires configuration and confirmation | No |
| policy | Search local company policy | No |
| papers | Search arXiv | No |
| paper_text | Extract text from an arXiv paper | No |

## A3. Example requests
1. Get 2 latest posts from karpathy.
2. Read https://example.com/research.
3. Remove duplicate URLs: [{"url":"https://example.com/a"},{"url":"https://example.com/a"}].
4. Format the supplied articles as bullets.

# PH?N B ? Chi ti?t / B?ng ch?ng

## B1. Version evidence
Source: artifacts/version_log.csv and runs/v0?v3 JSON files.

| Version | Passed | Case accuracy | Tool routing | Multiturn |
|---|---:|---:|---:|---:|
| v0 | 11/20 | 55% | 65% | 83.33% |
| v1 | 11/20 | 55% | 60% | 66.67% |
| v2 | 13/20 | 65% | 75% | 83.33% |
| v3 | 14/20 | 70% | 85% | 83.33% |

- v1: replaced guessing with clarification. R10 and R11 passed, but over-clarification caused regressions for named people. Total accuracy remained 55%.
- v2: distinguish absent/ambiguous targets from clearly identified people. Accuracy increased to 65%.
- v3: require confirmation before delivery. R12 called clarify instead of send, but used text rather than yes_no. The target case still failed. Total 70% does not prove the confirmation hypothesis succeeded.
- Adding deduplicate changes tools.yaml after v3. The group suite uses version v4-deduplicate; v3 base accuracy is not a measurement of the expanded tool set.

## B2. Remaining v3 failures
- R03_web_news_routing: wrong_tool; query: expected 'AI', got 'latest AI news highlights'
- R08_out_of_scope: out_of_scope; expected no tool call
- R09_no_tool_capability: unnecessary_tool; expected no tool call
- R12_confirm_before_send: wrong_boundary; response_type: expected 'yes_no', got 'text'
- R13_parallel_web_and_tweets: wrong_tool; query: expected 'AI', got 'AI news'; missing tool call social_search
- M02_carryover_timeframe: wrong_arg_value; query: expected 'robotics', got 'robotics news'

## B3. Team eval
10 cases in data/eval_group.json: exactly 5 single-turn and 5 multi-turn.
Coverage: new-tool routing, missing URLs, exact limits, social sorting, supplied-item formatting, account corrections, URL carryover, sort corrections, item carryover, and template corrections.
Results: 10/10 PASS (100% case, routing, argument, and multiturn accuracy); no provider errors. Evidence: runs/v4-deduplicate_B_group_gemini_20261110T112216163771.json. This is a separate group dataset and is not directly comparable to the 70% base score.

## B4. Live chat
Real-API CLI demo with 3 scripted user inputs (not a human interactive session):
Evidence: transcripts/v4-deduplicate_gemini_20261110T112423997480.transcript.json.

| Turn | Request | Actual tool | Status |
|---|---|---|---|
| 1 | Summarize an article without a URL | clarify | waiting_for_user |
| 2 | Supply https://example.com | fetch | answered |
| 3 | Remove duplicate URLs from two articles | deduplicate | answered |

The demo used the real Gemini provider and real Firecrawl fetch, not mocked outputs. Automated UI interaction checks passed. Human demo rehearsal and public deployment remain to be completed.

## B5. Implementation and unit tests
- New tool: tools/deduplicate/tool.py with TOOL.md, registry entry, and schema.
- 14 new tool test cases cover deduplication, metadata/order preservation, no input mutation, distinct URLs, empty input, and malformed input.
- Found a harness bug: normalize_value attempted to sort dictionaries directly, raising TypeError for items arrays. Sort by a deterministic JSON representation instead, retaining the existing order-insensitive comparison convention. A regression test covers object-list comparison.
- Latest offline test result: 104 passed, 0 skipped, 0 failed. All starter TODO tests are implemented with mocked HTTP and local policy input.
- UI: app.py with chat history, model selection, tool-result inspection, reset, transcript persistence, and JSON download. Streamlit AppTest passed for chat, persistence, reset, and provider-error handling. Local server health check returned HTTP 200.

## B6. Reflection
Missing-information and confirmation rules belong in the system prompt. Tool descriptions and argument conventions belong in tools.yaml.
R12 needs manual review: requesting missing content via text avoids sending, but the automatic test expects yes_no. This distinction must remain visible rather than reporting it as a full success.
Next: publish a demo URL, have a human try the conversation, and review remaining routing/argument failures.

## B7. Small local model challenge
Not attempted. No local-model results are claimed.

UI Windows encoding fix: tool diagnostics now use ASCII-safe output; transcript content remains Unicode. A cp1252-console regression test and a real Gemini UI turn passed. Launch Streamlit with python -X utf8.

## Integration with shared main
Merged shared main commit 40d802b, preserving its current prompt/tool descriptions and stock_quote implementation and tests, alongside deduplicate and the UI. Historical Gemini snapshots and their 70% v3 evidence remain separate from the OpenRouter results contributed on main. UI v1-v3 still selects the historical Gemini snapshots. Post-merge verification: 115 tests passed, no skipped tests.
