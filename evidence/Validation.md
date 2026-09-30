# Validation and evidence

These are actual local runs on the user’s Mac, reviewed by the assistant against source passages. They are not proof that internet access was disconnected. The user should review the results before submission.

## Final reviewed research checks

| Test | Observed result | Evidence |
|---|---|---|
| ask-01 | All three group results and seven points | [Actual trace](runs/20260930T060024-ask-e61788.json) |
| ask-02 | 1–1 after extra time; shootout 4–2; Muslera saves and Abreu’s deciding kick | [Actual trace](runs/20260930T060212-ask-e0d205.json) |
| ask-03 | Netherlands and Germany both 2–3; fourth overall | [Actual trace](runs/20260930T060436-ask-556a03.json) |
| ask-04 | Explicit insufficient-evidence response to the breakfast question | [Actual trace](runs/20260930T060310-ask-12c3dd.json) |

The stage-coverage answer needed a retest: the earlier version omitted the semi-final. The harness now interprets “after the quarter-finals” as the semi-final and subsequent final or third-place match. This supplies stage vocabulary, not an opponent or result. The original question and interpreted question are retained. This is a small, domain-specific rule, not proof of general comprehension.

## Conversation and separation

[Actual chat transcript](evaluation-20260930T055946/chat-transcript.txt): both capability questions received conversational answers; a suggested study plan was shortened using recent context. The model unnecessarily refused a clearly fictional password exercise despite the prompt permitting fiction. This remains a chat limitation. The fictional string was nevertheless in user chat history, and the [independent factual ask](evaluation-20260930T055946/chat-isolation-ask.txt) returned insufficient evidence. Unit checks additionally verify that `ask` receives no chat history.

## Integrity and model-free behavior

- [Nine unit tests passed](unit-tests.txt). They check original-source substring integrity, original-only indexing, citation rejection, source coverage, routing, local-only endpoints, and history isolation.
- [Re-ingestion evidence](idempotent-ingestion.json): all 13 notes were skipped and their SHA-256 hashes were unchanged.
- [Search evidence](search-with-model-unloaded.json): original passages were returned after `ollama stop`; [runtime list](model-unloaded.txt) was empty. The Ollama server remained available, but no model was loaded or called by search.
- [Obsidian index](obsidian/01-index.png), [reviewed note and source links](obsidian/02-note-sources.png), and [graph](obsidian/03-graph.png) were captured from the actual application.

## Exact model and measured performance

Model: `gemma4:e4b-it-q4_K_M`. Runtime: Ollama `0.35.0`. Format: GGUF. Quantization: `Q4_K_M`. Ollama reports `7.5B` total parameters; E4B is the model variant name, not a claim that the file contains only four billion parameters.

Digest: `dc35e8d9c6061baa6f0fa870975ab6932e2542b579b13ea0f199fa4bb7300c9c`. Download size reported by Ollama: 6,583,656,505 bytes (approximately 6.58 GB).

Across 35 measured E4B calls, wall time ranged from 3.71 to 68.77 seconds, with a median of 18.09 seconds. Sampled peak sum of Ollama process RSS was 4,969,283,584 bytes (4.63 GiB).

Some evaluation and ingestion calls overlapped and queued behind the single inference worker, so these timings are observed workflow latency, not an isolated throughput benchmark. Initial loading and cache state also affect timing. RSS was sampled every 0.3 seconds and is not a full measurement of macOS unified-memory or GPU consumption. Raw token counts and runtime timings remain in each trace. The model completed the workload on the 16 GB M4; this is empirical fit for this configuration, not a minimum-memory guarantee.

## Failures and review changes

The E2B candidate produced incomplete group answers and malformed/unsupported quotations. E4B also needed corrections: one Ghana answer joined non-contiguous source fragments into a quotation. The validator rejected it; one corrective model call returned valid quotations. Both attempts are saved in the final trace. One retry is allowed; persistent validation failure is reported rather than silently displayed.

All 13 Gemma-generated notes were reviewed against their originals. Unedited generated versions are retained in `generated-before-review/`, and raw model JSON is preserved in `runs/`. Review corrected an unfinished France summary, clarified that Mexico and South Africa shared points rather than second place, fixed the Netherlands note’s incorrect attribution of Maxi Pereira’s goal, completed Muslera’s two saves, clarified pre-tournament squad data, added source-supported Uruguay qualifying totals and Forlán statistics, and replaced generic related-link descriptions. These are assistant-reviewed notes, not claimed human-reviewed work. The user should inspect them.

## Remaining work

Run `./scripts/offline_demo.sh` from the project as described in START_HERE after actually disconnecting Wi-Fi/Ethernet. No offline demonstration has been claimed or fabricated. Review the newly regenerated draw note afterward. The repository is published at https://github.com/sbardacosta-code/uruguay-2010-wiki; course-portal submission has not been done.

## Public-copy privacy note

Local usernames in absolute filesystem paths were replaced with `REDACTED` before publication, including vendor build paths embedded in model metadata. Model answers, quotations, timing measurements, and source snapshots were not changed by this redaction.
