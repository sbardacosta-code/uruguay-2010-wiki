"""Deterministic original-source selection, chunking and local FTS5 retrieval."""

import hashlib
import json
import re
import sqlite3
import unicodedata
from pathlib import Path

# Curated boundaries are source locations, never expected answers.
SECTIONS = [
    ("S01", "Group A introduction", None, "Standings"),
    ("S01", "Group A standings", "Standings", "Matches"),
    ("S01", "Uruguay vs France", "Uruguay vs France", "South Africa vs Uruguay"),
    ("S01", "South Africa vs Uruguay", "South Africa vs Uruguay", "France vs Mexico"),
    ("S01", "Mexico vs Uruguay", "Mexico vs Uruguay", "France vs South Africa"),
    (
        "S02",
        "Uruguay vs South Korea",
        "Uruguay vs South Korea",
        "United States vs Ghana",
    ),
    ("S02", "Uruguay vs Ghana", "Uruguay vs Ghana", "Argentina vs Germany"),
    ("S02", "Uruguay vs Netherlands", "Uruguay vs Netherlands", "Germany vs Spain"),
    ("S02", "Match for third place", "Match for third place", "Final"),
    ("S03", "Uruguay squad", "Uruguay", "Group B"),
    ("S04", "South American qualification", None, None),
    ("S05", "Costa Rica playoff", None, None),
    ("S06", "Tournament goalscorers", "Goalscorers", "Discipline"),
    ("S06", "Final standings", "Final standings", "Awards"),
    ("S06", "Individual awards", "Awards", "Marketing"),
    ("S07", "World Cup group draw", None, None),
]
STOP = set(
    "a an and are as at be been by can did do does for from had has have how i in is it its me of on or our that the their them they this to was were what when where which who why with would you your uruguay world cup 2010 please tell about".split()
)


def marker(text, heading, start=0, last=False):
    hits = list(re.finditer(r"(?m)^" + re.escape(heading) + r"\s*$", text))
    hits = [h for h in hits if h.start() >= start]
    if not hits:
        raise ValueError("Missing source section: " + heading)
    return hits[-1 if last else 0].start()


def selected_sections(root):
    """Read only cataloged original sections and verify their saved SHA-256 hashes."""
    catalog = json.loads((root / "research/sources.json").read_text())["sources"]
    sources = {s["id"]: s for s in catalog}
    result = []
    for sid, title, begin, end in SECTIONS:
        source = sources[sid]
        path = root / source["text_path"]
        text = path.read_text(encoding="utf-8")
        if hashlib.sha256(path.read_bytes()).hexdigest() != source["text_sha256"]:
            raise ValueError(
                "Source changed: "
                + source["text_path"]
                + ". Restore it or explicitly refresh the source catalog."
            )
        start = (
            marker(text, begin, last=(title == "Match for third place")) if begin else 0
        )
        finish = marker(text, end, start + len(begin or "")) if end else len(text)
        stage_matches = list(
            re.finditer(
                r"(?m)^(Round of 16|Quarter-finals|Semi-finals|Match for third place|Final)\s*$",
                text[: start + len(begin or "")],
            )
        )
        stage = stage_matches[-1].group(1) if sid == "S02" and stage_matches else None
        result.append(
            dict(
                stage=stage,
                source_id=sid,
                path=source["text_path"],
                section=title,
                start=start,
                end=finish,
                text=text[start:finish],
                source_url=source["permanent_url"],
            )
        )
    return result


def make_chunks(sections, words=240, overlap=45):
    """Create overlapping exact source substrings with stable IDs and offsets."""
    if words <= overlap or overlap < 0:
        raise ValueError("Chunk size must exceed overlap")
    result = []
    for s in sections:
        tokens = list(re.finditer(r"\S+", s["text"]))
        for i in range(0, len(tokens), words - overlap):
            chosen = tokens[i : i + words]
            if not chosen:
                continue
            start = s["start"] + chosen[0].start()
            end = s["start"] + chosen[-1].end()
            body = s["text"][chosen[0].start() : chosen[-1].end()]
            cid = (
                s["source_id"]
                + "-"
                + hashlib.sha256((s["path"] + str(start) + body).encode()).hexdigest()[
                    :10
                ]
            )
            result.append(
                dict(
                    id=cid,
                    source_id=s["source_id"],
                    path=s["path"],
                    section=s["section"],
                    start=start,
                    end=end,
                    text=body,
                    source_url=s["source_url"],
                )
            )
            if i + words >= len(tokens):
                break
    return result


