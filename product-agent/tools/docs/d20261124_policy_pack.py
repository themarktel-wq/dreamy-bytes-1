# Builds the Groomer & Sitter Policy and Intake Pack (python-docx). Usage: python3 d20261124_policy_pack.py outdir
import sys, os
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
FOOT = 'Template only, not legal advice; check local rules. Fill every [bracketed field] before use.'
ACC = RGBColor(0x2a, 0x7f, 0x62)
def new(title, sub):
    d = Document(); s = d.sections[0]; s.left_margin = s.right_margin = Inches(0.9); s.top_margin = s.bottom_margin = Inches(0.8)
    st = d.styles['Normal']; st.font.name = 'Calibri'; st.font.size = Pt(11)
    p = d.add_paragraph(); r = p.add_run('[Your Business Name]'); r.bold = True; r.font.size = Pt(11); r.font.color.rgb = ACC
    h = d.add_paragraph(); r = h.add_run(title); r.bold = True; r.font.size = Pt(22)
    q = d.add_paragraph(); r = q.add_run(sub); r.italic = True; r.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
    fp = s.footer.paragraphs[0]; fp.text = FOOT; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in fp.runs: r.font.size = Pt(8); r.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
    return d
def H(d, t): p = d.add_paragraph(); r = p.add_run(t); r.bold = True; r.font.size = Pt(13); r.font.color.rgb = ACC
def P(d, t): d.add_paragraph(t)
def B(d, items):
    for i in items: d.add_paragraph(i, style='List Bullet')
def FIELDS(d, rows):
    t = d.add_table(rows=0, cols=2); t.style = 'Table Grid'
    for a, b in rows:
        c = t.add_row().cells; c[0].text = a; c[1].text = b; c[0].width = Inches(2.4); c[1].width = Inches(4.3)
        for r in c[0].paragraphs[0].runs: r.bold = True
    d.add_paragraph()
def SIGN(d, who):
    d.add_paragraph()
    FIELDS(d, [(who + ' name', '[Name]'), (who + ' signature', '[Signature]'), ('Date', '[DD/MM/YYYY]'), ('Provider signature', '[Signature]'), ('Provider name and date', '[Name, date]')])
