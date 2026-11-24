import os, json
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = '/home/user/dreamy-bytes-1/product-agent/daily/2026-11-24/products/room-by-room-qc-inspection-pack'
ACC = RGBColor(0x1D, 0x4E, 0x89)
FOOT = 'Adapt to your local rules and your client agreements. Sample wording is a starting point, not legal or safety advice.'

def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr(); shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), hexcolor); tcPr.append(shd)

def set_widths(table, widths):
    table.autofit = False
    for i, w in enumerate(widths):
        table.columns[i].width = Inches(w)
    for row in table.rows:
        for i, w in enumerate(widths):
            row.cells[i].width = Inches(w)

def new_doc(title, subtitle=None, landscape=False):
    d = Document()
    s = d.sections[0]
    s.left_margin = s.right_margin = Inches(0.7); s.top_margin = Inches(0.6); s.bottom_margin = Inches(0.6)
    st = d.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(10)
    st.element.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')
    p = d.add_paragraph(); r = p.add_run(title); r.bold = True; r.font.size = Pt(20); r.font.color.rgb = ACC
    p.paragraph_format.space_after = Pt(2)
    if subtitle:
        q = d.add_paragraph(); r = q.add_run(subtitle); r.italic = True; r.font.size = Pt(10); r.font.color.rgb = RGBColor(0x6B, 0x72, 0x80)
    f = s.footer.paragraphs[0]; f.text = FOOT; f.runs[0].font.size = Pt(8); f.runs[0].font.color.rgb = RGBColor(0x6B, 0x72, 0x80)
    return d

def h(d, text, size=12):
    p = d.add_paragraph(); r = p.add_run(text); r.bold = True; r.font.size = Pt(size); r.font.color.rgb = ACC
    p.paragraph_format.space_before = Pt(8); p.paragraph_format.space_after = Pt(3); return p

def para(d, text, bold=False, italic=False, size=10):
    p = d.add_paragraph(); r = p.add_run(text); r.bold = bold; r.italic = italic; r.font.size = Pt(size); p.paragraph_format.space_after = Pt(3); return p

def fields(d, labels, cols=2):
    t = d.add_table(rows=0, cols=cols * 2); t.style = 'Table Grid'
    for i in range(0, len(labels), cols):
        row = t.add_row()
        for j in range(cols):
            if i + j < len(labels):
                row.cells[j * 2].text = labels[i + j]; shade(row.cells[j * 2], 'E8EEF6')
                for pp in row.cells[j * 2].paragraphs:
                    for rr in pp.runs: rr.bold = True; rr.font.size = Pt(9)
    set_widths(t, [1.25, 2.3] * cols); return t

def checklist(d, items, boxes=True):
    for it in items:
        p = d.add_paragraph(); p.add_run(('☐  ' if boxes else '- ') + it); p.paragraph_format.space_after = Pt(1)

def score_table(d, room, checks):
    t = d.add_table(rows=1, cols=4); t.style = 'Table Grid'; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t.rows[0].cells
    for c, txt in zip(hdr, [room, 'Score\n1 / 0 / NA', 'Notes / photo #', '']):
        c.text = txt; shade(c, '1D4E89')
        for pp in c.paragraphs:
            for rr in pp.runs: rr.bold = True; rr.font.color.rgb = RGBColor(255, 255, 255); rr.font.size = Pt(9)
    hdr[2].merge(hdr[3])
    for i, ch in enumerate(checks, 1):
        row = t.add_row().cells; row[0].text = '%d. %s' % (i, ch); row[1].text = ''; row[2].text = ''
        for pp in row[0].paragraphs:
            for rr in pp.runs: rr.font.size = Pt(9)
    sub = t.add_row().cells; sub[0].text = 'Room subtotal'; sub[1].text = ''; sub[2].text = 'Points earned ____  of possible ____'
    for c in sub: shade(c, 'F3F4F6')
    sub[2].merge(sub[3])
    for pp in sub[0].paragraphs:
        for rr in pp.runs: rr.bold = True; rr.font.size = Pt(9)
    set_widths(t, [3.6, 0.9, 1.5, 1.0]); d.add_paragraph().paragraph_format.space_after = Pt(2)
    return t

