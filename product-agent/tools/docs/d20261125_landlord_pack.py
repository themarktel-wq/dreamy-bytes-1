# Small Landlord Notice + Addendum Pack (python-docx). Usage: python3 d20261125_landlord_pack.py outdir
import sys, os
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
FOOT = 'Template only, not legal advice. Landlord-tenant laws vary by state and city: check your local rules before use.'
ACC = RGBColor(0x1c, 0x5f, 0x8f)
def shade(cell, hexfill):
    tcPr = cell._tc.get_or_add_tcPr(); sh = OxmlElement('w:shd'); sh.set(qn('w:val'), 'clear'); sh.set(qn('w:color'), 'auto'); sh.set(qn('w:fill'), hexfill); tcPr.append(sh)
def new(title, sub):
    d = Document(); s = d.sections[0]; s.left_margin = s.right_margin = Inches(0.9); s.top_margin = s.bottom_margin = Inches(0.8)
    st = d.styles['Normal']; st.font.name = 'Calibri'; st.font.size = Pt(11)
    t = d.add_table(rows=1, cols=1); t.style = 'Table Grid'; c = t.rows[0].cells[0]; shade(c, 'FFF4C2')
    c.text = 'IMPORTANT: This is a template only, not legal advice. Landlord-tenant law varies by state, county and city (notice periods, fees, deadlines, required wording). Check your local rules or ask a qualified professional before using this document. Replace every [bracketed field].'
    for r in c.paragraphs[0].runs: r.font.size = Pt(9); r.bold = True
    d.add_paragraph()
    h = d.add_paragraph(); r = h.add_run(title); r.bold = True; r.font.size = Pt(21); r.font.color.rgb = ACC
    q = d.add_paragraph(); r = q.add_run(sub); r.italic = True; r.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
    fp = s.footer.paragraphs[0]; fp.text = FOOT; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in fp.runs: r.font.size = Pt(8); r.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
    return d
def H(d, t): p = d.add_paragraph(); r = p.add_run(t); r.bold = True; r.font.size = Pt(13); r.font.color.rgb = ACC
def P(d, t): d.add_paragraph(t)
def B(d, items):
    for i in items: d.add_paragraph(i, style='List Bullet')
def F(d, rows, w=(2.6, 4.1)):
    t = d.add_table(rows=0, cols=2); t.style = 'Table Grid'
    for a, b in rows:
        c = t.add_row().cells; c[0].text = a; c[1].text = b; c[0].width = Inches(w[0]); c[1].width = Inches(w[1]); shade(c[0], 'EEF3F8')
        for r in c[0].paragraphs[0].runs: r.bold = True
    d.add_paragraph()
def T(d, header, rows, widths=None):
    t = d.add_table(rows=1, cols=len(header)); t.style = 'Table Grid'
    for i, h in enumerate(header):
        t.rows[0].cells[i].text = h; shade(t.rows[0].cells[i], 'EEF3F8')
        for r in t.rows[0].cells[i].paragraphs[0].runs: r.bold = True
    for row in rows:
        c = t.add_row().cells
        for i, v in enumerate(row): c[i].text = v
    d.add_paragraph()
def SIGN(d, a='Landlord / manager', b='Tenant'):
    d.add_paragraph(); F(d, [(a + ' name', '[Name]'), (a + ' signature and date', '[Signature, DD/MM/YYYY]'), (b + ' name', '[Name]'), (b + ' signature and date', '[Signature, DD/MM/YYYY]')])
