from PIL import Image, ImageDraw, ImageFont
import os

def create_college_logo():
    """Create a simple college logo"""
    # Create a 120x120 image with white background
    img = Image.new('RGB', (120, 120), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw a circle border
    draw.ellipse([10, 10, 110, 110], outline='navy', width=3)
    
    # Draw inner circle
    draw.ellipse([20, 20, 100, 100], outline='darkblue', width=2)
    
    # Try to use a font, fallback to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 12)
        small_font = ImageFont.truetype("arial.ttf", 10)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Add text
    draw.text((60, 40), "GNDEC", font=font, fill='darkblue', anchor='mm')
    draw.text((60, 55), "BIDAR", font=small_font, fill='navy', anchor='mm')
    draw.text((60, 70), "ENGINEERING", font=small_font, fill='darkblue', anchor='mm')
    draw.text((60, 85), "COLLEGE", font=small_font, fill='navy', anchor='mm')
    
    # Save the logo
    logo_path = os.path.join(os.path.dirname(__file__), 'college_logo.png')
    img.save(logo_path)
    print(f"Logo created at: {logo_path}")
    return logo_path

if __name__ == "__main__":
    create_college_logo()