def totals_block(d):
    h(d, 'Result')
    t = d.add_table(rows=3, cols=4); t.style = 'Table Grid'
    vals = [('Total points earned (all 1s)', '', 'Pass mark (your standard)', '____ %'),
            ('Total points possible (all 1s and 0s, NA excluded)', '', 'Score % = earned / possible x 100', '____ %'),
            ('Result', '☐ Pass   ☐ Re-clean needed', 'Re-clean date / by whom', '')]
    for r, v in zip(t.rows, vals):
        for c, x in zip(r.cells, v): c.text = x
        shade(r.cells[0], 'E8EEF6'); shade(r.cells[2], 'E8EEF6')
    set_widths(t, [2.3, 1.5, 2.1, 1.1])
    h(d, 'Inspector sign-off')
    fields(d, ['Inspector name', 'Signature', 'Cleaner / crew lead acknowledged', 'Date'])

HEAD = ['Client name', 'Visit type', 'Address', 'Inspection date', 'Cleaner / crew', 'Inspector']
HOWTO = 'Scoring: write 1 if the check is done to your standard, 0 if not, NA if it does not apply. Score % = total of 1s / (number of 1s + number of 0s) x 100. NA items are left out. Set your own pass mark in the Result box.'

ROOMS = {
 'standard': ('Standard Clean Inspection Scorecard', 'Regular recurring visit: spot-check by a supervisor in about 10 minutes.', [
  ('Entry and hallways', ['Floors vacuumed or mopped, no crumbs in corners', 'Door glass and handles wiped', 'Mats shaken or straightened', 'Light switches and door frames spot-wiped', 'Visible cobwebs removed', 'Shoes / items left as found']),
  ('Kitchen', ['Counters cleared of crumbs and wiped dry', 'Sink and tap polished, no residue', 'Stovetop wiped, no splatter left', 'Microwave inside and outside wiped', 'Appliance fronts free of fingerprints', 'Cabinet fronts spot-wiped', 'Table / island wiped', 'Floor swept and mopped including edges', 'Bin emptied and re-lined', 'Dishes left as the client asked']),
  ('Living areas', ['Surfaces dusted (shelves, TV stand, tables)', 'Cushions straightened', 'Floors vacuumed incl. under movable furniture', 'Mirrors and glass tables streak-free', 'Baseboards spot-checked', 'Remote controls and clutter put back', 'Bins emptied', 'Vents / fan blades dusted if reachable']),
  ('Bedrooms', ['Beds made or changed as agreed', 'Surfaces and nightstands dusted', 'Floors vacuumed incl. under bed edges', 'Mirrors wiped', 'Bins emptied', 'Clothes / items not moved', 'Door handles and switches wiped', 'Lamps and shades dusted']),
  ('Bathrooms', ['Toilet cleaned inside, seat, base and behind', 'Sink and tap polished, no spots', 'Mirror streak-free', 'Shower / tub walls and floor cleaned', 'Shower door or curtain checked for residue', 'Floor mopped including behind toilet', 'Counter and cabinet fronts wiped', 'Towels hung straight / replaced as agreed', 'Bin emptied', 'No cleaning-product smell or residue left']),
  ('Laundry and utility', ['Surfaces and machine tops wiped', 'Lint trap emptied if in scope', 'Floor swept and mopped', 'Sink cleaned', 'Supplies put back neatly', 'Bin emptied']),
  ('Stairs and landings', ['Steps vacuumed edge to edge', 'Handrail wiped', 'Spindles / banister dusted', 'Landing floor cleaned', 'Wall marks spot-cleaned if in scope', 'No loose debris at the bottom']),
  ('Final walk-through', ['Lights and doors left as client prefers', 'Windows locked / blinds as found', 'Equipment and chemicals removed', 'Pets secure and fed areas untouched', 'Client notes from last visit actioned', 'No damage or breakage found (if found, note and photo)']),
 ]),
 'deep': ('Deep Clean Inspection Scorecard', 'First clean, seasonal or overdue clean: detail checks beyond the regular visit.', [
  ('Entry and hallways', ['Baseboards wiped by hand along the full length', 'Door frames and doors wiped top to bottom', 'Light fixtures and switch plates cleaned', 'Vents and returns wiped or vacuumed', 'Floors cleaned including edges and corners', 'Cobwebs removed from ceiling corners']),
  ('Kitchen', ['Inside of oven cleaned', 'Inside of fridge shelves and drawers cleaned', 'Inside of microwave cleaned, turntable washed', 'Range hood and filter wiped / degreased', 'Cabinet fronts and handles degreased', 'Backsplash cleaned', 'Small appliances wiped', 'Inside of sink and drain area scrubbed', 'Behind and under movable items cleaned', 'Floor scrubbed including grout lines']),
  ('Living areas', ['Furniture moved and cleaned under', 'Upholstery vacuumed incl. crevices', 'Baseboards and window sills wiped', 'Ceiling fans and light fixtures dusted', 'Picture frames and decor dusted', 'Blinds dusted or wiped', 'Window glass cleaned inside', 'Floors cleaned edge to edge']),
  ('Bedrooms', ['Under beds vacuumed', 'Headboards and furniture tops dusted', 'Closet floors and shelves cleaned', 'Baseboards and sills wiped', 'Fans and fixtures dusted', 'Blinds dusted or wiped', 'Window glass cleaned inside', 'Mattress surface vacuumed if agreed']),
  ('Bathrooms', ['Grout and tile scrubbed', 'Shower head and fixtures descaled', 'Inside of drawers / cabinets wiped', 'Exhaust fan cover cleaned', 'Toilet base, hinges and behind cleaned', 'Baseboards wiped', 'Tub / shower track cleaned', 'Mirror and glass free of spots', 'Floor scrubbed including corners', 'Soap scum removed from all surfaces']),
  ('Windows and sills', ['Interior glass streak-free', 'Window tracks vacuumed and wiped', 'Sills wiped', 'Screens dusted if in scope', 'Blinds / curtain rods dusted', 'Sliding door track cleaned']),
  ('Laundry and utility', ['Behind / on top of machines wiped', 'Inside washer door seal wiped', 'Shelves emptied and wiped if agreed', 'Floor scrubbed', 'Sink and tap cleaned', 'Vents cleaned']),
  ('Stairs and landings', ['Each step vacuumed incl. corners', 'Handrail and spindles wiped', 'Baseboards wiped', 'Wall marks spot-cleaned', 'Light fixtures dusted', 'Landing floor cleaned']),
  ('Walls, doors and fixtures', ['Scuffs on walls spot-removed where safe', 'Door handles disinfected', 'Switch plates cleaned', 'Vent covers wiped', 'Ceiling corners cobweb-free', 'Hard-to-reach dust removed']),
  ('Final walk-through', ['Before / after photos taken', 'Client list of priority areas checked', 'Items moved were returned', 'Equipment and chemicals removed', 'Lights, locks and blinds as found', 'Damage or concerns noted with photo']),
 ]),
 'moveout': ('Move-Out Inspection Scorecard', 'Empty-home clean for tenants, landlords and agents: check against your written scope.', [
  ('Kitchen', ['Inside of cabinets and drawers wiped', 'Inside and outside of oven cleaned', 'Inside of fridge and freezer cleaned, defrosted if agreed', 'Dishwasher inside, filter and seal cleaned', 'Range hood and filter degreased', 'Counters, backsplash and sink scrubbed', 'Floors scrubbed including corners', 'No food, labels or debris left']),
  ('Bathrooms', ['Toilet, tub and shower scrubbed', 'Grout and tile cleaned', 'Inside of vanity and medicine cabinet wiped', 'Mirrors and fixtures polished', 'Exhaust fan cover cleaned', 'Floor scrubbed incl. behind toilet', 'No hair, soap scum or limescale left']),
  ('Bedrooms', ['Closet shelves, rods and floors wiped', 'Baseboards and sills wiped', 'Doors and frames wiped', 'Windows and tracks cleaned', 'Floors vacuumed or mopped edge to edge', 'Fans and fixtures dusted', 'Walls checked for marks (note, do not paint)']),
  ('Living and dining', ['Baseboards wiped by hand', 'Windows, tracks and sills cleaned', 'Fireplace or built-ins wiped if in scope', 'Light fixtures and fans dusted', 'Floors fully cleaned', 'Doors, frames and handles wiped', 'Vents wiped']),
  ('Hallways and entry', ['Closet interiors cleaned', 'Floors cleaned', 'Baseboards wiped', 'Door glass and handles cleaned', 'Intercom / thermostat wiped', 'Light fixtures dusted']),
  ('Laundry and utility', ['Washer and dryer interior and exterior wiped', 'Lint cleared', 'Shelves and cabinets wiped', 'Floors scrubbed', 'Sink cleaned', 'No items left behind']),
  ('Windows and doors', ['All interior glass streak-free', 'Tracks vacuumed and wiped', 'Screens dusted', 'Patio / sliding door cleaned', 'Entry door both sides wiped', 'Window hardware wiped']),
  ('Garage / storage / balcony', ['Floor swept', 'Shelving wiped', 'Cobwebs removed', 'Balcony floor and rails wiped', 'No rubbish left', 'Door and handle wiped']),
  ('Walls, ceilings and fixtures', ['Cobwebs removed', 'Light covers cleaned', 'Switch plates and outlets wiped', 'Vent covers wiped', 'Marks spot-cleaned where safe', 'Smoke alarm covers dusted (do not test or remove)']),
  ('Condition notes and photos', ['Pre-existing damage photographed and listed', 'Meter / key / access items per client instructions', 'Before and after photo set complete', 'Rubbish removed if in scope', 'Lights and fixtures left working', 'Doors locked / keys handed per instructions']),
 ]),
}

