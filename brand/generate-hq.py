import os, smtplib, io
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend', '.env'))

BRAND_DIR = os.path.dirname(os.path.abspath(__file__))

# Render at 4x then downscale for smooth anti-aliasing
SUPERSAMPLE = 4

def draw_bolt(draw, x, y, s):
    points = [
        (x + 36*s, y + 4*s),
        (x + 16*s, y + 34*s),
        (x + 30*s, y + 34*s),
        (x + 26*s, y + 60*s),
        (x + 50*s, y + 26*s),
        (x + 34*s, y + 26*s),
    ]
    draw.polygon(points, fill='#10b981')
    # Add highlight for gradient effect
    highlight = [
        (x + 36*s, y + 4*s),
        (x + 22*s, y + 28*s),
        (x + 30*s, y + 28*s),
        (x + 34*s, y + 26*s),
    ]
    draw.polygon(highlight, fill='#059669')

def create_icon(target_size, bg_color, filename):
    size = target_size * SUPERSAMPLE
    img = Image.new('RGBA', (size, size), bg_color)
    draw = ImageDraw.Draw(img)
    s = size / 64
    draw_bolt(draw, 0, 0, s)
    img = img.resize((target_size, target_size), Image.LANCZOS)
    path = os.path.join(BRAND_DIR, filename)
    img.save(path, 'PNG')
    return path

def get_font(size):
    try:
        return ImageFont.truetype("C:\\Windows\\Fonts\\arialbd.ttf", size)
    except:
        try:
            return ImageFont.truetype("arial.ttf", size)
        except:
            return ImageFont.load_default()

def create_wordmark(target_w, target_h, dark, filename):
    w = target_w * SUPERSAMPLE
    h = target_h * SUPERSAMPLE
    bg = '#0f172a' if dark else '#ffffff'
    img = Image.new('RGBA', (w, h), bg)
    draw = ImageDraw.Draw(img)
    
    icon_h = int(h * 0.6)
    s = icon_h / 64
    icon_x = int(h * 0.3)
    icon_y = int((h - icon_h) / 2)
    draw_bolt(draw, icon_x, icon_y, s)
    
    font_size = int(h * 0.3)
    font = get_font(font_size)
    
    text_x = int(icon_x + icon_h + h * 0.15)
    text_y = int(h / 2)
    
    hero_color = '#f0f0f5' if dark else '#0f172a'
    hero_bbox = draw.textbbox((0, 0), "Hero", font=font)
    hero_w = hero_bbox[2] - hero_bbox[0]
    hero_h = hero_bbox[3] - hero_bbox[1]
    
    y_pos = int((h - hero_h) / 2)
    draw.text((text_x, y_pos), "Hero", fill=hero_color, font=font)
    draw.text((text_x + hero_w + int(w*0.005), y_pos), "Call", fill='#10b981', font=font)
    
    img = img.resize((target_w, target_h), Image.LANCZOS)
    path = os.path.join(BRAND_DIR, filename)
    img.save(path, 'PNG')
    return path

def create_square(target_size, dark, filename):
    size = target_size * SUPERSAMPLE
    bg = '#0f172a' if dark else '#ffffff'
    img = Image.new('RGBA', (size, size), bg)
    draw = ImageDraw.Draw(img)
    
    icon_h = int(size * 0.4)
    s = icon_h / 64
    icon_x = int((size - icon_h) / 2)
    icon_y = int(size * 0.12)
    draw_bolt(draw, icon_x, icon_y, s)
    
    font_size = int(size * 0.1)
    font = get_font(font_size)
    small_font = get_font(int(size * 0.04))
    
    hero_color = '#f0f0f5' if dark else '#0f172a'
    
    hero_bbox = draw.textbbox((0, 0), "Hero", font=font)
    hero_w = hero_bbox[2] - hero_bbox[0]
    call_bbox = draw.textbbox((0, 0), "Call", font=font)
    call_w = call_bbox[2] - call_bbox[0]
    total_w = hero_w + call_w + int(size * 0.01)
    
    tx = int((size - total_w) / 2)
    ty = int(size * 0.65)
    draw.text((tx, ty), "Hero", fill=hero_color, font=font)
    draw.text((tx + hero_w + int(size*0.01), ty), "Call", fill='#10b981', font=font)
    
    tag = "Make the right call."
    tag_bbox = draw.textbbox((0, 0), tag, font=small_font)
    tag_w = tag_bbox[2] - tag_bbox[0]
    tag_color = '#64748b' if dark else '#94a3b8'
    draw.text((int((size - tag_w)/2), int(size * 0.8)), tag, fill=tag_color, font=small_font)
    
    img = img.resize((target_size, target_size), Image.LANCZOS)
    path = os.path.join(BRAND_DIR, filename)
    img.save(path, 'PNG')
    return path