def build_index(root, config):
    """Build a replacement FTS5 index atomically outside the human-readable vault."""
    root = Path(root)
    sections = selected_sections(root)
    chunks = make_chunks(sections, config["chunk_words"], config["overlap_words"])
    directory = root / ".local"
    directory.mkdir(exist_ok=True)
    temp = directory / "index.next.sqlite"
    temp.unlink(missing_ok=True)
    con = sqlite3.connect(temp)
    con.execute(
        'CREATE VIRTUAL TABLE passages USING fts5(id UNINDEXED, source_id UNINDEXED, path UNINDEXED, section, text, start UNINDEXED, end UNINDEXED, source_url UNINDEXED, tokenize="porter unicode61 remove_diacritics 2")'
    )
    con.executemany(
        "INSERT INTO passages VALUES (:id,:source_id,:path,:section,:text,:start,:end,:source_url)",
        chunks,
    )
    con.commit()
    con.close()
    temp.replace(directory / "index.sqlite")
    return dict(
        sources=len(set(c["source_id"] for c in chunks)),
        sections=len(sections),
        passages=len(chunks),
    )


def query_terms(query):
    """Normalize search vocabulary without inserting factual answers."""
    normalized = "".join(
        c
        for c in unicodedata.normalize("NFKD", query.lower())
        if not unicodedata.combining(c)
    )
    terms = [
        x for x in re.findall(r"[a-z0-9]+", normalized) if x not in STOP and len(x) > 1
    ]
    if "group" in terms:
        terms += ["standings"]
    if "after" in terms and ("quarter" in terms or "quarters" in terms):
        terms += ["semi", "final", "third", "standings"]
    if "holland" in terms:
        terms += ["netherlands"]
    if any(t.startswith("coach") or t == "manager" for t in terms):
        terms += ["coach", "manager"]
    return list(dict.fromkeys(terms))[:30]


def search(root, query, limit=6):
    """Rank original passages and preserve useful coverage of requested matches."""
    db = Path(root) / ".local/index.sqlite"
    if not db.exists():
        raise ValueError("No index. Run ./wiki ingest vault/raw --index-only first.")
    terms = query_terms(query)
    if not terms:
        return []
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT *, bm25(passages,0,0,0,2,1,0,0,0) AS rank FROM passages WHERE passages MATCH ? ORDER BY rank LIMIT 60",
        (" OR ".join('"' + t + '"' for t in terms),),
    ).fetchall()
    con.close()
    # Prefer Uruguay match sections over incidental references to other teams.
    ranked = []
    for row in rows:
        item = dict(row)
        title = item["section"].lower()
        bonus = sum(t in title for t in terms) * 1.4
        if "group" in terms and item["source_id"] == "S01":
            bonus += 3
        item["score"] = -item.pop("rank") + bonus
        ranked.append(item)
    ranked.sort(key=lambda r: r["score"], reverse=True)
    # Broad group-stage questions need coverage across the stage, not six near-duplicates.
    # Named-match questions receive the original opening narrative before supporting details.
    preferred = []
    later_rounds = "after" in terms and ("quarter" in terms or "quarters" in terms)
    if later_rounds:
        preferred = [
            s["section"]
            for s in selected_sections(Path(root))
            if s.get("stage") in ("Semi-finals", "Match for third place")
        ]
        preferred.append("Final standings")
    elif "group" in terms and any(
        t in terms for t in ["results", "matches", "stage", "points"]
    ):
        preferred = [
            "Group A standings",
            "Uruguay vs France",
            "South Africa vs Uruguay",
            "Mexico vs Uruguay",
        ]
    else:
        for _, title, _, _ in SECTIONS:
            if " vs " in title and any(
                t in title.lower()
                for t in terms
                if t in ["ghana", "france", "mexico", "korea", "netherlands"]
            ):
                preferred.append(title)
        if "germany" in terms:
            preferred.append("Match for third place")
    selected = []
    counts = {}
    if preferred:
        con = sqlite3.connect(db)
        con.row_factory = sqlite3.Row
        for title in preferred:
            row = con.execute(
                "SELECT * FROM passages WHERE section=? ORDER BY CAST(start AS INTEGER) LIMIT 2",
                (title,),
            ).fetchall()
            for candidate in row:
                if len(selected) >= limit:
                    break
                # One opening passage per match in broad stage queries; two for a single match.
                if len(preferred) > 1 and counts.get(
                    (candidate["source_id"], candidate["section"]), 0
                ):
                    continue
                item = dict(candidate)
                item["score"] = None
                selected.append(item)
                key = (item["source_id"], item["section"])
                counts[key] = counts.get(key, 0) + 1
        con.close()
    for item in ranked:
        key = (item["source_id"], item["section"])
        if len(selected) >= limit:
            break
        if any(p["id"] == item["id"] for p in selected):
            continue
        if len(preferred) == 1 and item["section"] != preferred[0]:
            continue
        if (
            "group" in terms
            and any(t in terms for t in ["results", "matches", "stage", "points"])
            and item["source_id"] != "S01"
        ):
            continue
        if counts.get(key, 0) >= (4 if len(preferred) == 1 else 2):
            continue
        selected.append(item)
        counts[key] = counts.get(key, 0) + 1
        if len(selected) == limit:
            break
    return selected