def scorecard(key, fn):
    title, sub, rooms = ROOMS[key]
    d = new_doc(title, sub)
    fields(d, HEAD)
    para(d, HOWTO, italic=True, size=8.5)
    for room, checks in rooms:
        score_table(d, room, checks)
    totals_block(d)
    d.save(os.path.join(OUT, fn))
    return {'file': fn, 'rooms': len(rooms), 'checks': [len(c) for _, c in rooms]}

def start_here(fn):
    d = new_doc('Room-by-Room QC Inspection Pack: Start Here', 'How to score a visit, and a worked example. All names and numbers below are invented examples.')
    h(d, 'What is in this pack')
    for line in ['01 Standard Clean Scorecard (8 rooms)', '02 Deep Clean Scorecard (10 rooms)', '03 Move-Out Inspection Scorecard (10 rooms)', '04 Photo-Proof Sheet (before / after slots)', '05 Client Visit Summary slips (what we did today)', '06 Crew Onboarding SOP and training checklist', '07 Cleaner-Swap Handover Note', 'Every file comes as Word (.docx, editable) and PDF (print-ready).']:
        para(d, '- ' + line)
    h(d, 'How scoring works')
    para(d, 'Walk each room with the scorecard. For every check write 1 (done to your standard), 0 (not done) or NA (does not apply). Add up each room, then the total.')
    para(d, 'Score % = number of 1s / (number of 1s + number of 0s) x 100. NA items are not counted either way.', bold=True)
    para(d, 'Pick your own pass mark in the Result box. Many teams start with a high mark and adjust after a few weeks; the right number depends on your service promise.')
    h(d, 'Worked example (invented numbers)')
    t = d.add_table(rows=1, cols=5); t.style = 'Table Grid'
    for c, x in zip(t.rows[0].cells, ['Room', '1s', '0s', 'NA', 'Room %']):
        c.text = x; shade(c, 'E8EEF6')
    for r in [('Kitchen', 8, 2, 0), ('Bathrooms', 7, 1, 2), ('Bedrooms', 6, 0, 2)]:
        row = t.add_row().cells
        for c, x in zip(row, r + ('%.1f%%' % (100.0 * r[1] / (r[1] + r[2])),)): c.text = str(x)
    row = t.add_row().cells
    for c, x in zip(row, ['Total', 21, 3, 4, '%.1f%%' % (100.0 * 21 / 24)]): c.text = str(x); shade(c, 'F3F4F6')
    para(d, 'Total score = 21 / (21 + 3) x 100 = 87.5%. If your pass mark is 90%, this visit needs a re-clean of the three missed items.')
    h(d, 'Suggested routine')
    checklist(d, ['Supervisor inspects 1 in every few visits per crew (choose your own rhythm) and always after a client complaint.', 'Take photos of any 0 and attach the photo number in Notes.', 'Share the Client Visit Summary slip after the clean.', 'Review scores weekly with each crew; praise the 1s, fix the 0s.', 'Keep the completed scorecards for your records.'], boxes=True)
    h(d, 'Good to know')
    para(d, 'These are templates. Edit the checks to match what you actually promise clients. Adapt to your local rules and client agreements. Not legal, insurance or safety advice.')
    d.save(os.path.join(OUT, fn))

