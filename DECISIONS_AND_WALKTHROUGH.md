# Project decisions and walkthrough

This guide explains the choices behind the Uruguay 2010 wiki and traces a real question through the application. The user chose the subject, English-language output, and publication of the repository. The assistant proposed and implemented the technical choices below. The user should review this explanation and practice the commands before presenting the project; a written explanation does not establish the user's understanding.

## The three required choices

| Choice | Selected approach | Why | Tradeoff |
|---|---|---|---|
| Data | Uruguay’s qualification and seven-match 2010 World Cup campaign; seven English articles | The user chose Uruguay. These sources support a bounded, inspectable campaign history | Mostly Wikipedia plus Wikinews; seven documents are not seven independent viewpoints |
| Model | Local `gemma4:e4b-it-q4_K_M` with Ollama 0.35.0 | E2B was tried first and gave incomplete answers and invalid quotes; E4B completed the workload on the M4 with 16 GB unified memory | Larger/slower than E2B and still fallible; 26B MoE was unnecessary and would leave little memory headroom |
| Retrieval | SQLite FTS5 keyword search with BM25 ranking and source-section coverage | Small corpus, inspectable passages, no hosted service or extra embedding model | Wording and source organization matter; curated sections are still domain-specific |

E2B and E4B describe effective parameter counts, not total storage or complete application memory. Quantization stores weights with fewer bits to reduce memory needs, with a potential quality tradeoff. A 26B A4B mixture-of-experts model activates a subset for each token but still has the larger total weight footprint. We did not need to test every model size.

The model comparison is an observed development trial, not a controlled benchmark. [Runtime identity](evidence/model-identity.json), [historical measurements](evidence/measurements.json), [device](evidence/device.json), and [current resource availability](evidence/resource-availability.json) provide the exact data. The availability snapshot was collected after installation while the Mac was doing work; it is not a reconstruction of the original setup state.

## Other implementation choices

| Decision | Implemented behavior and reason |
|---|---|
| Runtime and CLI | Ollama performs inference; Python implements the project's connecting code. The CLI uses the standard library, including SQLite FTS5, so normal operation needs no Python package downloads |
| Sources | Unchanged HTML downloads are in `vault/raw/originals/`; extracted text is alongside them in `vault/raw/`. The catalog identifies both. Historical HTML copies in `research/originals/` remain for earlier evidence links |
| Notes | Thirteen subject notes organized into Qualification, Tournament, Matches, and Team. Short filenames and matching headings make Obsidian navigation readable |
| Generation | Local Gemma drafts each note from up to 1,400 words of a source section. The harness supplies links and source labels. The assistant checks and corrects the draft; original outputs remain saved |
| Retrieval size | Up to 240 words per passage, 45-word overlap, six passages per answer. This retains local context while keeping the prompt within an 8,192-token context budget |
| Stage coverage | Stage labels come from headings in the original knockout article. Later-stage queries select matching source sections; query expansion no longer supplies opponent or coach names as answers |
| Model instructions | Separate files for research, persona, and ingestion. Research requires evidence; chat supports suggestions and explicitly labeled fiction |
| Re-ingestion | Fingerprints detect unchanged source text, ingestion prompts, and configuration. A tracked baseline manifest preserves reviewed notes in fresh clones; `.local/` stores subsequent machine-specific state. `--force` backs up and regenerates a note |
| Reproducibility | Temperature 0 and seed 42 reduce variability; they do not guarantee identical results across runtime versions or machines |
| Publication | Source attribution, code, notes, and evidence are public. Model weights, private cache files, and personal Obsidian workspace settings are excluded |

## Trace the Ghana question through the code

In a terminal at the project root, with local Ollama running:

```sh
./wiki search "Ghana penalty shootout"
./wiki ask "How was Uruguay’s match against Ghana decided, and what did Muslera and Abreu do?" --mode local
```

1. **CLI:** the executable `wiki` starts `wiki.py`. Its argument parser sees `ask`, so it calls `ask()` with the question. It does not pass chat history.
2. **Retrieval tool:** `retrieval.search()` queries the local SQLite index. For this named match, it includes the opening narrative and the subsequent shootout passage from `vault/raw/Knockout Stage Matches.txt`. Generated notes and evaluation answer keys are not searched.
3. **RAG prompt:** `ask()` labels the retrieved passages P1, P2, and so on, and combines them with `prompts/research.txt` and the current question. This supplies evidence at inference time; it does not train Gemma.
4. **Local model:** `LocalModel.chat()` sends the prompt to `127.0.0.1:11434`, checks the model's local identity, and records actual timing and memory observations. Gemma returns structured claims and quotations.
5. **Citation check:** `validate_answer()` requires referenced passages to exist and quoted text to occur in them. One repair call is allowed after quotation validation failure. These checks do not independently prove every claim is true.
6. **Display and evidence:** the harness displays the answer with stable source IDs, source paths, and a link to the saved evidence. `save_record()` writes JSON and a readable Markdown card containing the prompt, response, passages, identity, and measurements.
7. **Source review:** open the cited text and verify the material claims. The Ghana source establishes a 1–1 draw after extra time, a 4–2 shootout, Muslera's saves from Mensah and Adiyiah, and Abreu's decisive chip. A citation label by itself is not this review.

The distinction matters: `search` stops at step 2 without generating an answer. `chat` uses `prompts/persona.txt` and recent conversation; factual questions can route to research, while a draft or follow-up can skip retrieval.

## Trace a note in Obsidian

Open `vault/` itself. Open `index.md`, follow **Uruguay and Ghana**, then its related **Uruguay and Netherlands** note. Follow **Original local text**. On this Mac the `.txt` source opens in TextEdit. Find “Uruguay vs Netherlands” and compare the result with the note.

This sequence was performed through the actual UI. The [original-source screenshot](evidence/obsidian/04-original-source.png) shows the text reached from the source link. The three required [Obsidian screenshots](evidence/obsidian/) also show the note, index, and graph. Source hashes were checked after navigation to detect accidental edits.

## Practice explaining the project

You should be able to explain why `search` works without a model, why chat history is excluded from `ask`, why missing evidence leads to abstention, and why a fluent answer with a valid citation can still be wrong. Use the saved failed third-place answer as a concrete example: it cited a genuine match passage but inferred the wrong final rank. The revised instruction directs rank questions to the Final standings table.

The assistant has prepared and tested the implementation. Personal source review, practicing this explanation, the genuinely disconnected demonstration, and submission through the course portal remain user actions. No personal review or offline evidence is claimed on the user's behalf.
