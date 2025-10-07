from typing import Dict, List
import re

WEIGHTS = {
    "literature_survey": 20,
    "problem_identification": 10,
    "presentation": 10,
    "question_answer": 10,
}
TOTAL_MAX = 50

def normalize_header(h: str) -> str:
    """
    Normalize CSV header names to a stable snake_case token.
    - Removes BOM and non-breaking spaces
    - Lowercases and collapses any non-alphanumeric to single underscores
    - Trims leading/trailing underscores
    """
    s = (h or "")
    # Remove BOM and NBSP and unify whitespace
    s = s.replace("\ufeff", "").replace("\xa0", " ")
    s = s.strip().lower()
    # Replace any run of non-alphanumerics with underscore
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s

def _hamilton_round(values: Dict[str, float], target_sum: int) -> Dict[str, int]:
    # Largest remainder method keeps sum stable and fair
    floors = {k: int(v) for k, v in values.items()}
    remainder = target_sum - sum(floors.values())
    if remainder == 0:
        return floors
    fracs: List[tuple[str, float]] = sorted(((k, values[k] - floors[k]) for k in values), key=lambda x: x[1], reverse=True)
    result = floors.copy()
    for i in range(remainder):
        result[fracs[i % len(fracs)][0]] += 1
    return result

def reverse_engineer_components(total: int) -> Dict[str, int]:
    t = max(0, min(int(total), TOTAL_MAX))
    if t == 0:
        return {k: 0 for k in WEIGHTS}
    # proportional allocation by max weights, then Hamilton rounding to maintain sum
    scaled = {k: (t * (w / TOTAL_MAX)) for k, w in WEIGHTS.items()}
    return _hamilton_round(scaled, t)