PARTIES = [('Landlord / manager name', '[Name]'), ('Tenant name(s)', '[Name(s)]'), ('Rental address', '[Address, unit]'), ('Date of this document', '[DD/MM/YYYY]')]
# 1 late rent
d = new('Late Rent Reminder and Notice', 'Two-step template: a friendly reminder first, then a formal notice if rent stays unpaid.')
H(d, 'Part A: Friendly reminder (send first)'); F(d, PARTIES)
P(d, 'Dear [Tenant name],'); P(d, 'Our records show that rent of [amount] for [month] was due on [due date] and has not been received. If you have already paid, thank you, and please send me the payment details so I can check. If you need to talk about the payment, please contact me by [date] at [phone / email].')
P(d, 'You can pay by [accepted payment methods and instructions]. Under your lease, [late fee wording from your lease, only if your lease and local law allow it] applies after [grace period from your lease].'); P(d, 'Sincerely,\n[Landlord name]  [phone / email]')
H(d, 'Part B: Formal notice (use only if rent is still unpaid)'); P(d, 'Many places require specific wording, a specific notice period and a specific delivery method. Fill the fields from your local rules; this template does not decide them for you.')
F(d, [('Notice type required locally', '[Name of the notice, e.g. as published by your court or housing authority]'), ('Amount of rent unpaid', '[Amount and periods]'), ('Late fees claimed (only if allowed)', '[Amount or none]'), ('Payment deadline stated by local rules', '[Date / number of days]'), ('How to pay', '[Methods]'), ('Delivery method used (as allowed locally)', '[Hand delivery / posting / mail, date, time]'), ('Required statements under local law', '[Paste the wording required where you operate]')])
P(d, 'Keep a copy of this notice, proof of how and when it was delivered, and a record of any payments and conversations.'); SIGN(d); d.save(OUT + '/01-Late-Rent-Reminder-and-Notice.docx')
# 2 maintenance addendum
d = new('Maintenance Request Procedure Addendum', 'Attach to the lease so everyone knows how repairs are requested and handled.')
F(d, PARTIES)
H(d, '1. How to request maintenance'); B(d, ['Requests must be sent by [method: email / app / form / text] to [contact]. Phone calls should be followed by a written request.', 'Each request should include: the unit, a description of the problem, when it started, photos if possible, and the best times to enter.'])
H(d, '2. Emergencies'); P(d, 'An emergency is [your definition, e.g. fire, flooding, no heat in cold weather, gas smell, no working lock]. For emergencies contact [emergency phone] immediately. For fire, gas or danger to life call [local emergency number] first.')
H(d, '3. Response times (targets, not guarantees)'); T(d, ['Priority', 'Examples', 'Target first response'], [['Emergency', '[Examples]', '[Time]'], ['Urgent', '[Examples]', '[Time]'], ['Routine', '[Examples]', '[Time]']])
H(d, '4. Entry to the unit'); P(d, 'Except in emergencies, the landlord will give notice before entering, as required by local law: [notice period and method required where you operate]. The tenant agrees to [allow access / be present / provide a key arrangement].')
H(d, '5. Who pays'); B(d, ['The landlord is responsible for [list] as required by law and the lease.', 'The tenant is responsible for [list, e.g. light bulbs, batteries, damage caused by tenant or guests].', 'Costs above [amount] require written approval before work starts, except in emergencies.'])
H(d, '6. Tenant duties'); B(d, ['Report problems promptly to prevent damage.', 'Do not attempt repairs on [electrical / gas / structural items].', 'Keep pets secured and the area clear when workers arrive.'])
H(d, '7. Records'); P(d, 'The landlord keeps a log of requests, dates, contractors and costs. Tenants may ask for the status of any request in writing.'); SIGN(d); d.save(OUT + '/02-Maintenance-Request-Procedure-Addendum.docx')
# 3 condition form
d = new('Move-In / Move-Out Condition Form', 'Complete together at move-in and again at move-out. Take dated photos and note the file names.')
F(d, PARTIES + [('Move-in date', '[Date]'), ('Move-out date', '[Date]'), ('Keys / remotes / fobs given', '[Number and type]')])
P(d, 'Condition codes: [e.g. G = good, F = fair, P = poor, D = damaged, N/A]. Describe scratches, stains, holes, missing items and anything not working.')
rooms = ['Entry / hallway', 'Living room', 'Kitchen', 'Dining area', 'Bedroom 1', 'Bedroom 2', 'Bathroom 1', 'Bathroom 2', 'Laundry / utility', 'Garage / storage', 'Outdoor / yard']
T(d, ['Room / item', 'Move-in condition', 'Move-in notes + photo file', 'Move-out condition', 'Move-out notes + photo file'], [[r + ' (walls, floor, ceiling, doors, windows, fixtures)', '[Code]', '[Notes, photo]', '[Code]', '[Notes, photo]'] for r in rooms])
T(d, ['Appliance / system', 'Working at move-in?', 'Working at move-out?', 'Notes'], [[a, '[Yes / no]', '[Yes / no]', '[Notes]'] for a in ['Stove / oven', 'Refrigerator', 'Dishwasher', 'Washer / dryer', 'Heating / cooling', 'Smoke / CO alarms', 'Water heater']])
P(d, 'Meter readings (if applicable): electric [reading], gas [reading], water [reading].'); P(d, 'The tenant confirms this form reflects the condition at move-in and will return any corrections in writing within [number] days.'); SIGN(d); d.save(OUT + '/03-Move-In-Move-Out-Condition-Form.docx')
# 4 move-out instructions
d = new('Move-Out Instructions Letter', 'Send when notice to leave is given or accepted.')
F(d, PARTIES + [('Move-out date', '[Date]'), ('Key return', '[Where, when, how]')])
P(d, 'Dear [Tenant name],'); P(d, 'Thank you for living at [address]. This letter explains what to do before you leave so that your move-out inspection and deposit statement go smoothly.')
H(d, 'Before you leave'); B(d, ['Remove all belongings and rubbish. Items left behind will be handled as allowed by your lease and local law: [wording].', 'Clean the unit: [list of expectations, e.g. kitchen appliances, bathrooms, floors, windows tracks].', 'Repair or tell us about any damage beyond normal wear and tear.', 'Return all keys, remotes and access cards by [date and time].', 'Give us your forwarding address in writing: [address / email to send it to].', 'Cancel or transfer utilities and internet effective [date].'])
H(d, 'Move-out inspection'); P(d, 'We will inspect the unit on [date and time]. You are welcome to attend. We will compare the unit with the move-in condition form and dated photos.')
H(d, 'Your security deposit'); P(d, 'Your deposit of [amount] will be handled as set out in your lease and local law. We will send an itemized statement and any refund within [deadline set by your local rules] after you return possession, to the forwarding address you give us.')
P(d, 'Contact: [name, phone, email].'); P(d, 'Sincerely,\n[Landlord name]'); d.save(OUT + '/04-Move-Out-Instructions-Letter.docx')
# 5 deposit itemization cover letter
d = new('Deposit Itemization Cover Letter', 'Goes with the itemized statement (see the MoveOut Ledger tool, or fill the table below).')
F(d, PARTIES + [('Move-out / possession returned date', '[Date]'), ('Deadline under local rules', '[Date; check your state or city]'), ('Letter sent on / by', '[Date, method]')])
P(d, 'Dear [Tenant name],'); P(d, 'This letter accompanies the itemized statement for the security deposit on [address]. You paid a deposit of [amount] on [date].')
T(d, ['Item / description', 'Condition (move-in vs move-out)', 'Cost', 'Receipt / invoice ref.', 'Photo ref.'], [['[Item]', '[Description]', '[Amount]', '[Ref]', '[File]'] for _ in range(6)])
F(d, [('Deposit held', '[Amount]'), ('Total deductions', '[Amount]'), ('Refund due to tenant', '[Amount]'), ('Amount owed by tenant (if any)', '[Amount]'), ('Refund sent by', '[Check / transfer, date]')])
P(d, 'Deductions are for [damage beyond normal wear and tear / unpaid rent / other items allowed by law and the lease: edit to match]. Receipts and photos are enclosed. If you disagree with any item please contact me at [phone / email] by [date] with your reasons.'); P(d, 'Sincerely,\n[Landlord name]  [address]'); d.save(OUT + '/05-Deposit-Itemization-Cover-Letter.docx')
# 6 rent increase
d = new('Rent Increase Notice', 'Check local rent-control, notice-period and delivery rules before sending.')
F(d, PARTIES + [('Current monthly rent', '[Amount]'), ('New monthly rent', '[Amount]'), ('Increase', '[Amount and %]'), ('Effective date', '[Date, after the notice period required locally]'), ('Lease type / term', '[Month-to-month / fixed term ends date]')])
P(d, 'Dear [Tenant name],'); P(d, 'This notice tells you that the monthly rent for [address] will change from [current rent] to [new rent] starting [effective date]. All other lease terms remain the same.')
P(d, '[Required local wording or statements, if any: for example required notices about rent limits, tenant rights, or registration numbers. Paste what your local authority requires.]')
P(d, 'If you have questions, contact me at [phone / email]. If you plan to move out instead, please tell me in writing as required by your lease: [notice requirement].'); P(d, 'Delivery record: delivered by [method] on [date, time] by [name].'); SIGN(d); d.save(OUT + '/06-Rent-Increase-Notice.docx')
# guide
d = new('Start Here: how to use this pack', 'Six fill-in documents for small landlords (1 to 5 units).')
H(d, 'What is inside'); B(d, ['01 Late Rent Reminder and Notice (friendly reminder, then a formal-notice template with fields for your local rules)', '02 Maintenance Request Procedure Addendum', '03 Move-In / Move-Out Condition Form', '04 Move-Out Instructions Letter', '05 Deposit Itemization Cover Letter', '06 Rent Increase Notice'])
H(d, 'How to use'); B(d, ['Open each file in Word or Google Docs and search for "[" to find every field.', 'Nothing here states your notice periods, fee limits, deposit deadlines or required wording, because they differ by state and city. Look them up for where you operate and type them into the fields.', 'Keep a copy of everything you send, proof of how and when you delivered it, dated photos and receipts.', 'If a tenant dispute is serious, talk to a local landlord association, housing authority or a lawyer.'])
P(d, 'This is a template only, not legal advice.'); d.save(OUT + '/00-Start-Here.docx')
print('landlord docs built')
