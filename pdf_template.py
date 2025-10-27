from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import date
import io
import os
from review_config import get_review_config

def get_college_logo():
    """Get the college logo image"""
    logo_path = os.path.join(os.path.dirname(__file__), 'college_logo.png')
    if os.path.exists(logo_path):
        return Image(logo_path, width=25*mm, height=25*mm)
    else:
        # Create a simple placeholder
        return Paragraph("<b>LOGO</b>", ParagraphStyle('Logo', fontSize=8, alignment=TA_CENTER))

def build_review1_pdf(student, ev, phase=None, review=None):
    """
    Build a perfectly formatted PDF matching the exact document layout
    
    Args:
        student: Student object
        ev: Evaluation object
        phase: Phase number (optional, uses ev.phase if not provided)
        review: Review number (optional, uses ev.review_no if not provided)
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
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Create professional styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Normal'],
        fontSize=14,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=3
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica',
        alignment=TA_CENTER,
        spaceAfter=2
    )
    
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Normal'],
        fontSize=12,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=4
    )
    
    info_style = ParagraphStyle(
        'Info',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica',
        alignment=TA_LEFT,
        leading=14,  # Increased line spacing to prevent text overlap
        spaceAfter=6  # Extra space after paragraph
    )
    
    # Header with logo and college info in a single row
    header_data = [[
        get_college_logo(),
        Paragraph("<b>GURU NANAK DEV ENGINEERING COLLEGE, BIDAR 585403</b><br/>"
                 "<font size=9>Affiliated to VTU Belagavi & Approved by AICTE New Delhi</font><br/>"
                 "<font size=10><b>Department of Computer Science Engineering</b></font>", title_style)
    ]]
    
    header_table = Table(header_data, colWidths=[30*mm, 150*mm])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 8))
    
    # Academic info in corners
    academic_data = [[
        "Academic Year: _______________",
        "Semester: _______________"
    ]]
    academic_table = Table(academic_data, colWidths=[90*mm, 90*mm])
    academic_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    elements.append(academic_table)
    elements.append(Spacer(1, 8))
    
    # Main section titles - dynamic phase and review
    phase_roman = "I" if ev.phase == 1 else "II"
    review_roman = "I" if ev.review_no == 1 else "II"
    
    elements.append(Paragraph(f"FINAL YEAR STUDENTS MAJOR PROJECT WORK PHASE - {phase_roman}", section_style))
    elements.append(Paragraph(f"CONTINUOUS INTERNAL EVALUATION (CIE) OF MAJOR PROJECT WORK PHASE - {phase_roman}", section_style))
    elements.append(Paragraph(f"REVIEW - {review_roman}", section_style))
    elements.append(Spacer(1, 12))
    
    # Group and project info with manual-style title wrapping
    project_title = student.project_title or "........................................................................................................................................................................................................."
    
    # Wrap long project titles to two lines like manual form filling
    if len(project_title) > 85:  # Wrap at reasonable line length
        # Find the best break point (prefer spaces, then punctuation)
        mid_point = 85  # Target first line length
        break_point = mid_point
        
        # Look backwards from target length for natural break
        for i in range(mid_point, max(0, mid_point - 20), -1):
            if i < len(project_title) and project_title[i] in [' ', ',', '-', ':', ';', '.']:
                break_point = i + (1 if project_title[i] != '-' else 0)
                break
        
        # Create properly formatted two-line title
        line1 = project_title[:break_point].strip()
        line2 = project_title[break_point:].strip()
        
        # Add proper spacing for second line alignment (like manual forms)
        spaces = "&nbsp;" * 38  # Align with "Project Title:" label
        project_title = f"{line1}<br/>{spaces}{line2}"
    
    project_info = Paragraph(f"Group No: {student.group_no or '.........'}     Project Title: {project_title}", info_style)
    elements.append(project_info)
    elements.append(Spacer(1, 12))  # Increased spacing to prevent overlap
    
    # Get configuration for this phase/review
    config = get_review_config(ev.phase, ev.review_no)
    if not config:
        # Fallback if config not found
        config = get_review_config(1, 1)
    
    # Calculate marks dynamically based on criteria
    criteria_marks = []
    for i in range(1, 5):  # criteria1 to criteria4
        criterion_config = config['criteria'][i-1]
        m1 = int(getattr(ev, f'member1_criteria{i}', 0) or 0)
        m2 = int(getattr(ev, f'member2_criteria{i}', 0) or 0)
        m_guide = int(getattr(ev, f'guide_criteria{i}', 0) or 0)
        
        # Check if guide marks are applicable for this criterion
        guide_marks_applicable = criterion_config.get('guide_marks', True)
        
        # Calculate average: if guide marks not applicable, average only m1 and m2
        if guide_marks_applicable:
            avg = int(round((m1 + m2 + m_guide) / 3)) if (m1 + m2 + m_guide) > 0 else 0
        else:
            avg = int(round((m1 + m2) / 2)) if (m1 + m2) > 0 else 0
        
        criteria_marks.append({
            'm1': m1, 
            'm2': m2, 
            'guide': m_guide,  # Always store guide marks for display
            'avg': avg,
            'guide_applicable': guide_marks_applicable
        })
    
    total_marks = sum(c['avg'] for c in criteria_marks)
    
    # Create the main evaluation table with dynamic criteria
    table_data = [
        # Header row with CIE span
        ['', '', '', '', 'Continuous Internal Evaluation (CIE)\nby', '', '', 'Average CIE\nMarks\n(50 Marks)'],
        
        # Sub-header row
        ['Sl.\nNo.', 'Univ.\nSeat No.', 'Name of the\nStudent', 'Aspect for Assessment', 
         'Chairperson\n(Member-1)\nMarks', 'Member-2\nMarks', 'Internal\nGuide\nMarks', ''],
        
        # Project Guide section header
        ['', '', '', config.get('guide_section_label', 'Marks allotted by Project Guide'), '', '', '', ''],
    ]
    
    # Add first two criteria (guide marks) with student info on first row
    # Per reference format, for "Marks allotted by Project Guide" section:
    # - Chairperson (Member-1): shows NA
    # - Member-2: shows NA  
    # - Internal Guide: shows actual marks
    for idx, criterion in enumerate(config['criteria'][:2], 1):
        marks = criteria_marks[idx-1]
        
        row = [
            '1' if idx == 1 else '',
            student.seat_no if idx == 1 else '',
            student.name if idx == 1 else '',
            f"({chr(96+idx)}) {criterion['name']} ({criterion['max_marks']} Marks)",
            'NA',  # Chairperson shows NA in guide section (per reference docs)
            'NA',  # Member-2 shows NA in guide section (per reference docs)
            str(marks['guide']) if marks['guide'] > 0 else '',  # Guide shows actual marks
            str(marks['avg'])
        ]
        table_data.append(row)
    
    # Committee section header
    table_data.append(['', '', '', config.get('committee_section_label', 'Marks allotted by Committee'), '', '', '', ''])
    
    # Add last two criteria (committee marks)
    # In the reference format, for "Marks allotted by Committee" section:
    # - Chairperson (Member-1) shows actual marks
    # - Member-2 shows actual marks
    # - Internal Guide shows actual marks
    for idx, criterion in enumerate(config['criteria'][2:], 3):
        marks = criteria_marks[idx-1]
        
        row = [
            '', '', '',
            f"({chr(96+idx)}) {criterion['name']} ({criterion['max_marks']} Marks)",
            str(marks['m1']),  # Chairperson shows actual marks
            str(marks['m2']),  # Member-2 shows actual marks
            str(marks['guide']) if marks['guide'] > 0 else '',  # Internal Guide shows actual marks
            str(marks['avg'])
        ]
        table_data.append(row)
    
    # Total row
    table_data.append(['', '', '', 'Total Marks (50 Marks)', '', '', '', str(total_marks)])
    
    # Perfect column widths for A4 with proper row heights
    col_widths = [12*mm, 18*mm, 35*mm, 62*mm, 20*mm, 18*mm, 20*mm, 20*mm]
    
    # Calculate dynamic row heights based on number of criteria
    row_heights = [
        20*mm,  # Header row 1
        20*mm,  # Header row 2
        15*mm,  # Project Guide section header
    ]
    # Add heights for guide criteria (first 2 criteria)
    row_heights.append(25*mm)  # First criterion with student info
    row_heights.append(18*mm)  # Second criterion
    # Committee section header
    row_heights.append(15*mm)
    # Add heights for committee criteria (last 2 criteria)
    row_heights.append(18*mm)  # Third criterion
    row_heights.append(18*mm)  # Fourth criterion
    # Total row
    row_heights.append(18*mm)
    
    main_table = Table(table_data, colWidths=col_widths, rowHeights=row_heights)
    
    # Apply enhanced styling with better colors and visibility
    main_table.setStyle(TableStyle([
        # Overall grid with better visibility
        ('GRID', (0, 0), (-1, -1), 0.75, colors.HexColor('#404040')),
        
        # Font settings
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        
        # Header styling with attractive colors
        ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 1), 10),
        ('BACKGROUND', (0, 0), (-1, 1), colors.HexColor('#1e3a8a')),  # Deep blue
        ('TEXTCOLOR', (0, 0), (-1, 1), colors.white),
        ('TOPPADDING', (0, 0), (-1, 1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, 1), 15),
        
        # Section headers styling with distinct colors
        ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 2), (-1, 2), 9),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#fef3c7')),  # Light yellow
        ('FONTNAME', (0, 5), (-1, 5), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 5), (-1, 5), 9),
        ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor('#fef3c7')),  # Light yellow
        
        # Total row styling
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 10),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#dbeafe')),  # Light blue
        
        # Student info styling - enhanced
        ('FONTNAME', (0, 3), (2, 6), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 3), (2, 6), 10),
        ('BACKGROUND', (0, 3), (2, 6), colors.HexColor('#e0f2fe')),  # Light cyan
        ('TEXTCOLOR', (0, 3), (2, 6), colors.HexColor('#003366')),
        
        # Cell merging
        ('SPAN', (4, 0), (6, 0)),  # CIE header span
        ('SPAN', (0, 3), (0, 6)),  # Sl No spanning
        ('SPAN', (1, 3), (1, 6)),  # Seat No spanning
        ('SPAN', (2, 3), (2, 6)),  # Name spanning
        
        # Alignment
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (3, 2), (3, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('VALIGN', (0, 3), (2, 6), 'MIDDLE'),
        ('ALIGN', (0, 3), (2, 6), 'CENTER'),
        
        # Enhanced padding for better spacing
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 2), (-1, -2), 12),
        ('BOTTOMPADDING', (0, 2), (-1, -2), 12),
        
        # Thicker borders for sections
        ('LINEABOVE', (0, 2), (-1, 2), 1.5, colors.HexColor('#666666')),
        ('LINEABOVE', (0, 5), (-1, 5), 1.5, colors.HexColor('#666666')),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#1e3a8a')),
        
        # Marks styling - make them stand out
        ('FONTNAME', (4, 3), (-1, -2), 'Helvetica-Bold'),
        ('FONTSIZE', (4, 3), (-1, -2), 9),
        ('TEXTCOLOR', (7, 3), (7, -2), colors.HexColor('#059669')),  # Green for averages
        
    ]))
    
    elements.append(main_table)
    elements.append(Spacer(1, 25))
    
    # Professional signature section
    sig_data = [[
        'Project coordinator', 'Chairperson\n(Member – 1)', 'Member – 2', 'Guide'
    ]]
    
    sig_table = Table(sig_data, colWidths=[45*mm, 45*mm, 45*mm, 45*mm])
    sig_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
        ('TOPPADDING', (0, 0), (-1, -1), 35),
        ('LINEABOVE', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(sig_table)
    
    # Build the beautiful PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


def build_summary_pdf(students_evaluations):
    """
    Build a beautifully formatted summary PDF document for all students with college branding
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=15*mm, 
        leftMargin=15*mm, 
        topMargin=15*mm, 
        bottomMargin=20*mm
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Enhanced custom styles
    college_title_style = ParagraphStyle(
        'CollegeTitle',
        parent=styles['Normal'],
        fontSize=16,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=4,
        textColor=colors.black
    )
    
    affiliation_style = ParagraphStyle(
        'Affiliation',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica',
        alignment=TA_CENTER,
        spaceAfter=4,
        textColor=colors.darkblue
    )
    
    department_style = ParagraphStyle(
        'Department',
        parent=styles['Normal'],
        fontSize=12,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=10,
        textColor=colors.black
    )
    
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Normal'],
        fontSize=18,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=12,
        textColor=colors.darkred
    )
    
    # Header with logo and college info
    header_data = [[
        get_college_logo(),
        Paragraph("<b>GURU NANAK DEV ENGINEERING COLLEGE, BIDAR 585403</b><br/>"
                 "<font size=10>Affiliated to VTU Belagavi & Approved by AICTE New Delhi</font><br/>"
                 "<font size=11><b>Department of Computer Science Engineering</b></font>", college_title_style)
    ]]
    
    header_table = Table(header_data, colWidths=[30*mm, 150*mm])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_table)
    
    # Report title
    elements.append(Paragraph("FINAL YEAR PROJECT REVIEW-I SUMMARY REPORT", title_style))
    elements.append(Paragraph(f"Academic Year: 2024-25 | Generated on: {date.today().strftime('%d/%m/%Y')}", affiliation_style))
    elements.append(Spacer(1, 20))
    
    # Summary statistics
    total_students = len(students_evaluations)
    avg_score = sum(ev.total_marks for _, ev in students_evaluations) / total_students if total_students > 0 else 0
    
    stats_data = [[
        f"Total Students: {total_students}",
        f"Average Score: {avg_score:.1f}/50",
        f"Pass Rate: {sum(1 for _, ev in students_evaluations if ev.total_marks >= 25)/total_students*100:.1f}%" if total_students > 0 else "Pass Rate: 0%"
    ]]
    
    stats_table = Table(stats_data, colWidths=[60*mm, 60*mm, 60*mm])
    stats_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightyellow),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(stats_table)
    elements.append(Spacer(1, 20))
    
    # Main summary table
    table_data = [
        ['Sl.\nNo.', 'Group\nNo.', 'Seat No.', 'Student Name', 'Project Title', 
         'Literature\n(20)', 'Problem\n(10)', 'Presentation\n(10)', 'Q&A\n(10)', 'Total\n(50)', 'Grade']
    ]
    
    # Add student data with proper formatting
    for idx, (student, evaluation) in enumerate(students_evaluations, 1):
        # Calculate grade
        total = evaluation.total_marks or 0
        if total >= 40:
            grade = 'A'
        elif total >= 35:
            grade = 'B'
        elif total >= 30:
            grade = 'C'
        elif total >= 25:
            grade = 'D'
        else:
            grade = 'F'
            
        # Wrap long project titles in same column (2 lines)
        project_title = student.project_title or ""
        if len(project_title) > 35:  # If longer than column width
            # Find natural break point
            mid_point = 35
            break_point = mid_point
            
            # Look backwards for space, comma, etc.
            for i in range(mid_point, max(0, mid_point - 10), -1):
                if i < len(project_title) and project_title[i] in [' ', ',', '-', ':', '.']:
                    break_point = i + (1 if project_title[i] != '-' else 0)
                    break
            
            # Create wrapped title using Paragraph for proper line breaks
            line1 = project_title[:break_point].strip()
            line2 = project_title[break_point:].strip()
            
            # If second line is still too long, truncate it
            if len(line2) > 35:
                line2 = line2[:32] + "..."
            
            # Create paragraph with line breaks  
            project_title_para = Paragraph(f"<font size=7>{line1}<br/>{line2}</font>", 
                                         ParagraphStyle('ProjectTitle', fontSize=7, leading=9))
        else:
            # Short title - use as is
            project_title_para = project_title
            
        table_data.append([
            str(idx),
            student.group_no or "-",
            student.seat_no,
            student.name,
            project_title_para,  # Use paragraph for wrapped titles
            str(evaluation.literature_survey or 0),
            str(evaluation.problem_identification or 0),
            str(evaluation.presentation or 0),
            str(evaluation.question_answer or 0),
            str(total),
            grade
        ])
    
    # Create table with optimized widths for A4 and dynamic row heights
    col_widths = [10*mm, 12*mm, 18*mm, 35*mm, 45*mm, 12*mm, 12*mm, 16*mm, 12*mm, 12*mm, 12*mm]
    summary_table = Table(table_data, colWidths=col_widths, repeatRows=1, rowHeights=None)  # Allow dynamic row heights
    
    # Apply beautiful styling
    summary_table.setStyle(TableStyle([
        # Header styling
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        
        # Data styling
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),    # Serial number
        ('ALIGN', (1, 1), (2, -1), 'CENTER'),    # Group and seat
        ('ALIGN', (3, 1), (4, -1), 'LEFT'),      # Name and project
        ('ALIGN', (5, 1), (-1, -1), 'CENTER'),   # Marks and grade
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        
        # Alternating row colors
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        
        # Grid and borders
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkblue),
        
        # Padding - extra for project title column
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        # Extra padding for project title column to accommodate wrapped text
        ('TOPPADDING', (4, 1), (4, -1), 2),
        ('BOTTOMPADDING', (4, 1), (4, -1), 2),
        
        # Special formatting for grades
        ('FONTNAME', (-1, 1), (-1, -1), 'Helvetica-Bold'),
    ]))
    
    # Add alternating row colors
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, i), (-1, i), colors.lightgrey)
            ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 30))
    
    # Footer with summary statistics
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica',
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    elements.append(Paragraph(
        f"Report Generated on {date.today().strftime('%d/%m/%Y')} | "
        f"Total Students Evaluated: {total_students} | "
        f"Class Average: {avg_score:.1f}/50",
        footer_style
    ))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer
