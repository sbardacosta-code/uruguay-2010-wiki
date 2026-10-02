# Celeste visual dashboard

The browser dashboard is an additional interface to the existing local wiki. It does not replace the CLI required by the assignment.

## Open it

Start Ollama using the existing setup instructions. On macOS, double-click **Open Celeste.command**, or run this from the repository folder:

```sh
python3 dashboard.py --open
```

The default URL is **http://127.0.0.1:8000**. Keep the launcher terminal open. Ctrl+C stops the dashboard. Use `--port 8001` if another application already uses port 8000. If the dashboard is already running, simply reopen its URL.

Browsing notes, match cards, original sources, and source search do not require Gemma to be loaded. Ask and Chat require the configured local model. The status button checks model availability; it does not claim the internet is disconnected.

## What to explore

- **Home:** campaign overview, seven scorecards, Forlán's five goals, and a Ghana feature.
- **Journey:** select a match for its score, venue, scorers, reviewed wiki note, related notes, and original source.
- **Library:** filter notes by text/category and open all seven original source snapshots.
- **Celeste:** Ask for independent sourced answers, Chat for contextual follow-ups, or Search for original passages without a model call. Click a citation to expand its passage. Saved JSON traces are inspectable from each response.

Chat history lasts only in the current browser tab. Clear conversation removes it from the interface, but previously saved evidence traces remain in `evidence/runs/`. Reloading clears the browser conversation. Failed requests retain the question for retry. The local inference worker admits one dashboard model request at a time; source browsing and search remain available.

## Implementation and boundaries

`dashboard.py` uses Python's standard library and binds only to loopback. It calls the existing `wiki.ask`, `wiki.chat_turn`, and original-source retrieval functions. Ask discards incoming history. Only Chat accepts up to five previous exchanges; supplied system messages are rejected. Same-origin and Host checks, bounded JSON requests, explicit file routes, and DOM text rendering keep browser input out of arbitrary filesystem/HTML execution paths.

The site uses vanilla JavaScript, local CSS, system fonts, and a repository-authored SVG shirt illustration. There are no CDNs, analytics, external font requests, frontend package installs, or cloud-model services. Published-source/license links open external pages only when clicked; the original text is available locally. Historical match data and reviewed notes are the existing repository artifacts, not newly generated dashboard copy. Illustrative art is not a historical photograph or official kit reproduction.

## Verification

See [dashboard validation](../evidence/dashboard/README.md) for actual tests and screenshots. Automated coverage includes HTTP routing, cross-origin rejection, source access boundaries, chat-role validation, history isolation, model-free search, and busy-worker behavior. Browser checks cover navigation and actual local inference.

Dashboard interactions have now been reviewed in the [recorded disconnected session](../evidence/offline/20261002T191406Z/review.md); publication of the recording awaits approval. After installation/downloads, disconnect the internet, open the dashboard, and try Journey, Library, Search, Ask, and Chat. Capture real results alongside the required CLI demonstration. Online local testing is not evidence of disconnection.