def photo_sheet(fn):
    d = new_doc('Photo-Proof Sheet', 'Paste or place before / after photos for each area. Keep the file name or photo number in the box.')
    fields(d, ['Client name', 'Address', 'Visit date', 'Cleaner / crew'])
    for area in ['Kitchen', 'Bathroom 1', 'Bathroom 2', 'Bedroom', 'Living area', 'Extra / issue found']:
        h(d, area, 11)
        t = d.add_table(rows=2, cols=2); t.style = 'Table Grid'
        t.rows[0].cells[0].text = 'BEFORE (photo # / time)'; t.rows[0].cells[1].text = 'AFTER (photo # / time)'
        for c in t.rows[0].cells:
            shade(c, 'E8EEF6')
            for pp in c.paragraphs:
                for rr in pp.runs: rr.bold = True; rr.font.size = Pt(8)
        tr = t.rows[1]; tr.height = Inches(1.35)
        set_widths(t, [3.5, 3.5])
    para(d, 'Notes (damage, items moved, client requests):'); para(d, '_' * 90); para(d, '_' * 90)
    d.save(os.path.join(OUT, fn))

def visit_slip(fn):
    d = new_doc('Client Visit Summary', 'What we did today. Print two per page, cut along the line, leave one with the client.')
    for k in range(2):
        t = d.add_table(rows=1, cols=1); t.style = 'Table Grid'; c = t.rows[0].cells[0]
        c.text = 'Your business name: ____________________    Visit date: ___ / ___ / ______    Cleaner(s): ____________________\nClient: ____________________    Time in: ______    Time out: ______'
        for pp in c.paragraphs:
            for rr in pp.runs: rr.font.size = Pt(9)
        d.add_paragraph().add_run('What we did today').bold = True
        checklist(d, ['Kitchen cleaned', 'Bathrooms cleaned', 'Bedrooms cleaned', 'Living areas cleaned', 'Floors vacuumed / mopped', 'Bins emptied', 'Extras: ________________________'])
        para(d, 'Needs your attention / items we could not do: ______________________________________________', size=9)
        para(d, 'Next visit: ___ / ___ / ______    Questions or changes: please reply to ____________________', size=9)
        para(d, 'Rate today’s clean:  ☐ 1   ☐ 2   ☐ 3   ☐ 4   ☐ 5     Cleaner signature: ________________', size=9)
        if k == 0:
            p = para(d, '- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -', size=9); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    d.save(os.path.join(OUT, fn))

