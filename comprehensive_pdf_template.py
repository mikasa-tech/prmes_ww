#!/usr/bin/env python3

import io
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from review_config import get_review_config, get_criteria_labels, get_max_marks
from datetime import date

def get_college_logo():
    """Get the college logo image"""
    logo_path = os.path.join(os.path.dirname(__file__), 'college_logo.png')
    if os.path.exists(logo_path):
        return Image(logo_path, width=25*mm, height=25*mm)
    else:
        return Paragraph("<b>LOGO</b>", ParagraphStyle('Logo', fontSize=8, alignment=TA_CENTER))

def build_comprehensive_pdf(all_data):
    """Build a comprehensive PDF report for all phases and reviews
    
    Args:
        all_data: Dictionary with structure {(phase, review): {'guides': {...}, 'groups': {...}}}
    """
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=15*mm, 
        leftMargin=15*mm, 
        topMargin=10*mm, 
        bottomMargin=15*mm
    )
    
    # Create professional styles
    styles = getSampleStyleSheet()
    
    college_title_style = ParagraphStyle(
        'CollegeTitle',
        parent=styles['Normal'],
        fontSize=14,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=3
    )
    
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Normal'],
        fontSize=16,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=6,
        textColor=colors.darkblue
    )
    
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Normal'],
        fontSize=12,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=8,
        textColor=colors.darkred
    )
    
    info_style = ParagraphStyle(
        'Info',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica',
        alignment=TA_LEFT
    )
    
    story = []
    
    # Header with logo and college info
    header_data = [[
        get_college_logo(),
        Paragraph("<b>GURU NANAK DEV ENGINEERING COLLEGE, BIDAR 585403</b><br/>"
                 "<font size=9>Affiliated to VTU Belagavi & Approved by AICTE New Delhi</font><br/>"
                 "<font size=10><b>Department of Computer Science Engineering</b></font>", college_title_style)
    ]]
    
    header_table = Table(header_data, colWidths=[30*mm, 150*mm])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))
    
    # Academic info
    academic_data = [[
        "Academic Year: 2024-25",
        "Semester: VII"
    ]]
    academic_table = Table(academic_data, colWidths=[90*mm, 90*mm])
    academic_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    story.append(academic_table)
    story.append(Spacer(1, 12))
    
    # Main title
    story.append(Paragraph("COMPREHENSIVE PROJECT EVALUATION REPORT", title_style))
    story.append(Paragraph(f"Generated on: {date.today().strftime('%d/%m/%Y')}", info_style))
    story.append(Spacer(1, 20))
    
    # Process each phase-review combination
    for idx, ((phase, review), data) in enumerate(sorted(all_data.items())):
        students_by_group = data['groups']
        
        if not students_by_group:
            continue
        
        # Get review configuration
        criteria = get_criteria_labels(phase, review)
        max_marks = get_max_marks(phase, review)
        
        # Add page break between sections
        if idx > 0:
            story.append(PageBreak())
            # Add header again for new page
            story.append(header_table)
            story.append(Spacer(1, 8))
        
        # Phase and review header
        phase_roman = "I" if phase == 1 else "II"
        review_roman = "I" if review == 1 else "II"
        story.append(Paragraph(f"PHASE - {phase_roman}, REVIEW - {review_roman}", section_style))
        story.append(Spacer(1, 12))
        
        # Collect all students for this phase-review
        all_students = []
        for group_no, student_list in sorted(students_by_group.items()):
            all_students.extend(student_list)
        
        if not all_students:
            continue
        
        # Create simple summary table
        table_data = [[
            "Sl.\nNo.",
            "Group\nNo.",
            "Seat No.",
            "Student Name",
            "Project Guide"
        ]]
        
        # Add criteria headers dynamically
        for i, crit in enumerate(criteria, 1):
            table_data[0].append(f"{crit}\n({max_marks[i-1]})")
        table_data[0].append("Total\n(50)")
        
        # Add student data
        for idx, (student, ev) in enumerate(sorted(all_students, key=lambda x: (x[0].group_no or '', x[0].name)), 1):
            row = [
                str(idx),
                str(student.group_no or '-'),
                student.seat_no,
                student.name,
                student.project_guide or '-'
            ]
            # Add criteria marks
            for i in range(1, len(criteria) + 1):
                row.append(str(getattr(ev, f"criteria{i}", 0)))
            row.append(str(ev.total_marks))
            table_data.append(row)
        
        # Create table with proper column widths
        col_widths = [12*mm, 15*mm, 20*mm, 40*mm, 35*mm] + [15*mm] * len(criteria) + [15*mm]
        summary_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # Apply styling
        summary_table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            
            # Data styling
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (2, -1), 'CENTER'),  # Serial, group, seat
            ('ALIGN', (3, 1), (4, -1), 'LEFT'),    # Name and guide
            ('ALIGN', (5, 1), (-1, -1), 'CENTER'), # Marks
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
            
            # Grid and borders
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkblue),
            
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        # Add alternating row colors
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, i), (-1, i), colors.lightgrey)
                ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer
