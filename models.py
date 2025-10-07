from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_no = db.Column(db.String(50))
    project_title = db.Column(db.String(255))
    seat_no = db.Column(db.String(64), nullable=False, index=True)
    name = db.Column(db.String(128), nullable=False)
    evaluations = db.relationship("Evaluation", backref="student", lazy=True, cascade="all, delete-orphan")

class Evaluation(db.Model):
    __table_args__ = (
        db.UniqueConstraint('student_id', 'review_no', name='uq_eval_student_review'),
    )
    id = db.Column(db.Integer, primary_key=True)
    review_no = db.Column(db.Integer, default=1, nullable=False)
    total_marks = db.Column(db.Integer, nullable=False)
    literature_survey = db.Column(db.Integer, nullable=False)
    problem_identification = db.Column(db.Integer, nullable=False)
    presentation = db.Column(db.Integer, nullable=False)
    question_answer = db.Column(db.Integer, nullable=False)
    # Individual evaluator marks
    member1_literature = db.Column(db.Integer, nullable=True)
    member1_problem = db.Column(db.Integer, nullable=True)
    member1_presentation = db.Column(db.Integer, nullable=True)
    member1_qa = db.Column(db.Integer, nullable=True)
    member2_literature = db.Column(db.Integer, nullable=True)
    member2_problem = db.Column(db.Integer, nullable=True)
    member2_presentation = db.Column(db.Integer, nullable=True)
    member2_qa = db.Column(db.Integer, nullable=True)
    guide_literature = db.Column(db.Integer, nullable=True)
    guide_problem = db.Column(db.Integer, nullable=True)
    guide_presentation = db.Column(db.Integer, nullable=True)
    guide_qa = db.Column(db.Integer, nullable=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