# 1 intake
d = new('Client and Pet Intake Form', 'Complete one form per pet. Keep a copy in the client file.')
H(d, '1. Owner details'); FIELDS(d, [('Owner full name', '[Name]'), ('Phone (mobile)', '[Number]'), ('Email', '[Email]'), ('Address', '[Address]'), ('Emergency contact (name, phone)', '[Name, phone]'), ('Preferred contact method', '[Text / call / email]')])
H(d, '2. Pet details'); FIELDS(d, [('Pet name', '[Name]'), ('Species / breed', '[Dog / cat / other, breed]'), ('Age / birth date', '[Age or date]'), ('Sex / spayed or neutered', '[Sex, yes/no]'), ('Weight (approx.)', '[Weight]'), ('Coat type and colour', '[Description]'), ('Microchip number (if any)', '[Number]')])
H(d, '3. Veterinarian and health'); FIELDS(d, [('Vet clinic name and phone', '[Clinic, phone]'), ('Vaccinations up to date (rabies, other as required where you live)', '[Yes / no, dates]'), ('Proof of vaccination provided', '[Yes / no, date seen]'), ('Allergies', '[List or none]'), ('Medical conditions / medication', '[List or none]'), ('Skin, ear or joint sensitivities', '[List or none]'), ('Fleas or ticks in the last 30 days', '[Yes / no]')])
H(d, '4. Behaviour disclosure'); P(d, 'Please tell us honestly so we can keep your pet and our team safe. Tick or write below.')
FIELDS(d, [('Has bitten or snapped at a person or animal', '[Yes / no, details]'), ('Afraid of: clippers, dryers, thunder, other dogs, strangers', '[List or none]'), ('Reactive on leash / with other dogs', '[Yes / no, details]'), ('Known triggers', '[Details]'), ('Needs a muzzle or frequent breaks', '[Yes / no]'), ('Previous grooming or sitting experience', '[Details]')])
H(d, '5. Service and care instructions'); FIELDS(d, [('Services requested', '[Services]'), ('Style / clip length / special instructions', '[Details]'), ('Food, treat and feeding rules', '[Details]'), ('Walking routine / house rules (sitting)', '[Details]'), ('Home access details (sitting only)', '[Key, alarm, parking: share securely]')])
H(d, '6. Acknowledgement'); P(d, 'I confirm the information above is accurate to the best of my knowledge and I will tell [Your Business Name] about any change before the next visit.')
SIGN(d, 'Owner'); d.save(OUT + '/01-Client-and-Pet-Intake-Form.docx')
# 2 grooming policy
d = new('Grooming Policy', 'Booking, deposit, matting, vaccinations and pick-up rules. Replace every bracketed value with your own.')
H(d, '1. Booking and deposit'); B(d, ['A deposit of [amount per pet] is required to hold an appointment. The deposit is [credited toward the final price / non-refundable if the appointment is missed or cancelled late].', 'Prices quoted are starting prices. The final price depends on coat condition, size, behaviour and time taken, and we will tell you before we go above the quote by more than [percentage or amount].'])
H(d, '2. Cancellations, late arrivals and no-shows'); B(d, ['Please give at least [number] hours notice to cancel or reschedule.', 'Cancellations with less than [number] hours notice, or a no-call/no-show, may be charged [fee amount or % of the service] and a deposit may be required for future bookings.', 'If you are more than [number] minutes late we may shorten the service, reschedule, or charge a late fee of [amount].', 'We confirm appointments by [text / email] about [48 / 24] hours before; please reply to confirm. Unconfirmed appointments may be released to the waitlist [number] hours before the start time.'])
H(d, '3. Matting and coat condition'); B(d, ['Matting is painful. Brushing and de-matting takes extra time and can irritate the skin. We charge a de-matting fee of [amount or hourly rate] depending on severity: [light / moderate / severe levels and prices].', 'If matting is too tight to brush out safely, we may shave the coat for the pet\'s comfort. By signing you consent to this in that case. Shaving may reveal skin conditions that were hidden.', 'We may decline to continue if a pet is in distress.'])
H(d, '4. Vaccinations and health'); B(d, ['Pets must be up to date on [vaccinations required where you operate]. Please provide proof at or before the first visit.', 'Tell us about fleas, ticks, skin conditions, injuries, pregnancy, or contagious illness before your appointment. Extra flea or tick treatment is charged at [amount].', 'We may refuse service to a pet that appears unwell.'])
H(d, '5. Behaviour and safety'); B(d, ['You have disclosed all known behaviour concerns on the intake form. We may use a muzzle, restraint or extra handler for safety and may charge a handling fee of [amount].', 'We may end a service early for safety; the time already used is charged at [rate].'])
H(d, '6. Pick-up and payment'); B(d, ['Please collect your pet within [number] minutes of the pick-up call. After that a boarding/waiting fee of [amount] per [period] applies.', 'Payment is due at pick-up by [accepted methods].'])
H(d, '7. Photos and incidents'); P(d, 'Photos may be taken for records and, only if you sign the Photo Release, for marketing. Any injury or illness during care will be reported to you promptly and recorded on an incident note. Our responsibility is limited as permitted by the laws where we operate: [local limits to be confirmed by you].')
P(d, 'By signing I agree to this policy for all current and future appointments unless it is updated and re-issued to me.'); SIGN(d, 'Owner'); d.save(OUT + '/02-Grooming-Policy.docx')
# 3 sitter agreement
d = new('Dog Walking and Pet Sitting Service Agreement', 'Skeleton agreement between a walker or sitter and a pet owner. Complete the brackets and have your own adviser review it for your area.')
H(d, '1. Parties and pets'); FIELDS(d, [('Provider', '[Your name / business]'), ('Client', '[Client name]'), ('Pet(s) covered', '[Names]'), ('Start date and service type', '[Walks / drop-in / overnight, dates]')])
H(d, '2. Services and schedule'); B(d, ['Services: [walk length, number of visits, feeding, medication, overnight stays].', 'Visit window: [times]. The provider may arrive up to [number] minutes either side of the window due to traffic or earlier visits.', 'Extra services (extra pet, puppy, holiday, last-minute booking): [prices].'])
H(d, '3. Fees and payment'); B(d, ['Rates: [rate card or package, e.g. per visit or prepaid package of [number] visits].', 'Prepaid packages are valid for [number] months and are [non-refundable / refunded pro-rata]. Payment is due [when].', 'Cancellations with less than [number] hours notice are charged [percentage or amount].'])
H(d, '4. Access, keys and home'); B(d, ['The client provides safe access to the home and pet supplies. Keys and codes are kept [how] and returned [when].', 'The client tells the provider about alarms, hazards and other people in the home.'])
H(d, '5. Health, emergencies and vet care'); B(d, ['Vaccination status and health conditions have been disclosed on the intake form.', 'In an emergency the provider will try to reach the client and the emergency contact, and may take the pet to [vet clinic] or the nearest emergency vet. The client agrees to pay reasonable vet costs, up to [limit] without prior approval.'])
H(d, '6. Behaviour and safety'); B(d, ['Pets are walked on leash unless the client approves otherwise in writing. The provider may refuse or end a visit that is unsafe.', 'The client is responsible for damage or injury caused by a pet that was not accurately described.'])
H(d, '7. Liability and insurance'); P(d, '[State your insurance or bonding, if any, and your limit of liability as allowed where you operate. This is a skeleton clause: have it checked for your location.]')
H(d, '8. Ending the agreement'); P(d, 'Either party may end this agreement with [number] days written notice, or immediately for safety reasons. Unused prepaid visits are [handled as stated in section 3].')
SIGN(d, 'Client'); d.save(OUT + '/03-Dog-Walking-and-Pet-Sitting-Agreement.docx')
# 4 photo release
d = new('Photo and Video Release', 'Optional: lets you share photos of the pet (and, if you choose, the owner) in your marketing.')
P(d, 'I give [Your Business Name] permission to take photos and short videos of my pet [Pet name] during grooming, walking or sitting.')
H(d, 'Please tick one'); B(d, ['[ ] Records only: photos may be kept in my pet\'s client file and sent to me.', '[ ] Marketing: photos may also be used on [website, Instagram, Facebook, printed material].', '[ ] Marketing, no names: as above but my name and my pet\'s name will not be shown.', '[ ] No photos.'])
P(d, 'I understand I can withdraw this permission by telling [Your Business Name] in writing; photos already published may take [number] days to remove. No payment is due for photo use. Images will not show my home address or door numbers.'); SIGN(d, 'Owner'); d.save(OUT + '/04-Photo-and-Video-Release.docx')
# 5 incident note
d = new('Incident Note', 'Write it down the same day. Share a copy with the owner and keep one in the file.')
FIELDS(d, [('Date and time of incident', '[Date, time]'), ('Pet name / owner', '[Names]'), ('Service at the time', '[Grooming / walk / sitting]'), ('Location', '[Where]'), ('Staff member present', '[Name]')])
H(d, 'What happened (facts only)'); P(d, '[Describe what you saw, in order. No guesses or blame.]')
H(d, 'Injury, illness or damage'); P(d, '[Describe, with photos if taken: where, how serious, what first aid was given.]')
H(d, 'Actions taken'); FIELDS(d, [('Owner contacted (time, how)', '[Details]'), ('Vet contacted / visited (clinic, time)', '[Details]'), ('Other people or animals involved', '[Details]'), ('Follow-up needed and by whom', '[Details]')])
H(d, 'Sign-off'); SIGN(d, 'Owner'); d.save(OUT + '/05-Incident-Note.docx')
# guide
d = new('Start Here: how to use this pack', 'Five fill-in documents for groomers, dog walkers and pet sitters.')
H(d, 'What is inside'); B(d, ['01 Client and Pet Intake Form: contact, vet, vaccination, health and behaviour disclosure.', '02 Grooming Policy: deposit, cancellation / no-show, late arrival, matting consent, vaccination rules, pick-up.', '03 Dog Walking and Pet Sitting Agreement: skeleton service agreement.', '04 Photo and Video Release (optional).', '05 Incident Note.'])
H(d, 'How to use'); B(d, ['Open each file in Word or Google Docs (File > Open > Upload). Search for "[" to find every field.', 'Replace every [bracketed field] with your own business name, amounts and rules; delete clauses that do not apply to you. Nothing is pre-set: your prices, deposit and fees are yours to choose.', 'Have clients sign (paper or e-signature) before their first visit and keep the intake form up to date.', 'Ask a local professional to review the agreement and liability wording before you rely on it.'])
H(d, 'Where the structure comes from'); P(d, 'The clauses follow patterns visible on public groomer policy pages: a deposit per pet, late-cancel and no-call/no-show fees, matting surcharges by severity, and "prices are starting rates". The wording is original to this pack.')
P(d, 'Important: this is a template only, not legal advice. Laws on contracts, liability, vaccination and data protection differ by country and state.'); d.save(OUT + '/00-Start-Here.docx')
print('docs built')
