# Improvements after the recorded demonstration

The original [video](https://github.com/sbardacosta-code/uruguay-2010-wiki/releases/tag/offline-demo-2026-10-02), [offline transcript](../offline/20261002T191406Z/terminal.txt), and reviewed offline cards remain unchanged. They demonstrate [code at recording: `1a040a5`](https://github.com/sbardacosta-code/uruguay-2010-wiki/tree/1a040a5babb3cdf1a2d045e32fbf6dda2ee4fe17). Later improvements are supplemental work, not replacements for the demonstration. No new recording was made; these local-model runs do not claim verified internet disconnection.

## Changes and reasons

- **Readable code:** expanded compressed statements and data structures, applied consistent formatting, and added explanations at retrieval, ingestion, and answer-validation boundaries. Normal operation still needs only Python's standard library and the installed Ollama runtime.
- **Independent tests:** both integration and harness tests create temporary source indexes. Running tests before ingestion no longer depends on cached state or test order. [All 24 tests pass in a clean checkout](clean-checkout-tests.txt), with [method and code hashes](clean-checkout.json).
- **Ambiguous questions:** unresolved references such as “that match” now ask for an opponent instead of generating an answer from unrelated passages. This conservative heuristic is not full natural-language reference resolution.
- **Meaning as well as quotation checks:** after deterministic quotation validation, a separate local Gemma call checks every claim for source support and relevance. Rejected drafts are suppressed, and raw outputs, verdicts, prompts, and measurements remain inspectable. Uncited free-form model notes are not displayed as verified facts.
- **Actionable repair:** invalid quotations identify the exact claim and evidence item. One correction is allowed; it asks the model to remove unrelated background and use contiguous original text. Persistent failures remain errors, not silent successes.
- **Evaluation reporting:** evaluation scripts return a nonzero exit status for failed CLI commands. Successful execution still does not substitute for source-based assessment.
- **Measured overhead:** records include complete answer-workflow time, including repair and review; the dashboard uses that total. Per-call model measurements remain separate.

## Actual answer checks

The original four expectations were preserved. Additional questions were written in [a separate evaluation file](../../evaluation/improvement-questions.json) outside the searchable corpus before this run.

| Check | Reviewed result | Actual evidence |
|---|---|---|
| ask-01 | Pass: all three scores and seven points agree with the group table and match sections; the dates also occur in the original passages. | [Card](../runs/20261002T195356-ask-fa2e91.md) |
| ask-02 | Pass: 1–1 after extra time, 4–2 penalties, both Muslera saves, and Abreu’s decisive chip match the Ghana source. | [Card](../runs/20261002T200206-ask-ae0d39.md) |
| ask-03 | Pass: Netherlands and Germany each won 3–2; the final standings place Uruguay fourth. | [Card](../runs/20261002T195525-ask-b60b21.md) |
| ask-04 | Pass: explicit abstention; the source collection provides no breakfast information. | [Card](../runs/20261002T195538-ask-85fe04.md) |
| ghana-paraphrase | Pass after repair improvement: the answer identifies a 4–2 penalty shootout. The first supplemental attempt failed quotation validation and is retained. The final generic caveat is conservative; it does not invalidate the supported deciding mechanism. | [Card](../runs/20261002T200124-ask-ed98cc.md) |
| abreu-specific | Pass: Abreu’s decisive chipped penalty is supported; no unrelated match or merged player names appear. | [Card](../runs/20261002T195640-ask-4074b9.md) |
| abreu-ambiguous | Pass: requests the match/opponent without retrieval or a model call. | [Card](../runs/20261002T195640-ask-9229a4.md) |
| korea-scorer | Pass: both goals attributed to Luis Suárez; Forlán is correctly described as supplying a cross, not scoring. | [Card](../runs/20261002T195712-ask-b1ddab.md) |

The [first supplemental batch](../improvements-20261002T195310Z/summary.json) completed seven of eight CLI executions successfully. Its Ghana paraphrase failed with a non-contiguous quotation despite the initial repair. That [failed trace](../runs/20261002T195622-ask-15043a.json) remains unchanged. More specific validation feedback fixed the observed failure; both the paraphrase and original Ghana question were then rerun. The table links the final observed outputs; [structured assessments](reviewed-results.json) distinguish them from expectations.

[Re-ingestion](reingestion.json) rebuilt the index while preserving all thirteen reviewed notes. Model, source snapshots, and ingestion configuration were unchanged.

## Limits of the improvement

A second call to the same model is an extra filter, not independent factual proof. It can repeat the first call's mistake, approve insufficient support, or reject a correct draft. It also adds latency. The original passages and assistant source assessments remain necessary; this is a small regression set, not proof of general accuracy. In the [synthetic adversarial check](adversarial-review.json), the local model accepted “Uruguay finished fourth” and rejected “Uruguay won the tournament” against the same quoted fixture. This demonstrates the extra check on one deliberately constructed case; it is stored separately from historical source evidence.

The recorded offline version remains available at its original commit. The supplemental tests improve the current repository without rewriting the earlier demonstration or claiming a guaranteed grade.
