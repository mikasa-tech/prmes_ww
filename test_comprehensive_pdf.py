#!/usr/bin/env python3

from models import db, Student, Evaluation
from app import create_app
from comprehensive_pdf_template import build_comprehensive_pdf

def test_comprehensive_pdf():
    """Test comprehensive PDF generation with current data"""
    app = create_app()
    
    with app.app_context():
        print("Testing Comprehensive PDF Generation...")
        
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
        
        print(f"Guide-wise data: {list(guides.keys())}")
        print(f"Group-wise data: {list(groups.keys())}")
        
        if not guides and not groups:
            print("❌ No data found for PDF generation")
            return
        
        try:
            pdf_buffer = build_comprehensive_pdf(guides, groups)
            
            # Save test PDF
            with open("test_comprehensive_report.pdf", "wb") as f:
                f.write(pdf_buffer.getvalue())
            
            print("✅ Comprehensive PDF generated successfully!")
            print("   - Saved as: test_comprehensive_report.pdf")
            print(f"   - Guides included: {list(guides.keys())}")
            print(f"   - Groups included: {list(groups.keys())}")
            
        except Exception as e:
            print(f"❌ Error generating PDF: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_comprehensive_pdf()