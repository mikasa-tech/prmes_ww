import io
import os
import csv
from pathlib import Path
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from models import db, Student, Evaluation
from utils import reverse_engineer_components, normalize_header, TOTAL_MAX
from pdf_template import build_review1_pdf
from comprehensive_pdf_template import build_comprehensive_pdf
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy import text
from openpyxl import load_workbook

APP_DIR = Path(__file__).parent.resolve()
EXPORTS_DIR = APP_DIR / "exports"

def create_app() -> Flask:
    # Load .env if present
    load_dotenv()

    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret"

    # Optional MySQL auto-creation if envs provided; fallback to SQLite
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASS", "")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME")

    if db_host and db_user and db_name:
        # Ensure database exists
        engine_no_db = sqlalchemy.create_engine(
            f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/?charset=utf8mb4",
            future=True,
        )
        with engine_no_db.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{db_name}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"))
        app.config["SQLALCHEMY_DATABASE_URI"] = (
            f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
        )
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{APP_DIR/'app.db'}"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()

    @app.route("/")
    def index():
        return redirect(url_for("upload_csv"))

    @app.route("/upload", methods=["GET", "POST"])
    def upload_csv():
        if request.method == "POST":
            file = request.files.get("file")
            if not file or file.filename.strip() == "":
                flash("Please choose an .xlsx file.", "error")
                return redirect(request.url)

            filename = file.filename.lower().strip()
            if not filename.endswith(".xlsx"):
                flash("Only .xlsx files are accepted.", "error")
                return redirect(request.url)

            # Read Excel (.xlsx) with openpyxl
            raw = file.stream.read()
            try:
                wb = load_workbook(io.BytesIO(raw), data_only=True)
            except Exception:
                flash("Could not read the .xlsx file. Please ensure it is a valid Excel file.", "error")
                return redirect(request.url)
            ws = wb.active

            header_row = next(ws.iter_rows(min_row=1, max_row=1, values_only=True), tuple())
            fieldnames = [str(v) if v is not None else "" for v in header_row]
            headers = [normalize_header(h) for h in fieldnames]

            def iter_rows_dict():
                for vals in ws.iter_rows(min_row=2, values_only=True):
                    row = {}
                    for i, key in enumerate(fieldnames):
                        val = vals[i] if i < len(vals) else None
                        row[key] = val
                    yield row
            rows_iter = iter_rows_dict()

            # Map common header names to our keys
            # Required: student name, seat no. Optional: group no, project title, evaluator marks.
            key_map = {}
            for raw in fieldnames or []:
                h = normalize_header(raw)
                if h in ("name", "student_name"):
                    key_map["name"] = raw
                elif h in ("seat_no", "seatno", "usn", "univ_seat_no"):
                    key_map["seat_no"] = raw
                elif h in ("total", "total_marks", "average", "avg"):
                    key_map["total"] = raw
                elif h in ("group", "group_no", "group_number", "project_group"):
                    key_map["group_no"] = raw
                elif h in ("project_title", "title"):
                    key_map["project_title"] = raw
                elif h in ("project_guide",):
                    key_map["project_guide"] = raw
                elif h in ("member1", "member_1", "chairperson"):
                    key_map["member1"] = raw
                elif h in ("member2", "member_2"):
                    key_map["member2"] = raw
                elif h in ("internal_guide", "guide", "project_guide"):
                    key_map["internal_guide"] = raw
                elif h in ("literature", "literature_survey"):
                    key_map["literature_survey"] = raw
                elif h in ("problem", "problem_identification"):
                    key_map["problem_identification"] = raw
                elif h in ("presentation", "project_presentation_skill", "presentation_skill"):
                    key_map["presentation"] = raw
                elif h in ("qa", "qna", "question_answer", "question_and_answer_session"):
                    key_map["question_answer"] = raw

            missing = [k for k in ("name", "seat_no") if k not in key_map]
            has_components = all(k in key_map for k in ("literature_survey","problem_identification","presentation","question_answer"))
            has_three_evaluators = all(k in key_map for k in ("member1","member2","internal_guide"))
            if "total" not in key_map and not has_components and not has_three_evaluators:
                missing.append("total or all four component columns or Member 1 + Member 2 + Internal Guide")
            if missing:
                flash(f"Excel file missing required columns: {', '.join(missing)}", "error")
                return redirect(request.url)

            # Replace all existing data before importing new Excel (no UI toggle)
            try:
                # Delete in FK-safe order
                db.session.execute(text("DELETE FROM evaluation"))
                db.session.execute(text("DELETE FROM student"))
                db.session.commit()
            except Exception:
                db.session.rollback()
                flash("Failed to reset existing data before import.", "error")
                return redirect(request.url)

            created = 0
            for row in rows_iter:
                name = str(row.get(key_map["name"]) or "").strip()
                seat_no = str(row.get(key_map["seat_no"]) or "").strip()
                if not name or not seat_no:
                    continue

                group_no = str(row.get(key_map.get("group_no", ""), "") or "").strip()
                project_title = str(row.get(key_map.get("project_title", ""), "") or "").strip()
                project_guide = str(row.get(key_map.get("project_guide", ""), "") or "").strip()

                student = Student.query.filter_by(seat_no=seat_no).one_or_none()
                if not student:
                    student = Student(name=name, seat_no=seat_no, group_no=group_no, project_title=project_title, project_guide=project_guide)
                    db.session.add(student)
                else:
                    # update optional meta if provided
                    if group_no:
                        student.group_no = group_no
                    if project_title:
                        student.project_title = project_title
                    if project_guide:
                        student.project_guide = project_guide

                # Handle different input formats
                if "member1" in key_map and "member2" in key_map and "internal_guide" in key_map:
                    # Three evaluator format - use their marks directly
                    try:
                        member1_total = int(float(row.get(key_map["member1"], 0)))
                        member2_total = int(float(row.get(key_map["member2"], 0)))
                        guide_total = int(float(row.get(key_map["internal_guide"], 0)))
                        
                        # Calculate average of three evaluators
                        total = int(round((member1_total + member2_total + guide_total) / 3))
                        
                        # Distribute each evaluator's total across components proportionally
                        member1_comp = reverse_engineer_components(member1_total)
                        member2_comp = reverse_engineer_components(member2_total)
                        guide_comp = reverse_engineer_components(guide_total)
                        
                        # Calculate average components from the three evaluators
                        comp = {
                            "literature_survey": int(round((member1_comp["literature_survey"] + member2_comp["literature_survey"] + guide_comp["literature_survey"]) / 3)),
                            "problem_identification": int(round((member1_comp["problem_identification"] + member2_comp["problem_identification"] + guide_comp["problem_identification"]) / 3)),
                            "presentation": int(round((member1_comp["presentation"] + member2_comp["presentation"] + guide_comp["presentation"]) / 3)),
                            "question_answer": int(round((member1_comp["question_answer"] + member2_comp["question_answer"] + guide_comp["question_answer"]) / 3)),
                        }
                        
                        # Ensure total matches the calculated components
                        total = sum(comp.values())
                        
                    except Exception:
                        flash("Invalid evaluator marks in Excel.", "error")
                        return redirect(request.url)
                        
                elif "literature_survey" in key_map:
                    # Component marks provided directly
                    try:
                        comp = {
                            "literature_survey": int(float(row.get(key_map["literature_survey"], 0))),
                            "problem_identification": int(float(row.get(key_map["problem_identification"], 0))),
                            "presentation": int(float(row.get(key_map["presentation"], 0))),
                            "question_answer": int(float(row.get(key_map["question_answer"], 0))),
                        }
                        total = sum(comp.values())
                        # Use same marks for all evaluators
                        member1_comp = comp.copy()
                        member2_comp = comp.copy()
                        guide_comp = comp.copy()
                    except Exception:
                        flash("Invalid component values in Excel.", "error")
                        return redirect(request.url)
                else:
                    # Total marks only - reverse engineer components
                    try:
                        raw_total = float(row.get(key_map["total"], 0))
                        total = int(round(raw_total))
                    except Exception:
                        flash("Invalid total marks value in Excel.", "error")
                        return redirect(request.url)

                    # Normalize totals that are out of 50 (e.g., out of 100)
                    if total > TOTAL_MAX:
                        if total <= 100:
                            # Scale percentage-like totals to the 50 mark scheme
                            scaled = int(round((raw_total / 100.0) * TOTAL_MAX))
                            total_for_components = max(0, min(scaled, TOTAL_MAX))
                        else:
                            # Clamp unexpected larger values
                            total_for_components = TOTAL_MAX
                    else:
                        total_for_components = total

                    comp = reverse_engineer_components(total_for_components)
                    # Use same marks for all evaluators
                    member1_comp = comp.copy()
                    member2_comp = comp.copy()
                    guide_comp = comp.copy()
                    total = sum(comp.values())

                # Upsert: one evaluation per student per review
                existing = Evaluation.query.filter_by(student=student, review_no=1).one_or_none()
                if existing:
                    existing.total_marks = total
                    existing.literature_survey = comp["literature_survey"]
                    existing.problem_identification = comp["problem_identification"]
                    existing.presentation = comp["presentation"]
                    existing.question_answer = comp["question_answer"]
                    existing.member1_literature = member1_comp["literature_survey"]
                    existing.member1_problem = member1_comp["problem_identification"]
                    existing.member1_presentation = member1_comp["presentation"]
                    existing.member1_qa = member1_comp["question_answer"]
                    existing.member2_literature = member2_comp["literature_survey"]
                    existing.member2_problem = member2_comp["problem_identification"]
                    existing.member2_presentation = member2_comp["presentation"]
                    existing.member2_qa = member2_comp["question_answer"]
                    existing.guide_literature = guide_comp["literature_survey"]
                    existing.guide_problem = guide_comp["problem_identification"]
                    existing.guide_presentation = guide_comp["presentation"]
                    existing.guide_qa = guide_comp["question_answer"]
                else:
                    evaluation = Evaluation(
                        review_no=1,
                        total_marks=total,
                        literature_survey=comp["literature_survey"],
                        problem_identification=comp["problem_identification"],
                        presentation=comp["presentation"],
                        question_answer=comp["question_answer"],
                        # Individual evaluator marks
                        member1_literature=member1_comp["literature_survey"],
                        member1_problem=member1_comp["problem_identification"],
                        member1_presentation=member1_comp["presentation"],
                        member1_qa=member1_comp["question_answer"]
                        ,
                        member2_literature=member2_comp["literature_survey"],
                        member2_problem=member2_comp["problem_identification"],
                        member2_presentation=member2_comp["presentation"],
                        member2_qa=member2_comp["question_answer"],
                        guide_literature=guide_comp["literature_survey"],
                        guide_problem=guide_comp["problem_identification"],
                        guide_presentation=guide_comp["presentation"],
                        guide_qa=guide_comp["question_answer"],
                        student=student,
                    )
                    db.session.add(evaluation)
                    created += 1

            db.session.commit()

            # Ensure exports directory exists
            EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

            # Auto-export latest evaluations with component marks to CSV
            export_path = EXPORTS_DIR / "evaluations_review1.csv"
            with export_path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "group_no",
                    "project_title",
                    "seat_no",
                    "name",
                    "review_no",
                    "member1_literature",
                    "member1_problem",
                    "member1_presentation",
                    "member1_qa",
                    "member1_total",
                    "member2_literature",
                    "member2_problem",
                    "member2_presentation",
                    "member2_qa",
                    "member2_total",
                    "guide_literature",
                    "guide_problem",
                    "guide_presentation",
                    "guide_qa",
                    "guide_total",
                    "avg_literature",
                    "avg_problem",
                    "avg_presentation",
                    "avg_qa",
                    "avg_total_marks",
                ])
                # For each student, pick latest evaluation (review 1) and write row
                students = Student.query.order_by(Student.group_no, Student.name).all()
                for s in students:
                    ev = sorted(s.evaluations, key=lambda e: (e.review_no, e.id))[-1] if s.evaluations else None
                    if not ev:
                        continue
                    
                    # Calculate individual evaluator totals
                    member1_total = (ev.member1_literature or 0) + (ev.member1_problem or 0) + (ev.member1_presentation or 0) + (ev.member1_qa or 0)
                    member2_total = (ev.member2_literature or 0) + (ev.member2_problem or 0) + (ev.member2_presentation or 0) + (ev.member2_qa or 0)
                    guide_total = (ev.guide_literature or 0) + (ev.guide_problem or 0) + (ev.guide_presentation or 0) + (ev.guide_qa or 0)
                    
                    # Calculate averages
                    avg_literature = int(round(((ev.member1_literature or 0) + (ev.member2_literature or 0) + (ev.guide_literature or 0)) / 3))
                    avg_problem = int(round(((ev.member1_problem or 0) + (ev.member2_problem or 0) + (ev.guide_problem or 0)) / 3))
                    avg_presentation = int(round(((ev.member1_presentation or 0) + (ev.member2_presentation or 0) + (ev.guide_presentation or 0)) / 3))
                    avg_qa = int(round(((ev.member1_qa or 0) + (ev.member2_qa or 0) + (ev.guide_qa or 0)) / 3))
                    avg_total = avg_literature + avg_problem + avg_presentation + avg_qa
                    
                    writer.writerow([
                        s.group_no or "",
                        s.project_title or "",
                        s.seat_no,
                        s.name,
                        ev.review_no,
                        # Member 1 marks
                        ev.member1_literature or 0,
                        ev.member1_problem or 0,
                        ev.member1_presentation or 0,
                        ev.member1_qa or 0,
                        member1_total,
                        # Member 2 marks
                        ev.member2_literature or 0,
                        ev.member2_problem or 0,
                        ev.member2_presentation or 0,
                        ev.member2_qa or 0,
                        member2_total,
                        # Guide marks
                        ev.guide_literature or 0,
                        ev.guide_problem or 0,
                        ev.guide_presentation or 0,
                        ev.guide_qa or 0,
                        guide_total,
                        # Average marks
                        avg_literature,
                        avg_problem,
                        avg_presentation,
                        avg_qa,
                        avg_total,
                    ])

            if created > 0:
                flash(f"Imported {created} evaluation record(s). Exported to 'exports/evaluations_review1.csv'.", "success")
            return redirect(url_for("list_students"))

        return render_template("upload.html")

    @app.route("/students")
    def list_students():
        students = Student.query.order_by(Student.group_no, Student.name).all()
        # pick latest evaluation per student (review 1)
        data = []
        for s in students:
            ev = sorted(s.evaluations, key=lambda e: (e.review_no, e.id))[-1] if s.evaluations else None
            if ev:
                data.append((s, ev))
        return render_template("students.html", items=data)
    
    @app.route("/students/groupwise")
    def students_groupwise():
        # Get all students with their evaluations, grouped by group_no
        students = Student.query.order_by(Student.group_no, Student.name).all()
        
        # Group students by group_no
        groups = {}
        for student in students:
            group_no = student.group_no or "No Group"
            if group_no not in groups:
                groups[group_no] = []
            
            # Get latest evaluation
            ev = sorted(student.evaluations, key=lambda e: (e.review_no, e.id))[-1] if student.evaluations else None
            if ev:
                groups[group_no].append((student, ev))
        
        return render_template("students_groupwise.html", groups=groups)
    
    @app.route("/students/guidewise")
    def students_guidewise():
        # Get all students with their evaluations, grouped by guide
        students = Student.query.order_by(Student.name).all()
        
        # Group students by their actual project guide from database
        guides = {}
        
        for student in students:
            ev = sorted(student.evaluations, key=lambda e: (e.review_no, e.id))[-1] if student.evaluations else None
            if ev and student.project_guide:
                guide_name = student.project_guide.strip()
                
                if guide_name not in guides:
                    guides[guide_name] = []
                guides[guide_name].append((student, ev))
        
        return render_template("students_guidewise.html", guides=guides)
    
    @app.route("/students/individual")
    def students_individual():
        # Enhanced individual view with more details
        students = Student.query.order_by(Student.name).all()
        data = []
        for s in students:
            ev = sorted(s.evaluations, key=lambda e: (e.review_no, e.id))[-1] if s.evaluations else None
            if ev:
                # Add more detailed individual data
                individual_data = {
                    'student': s,
                    'evaluation': ev,
                    'member1_total': (ev.member1_literature or 0) + (ev.member1_problem or 0) + 
                                   (ev.member1_presentation or 0) + (ev.member1_qa or 0),
                    'member2_total': (ev.member2_literature or 0) + (ev.member2_problem or 0) + 
                                   (ev.member2_presentation or 0) + (ev.member2_qa or 0),
                    'guide_total': (ev.guide_literature or 0) + (ev.guide_problem or 0) + 
                                  (ev.guide_presentation or 0) + (ev.guide_qa or 0),
                }
                data.append(individual_data)
        
        return render_template("students_individual.html", students_data=data)

    @app.route("/students/<int:student_id>")
    def student_detail(student_id: int):
        student = Student.query.get_or_404(student_id)
        ev = sorted(student.evaluations, key=lambda e: (e.review_no, e.id))[-1]
        return render_template("student_detail.html", student=student, ev=ev)

    @app.route("/students/<int:student_id>/download")
    def download_review1(student_id: int):
        student = Student.query.get_or_404(student_id)
        ev = sorted(student.evaluations, key=lambda e: (e.review_no, e.id))[-1]
        pdf_buffer = build_review1_pdf(student, ev)
        filename = f"Review-1_{student.seat_no}_{student.name.replace(' ', '_')}.pdf"
        return send_file(pdf_buffer, as_attachment=True, download_name=filename, mimetype="application/pdf")

    @app.route("/students/<int:student_id>/csv")
    def download_review1_csv(student_id: int):
        student = Student.query.get_or_404(student_id)
        ev = sorted(student.evaluations, key=lambda e: (e.review_no, e.id))[-1]

        # Prepare per-student CSV with component rows and averages
        bio = io.StringIO()
        writer = csv.writer(bio)
        writer.writerow(["Seat No", student.seat_no])
        writer.writerow(["Name", student.name])
        writer.writerow(["Group No", student.group_no or "-"])
        writer.writerow(["Project Title", student.project_title or "-"])
        writer.writerow([])
        writer.writerow(["Component", "Member 1", "Member 2", "Internal Guide", "Average"]) 

        rows = [
            ("Literature Survey (20)", ev.member1_literature or 0, ev.member2_literature or 0, ev.guide_literature or 0),
            ("Problem Identification (10)", ev.member1_problem or 0, ev.member2_problem or 0, ev.guide_problem or 0),
            ("Presentation (10)", ev.member1_presentation or 0, ev.member2_presentation or 0, ev.guide_presentation or 0),
            ("Q&A (10)", ev.member1_qa or 0, ev.member2_qa or 0, ev.guide_qa or 0),
        ]

        member1_total = 0
        member2_total = 0
        guide_total = 0
        avg_total = 0
        for label, m1, m2, g in rows:
            avg = int(round((int(m1) + int(m2) + int(g)) / 3))
            writer.writerow([label, m1, m2, g, avg])
            member1_total += int(m1)
            member2_total += int(m2)
            guide_total += int(g)
            avg_total += avg

        writer.writerow([])
        writer.writerow(["Total (50)", member1_total, member2_total, guide_total, avg_total])

        bio.seek(0)
        filename = f"Review-1_{student.seat_no}_{student.name.replace(' ', '_')}.csv"
        return send_file(io.BytesIO(bio.getvalue().encode("utf-8")), as_attachment=True, download_name=filename, mimetype="text/csv")

    @app.route("/export.csv")
    def download_export_csv():
        EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
        export_path = EXPORTS_DIR / "evaluations_review1.csv"
        if not export_path.exists():
            # If file missing (e.g., before any uploads), build it now from current DB
            with export_path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "group_no",
                    "project_title",
                    "seat_no",
                    "name",
                    "review_no",
                    "member1_literature",
                    "member1_problem",
                    "member1_presentation",
                    "member1_qa",
                    "member1_total",
                    "member2_literature",
                    "member2_problem",
                    "member2_presentation",
                    "member2_qa",
                    "member2_total",
                    "guide_literature",
                    "guide_problem",
                    "guide_presentation",
                    "guide_qa",
                    "guide_total",
                    "avg_literature",
                    "avg_problem",
                    "avg_presentation",
                    "avg_qa",
                    "avg_total_marks",
                ])
                students = Student.query.order_by(Student.group_no, Student.name).all()
                for s in students:
                    ev = sorted(s.evaluations, key=lambda e: (e.review_no, e.id))[-1] if s.evaluations else None
                    if not ev:
                        continue
                    
                    # Calculate individual evaluator totals
                    member1_total = (ev.member1_literature or 0) + (ev.member1_problem or 0) + (ev.member1_presentation or 0) + (ev.member1_qa or 0)
                    member2_total = (ev.member2_literature or 0) + (ev.member2_problem or 0) + (ev.member2_presentation or 0) + (ev.member2_qa or 0)
                    guide_total = (ev.guide_literature or 0) + (ev.guide_problem or 0) + (ev.guide_presentation or 0) + (ev.guide_qa or 0)
                    
                    # Calculate averages
                    avg_literature = int(round(((ev.member1_literature or 0) + (ev.member2_literature or 0) + (ev.guide_literature or 0)) / 3))
                    avg_problem = int(round(((ev.member1_problem or 0) + (ev.member2_problem or 0) + (ev.guide_problem or 0)) / 3))
                    avg_presentation = int(round(((ev.member1_presentation or 0) + (ev.member2_presentation or 0) + (ev.guide_presentation or 0)) / 3))
                    avg_qa = int(round(((ev.member1_qa or 0) + (ev.member2_qa or 0) + (ev.guide_qa or 0)) / 3))
                    avg_total = avg_literature + avg_problem + avg_presentation + avg_qa
                    
                    writer.writerow([
                        s.group_no or "",
                        s.project_title or "",
                        s.seat_no,
                        s.name,
                        ev.review_no,
                        # Member 1 marks
                        ev.member1_literature or 0,
                        ev.member1_problem or 0,
                        ev.member1_presentation or 0,
                        ev.member1_qa or 0,
                        member1_total,
                        # Member 2 marks
                        ev.member2_literature or 0,
                        ev.member2_problem or 0,
                        ev.member2_presentation or 0,
                        ev.member2_qa or 0,
                        member2_total,
                        # Guide marks
                        ev.guide_literature or 0,
                        ev.guide_problem or 0,
                        ev.guide_presentation or 0,
                        ev.guide_qa or 0,
                        guide_total,
                        # Average marks
                        avg_literature,
                        avg_problem,
                        avg_presentation,
                        avg_qa,
                        avg_total,
                    ])
        return send_file(export_path, as_attachment=True, download_name="evaluations_review1.csv", mimetype="text/csv")
    
    @app.route("/summary.pdf")
    def download_summary_pdf():
        # Get guide-wise data
        students = Student.query.order_by(Student.name).all()
        guides = {}
        for student in students:
            ev = sorted(student.evaluations, key=lambda e: (e.review_no, e.id))[-1] if student.evaluations else None
            if ev and student.project_guide:
                guide_name = student.project_guide.strip()
                if guide_name not in guides:
                    guides[guide_name] = []
                guides[guide_name].append((student, ev))
        
        # Get group-wise data
        groups = {}
        for student in students:
            group_no = student.group_no or "No Group"
            if group_no not in groups:
                groups[group_no] = []
            ev = sorted(student.evaluations, key=lambda e: (e.review_no, e.id))[-1] if student.evaluations else None
            if ev:
                groups[group_no].append((student, ev))
        
        if not guides and not groups:
            flash("No evaluation data found to generate summary.", "error")
            return redirect(url_for("list_students"))
        
        pdf_buffer = build_comprehensive_pdf(guides, groups)
        filename = f"CIE_Review1_Comprehensive_Report_{date.today().strftime('%Y%m%d')}.pdf"
        return send_file(pdf_buffer, as_attachment=True, download_name=filename, mimetype="application/pdf")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)