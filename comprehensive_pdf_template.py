#!/usr/bin/env python3

import io
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

def build_comprehensive_pdf(students_by_guide, students_by_group):
    """Build a comprehensive PDF report matching the reference document format"""
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), 
                           topMargin=0.5*inch, bottomMargin=0.5*inch,
                           leftMargin=0.5*inch, rightMargin=0.5*inch)
    
    # Create styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=14,
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        alignment=TA_LEFT
    )
    
    story = []
    
    # Document Header
    story.append(Paragraph("Academic Year: 2024-25&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Semester: VII", normal_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("FINAL YEAR STUDENTS MAJOR PROJECT WORK PHASE - 1", title_style))
    story.append(Paragraph("CONTINUOUS INTERNAL EVALUATION (CIE) OF MAJOR PROJECT WORK PHASE - 1", header_style))
    story.append(Paragraph("REVIEW - 1", header_style))
    story.append(Spacer(1, 20))
    
    # Section 1: Guide-wise Summary
    story.append(Paragraph("SECTION 1: GUIDE-WISE PROJECT EVALUATION SUMMARY", title_style))
    story.append(Spacer(1, 12))
    
    for guide_name, student_list in students_by_guide.items():
        if not student_list:
            continue
            
        # Guide header
        story.append(Paragraph(f"<b>Project Guide: {guide_name}</b>", header_style))
        story.append(Spacer(1, 6))
        
        # Create table for this guide's projects
        table_data = [
            ["Group No", "Project Title", "Univ. Seat No.", "Student Name", 
             "Literature\nSurvey\n(20)", "Problem\nIdentification\n(10)", 
             "Presentation\nSkill\n(10)", "Q&A Session\n(10)", "Total\n(50)"]
        ]
        
        # Group students by project within this guide
        projects = {}
        for student, ev in student_list:
            project_key = f"{student.group_no}_{student.project_title}"
            if project_key not in projects:
                projects[project_key] = []
            projects[project_key].append((student, ev))
        
        for project_key, project_students in projects.items():
            for i, (student, ev) in enumerate(project_students):
                group_no = student.group_no if i == 0 else ""  # Show group only for first student
                project_title = student.project_title if i == 0 else ""  # Show title only for first student
                
                table_data.append([
                    str(group_no),
                    project_title,
                    student.seat_no,
                    student.name,
                    str(ev.literature_survey),
                    str(ev.problem_identification),
                    str(ev.presentation),
                    str(ev.question_answer),
                    str(ev.total_marks)
                ])
        
        # Create and style the table
        table = Table(table_data, colWidths=[0.8*inch, 2.5*inch, 1.2*inch, 1.5*inch, 
                                            0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.6*inch])
        
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
    
    # Page break before next section
    story.append(PageBreak())
    
    # Section 2: Group-wise Summary
    story.append(Paragraph("SECTION 2: GROUP-WISE PROJECT EVALUATION SUMMARY", title_style))
    story.append(Spacer(1, 12))
    
    for group_no, student_list in students_by_group.items():
        if not student_list:
            continue
            
        # Get project info from first student
        first_student, first_ev = student_list[0]
        project_title = first_student.project_title
        project_guide = first_student.project_guide
        
        story.append(Paragraph(f"<b>Group No: {group_no}&nbsp;&nbsp;&nbsp;&nbsp;Project Title: {project_title}</b>", normal_style))
        story.append(Paragraph(f"<b>Project Guide: {project_guide}</b>", normal_style))
        story.append(Spacer(1, 8))
        
        # Create detailed evaluation table matching the reference format
        table_data = [
            ["Sl.\nNo", "Univ. Seat No.", "Name of the Student", "Aspect for Assessment", 
             "Chairperson\n(Member-1)\nMarks", "Member-2\nMarks", "Internal Guide\nMarks", "Average CIE Marks\n(50 Marks)"]
        ]
        
        for idx, (student, ev) in enumerate(student_list, 1):
            # Literature Survey row
            table_data.append([
                str(idx) if idx == 1 else "",
                student.seat_no if idx == 1 else "",
                student.name if idx == 1 else "",
                "(a) Literature Survey (20 Marks)",
                str(ev.member1_literature or 0),
                str(ev.member2_literature or 0),
                str(ev.guide_literature or 0),
                str(ev.literature_survey)
            ])
            
            # Problem Identification row
            table_data.append([
                "", "", "",
                "(b) Problem Identification (10 Marks)",
                str(ev.member1_problem or 0),
                str(ev.member2_problem or 0),
                str(ev.guide_problem or 0),
                str(ev.problem_identification)
            ])
            
            # Presentation row
            table_data.append([
                "", "", "",
                "(c) Project presentation skill (10 Marks)",
                str(ev.member1_presentation or 0),
                str(ev.member2_presentation or 0),
                str(ev.guide_presentation or 0),
                str(ev.presentation)
            ])
            
            # Q&A row
            table_data.append([
                "", "", "",
                "(d) Question and answer session (10 Marks)",
                str(ev.member1_qa or 0),
                str(ev.member2_qa or 0),
                str(ev.guide_qa or 0),
                str(ev.question_answer)
            ])
            
            # Total row
            member1_total = (ev.member1_literature or 0) + (ev.member1_problem or 0) + (ev.member1_presentation or 0) + (ev.member1_qa or 0)
            member2_total = (ev.member2_literature or 0) + (ev.member2_problem or 0) + (ev.member2_presentation or 0) + (ev.member2_qa or 0)
            guide_total = (ev.guide_literature or 0) + (ev.guide_problem or 0) + (ev.guide_presentation or 0) + (ev.guide_qa or 0)
            
            table_data.append([
                "", "", "",
                "<b>Total Marks (50 Marks)</b>",
                f"<b>{member1_total}</b>",
                f"<b>{member2_total}</b>",
                f"<b>{guide_total}</b>",
                f"<b>{ev.total_marks}</b>"
            ])
            
            # Add space between students
            if idx < len(student_list):
                table_data.append(["", "", "", "", "", "", "", ""])
        
        # Create table
        table = Table(table_data, colWidths=[0.5*inch, 1.2*inch, 1.5*inch, 2.2*inch, 
                                            1*inch, 1*inch, 1*inch, 1*inch])
        
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # Merge cells for student info (spans multiple rows per student)
            ('SPAN', (0, 1), (0, 5)),  # Sl.No spans 5 rows for first student
            ('SPAN', (1, 1), (1, 5)),  # Seat No spans 5 rows
            ('SPAN', (2, 1), (2, 5)),  # Name spans 5 rows
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        # Signatures section
        signatures_data = [
            ["", "", "", ""],
            ["Project coordinator", "Chairperson", "Member – 2", "Guide"],
            ["(Member – 1)", "", "", ""]
        ]
        
        sig_table = Table(signatures_data, colWidths=[2*inch, 2*inch, 2*inch, 2*inch])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, 1), 10),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica'),
            ('FONTSIZE', (0, 2), (-1, 2), 9),
            ('TOPPADDING', (0, 0), (-1, 0), 30),  # Space for signatures
        ]))
        
        story.append(sig_table)
        story.append(PageBreak())
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer