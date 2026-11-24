import re, os
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_COLOR_INDEX, WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
ACC = RGBColor(0x4A, 0x3F, 0x5C); DISC = 'Template only, not legal advice; have a lawyer review for your jurisdiction.'
FIELD = re.compile(r'(\[[^\]\[]+\])')
def new(title, subtitle, disclaimer=True):
    d = Document(); s = d.sections[0]; s.left_margin = s.right_margin = Inches(1); s.top_margin = s.bottom_margin = Inches(0.9)
    st = d.styles['Normal']; st.font.name = 'Calibri'; st.font.size = Pt(11); st.element.rPr.rFonts.set(qn('w:eastAsia'), 'Calibri')
    for h, sz in (('Heading 1', 15), ('Heading 2', 12.5)):
        x = d.styles[h]; x.font.name = 'Calibri'; x.font.size = Pt(sz); x.font.bold = True; x.font.color.rgb = ACC
    p = d.add_paragraph(); r = p.add_run(title); r.bold = True; r.font.size = Pt(22); r.font.color.rgb = ACC
    if subtitle: q = d.add_paragraph(); r = q.add_run(subtitle); r.italic = True; r.font.color.rgb = RGBColor(0x6B, 0x72, 0x80)
    f = s.footer.paragraphs[0]; f.alignment = WD_ALIGN_PARAGRAPH.CENTER; r = f.add_run(DISC if disclaimer else 'Template for your business. Replace every [bracketed field] before use.'); r.font.size = Pt(8.5); r.font.color.rgb = RGBColor(0x6B, 0x72, 0x80)
    return d
def runs(p, text, bold=False, italic=False):
    for part in FIELD.split(text):
        if not part: continue
        r = p.add_run(part); r.bold = bold; r.italic = italic
        if FIELD.fullmatch(part): r.font.highlight_color = WD_COLOR_INDEX.YELLOW
def para(d, text, bold=False, italic=False, indent=0, after=6):
    p = d.add_paragraph(); runs(p, text, bold, italic); p.paragraph_format.space_after = Pt(after)
    if indent: p.paragraph_format.left_indent = Inches(indent)
    return p
def clause(d, num, title, text):
    p = d.add_paragraph(); r = p.add_run('%s  %s. ' % (num, title)); r.bold = True; runs(p, text); p.paragraph_format.space_after = Pt(7)
def bullets(d, items):
    for i in items: p = d.add_paragraph(style='List Bullet'); runs(p, i); p.paragraph_format.space_after = Pt(2)
def shade(cell, hexc):
    tcPr = cell._tc.get_or_add_tcPr(); sh = OxmlElement('w:shd'); sh.set(qn('w:val'), 'clear'); sh.set(qn('w:color'), 'auto'); sh.set(qn('w:fill'), hexc); tcPr.append(sh)
def table(d, rows, widths=(2.4, 4.1), head=None):
    t = d.add_table(rows=0, cols=2); t.style = 'Table Grid'
    if head:
        c = t.add_row().cells
        for i, h in enumerate(head): c[i].text = ''; r = c[i].paragraphs[0].add_run(h); r.bold = True; r.font.color.rgb = RGBColor(255, 255, 255); shade(c[i], '4A3F5C')
    for a, b in rows:
        c = t.add_row().cells; c[0].text = ''; c[1].text = ''; runs(c[0].paragraphs[0], a, bold=True); runs(c[1].paragraphs[0], b); shade(c[0], 'F3F0F7')
    for row in t.rows:
        for i, w in enumerate(widths): row.cells[i].width = Inches(w)
    d.add_paragraph().paragraph_format.space_after = Pt(4)
OUT = 'out'; os.makedirs(OUT, exist_ok=True)
# ============ 1. CONTRACT
d = new('Wedding Photography Agreement', 'Template: fill every yellow [bracketed field], delete options you do not use, then have a lawyer review it.')
para(d, 'This Agreement is made on [DATE OF AGREEMENT] between [PHOTOGRAPHER / STUDIO LEGAL NAME], of [PHOTOGRAPHER ADDRESS] ("the Photographer"), and [CLIENT 1 FULL NAME] and [CLIENT 2 FULL NAME], of [CLIENT ADDRESS] ("the Clients").')
d.add_heading('Key terms at a glance', 1)
table(d, [('Wedding date', '[WEDDING DATE]'), ('Ceremony venue', '[CEREMONY VENUE AND ADDRESS]'), ('Reception venue', '[RECEPTION VENUE AND ADDRESS]'),
 ('Coverage', '[NUMBER] hours, from [START TIME] to [END TIME]'), ('Package', '[PACKAGE NAME]: [PACKAGE DESCRIPTION]'),
 ('Total fee', '[CURRENCY][TOTAL FEE]'), ('Retainer', '[CURRENCY][RETAINER AMOUNT], due on signing'),
 ('Delivery window', '[DELIVERY WINDOW, e.g. 8 weeks] after the wedding date, i.e. on or before [PROMISED DELIVERY DATE]'),
 ('Image count', 'Approximately [MINIMUM IMAGES] to [MAXIMUM IMAGES] edited images'),
 ('Online gallery access', '[GALLERY ACCESS MONTHS] months from the delivery date'),
 ('Editing style', '[EDITING STYLE NOTES, e.g. natural colour, light and airy, film-like]')], head=('Term', 'Detail'))
