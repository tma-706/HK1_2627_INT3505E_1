"""Deterministic matching stub used for API testing, not an AI model."""

import re


MODEL_VERSION = "mock-keyword-v1"


def _tokens(value):
    return set(re.findall(r"\w+", (value or "").lower(), flags=re.UNICODE))


def _score(query_post, candidate_post):
    score = 0.0
    evidence = []

    if query_post.category.casefold() == candidate_post.category.casefold():
        score += 0.45
        evidence.append("same category")

    if query_post.location.casefold() == candidate_post.location.casefold():
        score += 0.25
        evidence.append("same location")

    query_words = _tokens(f"{query_post.title} {query_post.description}")
    candidate_words = _tokens(
        f"{candidate_post.title} {candidate_post.description}"
    )
    union = query_words | candidate_words
    overlap = (len(query_words & candidate_words) / len(union)) if union else 0.0
    if overlap:
        score += 0.30 * overlap
        evidence.append("overlapping description keywords")

    return round(min(score, 1.0), 4), evidence


def rank_candidates(query_post, candidates, limit):
    ranked = []
    for candidate in candidates:
        score, evidence = _score(query_post, candidate)
        if score <= 0:
            continue
        ranked.append((candidate, score, evidence))

    ranked.sort(key=lambda entry: (-entry[1], entry[0].id))

    items = []
    for rank, (candidate, score, evidence) in enumerate(ranked[:limit], start=1):
        if score >= 0.7:
            confidence = "HIGH"
        elif score >= 0.4:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        items.append(
            {
                "candidate_post_id": candidate.id,
                "rank": rank,
                "score": score,
                "confidence_level": confidence,
                "evidence": evidence,
                "model_version": MODEL_VERSION,
                "candidate": candidate.to_dict(),
            }
        )

    return items
