"""
Review Configuration
Defines criteria and marks for each phase/review combination
"""

REVIEW_CRITERIA = {
    (1, 1): {  # Phase 1 Review 1
        'criteria': [
            {'name': 'Literature Survey', 'db_field': 'criteria1', 'max_marks': 20, 'guide_marks': True},
            {'name': 'Problem Identification', 'db_field': 'criteria2', 'max_marks': 10, 'guide_marks': True},
            {'name': 'Project presentation skill', 'db_field': 'criteria3', 'max_marks': 10, 'guide_marks': False},
            {'name': 'Question and answer session', 'db_field': 'criteria4', 'max_marks': 10, 'guide_marks': False},
        ],
        'total': 50,
        'guide_section_label': 'Marks allotted by Project Guide',
        'committee_section_label': 'Marks allotted by Committee',
        'title': 'PHASE - I REVIEW - I'
    },
    (1, 2): {  # Phase 1 Review 2
        'criteria': [
            {'name': 'Objectives', 'db_field': 'criteria1', 'max_marks': 10, 'guide_marks': True},
            {'name': 'Methodology', 'db_field': 'criteria2', 'max_marks': 10, 'guide_marks': True},
            {'name': 'Project presentation skill', 'db_field': 'criteria3', 'max_marks': 15, 'guide_marks': False},
            {'name': 'Question and answer session', 'db_field': 'criteria4', 'max_marks': 15, 'guide_marks': False},
        ],
        'total': 50,
        'guide_section_label': 'Marks allotted by Project Guide',
        'committee_section_label': 'Marks allotted by Committee',
        'title': 'PHASE - I REVIEW - II'
    },
    (2, 1): {  # Phase 2 Review 1
        'criteria': [
            {'name': 'Preliminary studies', 'db_field': 'criteria1', 'max_marks': 15, 'guide_marks': True},
            {'name': 'Execution & Result Analysis', 'db_field': 'criteria2', 'max_marks': 15, 'guide_marks': True},
            {'name': 'Project presentation skill', 'db_field': 'criteria3', 'max_marks': 10, 'guide_marks': False},
            {'name': 'Question and answer session', 'db_field': 'criteria4', 'max_marks': 10, 'guide_marks': False},
        ],
        'total': 50,
        'guide_section_label': 'Marks allotted by Project Guide',
        'committee_section_label': 'Marks allotted by Committee',
        'title': 'PHASE - II REVIEW - I'
    },
    (2, 2): {  # Phase 2 Review 2
        'criteria': [
            {'name': 'Conclusion & Future scope of work', 'db_field': 'criteria1', 'max_marks': 10, 'guide_marks': True},
            {'name': 'Publication of project work', 'db_field': 'criteria2', 'max_marks': 10, 'guide_marks': True},
            {'name': 'Project presentation skill', 'db_field': 'criteria3', 'max_marks': 15, 'guide_marks': False},
            {'name': 'Question and answer session', 'db_field': 'criteria4', 'max_marks': 15, 'guide_marks': False},
        ],
        'total': 50,
        'guide_section_label': 'Marks allotted by Project Guide',
        'committee_section_label': 'Marks allotted by Committee',
        'title': 'PHASE - II REVIEW - II'
    }
}

def get_review_config(phase, review):
    """Get configuration for a specific phase and review"""
    return REVIEW_CRITERIA.get((phase, review))

def get_criteria_labels(phase, review):
    """Get criteria labels for a specific phase and review"""
    config = get_review_config(phase, review)
    if config:
        return [c['name'] for c in config['criteria']]
    return []

def get_max_marks(phase, review):
    """Get max marks for each criterion"""
    config = get_review_config(phase, review)
    if config:
        return [c['max_marks'] for c in config['criteria']]
    return []

def get_weights_dict(phase, review):
    """Get weights dictionary for reverse engineering"""
    config = get_review_config(phase, review)
    if not config:
        return {}
    
    weights = {}
    for i, criterion in enumerate(config['criteria'], 1):
        weights[f"criteria{i}"] = criterion['max_marks']
    return weights
