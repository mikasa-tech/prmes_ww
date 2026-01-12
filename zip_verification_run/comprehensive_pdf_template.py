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
        fontSize=13,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=4,
        leading=16
    )
    
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Normal'],
        fontSize=14,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=8,
        textColor=colors.HexColor('#003366'),
        leading=17
    )
    
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Normal'],
        fontSize=13,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=10,
        textColor=colors.HexColor('#8B0000'),
        leading=16
    )
    
    info_style = ParagraphStyle(
        'Info',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica',
        alignment=TA_CENTER,
        leading=12
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
    story.append(Paragraph("<b>COMPREHENSIVE PROJECT EVALUATION REPORT</b>", title_style))
    story.append(Paragraph(f"<i>Generated on: {date.today().strftime('%d/%m/%Y')}</i>", info_style))
    story.append(Spacer(1, 15))
    
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
        
        # Create simple summary table with better formatting - prevent word breaking in headers
        # Increased leading to prevent text collision
        header_style_sm = ParagraphStyle('header_sm', fontSize=7, alignment=TA_CENTER, leading=9, wordWrap='LTR', splitLongWords=0)
        header_style_criteria = ParagraphStyle('header_crit', fontSize=6.5, alignment=TA_CENTER, leading=8, wordWrap='LTR', splitLongWords=0)
        
        table_data = [[
            Paragraph("<b>Sl.<br/>No.</b>", header_style_sm),  # Two lines to prevent collision
            Paragraph("<b>Group<br/>No.</b>", header_style_sm),  # Two lines to prevent collision
            Paragraph("<b>Seat<br/>No.</b>", header_style_sm),  # Two lines to prevent collision
            Paragraph("<b>Student<br/>Name</b>", header_style_sm),
            Paragraph("<b>Project<br/>Guide</b>", header_style_sm)
        ]]
        
        # Add criteria headers dynamically with proper formatting - prevent word breaking
        for i, crit in enumerate(criteria, 1):
            # Smart wrapping to prevent awkward word breaks
            crit_clean = crit.replace(' and ', '<br/>and<br/>')  # Break before 'and'
            
            if 'Literature' in crit:
                header_text = f"<b>Literature<br/>Survey<br/>({max_marks[i-1]})</b>"
            elif 'Problem' in crit and 'Identification' in crit:
                header_text = f"<b>Problem<br/>Identification<br/>({max_marks[i-1]})</b>"
            elif 'presentation' in crit or 'Presentation' in crit:
                header_text = f"<b>Project<br/>presentation<br/>Skill<br/>({max_marks[i-1]})</b>"
            elif 'Question' in crit or 'answer' in crit:
                header_text = f"<b>Question<br/>and answer<br/>session<br/>({max_marks[i-1]})</b>"
            elif len(crit) > 15:
                # For other long names, split by words
                words = crit.split()
                if len(words) >= 3:
                    line1 = words[0]
                    line2 = ' '.join(words[1:])
                    header_text = f"<b>{line1}<br/>{line2}<br/>({max_marks[i-1]})</b>"
                elif len(words) == 2:
                    header_text = f"<b>{words[0]}<br/>{words[1]}<br/>({max_marks[i-1]})</b>"
                else:
                    header_text = f"<b>{crit}<br/>({max_marks[i-1]})</b>"
            else:
                header_text = f"<b>{crit}<br/>({max_marks[i-1]})</b>"
            
            table_data[0].append(Paragraph(header_text, header_style_criteria))
        
        table_data[0].append(Paragraph("<b>Total<br/>(50)</b>", header_style_sm))
        
        # Add student data with proper formatting
        for idx, (student, ev) in enumerate(sorted(all_students, key=lambda x: (x[0].group_no or '', x[0].name)), 1):
            # Format student name to fit
            student_name = student.name
            if len(student_name) > 30:
                student_name = student_name[:27] + "..."
            
            # Format guide name to fit
            guide_name = student.project_guide or '-'
            if len(guide_name) > 25:
                guide_name = guide_name[:22] + "..."
            
            row = [
                Paragraph(str(idx), ParagraphStyle('center', fontSize=9, alignment=TA_CENTER)),
                Paragraph(str(student.group_no or '-'), ParagraphStyle('center', fontSize=9, alignment=TA_CENTER)),
                Paragraph(f'<font size=7>{student.seat_no}</font>', ParagraphStyle('center', fontSize=7, alignment=TA_CENTER, leading=9, wordWrap='CJK')),
                Paragraph(student_name, ParagraphStyle('left', fontSize=9, alignment=TA_LEFT)),
                Paragraph(guide_name, ParagraphStyle('left', fontSize=8, alignment=TA_LEFT, leading=10))
            ]
            # Add criteria marks with proper formatting
            for i in range(1, len(criteria) + 1):
                mark = str(getattr(ev, f"criteria{i}", 0))
                row.append(Paragraph(f"<b>{mark}</b>", ParagraphStyle('center', fontSize=10, alignment=TA_CENTER)))
            # Add total with emphasis
            row.append(Paragraph(f"<b>{ev.total_marks}</b>", ParagraphStyle('center', fontSize=11, alignment=TA_CENTER, textColor=colors.HexColor('#006400'))))
            table_data.append(row)
        
        # Create table with optimized column widths - wider columns for better spacing
        col_widths = [11*mm, 14*mm, 22*mm, 35*mm, 29*mm] + [18*mm] * len(criteria) + [14*mm]
        summary_table = Table(table_data, colWidths=col_widths, repeatRows=1, rowHeights=None)
        
        # Apply enhanced styling with better visibility
        summary_table.setStyle(TableStyle([
            # Header styling with gradient-like appearance
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),  # Deep blue
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            
            # Data styling - no font specifications for Paragraph content
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
            
            # Grid and borders with better visibility
            ('GRID', (0, 0), (-1, -1), 0.75, colors.HexColor('#404040')),
            ('LINEBELOW', (0, 0), (-1, 0), 2.5, colors.HexColor('#1e3a8a')),
            ('LINEAFTER', (4, 0), (4, -1), 1.5, colors.HexColor('#666666')),  # Separator after guide column
            
            # Enhanced padding for better text fit - increased for headers to prevent collision
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ]))
        
        # Add alternating row colors with better contrast
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f0f4f8'))
                ]))
            else:
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, i), (-1, i), colors.white)
                ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer
