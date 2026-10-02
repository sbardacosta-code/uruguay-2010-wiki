# Dashboard validation

Actual connected local checks performed on 30 September 2026. These results demonstrate the browser interface using the existing harness; they do **not** establish internet-disconnected operation.

## Observed checks

| Check | Actual result |
|---|---|
| Desktop layout, 1366 × 900 | Homepage, seven-match journey, answer and evidence columns inspected |
| Narrow layout, 390 × 844 | Stacked homepage and Search inspected; document width equals viewport width (390), with the match strip scrolling horizontally |
| Match navigation | Home → France → Ghana → original knockout source opened successfully |
| Note library | Searching “Ghana” returned relevant match/player notes; seven source readers available |
| Ask | Real local Gemma answer covers 1–1 after 120 minutes, 4–2 shootout, both Muslera saves, and Abreu's deciding chip; reviewed against the displayed S02 passages |
| Citation interaction | Clicking S02-4ae80b7615 expanded the original passage in the evidence panel |
| Search | “Ghana penalty shootout” returned four original passages without a model call |
| Chat | A three-step study plan was followed by “Make that shorter”; the resulting response shortened the same plan |
| Browser console | No error or warning logs observed during the check |
| Automated tests | All 18 passed: 11 existing harness tests plus 7 dashboard HTTP/mode-boundary tests |

## Actual screenshots and traces

- [Homepage](01-dashboard.png)
- [Answer with expanded original evidence](02-answer-sources.png)
- [Narrow-screen layout](03-mobile.png)
- [Seven-match journey and Ghana note](04-match-journey.png)
- [Ghana model trace](../runs/20260930T164349-ask-e5f1ed.json) and [readable card](../runs/20260930T164349-ask-e5f1ed.md)
- [Search trace](../runs/20260930T164529-search-272839.json)
- [Chat plan](../runs/20260930T164549-chat-7a716f.json)
- [Shorter follow-up, including actual prior messages](../runs/20260930T164642-chat-7350b7.json)
- [Automated test output](tests.txt)

The HTTP tests check denied arbitrary file paths, cross-origin requests and untrusted Host headers, malformed requests, rejected system roles in Chat input, discarded history in Ask, search without a model, and busy-worker rejection. Model correctness still requires source review; these checks do not turn exact quotations into a guarantee of semantic correctness.

## Scope and remaining work

The UI calls the same `ask`, `chat_turn`, retrieval, and evidence-saving functions as the CLI. No model prompt or source content was changed for this dashboard. The new launcher also supports `python3 dashboard.py --open` and an alternate `--port`. Model weights and Ollama must already be available for Ask/Chat; browsing and Search use local files.

The original checks above were connected. The [later recorded session](../offline/20261002T191406Z/review.md) now shows disconnected dashboard use and CLI tests; publication of that video awaits approval. Keep the required CLI offline demonstration and additionally capture the dashboard while disconnected. A ready model badge reports runtime availability only.
