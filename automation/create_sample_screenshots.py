#!/usr/bin/env python3
"""
Create sample screenshots for demonstration of the validation system
"""

import os
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

def create_sample_screenshot(name: str, screen_type: str, width: int = 1200, height: int = 800):
    """Create a sample screenshot image"""
    
    # Create image with modern gradient background
    img = Image.new('RGB', (width, height), color='#FAFAFA')
    draw = ImageDraw.Draw(img)
    
    # Create gradient background
    for y in range(height):
        r = int(99 + (102 - 99) * y / height)  # 6366F1 to 8B5CF6
        g = int(102 + (92 - 102) * y / height)
        b = int(241 + (246 - 241) * y / height)
        color = (r, g, b)
        draw.line([(0, y), (width, y)], fill=color)
    
    # Add overlay for content area
    content_x = 50
    content_y = 50
    content_width = width - 100
    content_height = height - 100
    
    # White content area with rounded corners effect
    draw.rectangle([content_x, content_y, content_x + content_width, content_y + content_height], 
                   fill='white', outline='#E5E7EB', width=2)
    
    try:
        # Try to use a system font
        title_font = ImageFont.truetype("arial.ttf", 32)
        subtitle_font = ImageFont.truetype("arial.ttf", 18)
        body_font = ImageFont.truetype("arial.ttf", 14)
    except:
        # Fallback to default font
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
    
    # Add screen-specific content
    if screen_type == 'login_screen':
        # Login screen elements
        draw.text((content_x + 50, content_y + 50), "Welcome Back", fill='#111827', font=title_font)
        draw.text((content_x + 50, content_y + 100), "Sign in to your account", fill='#4B5563', font=subtitle_font)
        
        # Email field
        draw.rectangle([content_x + 50, content_y + 150, content_x + 400, content_y + 190], 
                       outline='#D1D5DB', width=2)
        draw.text((content_x + 60, content_y + 160), "Email", fill='#9CA3AF', font=body_font)
        
        # Password field
        draw.rectangle([content_x + 50, content_y + 210, content_x + 400, content_y + 250], 
                       outline='#D1D5DB', width=2)
        draw.text((content_x + 60, content_y + 220), "Password", fill='#9CA3AF', font=body_font)
        
        # Sign in button
        draw.rectangle([content_x + 50, content_y + 280, content_x + 400, content_y + 320], 
                       fill='#6366F1', outline='#6366F1')
        draw.text((content_x + 200, content_y + 290), "Sign In", fill='white', font=subtitle_font)
        
    elif screen_type == 'dashboard':
        # Dashboard elements
        draw.text((content_x + 50, content_y + 50), "Dashboard", fill='#111827', font=title_font)
        draw.text((content_x + 50, content_y + 100), "Welcome to Auto Job Apply", fill='#4B5563', font=subtitle_font)
        
        # Stats cards
        for i, (label, value) in enumerate([("Applications", "24"), ("Interviews", "8"), ("Offers", "3")]):
            x = content_x + 50 + i * 150
            y = content_y + 150
            draw.rectangle([x, y, x + 120, y + 80], fill='#F8FAFC', outline='#E5E7EB', width=1)
            draw.text((x + 10, y + 10), label, fill='#6B7280', font=body_font)
            draw.text((x + 10, y + 40), value, fill='#111827', font=title_font)
    
    elif screen_type == 'job_application':
        # Job application form
        draw.text((content_x + 50, content_y + 50), "Apply for Job", fill='#111827', font=title_font)
        draw.text((content_x + 50, content_y + 100), "Fill out the application form", fill='#4B5563', font=subtitle_font)
        
        # Form fields
        fields = ["Job Title", "Company", "Location", "Salary Range"]
        for i, field in enumerate(fields):
            y = content_y + 150 + i * 60
            draw.rectangle([content_x + 50, y, content_x + 500, y + 40], 
                           outline='#D1D5DB', width=2)
            draw.text((content_x + 60, y + 10), field, fill='#9CA3AF', font=body_font)
    
    # Add timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    draw.text((content_x + content_width - 200, content_y + content_height - 30), 
              f"Generated: {timestamp}", fill='#9CA3AF', font=body_font)
    
    return img

def main():
    """Create sample screenshots for all screen types"""
    
    screenshots_dir = "automation/screenshots"
    
    # Screen configurations
    screens = [
        ("login_screen", "initial", 1200, 800),
        ("login_screen", "filled_form", 1200, 800),
        ("dashboard", "main_view", 1200, 800),
        ("dashboard", "drawer_open", 1200, 800),
        ("job_application", "form_view", 1200, 800),
        ("job_application", "filled_form", 1200, 800),
    ]
    
    # Responsive sizes
    responsive_sizes = [
        ("mobile", 375, 667),
        ("tablet", 768, 1024),
        ("desktop", 1920, 1080),
    ]
    
    print("🎨 Creating sample screenshots...")
    
    # Create main screen screenshots
    for screen_name, suffix, width, height in screens:
        img = create_sample_screenshot(f"{screen_name}_{suffix}", screen_name, width, height)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{screen_name}_{suffix}_{timestamp}.png"
        filepath = os.path.join(screenshots_dir, screen_name, filename)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        img.save(filepath)
        print(f"📸 Created: {filepath}")
    
    # Create responsive screenshots
    responsive_dir = os.path.join(screenshots_dir, "responsive")
    os.makedirs(responsive_dir, exist_ok=True)
    
    for size_name, width, height in responsive_sizes:
        img = create_sample_screenshot(f"responsive_{size_name}", "dashboard", width, height)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"responsive_{size_name}_{timestamp}.png"
        filepath = os.path.join(responsive_dir, filename)
        
        img.save(filepath)
        print(f"📱 Created: {filepath}")
    
    print(f"\n✅ Sample screenshots created successfully!")
    print(f"📁 Location: {screenshots_dir}")
    
    # Create a slightly different version for testing validation
    print("\n🔄 Creating modified screenshots for validation testing...")
    
    # Create a modified login screen for testing
    modified_img = create_sample_screenshot("login_screen_modified", "login_screen", 1200, 800)
    # Add a small difference
    draw = ImageDraw.Draw(modified_img)
    draw.rectangle([100, 100, 150, 150], fill='#EC4899')  # Pink square difference
    
    modified_path = os.path.join(screenshots_dir, "login_screen", f"login_screen_modified_{timestamp}.png")
    modified_img.save(modified_path)
    print(f"🔧 Created modified screenshot: {modified_path}")

if __name__ == "__main__":
    main()
