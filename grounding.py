"""Conservative question clarification and a fallible, local claim-support review.

Quotation validation stays deterministic in wiki.py. This separate model pass
checks meaning and relevance; it is an extra filter, never proof of correctness.
"""

import json
import re
from pathlib import Path

from local_model import LocalModel

ROOT = Path(__file__).resolve().parent
REVIEW_SCHEMA = {
    "type": "object",
    "properties": {
        "checks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "claim": {"type": "integer"},
                    "supported": {"type": "boolean"},
                    "relevant": {"type": "boolean"},
                    "reason": {"type": "string"},
                },
                "required": ["claim", "supported", "relevant", "reason"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["checks"],
    "additionalProperties": False,
}


def clarification_needed(question):
    """Reject unresolved references in independent Ask turns without using history."""
    lower = question.lower()
    match_reference = re.search(
        r"\b(that|this|the previous|the same) (match|game)\b", lower
    )
    named_match = re.search(
        r"\b(ghana|france|south africa|mexico|south korea|netherlands|holland|germany|costa rica)\b",
        lower,
    )
    if match_reference and not named_match:
        return "Please name the match or opponent. Each Ask question is independent; “that match” does not identify a source."
    pronoun = re.search(r"\b(he|his|him|they|their|them)\b", lower)
    entity = re.search(
        r"\b(uruguay|ghana|france|mexico|korea|netherlands|germany|forl[aá]n|su[aá]rez|muslera|abreu|tab[aá]rez)\b",
        lower,
    )
    if pronoun and not entity:
        return "Please name the player or team you mean. This factual question needs an explicit subject before I can check the sources."
    return None


def review_support(question, answer, passages, config):
    """Check every claim using only its cited source, with no chat context.

    A missing, duplicate, malformed, unsupported, or irrelevant verdict rejects the
    whole draft. Raw model output and measurements are retained for human review.
    """
    claims = []
    for number, claim in enumerate(answer["claims"], 1):
        evidence = []
        for item in claim["evidence"]:
            passage = passages[int(item["passage"][1:]) - 1]
            evidence.append({"section": passage["section"], "quote": item["quote"]})
        claims.append({"claim": number, "text": claim["text"], "evidence": evidence})
    messages = [
        {"role": "system", "content": (ROOT / "prompts/verify.txt").read_text()},
        {
            "role": "user",
            "content": json.dumps(
                {"question": question, "claims": claims}, ensure_ascii=False
            ),
        },
    ]
    raw, metadata = LocalModel(config).chat(messages, REVIEW_SCHEMA, max_tokens=900)
    result = {
        "raw_model_output": raw,
        "model": metadata,
        "prompt_messages": messages,
        "accepted": False,
    }
    try:
        checks = json.loads(raw)["checks"]
        expected = list(range(1, len(claims) + 1))
        if (
            len(checks) != len(expected)
            or sorted(check["claim"] for check in checks) != expected
        ):
            raise ValueError("Review must assess every claim exactly once.")
        result["checks"] = checks
        result["accepted"] = all(
            check["supported"] is True and check["relevant"] is True for check in checks
        )
    except (ValueError, TypeError, KeyError) as exc:
        result["error"] = str(exc)
    return result