def onboarding(fn):
    d = new_doc('Crew Onboarding SOP and Training Checklist', 'A fill-in standard operating procedure for new cleaners. Replace bracketed [fields] with your own rules.')
    fields(d, ['Company name', '[Your company]', 'Trainee name', 'Trainer name', 'Start date', 'Probation review date'])
    secs = [
     ('1. Before the shift', ['Check the job list: address, time, scope, access notes, pets, special requests.', 'Uniform, ID badge and closed-toe footwear as per [company rule].', 'Kit check: [list your standard kit]. Replace empty bottles; label every bottle.', 'Message the client or office if you will be late: at least [__] minutes before.']),
     ('2. Arrival and entry', ['Greet the client by name if home; introduce yourself.', 'Follow the access instructions exactly. Never share codes or keys; store them as [company rule].', 'Walk through with the client or read the notes; confirm extras and no-go areas.', 'Photograph any existing damage before starting; report it to the office.']),
     ('3. Cleaning order', ['Work top to bottom and back to front in every room.', 'Do dust before floors; wet areas last.', 'Use cloth colours for areas as per [your colour code] to avoid cross-contamination.', 'Follow product labels and safety data; never mix products; ventilate. Follow your local safety rules.']),
     ('4. Quality and proof', ['Use the Standard Clean Scorecard as your own end-of-job check.', 'Take the before / after photos listed on the Photo-Proof Sheet.', 'Fill in the Client Visit Summary slip.', 'Fix any missed item before leaving; do not rely on the supervisor to find it.']),
     ('5. Client communication', ['Be polite and calm; never argue about a complaint on site.', 'Write down what the client says and pass to the office the same day.', 'Do not accept cash or gifts unless [company rule].', 'Do not discuss other clients.']),
     ('6. End of visit', ['Take all equipment and rubbish as agreed.', 'Check lights, windows, locks, pets and alarm as per instructions.', 'Lock up; send the completion message to the office.', 'Report damage, safety issues or accidents immediately.']),
    ]
    for head, items in secs:
        h(d, head); checklist(d, items, boxes=False)
    h(d, 'Training sign-off')
    t = d.add_table(rows=1, cols=4); t.style = 'Table Grid'
    for c, x in zip(t.rows[0].cells, ['Skill / task', 'Shown by trainer (date, initials)', 'Done alone, trainer checked (date, initials)', 'Competent (trainer signature)']):
        c.text = x; shade(c, 'E8EEF6')
    for s in ['Kitchen standard clean', 'Bathroom standard clean', 'Bedroom and living areas', 'Floors (vacuum and mop)', 'Dusting and detail work', 'Deep-clean tasks (oven, fridge, windows)', 'Using the scorecard and taking photos', 'Client communication and handover slip', 'Safety: chemicals, lifting, slips', 'Locking up and reporting']:
        t.add_row().cells[0].text = s
    set_widths(t, [2.3, 1.7, 1.8, 1.4])
    para(d, ''); fields(d, ['Trainee signature', 'Date', 'Trainer signature', 'Date'])
    d.save(os.path.join(OUT, fn))

