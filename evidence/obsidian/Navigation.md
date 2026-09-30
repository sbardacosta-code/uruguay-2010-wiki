# Obsidian source navigation check

The assistant performed this sequence through the actual application UI:

1. Opened `vault/index.md` in reading mode.
2. Followed the index link to **Uruguay and Ghana**.
3. Followed its related-note link to **Uruguay and Netherlands**.
4. Clicked **Original local text** in the Netherlands note.
5. Verified TextEdit opened `vault/raw/Knockout Stage Matches.txt` and selected the paragraph beginning “Uruguay played the Netherlands”.

[Source screenshot](04-original-source.png) shows the original passage and score. Text files open in the Mac's associated editor; they are not missing simply because Obsidian's note list hides `.txt` attachments. [Source integrity](../source-integrity.json) checks all downloaded HTML and extracted text against the catalog after navigation. No source text was edited.

This records assistant verification, not a claim that the user personally completed the walkthrough. The earlier index, note/source-links, and graph screenshots remain in this folder. The graph used `path:wiki/` with attachments hidden.
