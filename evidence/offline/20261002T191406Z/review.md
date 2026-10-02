# Recorded offline run review

**The run is complete and its four required research answers pass assistant source review.** The unedited recording is published with explicit user approval. [Watch or download the recording](https://github.com/sbardacosta-code/uruguay-2010-wiki/releases/tag/offline-demo-2026-10-02). It retains the actual desktop and terminal footage; it has not been edited to replace or hide model outputs.

Run: **2 October 2026, 19:14:06–19:16:14 UTC**. Code at recording: `1a040a5babb3cdf1a2d045e32fbf6dda2ee4fe17`. Model: `gemma4:e4b-it-q4_K_M`, Ollama 0.35.0, digest `dc35e8d9c6061baa6f0fa870975ab6932e2542b579b13ea0f199fa4bb7300c9c`.

## Network and visual evidence

- [Before-run environment and model identity](environment.txt): Wi-Fi power off, no IPv4/IPv6 states, reachability “Not Reachable.”
- [After-run network observations](network-after.txt): the same disconnected state.
- [Complete terminal transcript](terminal.txt): fresh CLI processes, help, Gemma ingestion, all four research questions, chat checks, independent ask, model unloading, and search.
- [Recording metadata, SHA-256, and chapter guide](recording.json): original 684.245-second video, no audio track. It shows Wi-Fi switched off near 00:03, dashboard activity, and the CLI run beginning around 08:15. Sampled frames throughout the video and additional frames around network/CLI checkpoints were compared with the full transcript and traces. The recording is published as a release attachment: [Watch or download the recording](https://github.com/sbardacosta-code/uruguay-2010-wiki/releases/tag/offline-demo-2026-10-02).

The video and OS observations are consistent with disconnected execution. The local endpoint and model metadata alone would not establish disconnection. Individual evidence cards retain their original “not verified by this record” label; these run-level observations supply the additional context.

## Required research tests

| Test | Retrieval assessment | Answer assessment | Actual trace |
|---|---|---|---|
| Group stage | S01 standings and all three match passages present | PASS: France 0–0, South Africa 3–0, Mexico 1–0, seven points | [Card](../../runs/20261002T191424-ask-858e53.md) |
| Ghana | S02 match outcome and shootout sequence present | PASS: 1–1 after extra time; 4–2 shootout; Muslera's two saves; Abreu's deciding chip | [Card](../../runs/20261002T191458-ask-470bc4.md) |
| Final matches | S02 later matches plus S06 final standings present | PASS: Netherlands and Germany each won 3–2; Uruguay fourth | [Card](../../runs/20261002T191518-ask-731b81.md) |
| Breakfast | Ghana passages contain no breakfast evidence | PASS: explicit insufficient evidence, no invented meal | [Card](../../runs/20261002T191528-ask-07ba51.md) |

[Machine-readable reviewed results](reviewed-results.json) retain the actual answers. Passage character offsets were checked against unchanged originals, and quoted substrings were checked independently. Semantic source review is separate from these mechanical checks.

## Ingestion and mode checks

[Fresh Gemma ingestion](../../runs/20261002T191413-ingest-e3ff1c.json) generated the World Cup Group Draw note during the disconnected run; [total ingestion time](../../runs/20261002T191413-ingest-summary-fbf157.json) was 5.996 seconds. Its original [generated draft](draw-note-before-review.md) is preserved here; relative source links in that archived draft retain their original vault-relative form. Review against [S07](../../../vault/raw/World%20Cup%20Group%20Draw.txt) confirmed Cape Town, the presenters, audience estimate, Jabulani, and the listed groups. The production note was marked assistant-reviewed, clarified to “round-robin group stage,” and given specific related-link descriptions. No source file was altered.

The [chat transcript](../../runs/20261002T191601-chat-transcript-1a55d5.json) shows both capability prompts answered normally, a three-step study plan shortened to two steps, and an explicitly fictional password sentence. The [independent ask](../../runs/20261002T191613-ask-6997bb.md) then abstains on the password. [Search](../../runs/20261002T191614-search-2e30da.md) returns four original passages after `ollama stop`; `ollama ps` lists no loaded model.

## Dashboard scope and limitations

The recording also shows the UI answering paraphrased group/Ghana questions, opening evidence, abstaining on breakfast, planning and shortening in Chat, labeling a fictional nickname, and retrieving originals. These are supplementary UI checks, not substitutes for the four exact CLI questions. The nickname follow-up in the UI was in **Chat** mode and routed to source research; the separate CLI password test is the actual independent **Ask** isolation check.

Earlier experiments remain visible:

- [Rejected Ghana answer](../../runs/20261002T190151-ask-3516e8.json): a quoted excerpt failed validation after the repair attempt; the system reported the error rather than displaying it as verified.
- [Ambiguous standalone Ask](../../runs/20261002T190349-ask-9723c8.json): “what did Abreu do in that match?” has no explicit match name, and Ask intentionally has no conversation history. It returned unrelated match information. This is a failure of ambiguity handling, not a successful answer. [Naming Ghana explicitly](../../runs/20261002T190512-ask-31b0f1.json) retrieved the intended answer. A future improvement is to request clarification before answering an ambiguous research question.
- [Supplementary UI answer](../../runs/20261002T190829-ask-0e21c6.json): the deciding Abreu claim is supported, but the extra penalty-taker list merges “Victorino Scotti” due to flattened source-table text. Treat that extra wording as a limitation, not a fully correct player list. The fixed CLI Ghana question gives the required supported answer without that list.

These were not silently corrected in saved model outputs. The four final CLI tests passing does not guarantee correctness for all alternative phrasings.

## Earlier attempts

[18:47 run](../20261002T184720Z/terminal.txt) completed before this recording; its network logs and traces are retained. [18:55 attempt](../20261002T185543Z/terminal.txt) ends during the first question and has no after-run network file. It is **incomplete**, with no inferred reason and no success claim.

## Publication

The original video is published with the user's explicit approval as a GitHub release attachment, keeping the 348,722,421-byte file outside Git history. [Watch or download the recording](https://github.com/sbardacosta-code/uruguay-2010-wiki/releases/tag/offline-demo-2026-10-02) · [Direct video download](https://github.com/sbardacosta-code/uruguay-2010-wiki/releases/download/offline-demo-2026-10-02/Celeste-offline-demo.mov). Its SHA-256 and chapter guide are in [recording.json](recording.json). Course-portal submission and the student's personal understanding remain separate user responsibilities.