d.add_heading('Terms', 1)
clause(d, '1.', 'Services', 'The Photographer will provide wedding photography coverage as described in the Key terms above. Any additional coverage, locations or deliverables must be agreed in writing and may carry an extra fee.')
clause(d, '2.', 'Fees and payment', 'The total fee is shown above. The retainer is due on signing and reserves the date; the date is not reserved until the retainer and a signed copy of this Agreement are received. The balance is due [BALANCE DUE DATE, e.g. 14 days before the wedding]. Payments accepted by [ACCEPTED PAYMENT METHODS]. Late payments may be subject to [LATE FEE TERMS].')
clause(d, '3.', 'Delivery timeline', 'The Photographer will deliver the edited images to the Clients through a private online gallery within the delivery window shown above. The delivery window starts on the wedding date. The Photographer may share [NUMBER] preview images within [PREVIEW DAYS] days. If delivery will be delayed beyond the promised date because of illness, equipment or data problems, or events outside the Photographer\'s control, the Photographer will tell the Clients in writing as soon as reasonably possible, give a new expected date, and [DELAY REMEDY, e.g. offer a partial refund of X% / additional prints / extra preview images] if the new date is more than [DELAY GRACE DAYS] days after the promised date.')
clause(d, '4.', 'Image count', 'The number of delivered images depends on the events, light and the pace of the day. The Photographer expects to deliver the range shown above but does not guarantee an exact number. The Photographer chooses which images are delivered; unedited, duplicate, blurred or test frames are not included.')
clause(d, '5.', 'Editing style', 'The Clients have seen the Photographer\'s portfolio and agree to the Photographer\'s general editing style, described above. The Photographer will correct exposure, colour and cropping consistently. Requests for a different style, heavy retouching, body or face alteration or object removal beyond [INCLUDED RETOUCHING, e.g. blemishes and distracting items] may be declined or charged at [RETOUCHING RATE]. [RAW AND UNEDITED FILES: not provided / provided for an extra fee of AMOUNT].')
clause(d, '6.', 'Online gallery and backups', 'The online gallery will remain available for the gallery access period shown above, counted from the delivery date. The Clients are asked to download and back up all files within that period. After it ends the gallery and files may be deleted, and the Photographer may charge [GALLERY RESTORATION FEE] to restore them if still available. The Photographer keeps a backup of the files for [BACKUP RETENTION PERIOD] but does not guarantee storage after that.')
clause(d, '7.', 'Copyright and usage', 'The Photographer owns the copyright in all images. The Photographer grants the Clients a personal, non-exclusive licence to print, share and post the images for personal use, with credit where practical. Commercial use, resale, or entering images in competitions requires the Photographer\'s written permission. The Photographer may use the images in the portfolio, website, social media and promotion unless the Clients opt out here: [OPT OUT OF PORTFOLIO USE: yes / no].')
clause(d, '8.', 'Timeline and cooperation', 'The Clients will provide a shot list of family groups and a realistic schedule at least [TIMELINE DEADLINE, e.g. 14 days] before the wedding, and will nominate a person to gather family for group photographs. Time lost to delays is part of the coverage time. Additional coverage time is available at [EXTRA HOUR RATE] per hour, subject to availability.')
clause(d, '9.', 'Travel, meals and access', 'Travel is included within [INCLUDED TRAVEL DISTANCE]; beyond that, travel costs of [TRAVEL COST TERMS] apply. The Clients will provide a meal and a place to rest for the Photographer if coverage exceeds [MEAL HOURS] hours. The Clients are responsible for permissions needed to photograph at the venues.')
clause(d, '10.', 'Second photographer or assistant', '[SECOND PHOTOGRAPHER: included / not included / available for AMOUNT]. If included, the second photographer is chosen by the Photographer.')
clause(d, '11.', 'Cancellation and rescheduling', 'If the Clients cancel, the retainer is non-refundable [OR: refundable until DATE]. If the Clients cancel less than [CANCELLATION DAYS] days before the wedding, [CANCELLATION FEE TERMS]. If the Clients reschedule, the Photographer will move the booking to a new date if available; otherwise the cancellation terms apply. Different rules may apply by law where you live; check with a lawyer.')
clause(d, '12.', 'If the Photographer cannot attend', 'If illness, emergency or another cause prevents the Photographer from attending, the Photographer will make reasonable efforts to arrange a replacement of similar skill. If no replacement is found, the Photographer will refund all payments made. The Photographer\'s liability is limited to the fees paid, to the extent the law allows.')
clause(d, '13.', 'Equipment, data and force majeure', 'The Photographer uses professional equipment and backup practices. Neither party is liable for failure caused by events beyond reasonable control, such as severe weather, illness, travel disruption, venue restrictions, government orders or equipment or data loss despite reasonable precautions. In that case the Photographer will refund the portion of the fee for services not provided.')
clause(d, '14.', 'General', 'This Agreement is the entire agreement and can only be changed in writing signed by both parties. It is governed by the laws of [GOVERNING LAW, COUNTRY / STATE]. If part of it is unenforceable, the rest stays in force.')
d.add_heading('Signatures', 1)
table(d, [('Photographer', '[PHOTOGRAPHER NAME]    Signature: ______________________    Date: [DATE]'), ('Client 1', '[CLIENT 1 FULL NAME]    Signature: ______________________    Date: [DATE]'), ('Client 2', '[CLIENT 2 FULL NAME]    Signature: ______________________    Date: [DATE]')])
d.save(OUT + '/01-Wedding-Photography-Contract.docx')
# ============ 2. CLIENT GUIDE
d = new('Your Wedding Photography Guide', 'A client-facing guide: what happens before, on and after your wedding day.', disclaimer=False)
para(d, 'Hello [CLIENT NAMES]! Congratulations. This guide explains how we will work together so you always know what comes next. Everything here matches your agreement; if anything differs, the signed agreement applies.')
d.add_heading('1. Before the wedding', 1)
bullets(d, ['[DAYS BEFORE] days before: please return the questionnaire and your family group list.', '[DAYS BEFORE] days before: we confirm the day schedule, including sunset time and travel between venues.', 'Final payment is due on [BALANCE DUE DATE].'])
d.add_heading('2. On the day', 1)
bullets(d, ['I arrive at [ARRIVAL TIME] and will usually be with you from [START TIME] to [END TIME].', 'Family group photographs go fastest with one person who knows everyone. Please nominate [FAMILY HELPER ROLE].', 'Please tell guests the day is unplugged or let me know your preference: [UNPLUGGED CEREMONY PREFERENCE].', 'I will ask for a meal break if coverage is longer than [MEAL HOURS] hours.'])
d.add_heading('3. When will you get your photos?', 1)
para(d, 'Your agreement promises delivery within [DELIVERY WINDOW] of your wedding date, which is on or before [PROMISED DELIVERY DATE]. You will receive:')
bullets(d, ['[NUMBER] preview images within [PREVIEW DAYS] days (if included in your agreement).', 'Your full gallery of approximately [MINIMUM IMAGES] to [MAXIMUM IMAGES] edited images by the promised date.', 'A message from me if the date is at risk, as early as I know, with a new date and what I will do about it.'])
para(d, 'Editing is slow, careful work: culling thousands of frames, then colour and exposure correction on every delivered image. If you are worried, message me. I would rather you ask than wonder.')
d.add_heading('4. Your online gallery', 1)
bullets(d, ['Your gallery stays online for [GALLERY ACCESS MONTHS] months from the delivery date.', 'Please download everything and keep two backups (for example a hard drive and cloud storage) as soon as you receive it.', 'I will send you reminders at [REMINDER SCHEDULE, e.g. 60 and 14 days] before the gallery expires.'])
d.add_heading('5. About image count and style', 1)
para(d, 'I deliver the best images from each part of the day, not every frame I take. The number varies with how the day unfolds. My editing style is: [EDITING STYLE NOTES]. It is consistent across your gallery and matches the portfolio you chose me for. I do not provide RAW (unedited) files unless your agreement says so.')
d.add_heading('6. Using your photos', 1)
para(d, 'You can print, share and post your photos for personal use. For commercial use or competitions, please ask first. If you would like me to credit or tag someone, tell me and I will do the same where possible. Prints and albums: [PRINT AND ALBUM INFORMATION].')
d.add_heading('7. Questions', 1)
para(d, 'Reach me at [PHOTOGRAPHER EMAIL] or [PHOTOGRAPHER PHONE]. I reply within [REPLY TIME, e.g. 2 working days].')
d.save(OUT + '/02-Client-Guide.docx')
# ============ 3. QUESTIONNAIRE
d = new('Wedding Day Questionnaire', 'Please return this to [PHOTOGRAPHER EMAIL] by [QUESTIONNAIRE DEADLINE].', disclaimer=False)
d.add_heading('The couple', 1)
table(d, [('Names and pronouns', ''), ('Best phone and email', ''), ('Wedding date', ''), ('How did you meet (a line is fine)?', ''), ('Anything we should know about either of you that helps me photograph you naturally?', '')])
d.add_heading('Venues and timing', 1)
table(d, [('Getting-ready location(s) and address', ''), ('Ceremony start time and venue', ''), ('Expected ceremony length', ''), ('Reception venue and start time', ''), ('Is there a first look? Where and when?', ''), ('Travel time between venues (your estimate)', ''), ('Any photography restrictions (venue rules, officiant rules)?', '')])
d.add_heading('People', 1)
table(d, [('Planner or coordinator name and phone', ''), ('Person who will help gather family (name and phone)', ''), ('Family group photos you want (list; one group per line, e.g. couple with parents)', ''), ('Family dynamics I should know about (divorced parents, people who should not be photographed together)?', ''), ('Guests who need extra care (mobility, young children)?', ''), ('Other vendors (DJ, videographer, florist) and their contacts', '')])
d.add_heading('Style and priorities', 1)
table(d, [('Three moments you most want photographed', ''), ('Anything you do NOT want photographed', ''), ('Photos you have seen and loved (links) and what you liked about them', ''), ('Do you have a preference about social media posting before delivery?', ''), ('Do you want a sneak peek, and how soon?', '')])
d.add_heading('Delivery', 1)
table(d, [('Email for gallery delivery and updates', ''), ('Do you want prints or an album?', ''), ('Anything else?', '')])
d.save(OUT + '/03-Client-Questionnaire.docx')
# ============ 4. EMAILS
d = new('Delivery and Gallery Email Set', 'Copy, replace the yellow fields, and send from your own email.', disclaimer=False)
def mail(title, subject, body):
    d.add_heading(title, 1); para(d, 'Subject: ' + subject, bold=True)
    for b in body: para(d, b)
