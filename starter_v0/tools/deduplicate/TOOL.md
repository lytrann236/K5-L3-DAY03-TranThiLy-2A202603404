---
name: deduplicate
track: core
kind: local_formatter
requires_env: []
inputs: [items]
outputs: [items, input_count, item_count, removed_count]
side_effect: false
---
# deduplicate

Remove duplicate URLs from already-collected articles or posts. Keep the first
item and original order, preserving all its fields without modifying the input.
URLs are compared exactly after trimming surrounding whitespace. Query strings,
fragments, and trailing slashes remain significant; this is not semantic deduplication.

Use when the user asks to remove duplicate links from supplied results, before
formatting a digest. Do not use to search for articles or merge similar stories.
Each item must contain a non-empty HTTP(S) `url`. An empty list is valid.
Invalid input returns an error dict without partial results or raising.
No API key, network request, or file write is needed.
