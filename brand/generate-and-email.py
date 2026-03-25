import os, sys, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
TO_EMAIL = 'yesusera.hailu@gmail.com'

BRAND_DIR = os.path.dirname(os.path.abspath(__file__))

def draw_bolt(draw, x, y, s, color1='#059669', color2='#34d399'):
    """Draw the bolt shape"""
    points = [
        (x + 36*s, y + 4*s),
        (x + 16*s, y + 34*s),
        (x + 30*s, y + 34*s),
        (x + 26*s, y + 60*s),
        (x + 50*s, y + 26*s),
        (x + 34*s, y + 26*s),
    ]
    # Use solid color (gradient not easy in Pillow)
    draw.polygon(points, fill=color1)

def create_icon(size, bg_color, filename):
    img = Image.new('RGBA', (size, size), bg_color)
    draw = ImageDraw.Draw(img)
    s = size / 64
    draw_bolt(draw, 0, 0, s, '#10b981')
    path = os.path.join(BRAND_DIR, filename)
    img.save(path, 'PNG')
    return path

def create_banner(w, h, dark, filename):
    bg = '#0f172a' if dark else '#ffffff'
    img = Image.new('RGBA', (w, h), bg)
    draw = ImageDraw.Draw(img)
    
    # Bolt centered
    icon_size = h * 0.5
    s = icon_size / 64
    bolt_x = w/2 - icon_size * 0.5
    bolt_y = h * 0.1
    draw_bolt(draw, bolt_x, bolt_y, s, '#10b981')
    
    # Text "HeroCall" - use default font at large size
    try:
        font = ImageFont.truetype("arial.ttf", int(h * 0.15))
        small_font = ImageFont.truetype("arial.ttf", int(h * 0.05))
    except:
        font = ImageFont.load_default()
        small_font = font
    
    text_color = '#f0f0f5' if dark else '#0f172a'
    green = '#10b981'
    
    # Measure "Hero"
    hero_bbox = draw.textbbox((0,0), "Hero", font=font)
    hero_w = hero_bbox[2] - hero_bbox[0]
    call_bbox = draw.textbbox((0,0), "Call", font=font)
    call_w = call_bbox[2] - call_bbox[0]
    total_w = hero_w + call_w
    
    text_x = (w - total_w) / 2
    text_y = h * 0.55
    
    draw.text((text_x, text_y), "Hero", fill=text_color, font=font)
    draw.text((text_x + hero_w, text_y), "Call", fill=green, font=font)
    
    # Tagline
    tag = "AI agents that make the right call."
    tag_bbox = draw.textbbox((0,0), tag, font=small_font)
    tag_w = tag_bbox[2] - tag_bbox[0]
    tag_color = '#64748b' if dark else '#94a3b8'
    draw.text(((w - tag_w)/2, h * 0.78), tag, fill=tag_color, font=small_font)
    
    path = os.path.join(BRAND_DIR, filename)
    img.save(path, 'PNG')
    return path

def create_square(size, dark, filename):
    bg = '#0f172a' if dark else '#ffffff'
    img = Image.new('RGBA', (size, size), bg)
    draw = ImageDraw.Draw(img)
    
    icon_size = size * 0.45
    s = icon_size / 64
    icon_x = (size - icon_size) / 2
    icon_y = size * 0.12
    draw_bolt(draw, icon_x, icon_y, s, '#10b981')
    
    try:
        font = ImageFont.truetype("arial.ttf", int(size * 0.1))
        small_font = ImageFont.truetype("arial.ttf", int(size * 0.04))
    except:
        font = ImageFont.load_default()
        small_font = font
    
    text_color = '#f0f0f5' if dark else '#0f172a'
    green = '#10b981'
    
    hero_bbox = draw.textbbox((0,0), "Hero", font=font)
    hero_w = hero_bbox[2] - hero_bbox[0]
    call_bbox = draw.textbbox((0,0), "Call", font=font)
    call_w = call_bbox[2] - call_bbox[0]
    total_w = hero_w + call_w
    
    text_x = (size - total_w) / 2
    text_y = size * 0.68
    draw.text((text_x, text_y), "Hero", fill=text_color, font=font)
    draw.text((text_x + hero_w, text_y), "Call", fill=green, font=font)
    
    tag = "Make the right call."
    tag_bbox = draw.textbbox((0,0), tag, font=small_font)
    tag_w = tag_bbox[2] - tag_bbox[0]
    tag_color = '#64748b' if dark else '#94a3b8'
    draw.text(((size - tag_w)/2, size * 0.82), tag, fill=tag_color, font=small_font)
    
    path = os.path.join(BRAND_DIR, filename)
    img.save(path, 'PNG')
    return path

# Generate all PNGs
print("Generating PNGs...")
files = []
files.append(create_icon(512, '#0f172a', 'herocall-icon-dark-512.png'))
files.append(create_icon(512, '#ffffff', 'herocall-icon-light-512.png'))
files.append(create_icon(512, '#059669', 'herocall-icon-green-512.png'))
files.append(create_icon(256, '#0f172a', 'herocall-icon-dark-256.png'))
files.append(create_icon(128, '#0f172a', 'herocall-icon-dark-128.png'))
files.append(create_square(400, True, 'herocall-ig-dark-400.png'))
files.append(create_square(400, False, 'herocall-ig-light-400.png'))
files.append(create_banner(1500, 500, True, 'herocall-twitter-banner-dark.png'))
files.append(create_banner(1500, 500, False, 'herocall-twitter-banner-light.png'))
files.append(create_banner(800, 200, True, 'herocall-full-dark-800.png'))
files.append(create_banner(800, 200, False, 'herocall-full-light-800.png'))
print(f"Generated {len(files)} PNGs")

# Send email
print(f"Sending to {TO_EMAIL}...")
msg = MIMEMultipart()
msg['Subject'] = '⚡ HeroCall Brand Assets — Logo PNGs'
msg['From'] = SMTP_USER
msg['To'] = TO_EMAIL

body = """Hey Yesu,

Here are your HeroCall logo files in PNG format:

PROFILE PICS (Icon Only):
• herocall-icon-dark-512.png — Dark background, 512×512 (Twitter/X, Instagram)
• herocall-icon-light-512.png — White background, 512×512
• herocall-icon-green-512.png — Green background, 512×512
• herocall-icon-dark-256.png — Dark, 256×256
• herocall-icon-dark-128.png — Dark, 128×128

INSTAGRAM SQUARE:
• herocall-ig-dark-400.png — Dark, 400×400 with wordmark
• herocall-ig-light-400.png — Light, 400×400 with wordmark

TWITTER/X BANNER:
• herocall-twitter-banner-dark.png — 1500×500 dark
• herocall-twitter-banner-light.png — 1500×500 light

FULL WORDMARK:
• herocall-full-dark-800.png — 800×200 dark
• herocall-full-light-800.png — 800×200 light

Recommendation: Use the dark icon (512) for profile pics and the dark banner for Twitter header.

— HeroCall Frontend Agent ⚡
"""

msg.attach(MIMEText(body, 'plain'))

for filepath in files:
    fname = os.path.basename(filepath)
    with open(filepath, 'rb') as f:
        img_data = f.read()
    img_attachment = MIMEImage(img_data, name=fname)
    img_attachment.add_header('Content-Disposition', 'attachment', filename=fname)
    msg.attach(img_attachment)

with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
    server.starttls()
    server.login(SMTP_USER, SMTP_PASSWORD)
    server.send_message(msg)

print(f"✅ Email sent to {TO_EMAIL} with {len(files)} attachments!")
