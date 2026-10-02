# Validation and evidence

This page retains historical connected tests. The [2 October recorded offline run](offline/20261002T191406Z/review.md) is now reviewed separately and supplies disconnected-state observations. Its reviewed video is published: [Watch or download the recording](https://github.com/sbardacosta-code/uruguay-2010-wiki/releases/tag/offline-demo-2026-10-02). The README links the latest offline question cards.

## Final reviewed research checks

| Test | Observed result | Evidence |
|---|---|---|
| ask-01 | All three group results and seven points | [Actual trace](runs/20260930T064925-ask-041e45.json) |
| ask-02 | 1–1 after extra time; shootout 4–2; Muslera saves and Abreu’s deciding kick | [Actual trace](runs/20260930T065122-ask-0ddb25.json) |
| ask-03 | Netherlands and Germany both 2–3; fourth overall | [Actual trace](runs/20260930T065140-ask-b91576.json) |
| ask-04 | Explicit insufficient-evidence response to the breakfast question | [Actual trace](runs/20260930T065208-ask-52eb03.json) |

The stage-coverage answer needed a retest: the earlier version omitted the semi-final. The harness now interprets “after the quarter-finals” as the semi-final and subsequent final or third-place match. This supplies stage vocabulary, not an opponent or result. The original question and interpreted question are retained. This is a small, domain-specific rule, not proof of general comprehension.

## Conversation and separation

[Actual chat transcript](evaluation-20260930T055946/chat-transcript.txt): both capability questions received conversational answers; a suggested study plan was shortened using recent context. The model unnecessarily refused a clearly fictional password exercise despite the prompt permitting fiction. That earlier failure is preserved; the revised persona and new chat run accept the labeled fictional example. See the latest audit below. The fictional string was nevertheless in user chat history, and the [independent factual ask](evaluation-20260930T055946/chat-isolation-ask.txt) returned insufficient evidence. Unit checks additionally verify that `ask` receives no chat history.

## Integrity and model-free behavior

- [Eleven unit tests passed](unit-tests.txt). They check original-source substring integrity, original-only indexing, citation rejection, source coverage, routing, local-only endpoints, and history isolation.
- [Re-ingestion evidence](idempotent-ingestion.json): all 13 notes were skipped and their SHA-256 hashes were unchanged.
- [Search evidence](search-with-model-unloaded.json): original passages were returned after `ollama stop`; [runtime list](model-unloaded.txt) was empty. The Ollama server remained available, but no model was loaded or called by search.
- [Obsidian index](obsidian/01-index.png), [reviewed note and source links](obsidian/02-note-sources.png), and [graph](obsidian/03-graph.png) were captured from the actual application.

## Exact model and measured performance

Model: `gemma4:e4b-it-q4_K_M`. Runtime: Ollama `0.35.0`. Format: GGUF. Quantization: `Q4_K_M`. Ollama reports `7.5B` total parameters; E4B is the model variant name, not a claim that the file contains only four billion parameters.

Digest: `dc35e8d9c6061baa6f0fa870975ab6932e2542b579b13ea0f199fa4bb7300c9c`. Download size reported by Ollama: 6,583,656,505 bytes (approximately 6.58 GB).

In the historical sample of 35 measured E4B calls, wall time ranged from 3.71 to 68.77 seconds, with a median of 18.09 seconds. Sampled peak sum of Ollama process RSS was 4,969,283,584 bytes (4.63 GiB).

Some evaluation and ingestion calls overlapped and queued behind the single inference worker, so these timings are observed workflow latency, not an isolated throughput benchmark. Initial loading and cache state also affect timing. RSS was sampled every 0.3 seconds and is not a full measurement of macOS unified-memory or GPU consumption. Raw token counts and runtime timings remain in each trace. The model completed the workload on the 16 GB M4; this is empirical fit for this configuration, not a minimum-memory guarantee.

## Failures and review changes

The E2B candidate produced incomplete group answers and malformed/unsupported quotations. E4B also needed corrections: one Ghana answer joined non-contiguous source fragments into a quotation. The validator rejected it; one corrective model call returned valid quotations. Both attempts are saved in the final trace. One retry is allowed; persistent validation failure is reported rather than silently displayed.

All 13 Gemma-generated notes were reviewed against their originals. Unedited generated versions are retained in `generated-before-review/`, and raw model JSON is preserved in `runs/`. Review corrected an unfinished France summary, clarified that Mexico and South Africa shared points rather than second place, fixed the Netherlands note’s incorrect attribution of Maxi Pereira’s goal, completed Muslera’s two saves, clarified pre-tournament squad data, added source-supported Uruguay qualifying totals and Forlán statistics, and replaced generic related-link descriptions. These are assistant-reviewed notes, not claimed human-reviewed work. The user should inspect them.

## Remaining work

The [recorded offline run](offline/20261002T191406Z/review.md) has been reviewed. Its unedited video is published with explicit approval: [Watch or download the recording](https://github.com/sbardacosta-code/uruguay-2010-wiki/releases/tag/offline-demo-2026-10-02). The regenerated draw note has been reviewed and its original draft preserved. Course-portal submission remains unconfirmed.

## Public-copy privacy note

Local usernames in absolute filesystem paths were replaced with `REDACTED` before publication, including vendor build paths embedded in model metadata. Model answers, quotations, timing measurements, and source snapshots were not changed by this redaction.

## Latest requirement audit

The fresh local Git clone of implementation commit `ddc020c724b1ca595ff7dc8710fb66126ca845c9` had no copied `.local/` cache. Help, status, ingestion, and search succeeded; all 13 reviewed notes retained identical hashes. See the [clone record](clean-clone.json). This reused the Mac's installed Python, Ollama, and model weights and was connected to the internet; it is not a fresh-operating-system or offline test.

The four reviewed results at the top were repeated in that clone. The [complete evaluation](evaluation-20260930T064858/summary.json) records actual commands and separate retrieval/answer reviews. The [chat transcript](evaluation-20260930T064858/chat-transcript.txt) answers both capability prompts, shortens a three-step plan to two steps, and produces an explicitly fictional sentence. The [separate ask](runs/20260930T065541-ask-4163dd.md) abstains on the same fictional password.

Forced fresh Gemma ingestion also succeeded: [terminal output](clean-clone-generation.txt), [model trace](runs/20260930T065600-ingest-10835c.json), and [unaltered generated note](clean-clone-generated-note.md). Total ingestion wall time was 18.484 seconds. Assistant review against S07 confirms Cape Town, the presenters, estimated audience, Jabulani, and both listed groups. The artifact retains its original pending front matter and original vault-relative links as a generation record; use [the original source](../vault/raw/World%20Cup%20Group%20Draw.txt) here. It did not replace the production reviewed note.

All seven HTML snapshots and seven extracted texts passed [source-integrity checks](source-integrity.json). Actual Obsidian navigation reached the original source through a related note; see [navigation evidence](obsidian/Navigation.md). [Available memory and disk](resource-availability.json) were recorded after installation, without inventing earlier measurements.

Two failures found during this audit remain visible:

- [Wrong final rank](runs/20260930T064506-ask-707c1c.md): the model confused playing the third-place fixture with finishing third. The research prompt now requires the final standings row for rank. The [immediate retest](runs/20260930T064809-ask-1d4f19.md) and fresh-clone run both correctly say fourth.
- [South Korea scorer error](runs/20260930T065402-ask-ec83a5.md): the model gave Suarez's two goals correctly, then wrongly added Forlan as a scorer. The revised prompt tells it to stop after covering the question and distinguish an assist from a goal. This is an observed semantic failure despite valid source quotations, so source review remains necessary.

The additional coach question passed. The [additional test record](additional-tests.json) preserves both original outcomes. The final-prompt retests are recorded below. This was a connected development check; the later recorded offline run is linked below. The user's personal review/submission remain separate responsibilities.

### Final prompt retests

The [South Korea retest](runs/20260930T065848-ask-9368a6.md) passes assistant review: Suárez scored in the 8th and 80th minutes. The second claim repeats the winning goal but is supported; the false Forlán scorer claim is absent. Four-case regression results are saved in [the final-prompt regression record](final-prompt-regression.json).

All four final-prompt regression checks pass assistant review. The README cards and `evaluation/questions.json` point to these latest results. The table at the top of this report retains the separately verified fresh-clone run. This finite test set does not guarantee correctness on other questions.

## Recorded offline demonstration — 2 October

The [final run review](offline/20261002T191406Z/review.md) covers fresh ingestion, four passing research tests, chat capabilities and shortening, independent-Ask isolation, and model-free search. It includes before/after network observations, preserved earlier attempts, actual measured traces, and a reviewed generated note. The original 684.245-second recording is published with explicit user approval: [Watch or download the recording](https://github.com/sbardacosta-code/uruguay-2010-wiki/releases/tag/offline-demo-2026-10-02). Historical “pending” statements above describe the earlier development stage and are superseded by this run review.

## Improvements after the recording

The unchanged offline recording and its reviewed outputs remain the baseline evidence. See the [supplemental review](post-recording/README.md) for the later code-readability cleanup, isolated tests, ambiguity handling, and fallible local claim-support review. Supplemental local-model runs do not claim verified internet disconnection. Earlier failures remain preserved.
