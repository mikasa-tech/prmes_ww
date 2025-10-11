from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import date
import io
import os

def get_college_logo():
    """Get the college logo image"""
    logo_path = os.path.join(os.path.dirname(__file__), 'college_logo.png')
    if os.path.exists(logo_path):
        return Image(logo_path, width=25*mm, height=25*mm)
    else:
        # Create a simple placeholder
        return Paragraph("<b>LOGO</b>", ParagraphStyle('Logo', fontSize=8, alignment=TA_CENTER))

def build_review1_pdf(student, ev):
    """
    Build a perfectly formatted PDF matching the exact document layout
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
    
    # Main section titles
    elements.append(Paragraph("FINAL YEAR STUDENTS MAJOR PROJECT WORK PHASE - I", section_style))
    elements.append(Paragraph("CONTINUOUS INTERNAL EVALUATION (CIE) OF MAJOR PROJECT WORK PHASE - I", section_style))
    elements.append(Paragraph("REVIEW - I", section_style))
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
    
    # Calculate individual marks and averages correctly - ALWAYS show marks
    lit_m1 = int(ev.member1_literature or 0)
    lit_m2 = int(ev.member2_literature or 0) 
    lit_guide = int(ev.guide_literature or 0)
    lit_avg = int(round((lit_m1 + lit_m2 + lit_guide) / 3)) if (lit_m1 + lit_m2 + lit_guide) > 0 else 0
    
    prob_m1 = int(ev.member1_problem or 0)
    prob_m2 = int(ev.member2_problem or 0)
    prob_guide = int(ev.guide_problem or 0)
    prob_avg = int(round((prob_m1 + prob_m2 + prob_guide) / 3)) if (prob_m1 + prob_m2 + prob_guide) > 0 else 0
    
    pres_m1 = int(ev.member1_presentation or 0)
    pres_m2 = int(ev.member2_presentation or 0)
    pres_guide = int(ev.guide_presentation or 0)
    pres_avg = int(round((pres_m1 + pres_m2 + pres_guide) / 3)) if (pres_m1 + pres_m2 + pres_guide) > 0 else 0
    
    qa_m1 = int(ev.member1_qa or 0)
    qa_m2 = int(ev.member2_qa or 0)
    qa_guide = int(ev.guide_qa or 0)
    qa_avg = int(round((qa_m1 + qa_m2 + qa_guide) / 3)) if (qa_m1 + qa_m2 + qa_guide) > 0 else 0
    
    # All marks calculated and ready for display
    
    total_marks = lit_avg + prob_avg + pres_avg + qa_avg
    
    # Create the main evaluation table with exact structure
    table_data = [
        # Header row with CIE span
        ['', '', '', '', 'Continuous Internal Evaluation (CIE)\nby', '', '', 'Average CIE\nMarks\n(50 Marks)'],
        
        # Sub-header row
        ['Sl.\nNo.', 'Univ.\nSeat No.', 'Name of the\nStudent', 'Aspect for Assessment', 
         'Chairperson\n(Member-1)\nMarks', 'Member-2\nMarks', 'Internal\nGuide\nMarks', ''],
        
        # Project Guide section
        ['', '', '', 'Marks allotted by Project Guide', '', '', '', ''],
        
        # Literature Survey with student info - ALL evaluator marks
        ['1', student.seat_no, student.name, '(a) Literature Survey (20 Marks)', 
         str(lit_m1) if lit_m1 > 0 else 'NA', 
         str(lit_m2) if lit_m2 > 0 else '', 
         str(lit_guide) if lit_guide > 0 else '', 
         str(lit_avg)],
        
        # Problem Identification - ALL evaluator marks
        ['', '', '', '(b) Problem Identification (10 Marks)', 
         str(prob_m1) if prob_m1 > 0 else 'NA', 
         str(prob_m2) if prob_m2 > 0 else '', 
         str(prob_guide) if prob_guide > 0 else '', 
         str(prob_avg)],
        
        # Committee section header
        ['', '', '', 'Marks allotted by Committee', '', '', '', ''],
        
        # Presentation - ALL evaluator marks displayed
        ['', '', '', '(c) Project presentation skill (10 Marks)', 
         str(pres_m1), str(pres_m2), str(pres_guide), str(pres_avg)],
        
        # Q&A - ALL evaluator marks displayed
        ['', '', '', '(d) Question and answer session (10 Marks)', 
         str(qa_m1), str(qa_m2), str(qa_guide), str(qa_avg)],
        
        # Total row
        ['', '', '', 'Total Marks (50 Marks)', '', '', '', str(total_marks)],
    ]
    
    # Perfect column widths for A4 with proper row heights
    col_widths = [12*mm, 18*mm, 35*mm, 62*mm, 20*mm, 18*mm, 20*mm, 20*mm]
    
    # Set minimum row heights to prevent text overlapping
    row_heights = [
        12*mm,  # Header row 1
        12*mm,  # Header row 2  
        8*mm,   # Project Guide section header
        15*mm,  # Literature Survey (taller for student info)
        10*mm,  # Problem Identification
        8*mm,   # Committee section header
        10*mm,  # Presentation
        10*mm,  # Q&A
        10*mm   # Total
    ]
    
    main_table = Table(table_data, colWidths=col_widths, rowHeights=row_heights)
    
    # Apply perfect styling matching the document
    main_table.setStyle(TableStyle([
        # Overall grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        
        # Font settings - optimized for readability
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        
        # Header styling with extra space
        ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 1), 9),
        ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),
        # Extra padding for headers to prevent text cramping
        ('TOPPADDING', (0, 0), (-1, 1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 1), 10),
        
        # Section headers styling
        ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),  # Project Guide
        ('FONTNAME', (0, 5), (-1, 5), 'Helvetica-Bold'),  # Committee
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'), # Total
        
        # Student info styling - make it stand out beautifully
        ('FONTNAME', (0, 3), (2, 6), 'Helvetica-Bold'),   # S.No, Seat No, Name bold
        ('FONTSIZE', (0, 3), (2, 6), 9),                  # Slightly larger font
        
        # Cell merging - properly span student info across all 4 component rows
        ('SPAN', (4, 0), (6, 0)),  # CIE header span
        ('SPAN', (0, 3), (0, 6)),  # Sl No spanning all 4 component rows (lit, prob, pres, qa)
        ('SPAN', (1, 3), (1, 6)),  # Seat No spanning all 4 component rows
        ('SPAN', (2, 3), (2, 6)),  # Name spanning all 4 component rows
        
        # Alignment - Beautiful centered alignment for student info
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (3, 2), (3, -1), 'LEFT'),    # Assessment column left aligned
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Special vertical alignment for student info in spanned cells
        ('VALIGN', (0, 3), (2, 6), 'MIDDLE'),  # S.No, Seat No, Name perfectly centered
        ('ALIGN', (0, 3), (2, 6), 'CENTER'),   # Also center horizontally
        
        # Increased padding to prevent text overlapping on lines
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 8),   # Increased top padding
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8), # Increased bottom padding
        
        # Highlight important rows with beautiful colors
        ('BACKGROUND', (0, 2), (-1, 2), colors.lightyellow),  # Project Guide section
        ('BACKGROUND', (0, 5), (-1, 5), colors.lightyellow),  # Committee section
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue),  # Total row
        
        # Beautiful subtle background for student info columns
        ('BACKGROUND', (0, 3), (2, 6), colors.lightcyan),     # S.No, Seat No, Name region
        
        # Thicker borders for sections
        ('LINEABOVE', (0, 2), (-1, 2), 1, colors.black),     # Project Guide
        ('LINEABOVE', (0, 5), (-1, 5), 1, colors.black),     # Committee
        ('LINEABOVE', (0, -1), (-1, -1), 1.5, colors.black), # Total
        
        # Make numeric columns slightly darker for better readability
        ('TEXTCOLOR', (4, 1), (-1, -1), colors.black),
        
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
