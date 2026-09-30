# Offline demonstration

**Status: pending — this page is a procedure, not evidence that a disconnected run occurred.**

The assignment requires CLI ingestion, all four research questions, chat capabilities, a follow-up, original-source search, and chat/ask separation after disconnecting the internet and restarting the CLI. Existing connected local tests are linked from the main README and do not satisfy this requirement by themselves.

## Capture the demonstration

1. While connected, follow [START_HERE](../../START_HERE.md), start the local Ollama server, and confirm `./wiki status` works. Downloads must already be complete.
2. Start a screen recording or prepare to take screenshots. Turn off Wi-Fi and disconnect Ethernet and other internet connections. Show the disconnected state and the terminal in the recording or screenshots.
3. In a new terminal, change to the project folder and run `./scripts/offline_demo.sh`. Type `DISCONNECTED` only after actually disconnecting. The wrapper starts fresh CLI processes and saves real output.
4. Let the complete script finish. Keep failures and error messages. Capture the final output before reconnecting.
5. Review the regenerated World Cup Group Draw note against its original. Reconnect, review all test results, then commit and push the evidence to the same repository.

Each attempt gets its own timestamped subfolder, such as `20260930T070000Z/` (example only). The filenames below live inside that folder. Previous attempts are retained.

## Files to publish after the run

| File | Purpose | Current status |
|---|---|---|
| `environment.txt` | UTC time, user attestation, OS network observations, exact local model/runtime identity | Not captured |
| `network-after.txt` | OS network observations after recording | Not captured |
| `terminal.txt` | Actual offline ingestion, research questions, chat/follow-up, isolation, and model-free search output | Not captured |
| `wifi-off.png` and result screenshots, or a screen recording | Visible network state and real terminal interaction | Not captured |
| `review.md` | Links to this run’s individual cards in `../../runs/` from a timestamped run folder, assessment of answers/citations, and any failures | Not written |

The script creates the network observations and transcript. Individual CLI evidence cards are saved in `evidence/runs/`; the transcript prints their paths. Save visual captures in this folder. For a large recording, use a GitHub release attachment and link it here instead of exceeding GitHub’s file-size limit.

## Review before marking complete

- The network observations and visible capture are consistent with disconnection; Wi-Fi off alone does not rule out Ethernet or another connection.
- Ingestion actually generated a note with local Gemma after disconnection.
- All three answerable questions cover their requested facts with supporting source passages.
- The breakfast question returns insufficient evidence.
- Both capability questions work conversationally, and “make that shorter” uses the previous draft.
- The factual ask does not adopt the fictional chat-only password.
- Search returns original passages with the model unloaded.
- The notes, source references, and evidence files remain readable and traceable.

Do not change this status to complete merely because the script exited. Review the actual outputs, preserve failed attempts, and rerun after any necessary fix. Individual cards say “network disconnection not verified by this record”; the run-level capture provides the additional evidence. Do not rewrite the original model responses to make them pass.

## Optional visual dashboard capture

The new dashboard supplements the required CLI run. While still disconnected, start `python3 dashboard.py --open`, browse a match and its original source, then try Search, Ask, and a Chat follow-up. Record those actual interactions. The badge “Gemma is ready” checks model availability only; it is not an offline attestation. Published-source/license links need internet, while the local originals remain readable without it.
