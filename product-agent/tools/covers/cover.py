# usage: python3 cover.py out.png "Title" "Subtitle" "bullet1|bullet2|bullet3" "#hex accent" "Footer note"
import sys
from PIL import Image, ImageDraw, ImageFont
out, title, sub, bullets, acc, foot = sys.argv[1:7]
F = lambda n, s: ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-%s.ttf' % n, s)
rgb = tuple(int(acc[i:i+2], 16) for i in (1, 3, 5))
W, H = 2000, 1500
img = Image.new('RGB', (W, H), tuple(int(c * .12 + 255 * .88) for c in rgb)); d = ImageDraw.Draw(img)
d.rectangle([0, 0, W, 620], fill=rgb)
for k in range(6):  # simple generated pattern (no external art)
    d.ellipse([1500 + k * 70, 60 + k * 30, 1700 + k * 70, 260 + k * 30], outline=(255, 255, 255), width=3)
lines = ['']
for w in title.split():
    if d.textlength((lines[-1] + ' ' + w).strip(), font=F('Bold', 100)) > 1650: lines.append(w)
    else: lines[-1] = (lines[-1] + ' ' + w).strip()
y = 90
for ln in lines[:3]: d.text((100, y), ln, font=F('Bold', 100), fill='white'); y += 120
d.text((100, y + 20), sub, font=F('Regular', 46), fill='white')
by = 720
for b in bullets.split('|'):
    d.rounded_rectangle([100, by, W - 100, by + 150], 30, fill='white', outline=rgb, width=5)
    d.ellipse([140, by + 45, 200, by + 105], fill=rgb)
    d.text((240, by + 40), b, font=F('Bold', 56), fill=(30, 30, 40)); by += 190
d.text((100, 1420), foot, font=F('Regular', 32), fill=(90, 90, 100))
img.save(out)
