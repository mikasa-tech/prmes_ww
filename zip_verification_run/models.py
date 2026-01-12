from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_no = db.Column(db.String(50))
    project_title = db.Column(db.String(255))
    project_guide = db.Column(db.String(128))
    seat_no = db.Column(db.String(64), nullable=False, index=True)
    name = db.Column(db.String(128), nullable=False)
    evaluations = db.relationship("Evaluation", backref="student", lazy=True, cascade="all, delete-orphan")

class Evaluation(db.Model):
    __table_args__ = (
        db.UniqueConstraint('student_id', 'phase', 'review_no', name='uq_eval_student_phase_review'),
    )
    id = db.Column(db.Integer, primary_key=True)
    phase = db.Column(db.Integer, default=1, nullable=False)  # 1 or 2
    review_no = db.Column(db.Integer, default=1, nullable=False)  # 1 or 2
    total_marks = db.Column(db.Integer, nullable=False)
    
    # Generic criteria columns (meaning changes based on phase/review)
    criteria1 = db.Column(db.Integer, nullable=False)  # P1R1: Lit Survey(20), P1R2: Objectives(10), P2: Prelim(15)
    criteria2 = db.Column(db.Integer, nullable=False)  # P1R1: Problem(10), P1R2: Methodology(10), P2: Execution(15)
    criteria3 = db.Column(db.Integer, nullable=False)  # All: Presentation (10/15)
    criteria4 = db.Column(db.Integer, nullable=False)  # All: Q&A (10/15)
    
    # Individual evaluator marks for each criterion
    member1_criteria1 = db.Column(db.Integer, nullable=True)
    member1_criteria2 = db.Column(db.Integer, nullable=True)
    member1_criteria3 = db.Column(db.Integer, nullable=True)
    member1_criteria4 = db.Column(db.Integer, nullable=True)
    
    member2_criteria1 = db.Column(db.Integer, nullable=True)
    member2_criteria2 = db.Column(db.Integer, nullable=True)
    member2_criteria3 = db.Column(db.Integer, nullable=True)
    member2_criteria4 = db.Column(db.Integer, nullable=True)
    
    guide_criteria1 = db.Column(db.Integer, nullable=True)
    guide_criteria2 = db.Column(db.Integer, nullable=True)
    guide_criteria3 = db.Column(db.Integer, nullable=True)
    guide_criteria4 = db.Column(db.Integer, nullable=True)
    
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
