import json, os
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter
meta = json.load(open('meta.json')); os.makedirs('covers', exist_ok=True)
F = lambda n, s: ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-%s.ttf' % n, s)
ACC = {}
import importlib.util, sys
sys.path.insert(0, '.'); import xl, glob
for f in sorted(glob.glob('src/s*.py')): exec(compile(open(f).read(), f, 'exec'), {'__name__': 'x'})
for b in xl.Book.REG: ACC[b.id] = b.accent
BULLETS = {
 'freelancer-income-tax-tracker': ['Income + expense log', 'Quarterly tax set-aside estimate', 'Monthly charts and top clients'],
 'small-business-pl-cash-flow': ['Monthly P&L by category', 'Cash balance + runway', 'Dashboard with charts'],
 'debt-payoff-planner-snowball-avalanche': ['Snowball or avalanche', 'Debt-free date + interest saved', '180-month schedule'],
 'household-budget-planner-monthly': ['Plan vs actual by category', 'Savings rate + year view', 'Pick any month'],
 'etsy-seller-profit-tracker': ['Real profit after fees', 'Profit by product', 'Price calculator'],
 'rental-property-analyzer-roi-calculator': ['Cap rate, cash-on-cash, DSCR', '10-year projection', 'Portfolio + rent log'],
 'wedding-planner-budget-guest-list': ['Budget vs actual vs paid', 'RSVP, meals, seating', 'Countdown checklist'],
 'project-tracker-gantt-chart': ['Auto Gantt chart', 'Dependencies + working days', 'Status dashboard'],
 'inventory-tracker-reorder-alerts': ['Live stock + value', 'Reorder list by supplier', 'Best sellers'],
 'net-worth-tracker-savings-goals': ['Monthly net worth trend', 'Asset allocation', 'Savings goal planner'],
 'sales-crm-pipeline-tracker': ['Weighted forecast', 'Win rate by source', 'Follow-up list'],
 'job-search-tracker-application-dashboard': ['Application funnel', 'Follow-up reminders', 'Weekly goal tracker']}
def hexrgb(h): return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
for m in meta:
    acc = hexrgb(ACC[m['id']]); W, H = 2000, 1500
    img = Image.new('RGB', (W, H), tuple(int(c * .18 + 255 * .82) for c in acc)); dr = ImageDraw.Draw(img)
    dr.rectangle([0, 0, W, 560], fill=acc)
    title = m['title'].split(':')[0].split('+')[0].strip() if len(m['title']) > 40 else m['title']
    # wrap title
    words = m['title'].split(); lines = ['']; 
    for w in words:
        if dr.textlength(lines[-1] + ' ' + w, font=F('Bold', 84)) > 1700: lines.append(w)
        else: lines[-1] = (lines[-1] + ' ' + w).strip()
    y = 70
    for ln in lines[:3]: dr.text((100, y), ln, font=F('Bold', 84), fill='white'); y += 100
    dr.text((100, y + 10), 'Excel + Google Sheets template  |  Instant download', font=F('Regular', 40), fill=(255, 255, 255))
    shot = Image.open('shots/%s.png' % m['id']).convert('RGB'); bg = Image.new('RGB', shot.size, (255, 255, 255)); bb = ImageChops.difference(shot, bg).getbbox() or (0, 0) + shot.size
    shot = shot.crop((max(0, bb[0] - 20), max(0, bb[1] - 20), min(shot.width, bb[2] + 20), min(shot.height, bb[3] + 20)))
    tw = 1300; th = int(shot.height * tw / shot.width)
    if th > 780: th = 780; tw = int(shot.width * th / shot.height)
    tw = min(tw, 1280)
    shot = shot.resize((tw, th), Image.LANCZOS); sh = Image.new('RGBA', (tw + 80, th + 80), (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle([40, 50, tw + 40, th + 50], fill=(0, 0, 0, 110)); sh = sh.filter(ImageFilter.GaussianBlur(18))
    x0 = 100; y0 = 640; img.paste(sh, (x0 - 40, y0 - 40), sh); img.paste(shot, (x0, y0))
    bx = 1440; by = 660
    for i, bl in enumerate(BULLETS[m['id']]):
        dr.rounded_rectangle([bx, by + i * 150, W - 70, by + i * 150 + 120], 24, fill='white', outline=acc, width=4); dr.text((bx + 30, by + i * 150 + 32), bl, font=F('Bold', 31), fill=(30, 30, 40))
    dr.rounded_rectangle([bx, 1150, W - 70, 1300], 30, fill=acc); dr.text((bx + 60, 1185), 'No macros', font=F('Bold', 44), fill='white'); dr.text((bx + 60, 1240), 'Works offline', font=F('Regular', 36), fill='white')
    dr.text((100, 1440), 'Yellow cells = inputs. Sample data included. Not tax, legal or financial advice.', font=F('Regular', 30), fill=(90, 90, 100))
    img.save('covers/%s.png' % m['id'])
print('covers done')
