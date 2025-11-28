"""
Upload Helper Functions
Handles dynamic column mapping based on phase/review
"""

from typing import Dict, Tuple
from review_config import get_review_config
from utils import reverse_engineer_components

def map_excel_columns_to_criteria(row: Dict, key_map: Dict, phase: int, review: int) -> Tuple[Dict, Dict, Dict, Dict]:
    """
    Map Excel columns to generic criteria based on phase/review
    Returns: (comp, member1_comp, member2_comp, guide_comp)
    """
    config = get_review_config(phase, review)
    if not config:
        raise ValueError(f"No configuration found for Phase {phase} Review {review}")
    
    # Check if we have three evaluator totals
    if all(k in key_map for k in ("member1", "member2", "internal_guide")):
        return handle_three_evaluators(row, key_map, phase, review)
    
    # Check if we have individual component columns
    # Try to find columns matching the criteria names for this phase/review
    criteria_columns = {}
    for i, criterion in enumerate(config['criteria'], 1):
        criterion_name = criterion['name'].lower()
        # Try to find matching column
        for key, col_name in key_map.items():
            normalized_key = key.lower().replace('_', ' ').replace('-', ' ')
            if criterion_name.replace('_', ' ') in normalized_key or normalized_key in criterion_name.replace('_', ' '):
                criteria_columns[f'criteria{i}'] = col_name
                break
    
    if len(criteria_columns) == 4:
        return handle_component_columns(row, criteria_columns, phase, review)
    
    # Fall back to total marks
    if "total" in key_map:
        return handle_total_marks(row, key_map, phase, review)
    
    raise ValueError("Excel file must contain either: three evaluator totals, all four component columns, or total marks")

def handle_three_evaluators(row: Dict, key_map: Dict, phase: int, review: int) -> Tuple[Dict, Dict, Dict, Dict]:
    """Handle Excel with Member 1, Member 2, Internal Guide total marks"""
    member1_total = int(float(row.get(key_map["member1"], 0)))
    member2_total = int(float(row.get(key_map["member2"], 0)))
    guide_total = int(float(row.get(key_map["internal_guide"], 0)))
    
    # Reverse engineer components for each evaluator
    member1_comp = reverse_engineer_components(member1_total, phase, review)
    member2_comp = reverse_engineer_components(member2_total, phase, review)
    guide_comp = reverse_engineer_components(guide_total, phase, review)
    
    # Calculate average components (only count non-zero evaluators)
    comp = {}
    for key in member1_comp.keys():
        m1 = member1_comp[key]
        m2 = member2_comp[key]
        g = guide_comp[key]
        
        # Count how many evaluators actually provided marks (non-zero)
        evaluators = [m1, m2, g]
        non_zero_evaluators = [val for val in evaluators if val > 0]
        
        if non_zero_evaluators:
            comp[key] = int(round(sum(non_zero_evaluators) / len(non_zero_evaluators)))
        else:
            comp[key] = 0
    
    return comp, member1_comp, member2_comp, guide_comp

def handle_component_columns(row: Dict, criteria_columns: Dict, phase: int, review: int) -> Tuple[Dict, Dict, Dict, Dict]:
    """Handle Excel with individual component columns"""
    comp = {}
    for criteria_key, col_name in criteria_columns.items():
        comp[criteria_key] = int(float(row.get(col_name, 0)))
    
    # Use same marks for all evaluators
    member1_comp = comp.copy()
    member2_comp = comp.copy()
    guide_comp = comp.copy()
    
    return comp, member1_comp, member2_comp, guide_comp

def handle_total_marks(row: Dict, key_map: Dict, phase: int, review: int) -> Tuple[Dict, Dict, Dict, Dict]:
    """Handle Excel with only total marks"""
    raw_total = float(row.get(key_map["total"], 0))
    total = int(round(raw_total))
    
    # Normalize if out of range
    TOTAL_MAX = 50
    if total > TOTAL_MAX:
        if total <= 100:
            total = int(round((raw_total / 100.0) * TOTAL_MAX))
        else:
            total = TOTAL_MAX
    
    comp = reverse_engineer_components(total, phase, review)
    
    # Use same marks for all evaluators
    member1_comp = comp.copy()
    member2_comp = comp.copy()
    guide_comp = comp.copy()
    
    return comp, member1_comp, member2_comp, guide_comp

def get_criteria_key_map(phase: int, review: int) -> Dict[str, str]:
    """
    Get mapping of expected Excel column names to criteria keys
    Returns dict like {'objectives': 'criteria1', 'methodology': 'criteria2', ...}
    """
    config = get_review_config(phase, review)
    if not config:
        return {}
    
    mapping = {}
    for i, criterion in enumerate(config['criteria'], 1):
        # Create multiple possible column names for this criterion
        base_name = criterion['name'].lower()
        mapping[base_name] = f'criteria{i}'
        # Also try without spaces and with underscores
        mapping[base_name.replace(' ', '')] = f'criteria{i}'
        mapping[base_name.replace(' ', '_')] = f'criteria{i}'
        mapping[base_name.replace('&', 'and')] = f'criteria{i}'
    
    return mapping
