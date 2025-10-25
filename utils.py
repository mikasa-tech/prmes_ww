from typing import Dict, List
import re
from review_config import get_weights_dict

# Default weights for Phase 1 Review 1 (backward compatibility)
WEIGHTS = {
    "criteria1": 20,  # Literature Survey
    "criteria2": 10,  # Problem Identification
    "criteria3": 10,  # Presentation
    "criteria4": 10,  # Q&A
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

def reverse_engineer_components(total: int, phase: int = 1, review: int = 1) -> Dict[str, int]:
    """Reverse engineer component marks from total, using phase/review-specific weights"""
    weights = get_weights_dict(phase, review) or WEIGHTS
    t = max(0, min(int(total), TOTAL_MAX))
    if t == 0:
        return {k: 0 for k in weights}
    # proportional allocation by max weights, then Hamilton rounding to maintain sum
    scaled = {k: (t * (w / TOTAL_MAX)) for k, w in weights.items()}
    return _hamilton_round(scaled, t)
