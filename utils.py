from typing import Dict, List

WEIGHTS = {
    "literature_survey": 20,
    "problem_identification": 10,
    "presentation": 10,
    "question_answer": 10,
}
TOTAL_MAX = 50

def normalize_header(h: str) -> str:
    return (h or "").strip().lower().replace(" ", "_")

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