def create_banner(target_w, target_h, dark, filename):
    w = target_w * SUPERSAMPLE
    h = target_h * SUPERSAMPLE
    bg = '#0f172a' if dark else '#ffffff'
    img = Image.new('RGBA', (w, h), bg)
    draw = ImageDraw.Draw(img)
    
    icon_h = int(h * 0.4)
    s = icon_h / 64
    icon_x = int(w/2 - icon_h * 0.5)
    icon_y = int(h * 0.05)
    draw_bolt(draw, icon_x, icon_y, s)
    
    font_size = int(h * 0.18)
    font = get_font(font_size)
    small_font = get_font(int(h * 0.055))
    
    hero_color = '#f0f0f5' if dark else '#0f172a'
    
    hero_bbox = draw.textbbox((0, 0), "Hero", font=font)
    hero_w = hero_bbox[2] - hero_bbox[0]
    call_bbox = draw.textbbox((0, 0), "Call", font=font)
    call_w = call_bbox[2] - call_bbox[0]
    total_w = hero_w + call_w
    
    tx = int((w - total_w) / 2)
    ty = int(h * 0.52)
    draw.text((tx, ty), "Hero", fill=hero_color, font=font)
    draw.text((tx + hero_w, ty), "Call", fill='#10b981', font=font)
    
    tag = "AI agents that make the right call. Every time."
    tag_bbox = draw.textbbox((0, 0), tag, font=small_font)
    tag_w = tag_bbox[2] - tag_bbox[0]
    tag_color = '#64748b' if dark else '#94a3b8'
    draw.text((int((w - tag_w)/2), int(h * 0.76)), tag, fill=tag_color, font=small_font)
    
    img = img.resize((target_w, target_h), Image.LANCZOS)
    path = os.path.join(BRAND_DIR, filename)
    img.save(path, 'PNG')
    return path

# Generate all HQ PNGs
print("Generating HQ PNGs (4x supersample + LANCZOS downscale)...")
files = []
files.append(create_icon(512, '#0f172a', 'herocall-icon-dark-512.png'))
files.append(create_icon(512, '#ffffff', 'herocall-icon-light-512.png'))
files.append(create_icon(512, '#059669', 'herocall-icon-green-512.png'))
files.append(create_icon(256, '#0f172a', 'herocall-icon-dark-256.png'))
files.append(create_icon(128, '#0f172a', 'herocall-icon-dark-128.png'))
files.append(create_square(1080, True, 'herocall-ig-dark-1080.png'))
files.append(create_square(1080, False, 'herocall-ig-light-1080.png'))
files.append(create_banner(1500, 500, True, 'herocall-twitter-banner-dark.png'))
files.append(create_banner(1500, 500, False, 'herocall-twitter-banner-light.png'))
files.append(create_wordmark(800, 200, True, 'herocall-full-dark-800.png'))
files.append(create_wordmark(800, 200, False, 'herocall-full-light-800.png'))
print(f"Generated {len(files)} HQ PNGs")

# Email
print("Sending email...")
msg = MIMEMultipart()
msg['Subject'] = 'HeroCall Brand Assets - HQ Logo PNGs'
msg['From'] = os.getenv('SMTP_USER')
msg['To'] = 'yesusera.hailu@gmail.com'

body = """Hey Yesu,

Here are your HeroCall logos - HIGH QUALITY this time (4x supersampled, smooth edges):

PROFILE PICS (Icon Only):
- herocall-icon-dark-512.png - USE THIS for Twitter/X + Instagram
- herocall-icon-light-512.png - White background
- herocall-icon-green-512.png - Green background
- herocall-icon-dark-256.png - Smaller dark version
- herocall-icon-dark-128.png - Favicon size

INSTAGRAM (1080x1080 square):
- herocall-ig-dark-1080.png - Dark with bolt + wordmark
- herocall-ig-light-1080.png - Light version

TWITTER/X BANNER (1500x500):
- herocall-twitter-banner-dark.png
- herocall-twitter-banner-light.png

WORDMARK (800x200):
- herocall-full-dark-800.png
- herocall-full-light-800.png

These should be crisp and clean now. No more pixels.

- HeroCall Frontend Agent
"""

msg.attach(MIMEText(body, 'plain'))

for filepath in files:
    fname = os.path.basename(filepath)
    with open(filepath, 'rb') as f:
        att = MIMEImage(f.read(), name=fname)
        att.add_header('Content-Disposition', 'attachment', filename=fname)
        msg.attach(att)

with smtplib.SMTP(os.getenv('SMTP_HOST','smtp.gmail.com'), int(os.getenv('SMTP_PORT','587')), timeout=15) as s:
    s.starttls()
    s.login(os.getenv('SMTP_USER'), os.getenv('SMTP_PASSWORD'))
    s.send_message(msg)

print(f"Email sent with {len(files)} HQ attachments!")
