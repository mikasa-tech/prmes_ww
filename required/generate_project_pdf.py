import os
import sys
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted, PageBreak
from reportlab.lib.units import inch
from reportlab.lib import colors

# Define directories
BASE_DIR = Path(__file__).parent.resolve()
ARCHIVE_DIR = BASE_DIR / "project_pdf_archive"
TEMPLATES_DIR = BASE_DIR / "templates"

# Create archive directory if it doesn't exist
ARCHIVE_DIR.mkdir(exist_ok=True)

# List of files to convert (Relative to BASE_DIR)
FILES_TO_CONVERT = [
    # Core Logic
    "app.py",
    "models.py",
    "utils.py",
    "upload_helpers.py",
    "review_config.py",
    "pdf_template.py",
    "comprehensive_pdf_template.py",
    "serve.py",
    "run_local.py",
    
    # Templates
    "templates/base.html",
    "templates/student_detail.html",
    "templates/students.html",
    "templates/students_groupwise.html",
    "templates/students_guidewise.html",
    "templates/students_individual.html",
    "templates/upload.html",
    
    # Documentation & Config
    "README.md",
    "HOW_CODE_WORKS_SIMPLE.md",
    "LOCAL_SETUP.md",
    "EXCEL_FORMATS_GUIDE.md",
    "MULTI_REVIEW_GUIDE.md",
    "REVERSE_ENGINEERING_EXPLAINED.md",
    "requirements.txt",
    "run.bat",
    "run.ps1",
]

def convert_to_pdf(file_rel_path):
    file_path = BASE_DIR / file_rel_path
    if not file_path.exists():
        print(f"Skipping: {file_rel_path} (File not found)")
        return

    output_filename = file_rel_path.replace("/", "_").replace("\\", "_") + ".pdf"
    output_path = ARCHIVE_DIR / output_filename
    
    print(f"Converting: {file_rel_path} -> {output_filename}")
    
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )
    
    styles = getSampleStyleSheet()
    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=10,
        textColor=colors.black,
        wordWrap='CJK',
    )
    
    title_style = styles['Heading1']
    content = []
    
    # Add Title
    content.append(Paragraph(f"Project File: {file_rel_path}", title_style))
    content.append(Spacer(1, 0.2 * inch))
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
            
        # Join lines but limit each chunk to avoid ReportLab memory issues with massive strings
        # and splitting them across pages. Preformatted handles newlines well.
        text_content = "".join(lines)
        
        # Split text into chunks if it's too large for a single Preformatted block
        # (Though usually simple for source files)
        p = Preformatted(text_content, code_style)
        content.append(p)
        
    except Exception as e:
        content.append(Paragraph(f"Error reading file: {str(e)}", styles['Normal']))

    doc.build(content)

if __name__ == "__main__":
    print(f"Starting PDF Archive Generation in: {ARCHIVE_DIR}")
    for file_name in FILES_TO_CONVERT:
        convert_to_pdf(file_name)
    print("Done! All PDFs are in the 'project_pdf_archive' folder.")