def handover(fn):
    d = new_doc('Cleaner-Swap Handover Note', 'Use whenever a client moves to a new cleaner, so quality does not drop and the client does not have to repeat themselves.')
    fields(d, ['Client name', 'Address', 'Outgoing cleaner', 'Incoming cleaner', 'Last visit by outgoing', 'First visit by incoming', 'Visit frequency', 'Supervisor'])
    h(d, 'Access and logistics (do not write codes here; use your secure system)')
    checklist(d, ['Entry method: ☐ client home  ☐ key  ☐ code  ☐ lockbox     Where recorded: [secure location]', 'Parking / building rules: ______________________________', 'Alarm / pets / gate notes: ______________________________'])
    h(d, 'What this client likes')
    for q in ['Top 3 priorities for them:', 'Things they praised:', 'Preferred products or no-go products:', 'Rooms or items that are off limits:']:
        para(d, q + ' ' + '_' * 60)
    h(d, 'Trouble spots and history')
    for q in ['Areas that need extra attention each visit:', 'Past complaints and how they were solved:', 'Fragile or valuable items to take care with:']:
        para(d, q + ' ' + '_' * 60)
    h(d, 'Handover steps')
    checklist(d, ['Outgoing cleaner shares this note with incoming cleaner and supervisor.', 'Client told in advance about the change by [message / call].', 'Incoming cleaner reads the last 3 scorecards for this client.', 'Supervisor inspects the first visit with the new cleaner.', 'Check-in message sent to client after first visit.', 'Client feedback recorded: ________________________'])
    h(d, 'Sample message to the client (edit before sending)')
    para(d, 'Hi [client name], this is [business]. From [date], [new cleaner] will be taking over your cleans. [He/She/They] has been briefed on your preferences. We will check in after the first visit to make sure everything is right. Please tell us anything you would like done differently.', italic=True)
    d.save(os.path.join(OUT, fn))

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    meta = []
    start_here('00-Start-Here-How-to-Score.docx')
    meta.append(scorecard('standard', '01-Standard-Clean-Scorecard.docx'))
    meta.append(scorecard('deep', '02-Deep-Clean-Scorecard.docx'))
    meta.append(scorecard('moveout', '03-Move-Out-Inspection-Scorecard.docx'))
    photo_sheet('04-Photo-Proof-Sheet.docx'); visit_slip('05-Client-Visit-Summary-Slips.docx'); onboarding('06-Crew-Onboarding-SOP.docx'); handover('07-Cleaner-Swap-Handover-Note.docx')
    json.dump(meta, open('/tmp/qc_meta.json', 'w'))
    print(json.dumps(meta))