mail('1. Delivery on time', 'Your [COUPLE NAMES] wedding gallery is ready', ['Hi [CLIENT NAMES],', 'Your wedding gallery is ready! You can view it here: [GALLERY LINK]. It contains [IMAGE COUNT] edited images.', 'Please download all of your files and keep two backups. Your gallery stays online until [GALLERY EXPIRY DATE] ([GALLERY ACCESS MONTHS] months from today).', 'Thank you for trusting me with your day. It was a joy to photograph.', 'Warm wishes,', '[PHOTOGRAPHER NAME]'])
mail('2. Heads-up: delivery date at risk', 'An update on your wedding photos', ['Hi [CLIENT NAMES],', 'I want to be upfront with you. We agreed on [PROMISED DELIVERY DATE], and because of [REASON, e.g. my editing queue / illness] I now expect delivery by [NEW EXPECTED DATE].', 'I am sorry for the extra wait and I know how much you are looking forward to your photos. [DELAY REMEDY]. In the meantime I can send [NUMBER] more preview images if you would like.', 'If anything changes I will tell you straight away.', 'Warm wishes,', '[PHOTOGRAPHER NAME]'])
mail('3. Mid-way update (on track)', 'Your wedding photos: editing is on schedule', ['Hi [CLIENT NAMES],', 'A quick update: your photos are being edited and I expect to deliver on or before [PROMISED DELIVERY DATE]. I will message you the moment your gallery is ready.', 'Warm wishes,', '[PHOTOGRAPHER NAME]'])
mail('4. Late delivery apology (after the promised date has passed)', 'Your wedding photos are late and what I am doing about it', ['Hi [CLIENT NAMES],', 'Your gallery was promised for [PROMISED DELIVERY DATE] and I have missed it. That is on me, and I am sorry. Your gallery will be delivered by [NEW EXPECTED DATE]. As agreed in our contract, [DELAY REMEDY].', 'You can reach me directly at [PHOTOGRAPHER PHONE].', '[PHOTOGRAPHER NAME]'])
mail('5. Gallery expiry reminder (first)', 'Reminder: your wedding gallery expires on [GALLERY EXPIRY DATE]', ['Hi [CLIENT NAMES],', 'A friendly reminder that your online gallery will be removed on [GALLERY EXPIRY DATE], in [DAYS LEFT] days. Please download all your files before then: [GALLERY LINK].', 'If you need more time, reply to this email before the date and we can discuss an extension [EXTENSION TERMS, e.g. for a small fee].', 'Warm wishes,', '[PHOTOGRAPHER NAME]'])
mail('6. Gallery expiry reminder (final)', 'Final reminder: gallery expires in [DAYS LEFT] days', ['Hi [CLIENT NAMES],', 'Your gallery expires on [GALLERY EXPIRY DATE]. After that I cannot promise the files will still be available, and restoring them may cost [GALLERY RESTORATION FEE]. Please download everything today: [GALLERY LINK].', '[PHOTOGRAPHER NAME]'])
d.save(OUT + '/04-Delivery-and-Gallery-Emails.docx'); print('built')
