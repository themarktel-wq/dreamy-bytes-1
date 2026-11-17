CONTENT = {}

WA = {
"Greetings & First Reply": [
"Assalam o Alaikum [Name]! 👋 Welcome to [Brand]. How can we help you today?",
"Hi [Name]! Thanks for messaging [Brand] 😊 Are you looking for [Category A], [Category B] or something else?",
"Walaikum Assalam! Ji bilkul, hum aapki madad karte hain. Aap kis product ke baare mein poochna chahte hain?",
"Hello! Thanks for reaching out. Our team is available 10am–10pm. We'll reply within a few minutes.",
"Hi! We're closed right now but we've received your message. We'll reply first thing at 10am InshaAllah.",
"Welcome back [Name]! 💚 Great to hear from you again. What can we get for you this time?",
],
"Price & Product Questions": [
"[Product] is Rs [Price] with free delivery all over Pakistan 🚚 Available in [Variants]. Which one would you like?",
"Ji, [Product] ki price Rs [Price] hai. Delivery 2–4 din mein. Order confirm karne ke liye apna naam aur address bhej dein.",
"Here are the photos and details of [Product] 👇 [Photos]. Size: [ ], Material: [ ], Price: Rs [ ].",
"Great choice! [Product] is one of our best-sellers. [Short benefit]. Shall I book it for you?",
"Yes, we have it in stock ✅ Only [N] pieces left in [Colour].",
"Sorry, [Product] is out of stock right now 😔 We expect it on [Date]. Shall I reserve one for you, or would you like to see [Alternative]?",
"We have 3 options for you: Basic Rs [ ], Standard Rs [ ], Premium Rs [ ]. Most customers choose Standard because [reason].",
"Delivery charges: Free above Rs [X]. Below that, Rs [Y] all over Pakistan.",
],
"Objection Handling": [
"Price zyada hai? I understand! Our price includes [quality / warranty / free delivery]. Cheaper options often [issue]. We also offer COD so you pay only after receiving it.",
"I totally understand you want to think about it. Can I ask what's making you unsure — price, size or quality? I'll help you decide.",
"Many customers asked the same! Here's a real review from [Customer, City]: '[Review]'.",
"'Original hai?' — Yes, 100%. Here's a video of the actual product: [Video]. You can check it at delivery.",
"If size doesn't fit, you can exchange within [X] days. No tension 😊",
"We can't reduce the price, but I can add [Free gift / free delivery] for you today.",
"Our product is a bit higher than [Competitor] because [reason]. You'll notice the difference after one use.",
"No problem! I'll save your details. When you're ready just reply 'ORDER' and it'll be booked in 1 minute.",
],
"Order Taking & Confirmation": [
"To confirm your order please send: 1) Full name 2) Complete address with city 3) Phone number 4) Product & size/colour.",
"Thank you [Name]! Your order details: [Product] × [Qty], Total Rs [Amount] (COD). Address: [Address]. Reply YES to confirm ✅",
"Your order is confirmed 🎉 Order #[Number]. It will be dispatched within 24 hours.",
"Payment options: Cash on Delivery, JazzCash, Easypaisa or bank transfer. Advance payment gets [X]% off!",
"Our account details: [Bank/JazzCash details]. Please send a screenshot after payment ✅",
"Payment received, thank you! 💚 Your order is being packed.",
"Hi [Name], we haven't received your confirmation for order #[Number]. Please reply YES so we can dispatch it today.",
"Your order has been cancelled as requested. Hope to serve you again soon 🤍",
],
"Shipping & Delivery Updates": [
"Your parcel has been dispatched 🚚 Courier: [Name], Tracking: [Number]. Expected delivery: [Dates].",
"Your parcel is out for delivery today 📦 Please keep Rs [Amount] ready. Thank you!",
"Sorry for the delay, [Name] 🙏 Due to [Reason], your parcel will reach by [Date]. We've added [goodwill gesture].",
"The courier tried to deliver but couldn't reach you. Please share an alternate number or best time to deliver.",
"Delivered ✅ We hope you love your [Product]! Any issues, just message us.",
"Eid rush notice 🌙 Orders placed after [Date] may arrive after Eid. Order early to receive in time!",
],
"After-Sale & Reviews": [
"Hi [Name]! How are you liking your [Product]? 😊",
"Would you mind sharing a quick review or photo? It helps our small business a lot 💚",
"Thank you so much for the lovely review! Can we share it on our page (without your number)?",
"Here's how to use/care for your [Product]: [Tips].",
"As a thank you, here's [X]% off your next order: [Code] 🎁",
"Customers who bought [Product] also loved [Related Product]. Want to see it?",
],
"Complaints & Returns": [
"I'm really sorry about this, [Name] 🙏 Could you send a photo/video of the issue so we can fix it quickly?",
"Thank you for the photos. This shouldn't have happened. We'll [replace/refund] it — the courier will collect it on [Date].",
"Exchange process: 1) Send photo 2) We book return pickup 3) New item dispatched after we receive it.",
"We understand your frustration. Our manager [Name] will call you within 2 hours to resolve this.",
"Refund of Rs [Amount] has been sent to your [JazzCash/Bank]. Please confirm once received.",
"We've noted your feedback and we're improving [process]. Thank you for helping us get better.",
],
"Broadcasts & Follow-ups": [
"🔥 [Brand] SALE is LIVE! [X]% off everything till [Date]. Reply 'SALE' to see the catalogue.",
"New arrivals just landed ✨ Reply 'NEW' to get photos and prices.",
"Hi [Name], you asked about [Product] last week. It's back in stock — want me to book one?",
"Only for our WhatsApp family 💚 Use code [Code] for [X]% off this weekend.",
"Eid Mubarak from [Brand] 🌙 Thank you for being with us this year.",
"Reminder: our sale ends tonight at 12am ⏳",
"Hi [Name]! It's been a while 😊 Here's something new we think you'll love: [Product].",
"Want to stop receiving offers? Reply STOP and we'll remove you. No hard feelings!",
],
}

CONTENT["whatsapp-sales-scripts"] = """
# WhatsApp Business Setup
Most Pakistani customers prefer ordering on WhatsApp. A professional setup builds trust instantly.
## Setup checklist
[ ] Install WhatsApp Business (separate from personal WhatsApp)
[ ] Business name exactly as your brand
[ ] Logo as profile picture
[ ] Category, description, address/city, hours, website and email filled in
[ ] Catalogue with every product: photo, price, description, link
[ ] Greeting message on (for first-time chats)
[ ] Away message on (outside hours)
[ ] Labels: New Lead, Pending Payment, Confirmed, Dispatched, Delivered, Complaint
[ ] Quick replies saved for the scripts in this pack
[ ] Short link: wa.me/92XXXXXXXXXX for your bio and ads
## Quick-reply shortcuts (type / to use)
| Shortcut | Use |
| /hi | Greeting |
| /price | Price + delivery |
| /order | Order details request |
| /confirm | Order summary for confirmation |
| /pay | Payment details |
| /track | Dispatch + tracking |
| /review | Review request |
| /sorry | Complaint first response |
> Reply speed is your biggest sales weapon. Answering within 5 minutes can multiply conversion compared to replying hours later.
""" + "\n".join(f"# {cat}\n" + "\n".join(f"{i}. {s}" for i, s in enumerate(scripts, 1)) for cat, scripts in WA.items()) + """
# The WhatsApp Sales Process
| Step | Goal | Target time |
| 1. Greet | Make them feel welcome | Under 5 minutes |
| 2. Qualify | Understand need, size, budget | 1–2 questions |
| 3. Present | Photos, price, benefit, proof | One message |
| 4. Handle objection | Remove the doubt | Empathy + proof |
| 5. Close | Ask for order details | Direct question |
| 6. Confirm | Summary + YES | Same day |
| 7. Follow up | Delivery, review, repeat | After delivery |
## Broadcast rules
- Only message people who saved your number and opted in.
- Max 2–3 broadcasts per week, always with value (new stock, offer, tip).
- Make it easy to opt out. Spamming gets your number reported and banned.
"""

INTERVIEW = [
("Tell me about yourself.", "Use Present–Past–Future: 'I'm currently a [role] at [company] where I [key responsibility/achievement]. Before that, I [relevant past experience]. I'm now looking to [goal that matches this job], which is why this role excites me.' Keep it under 90 seconds."),
("Why do you want to work here?", "Show research: mention the company's product, values or growth, then connect it to your skills. 'I've followed [company]'s growth in [area]. Your focus on [value] matches how I work, and my experience in [skill] can help with [their goal].'"),
("What are your strengths?", "Pick 2–3 strengths relevant to the job, each with a short proof. 'I'm highly organised — in my last role I created a tracking sheet that reduced missed deadlines by 30%.'"),
("What is your biggest weakness?", "Choose a real but non-critical weakness and show improvement. 'I used to struggle with public speaking, so I joined a presentation workshop and now present weekly team updates.'"),
("Where do you see yourself in 5 years?", "Show ambition aligned with the company. 'I see myself having grown into a [senior/lead] role, having mastered [skill], and contributing to bigger projects here.'"),
("Why should we hire you?", "Summarise fit: skills + results + attitude. 'You need someone who can [requirement]. I've done that at [company], achieving [result], and I'm eager to bring that here.'"),
("Why are you leaving your current job?", "Stay positive. Focus on growth, not complaints. 'I've learned a lot, but I'm looking for more responsibility in [area], which this role offers.'"),
("What are your salary expectations?", "Research the market range first. 'Based on my research and experience, I'm looking for a range of Rs [X]–[Y]. I'm flexible depending on the overall package.'"),
("Tell me about a challenge you faced at work.", "Use STAR: Situation, Task, Action, Result. Choose a challenge where your action clearly made the difference and end with a measurable result."),
("Describe a time you worked in a team.", "STAR answer highlighting your specific contribution, how you communicated, and the team result."),
("Tell me about a conflict with a colleague.", "Show maturity: you listened, found common ground, focused on the goal, and the relationship improved."),
("Describe a time you failed.", "Own the mistake, explain what you learned and how you changed your process. Never blame others."),
("How do you handle pressure and deadlines?", "Give your method: prioritising, breaking work into steps, communicating early, plus an example."),
("How do you prioritise your work?", "Explain a system (urgent/important matrix, daily plan) with an example from work or studies."),
("What do you know about our company?", "Mention founding, products/services, recent news, competitors and culture. 2–3 specific facts are enough."),
("Do you have any questions for us?", "Always yes. Ask: 'What does success look like in the first 90 days?' 'What are the biggest challenges for the team?' 'How is performance reviewed?'"),
("What motivates you?", "Link to the job: solving problems, learning, helping customers, achieving targets — with a quick example."),
("How do you handle criticism?", "'I see feedback as a shortcut to improvement. For example, my manager once pointed out [X]; I [action] and [result].'"),
("Tell me about a time you showed leadership.", "Leadership isn't only titles — leading a project, mentoring a junior, organising an event. Use STAR."),
("Are you willing to relocate or travel?", "Answer honestly. If flexible, say so; if not, explain politely and show commitment otherwise."),
("Why is there a gap in your CV?", "Be honest and brief, then highlight what you did: courses, freelancing, family responsibilities, and readiness now."),
("What is your notice period?", "State it clearly. Show professionalism: 'My notice period is [X] weeks; I'd like to leave my current team in a good position.'"),
("How do you stay updated in your field?", "Mention courses, newsletters, communities, YouTube channels, or certifications relevant to the role."),
("Describe your ideal work environment.", "Describe one that matches the company: collaborative, clear goals, learning culture."),
("What makes you unique?", "Combine skills: 'I combine [technical skill] with [soft skill], which helps me [result].'"),
("How would your previous manager describe you?", "Use 3 adjectives and back one with a story or actual feedback."),
("Fresh graduate: why should we hire you without experience?", "Highlight projects, internships, FYP, leadership in societies, quick learning and enthusiasm, with proof."),
("Tell me about your final year project.", "Problem → your role → tools used → result → what you learned. Keep it simple for non-technical interviewers."),
("Banking: why banking?", "Interest in finance, customer service, stability and growth; mention the bank's products and your relevant skills."),
("Banking: how would you handle an angry customer?", "Listen, apologise for the experience, understand the issue, offer a solution within policy, follow up."),
("Sales: sell me this pen.", "Ask questions first: 'When do you use a pen? What matters to you?' Then sell the benefit that matches their answer, and close."),
("IT: explain a technical concept to a non-technical person.", "Pick a concept and use a daily-life analogy, e.g. 'An API is like a waiter who takes your order to the kitchen and brings back food.'"),
("IT: how do you debug a problem?", "Reproduce → isolate → check logs → form hypothesis → test → fix → write a test to prevent it."),
("Remote job: how do you stay productive working from home?", "Dedicated workspace, fixed hours, task tools (Trello/Notion), over-communication, and reliable internet + UPS backup."),
("Remote job: how do you handle time-zone differences?", "Share your overlap hours, async communication habits, and examples of meeting deadlines across time zones."),
("What would you do in your first 30 days?", "Learn: meet the team, understand processes and goals, get quick wins, and ask for feedback."),
("How do you handle multiple tasks at once?", "Prioritise by deadline and impact, communicate trade-offs, use a to-do system, and give an example."),
("Give an example of going beyond your job.", "STAR example where you took initiative and created value for the team or customer."),
("Why did you choose your degree?", "Genuine interest + how it connects to this role."),
("Is there anything else you'd like to add?", "Short closing pitch: 'I'm genuinely excited about this role. My experience in [X] and my [quality] make me confident I can contribute from day one.'"),
]

CONTENT["interview-prep-kit"] = """
# Before the Interview
## Research checklist
[ ] Company website: products, services, mission, recent news
[ ] LinkedIn: the interviewer's profile and the company's posts
[ ] The job description: highlight every skill and requirement
[ ] Glassdoor/Indeed/Rozee reviews for interview experience
[ ] Market salary range for the role and city
[ ] Prepare 5 stories using STAR (achievement, challenge, teamwork, failure, leadership)
## The STAR method
| Letter | Meaning | Share of answer |
| S | Situation — context | 15% |
| T | Task — your responsibility | 10% |
| A | Action — what YOU did | 60% |
| R | Result — measurable outcome | 15% |
> Spend most of your answer on Action. Interviewers want to know what you did, not what the team did.
## STAR worksheet
Write 5 stories in this format:
| Story | Situation | Task | Action | Result |
| 1. Achievement | | | | |
| 2. Challenge | | | | |
| 3. Teamwork | | | | |
| 4. Failure / lesson | | | | |
| 5. Leadership | | | | |
# 40 Questions with Model Answers
Adapt each answer to your own experience. Never memorise word for word — memorise the structure.
""" + "\n".join(f"## {i}. {q}\n{a}" for i, (q, a) in enumerate(INTERVIEW, 1)) + """
# Salary Negotiation
## Rules
1. Let them make the first offer when possible.
2. Give a researched range, with your target near the bottom of it.
3. Negotiate the whole package: salary, fuel, medical, bonus, leave, remote days, training.
4. Always be polite and enthusiastic about the role.
## Scripts
**When asked early:** "I'd love to learn more about the responsibilities first, but based on market research for similar roles, I'm looking at Rs [X]–[Y]."
**Countering an offer:** "Thank you, I'm excited about this offer. Based on my experience in [X] and the market range, I was hoping for Rs [Y]. Is there flexibility?"
**If salary is fixed:** "I understand. Could we discuss [fuel allowance / review after 6 months / remote days]?"
# Online Interview Setup
[ ] Stable internet + mobile data backup + UPS for load-shedding
[ ] Laptop camera at eye level, face well-lit from the front
[ ] Quiet room, plain background, phone on silent
[ ] Test Zoom/Teams/Meet link 15 minutes before
[ ] CV and notes open in a separate window
[ ] Professional username and profile photo on the platform
# Interview Day Checklist
[ ] Arrive 10–15 minutes early (or log in 5 minutes early)
[ ] Printed CV copies, CNIC, certificates file, pen
[ ] Formal, ironed clothes and clean shoes
[ ] Greet everyone politely — including reception
[ ] Firm handshake (if appropriate), eye contact, smile
[ ] Thank-you email within 24 hours
## Thank-you email
"Dear [Name], thank you for taking the time to meet with me today about the [Role] position. I enjoyed learning about [specific topic discussed]. I'm excited about the opportunity to contribute [skill/result]. Please let me know if you need any further information. Best regards, [Your name]"
"""

CONTENT["digital-product-creator-guide"] = """
# Why Digital Products?
Digital products are made once and sold unlimited times with no stock, no courier and no returns. For Pakistanis, they're one of the lowest-risk online businesses: start with a skill, a laptop and free tools.
## Types of digital products
| Type | Examples | Price range (PKR) |
| eBooks & guides | How-to guides, playbooks | 499–2,999 |
| Templates | CV, Canva, Notion, Excel | 299–1,999 |
| Prompt packs | ChatGPT prompts for a niche | 499–1,499 |
| Courses | Video lessons | 2,999–25,000 |
| Printables | Planners, worksheets | 299–999 |
| Presets & assets | Lightroom presets, fonts, icons | 499–2,499 |
| Memberships | Monthly community / content | 500–3,000/month |
# Validating Your Idea
Don't build first. Validate first.
## The 4-question test
1. **Do people already pay for this?** Look for similar products on Gumroad, Etsy, Daraz or Instagram.
2. **Is there a painful problem?** Search Facebook groups and comments for repeated questions.
3. **Can I reach buyers?** Do you have access to an audience, groups, or ad budget?
4. **Can I make it better or more local?** Urdu version, Pakistani examples, PKR pricing, local tools.
## Pre-sell method
Post about the product before it exists: "I'm creating a [product] to help [audience] [result]. Comment 'INTERESTED' for early-bird price." If 20+ people show real interest (or 5+ pre-pay), build it.
> Pre-selling is the ultimate validation. If no one pre-orders at a discount, change the offer before investing weeks of work.
# Creating the Product
## Workflow
1. Outline with AI: "Create a detailed outline for a [product] for [audience] that helps them [result]."
2. Add your experience, examples and local context in each section.
3. Design in Canva (eBook/workbook templates) or Google Docs.
4. Add worksheets, checklists, templates — practical tools sell better than pure reading.
5. Proofread, then ask 3 people to review before launch.
6. Export as PDF (or share templates with "Make a copy" links).
## Free tools
| Need | Tool |
| Writing & outlining | ChatGPT, Claude, Gemini, Google Docs |
| Design | Canva, Figma |
| Spreadsheets | Google Sheets |
| Video | CapCut, OBS, Loom |
| Mockups | Canva mockups, Smartmockups |
| Hosting files | Google Drive, Dropbox |
# Pricing for Pakistan
- **Entry product:** Rs 299–999 — impulse buy, builds trust.
- **Core product:** Rs 1,499–4,999 — your main offer.
- **Premium:** Rs 5,000+ — course, coaching or bundle.
- **Bundles:** sell multiple products at a big discount to raise order value.
- Show "original price" honestly only if you really sold at that price; otherwise show the value of what's included.
> Price on the value of the result, not the number of pages. A 20-page guide that helps someone earn their first Rs 50,000 is worth far more than Rs 500.
# Selling & Delivery
## Sales channels
- Instagram & Facebook (content + DMs)
- WhatsApp (catalogue + status + broadcast)
- Your own website (like Skillstack)
- Facebook groups (follow group rules)
- Marketplaces: Gumroad, Payhip, Etsy (international buyers)
## Payment & delivery in Pakistan
1. Customer pays via JazzCash / Easypaisa / bank transfer.
2. Customer sends a screenshot on WhatsApp.
3. You verify payment in your account.
4. You send a Google Drive "view-only" link or the file directly.
5. For automation: use a website with a payment gateway and automatic email delivery.
## Protect your product
- Add buyer license text in every file.
- Share Google Drive links as view-only where possible, or create a copy per buyer for templates.
- Don't panic about piracy — focus on serving your buyers well and updating your product.
# Launch Plan (14 Days)
| Day | Action |
| 1–3 | Teaser content: the problem and your story |
| 4–6 | Value posts on the topic, collect interested leads |
| 7 | Launch with early-bird price (48 hours) |
| 8–10 | Share buyer feedback, FAQs, behind the scenes |
| 11–13 | Run small ads to best posts |
| 14 | Close early-bird, keep evergreen sales running |
"""

CONTENT["canva-design-masterguide"] = """
# Design Principles Made Simple
Good design isn't about talent — it's about following a few rules consistently.
## 1. Hierarchy
The viewer should know what to read first, second and third. Make the most important text biggest and boldest. One headline, one supporting line, one CTA.
## 2. Spacing (white space)
Crowded designs look cheap. Leave margins of at least 5–8% of the canvas on every side. Group related items close together; separate unrelated items.
## 3. Alignment
Pick one alignment (left or centre) and stick to it. Use Canva's alignment guides. Random placement looks amateur.
## 4. Contrast
Light text on dark background or dark on light. Check readability on a phone at arm's length.
## 5. Consistency
Same fonts, colours and style across all posts. Consistency = brand recognition.
> The "squint test": squint at your design. If you can still see what's most important, the hierarchy works.
# Colours & Fonts
## Building a colour palette
- **1 primary colour** (brand colour)
- **1 accent colour** (CTAs, highlights)
- **2 neutrals** (dark for text, light for backgrounds)
- Use the 60-30-10 rule: 60% neutral, 30% primary, 10% accent.
## Palette ideas
| Mood | Colours |
| Premium | Navy #0A0F1F, Gold #F5B941, Off-white #F8FAFC |
| Fresh | Emerald #10B981, Mint #ECFDF5, Charcoal #1F2937 |
| Feminine | Blush #F9D5D3, Rose #C2185B, Cream #FFF8F0 |
| Bold | Black #111111, Yellow #FACC15, White #FFFFFF |
| Calm | Sage #9CAF88, Sand #E9DCC9, Brown #6B4F3A |
## Font pairing (available in Canva)
| Headline | Body | Feel |
| Montserrat Bold | Open Sans | Modern, clean |
| Playfair Display | Lato | Elegant, premium |
| Anton | Roboto | Bold, energetic |
| Poppins SemiBold | Poppins Regular | Friendly, simple |
| League Spartan | Inter | Startup, tech |
> Maximum 2 fonts per design. Use weight (bold/regular) and size for variety instead of more fonts.
# Canva Workflows
## Instagram post (1080×1080)
1. Create design → Instagram Post. Set background colour from your palette.
2. Add headline (60–90 pt), supporting text (28–36 pt), CTA (24–30 pt).
3. Add product photo; use "BG Remover" (Pro) or a clean photo.
4. Add your logo small in a corner, same position every time.
5. Check on phone preview, then download PNG.
## Carousel (1080×1350)
Slide 1: bold hook. Slides 2–6: one point per slide. Last slide: summary + CTA. Keep the same layout on every slide.
## YouTube thumbnail (1280×720)
Close-up face or subject, 3–4 words max, high contrast outline, bright accent colour.
## Ad creative (1080×1350 or 1080×1920)
Product hero, a benefit headline, price/offer badge, CTA button shape, logo. Keep text minimal.
## Brand kit
Add logo, colours and fonts to Canva Brand Kit (Pro) or create a "brand template" design to duplicate.
# Common Mistakes
- Too many fonts and colours
- Text on busy photo backgrounds without an overlay
- Low-resolution or stretched images
- Everything centred with no hierarchy
- Ignoring safe zones (Reels/Stories UI covers top and bottom)
- Copying another brand's design exactly
# Selling Design Services
| Service | Beginner (PKR) | Experienced (PKR) |
| 10 social posts | 3,000–6,000 | 10,000–25,000 |
| Logo (simple) | 3,000–8,000 | 15,000–50,000 |
| YouTube thumbnail | 500–1,500 | 3,000–8,000 |
| Monthly social media design | 15,000–30,000 | 40,000–100,000 |
On Fiverr/Upwork price in USD: start at $10–25 per small task and increase with reviews.
"""

CONTENT["student-study-planner"] = """
# How Learning Really Works
Most students re-read and highlight. Research shows these are among the least effective methods. The best methods feel harder but work much better.
## Science-backed techniques
| Technique | What to do |
| Active recall | Close the book and write/say everything you remember. Then check. |
| Spaced repetition | Revise after 1 day, 3 days, 7 days, 21 days. |
| Interleaving | Mix different types of questions instead of 50 of the same type. |
| Past papers | Practise under timed exam conditions. |
| Feynman technique | Explain the topic in simple words as if teaching a younger sibling. |
| Pomodoro | 25 minutes focus, 5 minutes break; long break after 4 rounds. |
> Your phone in another room can improve focus more than any app. Out of sight, out of mind.
# Planning Your Revision
## Step 1 — Syllabus audit
List every chapter for every subject and rate yourself: 🔴 weak, 🟡 okay, 🟢 strong. Weak chapters get more time.
## Step 2 — Exam countdown
Count the days to your first paper. Subtract 1 day per week for rest and buffer. That's your real study time.
## Step 3 — Weekly plan
Each week: new learning in the first half, active recall + past papers in the second half.
## Step 4 — Daily plan
Pick 3 key tasks per day. Finishing 3 important tasks beats a list of 15 you never complete.
---
# Printable: Syllabus Tracker
| Subject | Chapter | Status (R/A/G) | Revised 1 | Revised 2 | Past paper |
| | | | | | |
| | | | | | |
| | | | | | |
| | | | | | |
| | | | | | |
| | | | | | |
| | | | | | |
| | | | | | |
| | | | | | |
| | | | | | |
| | | | | | |
| | | | | | |
| | | | | | |
| | | | | | |
# Printable: Weekly Planner
Week of: ____________ Goal this week: ______________________
| Day | Morning | Afternoon | Evening | Done ✓ |
| Monday | | | | |
| Tuesday | | | | |
| Wednesday | | | | |
| Thursday | | | | |
| Friday | | | | |
| Saturday | | | | |
| Sunday | | | | |
## Reflection
- What went well this week?
- What will I improve next week?
- Which chapter needs extra attention?
# Printable: Daily Focus Page
Date: __________ Hours studied: ______
## Top 3 tasks
[ ] 1. ______________________________
[ ] 2. ______________________________
[ ] 3. ______________________________
## Pomodoro tracker
| Session | Subject / topic | Focus 1–5 |
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |
| 6 | | |
## Active recall notes
Write 5 things you learned today without looking:
1. ______________________________
2. ______________________________
3. ______________________________
4. ______________________________
5. ______________________________
# Printable: Exam Countdown
| Paper | Date | Days left | Chapters to revise | Past papers done |
| | | | | |
| | | | | |
| | | | | |
| | | | | |
| | | | | |
| | | | | |
| | | | | |
| | | | | |
# Beating Procrastination
- **2-minute start:** just open the book and do 2 minutes. Starting is the hardest part.
- **Study with a friend online** — cameras on, mics off.
- **Reward:** chai or a short walk after each Pomodoro block.
- **Remove friction:** keep books, pens and water ready the night before.
- **Sleep:** 7–8 hours. Memory is consolidated during sleep — all-nighters hurt marks.
## Exam-day checklist
[ ] Admit card, CNIC/B-form, stationery, calculator (if allowed)
[ ] Reach early; avoid last-minute discussions that cause panic
[ ] Read all questions first; attempt the ones you know best
[ ] Manage time per question; leave 10 minutes to review
"""

CONTENT["home-baking-business-kit"] = """
# Starting a Home Bakery
Home bakeries are one of Pakistan's fastest-growing home businesses — especially for custom cakes, brownies, cupcakes, cookies and dessert boxes. Success depends on three things: consistent taste, correct pricing and good photos.
## Start-up checklist
[ ] Perfect 3–5 signature recipes (bake each at least 5 times)
[ ] Basic equipment: oven, mixer, scale (digital), tins, piping tools, turntable
[ ] Packaging: cake boxes, boards, stickers, ribbon, brownie trays
[ ] Instagram page + WhatsApp Business
[ ] Price list based on real costing (Chapter 2)
[ ] Order form and advance-payment policy
[ ] Delivery method (self, rider service, or pickup)
[ ] Hygiene practices; check local food authority registration requirements
> Start with a small menu. 5 items you make perfectly beat 30 average items.
# Recipe Costing
## Step 1 — Ingredient cost per gram
Divide the price of the pack by its weight. Example: 1 kg flour at Rs 160 = Rs 0.16/g.
## Step 2 — Recipe cost
| Ingredient | Qty used | Price per unit | Cost (Rs) |
| Flour | 250 g | 0.16 /g | 40 |
| Sugar | 200 g | 0.18 /g | 36 |
| Eggs | 4 | 32 each | 128 |
| Butter | 150 g | 1.90 /g | 285 |
| Cocoa | 50 g | 2.40 /g | 120 |
| Cream & frosting | — | — | 300 |
| **Ingredients total** | | | **909** |
_Example prices only — update with your current market prices every month._
## Step 3 — Add other costs
- Packaging (box, board, sticker): Rs 150–300
- Gas & electricity: Rs 80–150 per bake
- Decorations & toppers
- Delivery (if free to customer)
# Pricing for Profit
**Price = (Ingredients + Packaging + Utilities) × 2.5 to 3**
Using the example: (909 + 220 + 100) × 2.5 ≈ Rs 3,070 for a 2-lb chocolate cake. Round to Rs 3,100–3,500 depending on your city and design.
## Custom design charges
| Design level | Extra charge |
| Simple (piping, sprinkles) | Included |
| Medium (drip, fresh flowers, topper) | + Rs 500–1,500 |
| Complex (fondant figures, tiers) | + Rs 2,000–10,000 |
> Never price by copying someone else. Their costs, quality and audience are different. Know your numbers.
# Taking Orders Professionally
## Order form (send on WhatsApp)
- Name & phone
- Date & time needed
- Item, flavour, size (lbs/pieces)
- Design reference photo
- Message on cake
- Pickup or delivery (address)
- Total price & advance paid
## Policies
- 50% advance to confirm custom orders; full advance for big orders.
- Orders accepted at least 48 hours in advance (custom: 3–5 days).
- Cancellation: advance non-refundable within 24 hours of delivery.
- Allergies must be informed at order time.
# Marketing Your Bakery
- **Photos:** natural daylight near a window, clean background, show the cut slice.
- **Reels:** decorating process, cutting the cake, packing boxes.
- **Occasions:** birthdays, anniversaries, Eid, Mother's Day, Valentine's, office events.
- **Local reach:** Facebook community groups of your area, nearby offices, schools.
- **Reviews:** ask every customer for a photo and short review.
- **Collaborations:** party planners, florists, photographers.
## Content calendar idea
| Day | Post |
| Mon | Menu / price list |
| Tue | Behind-the-scenes Reel |
| Wed | Customer review |
| Thu | Flavour spotlight |
| Fri | Weekend order reminder |
| Sat | Order delivered showcase |
| Sun | Poll: next flavour? |
# Growing the Business
- Introduce dessert boxes and gift hampers for higher order value.
- Corporate orders for offices (bulk brownies, cupcakes with logos).
- Workshops: teach baking classes once you're established.
- Track every order in a sheet: date, item, price, cost, profit, customer.
"""

CONTENT["real-estate-lead-kit"] = """
# Lead Generation for Property Consultants
Property buyers in Pakistan search on portals (Zameen, Graana, OLX), Facebook groups and YouTube before they ever call. The consultant who answers fastest, looks most professional and follows up longest wins the deal.
## The lead system
1. **Attract:** listings + content + ads
2. **Capture:** WhatsApp, lead forms, calls
3. **Qualify:** budget, location, timeline, purpose
4. **Nurture:** follow-ups, new options, market updates
5. **Close:** site visit → negotiation → token
6. **Refer:** happy clients bring new clients
# Listing Copy Templates
## Plot listing
"[Size] Marla Plot for Sale in [Block], [Society], [City] — Prime Location. ✅ [Corner/Park-facing/Main boulevard] ✅ Possession: [Status] ✅ Near [Landmarks] ✅ Price: Rs [Price] (Negotiable/Final). Documents clear. Call/WhatsApp [Name] — [Number] for site visit."
## House listing
"Brand New [Size] Marla House in [Area], [City]. 🛏 [N] Beds with attached baths 🍳 Modern kitchen ⚡ Solar / gas / water details 🚗 Parking for [N] cars. Ideal for families. Demand: Rs [Price]. Book a visit today: [Number]."
## Rental listing
"[Type] for Rent in [Area] — Rs [Rent]/month. [Beds], [Floor], [Features]. Suitable for [family/bachelors/office]. Advance: [X] months. Contact [Name]."
> Always use real photos of the actual property, verify documents with the owner, and never post fake prices to bait calls — it destroys trust and may break portal rules.
# Facebook Lead Ads Setup
1. Create a Lead (Instant Form) campaign in Ads Manager.
2. Target: the city + radius; age 28–60; let Advantage audience expand.
3. Creative: video walkthrough of the property or project, or a carousel of 5 photos.
4. Form questions: Name, phone, budget (multiple choice), timeline (multiple choice), preferred area.
5. Add a "Higher intent" review screen to reduce fake leads.
6. Connect leads to a Google Sheet (via Zapier/Make or download daily).
7. Call every lead within 15 minutes.
## Budget guide
| Goal | Daily budget | Expected cost per lead (rough) |
| Plots / files | Rs 1,500–3,000 | Rs 150–500 |
| Houses / apartments | Rs 2,000–5,000 | Rs 300–900 |
_Costs vary by city and season. Track your own data._
# Follow-Up Scripts
## First call
"Assalam o Alaikum [Name], this is [Your Name] from [Company]. You showed interest in [property/area]. Is this a good time for 2 minutes? Are you looking to buy for living or investment? What budget range are you considering? When are you planning to buy?"
## WhatsApp after call
"Thank you for your time, [Name]. As discussed, here are 3 options within Rs [budget] in [area]: 1) [ ] 2) [ ] 3) [ ]. When would you like to visit?"
## Follow-up sequence
| Day | Message |
| 1 | Options shared after call |
| 3 | "Did you get a chance to look at the options?" |
| 7 | New listing or market update |
| 14 | "Prices in [area] have [moved]. Still looking?" |
| 30 | Monthly check-in with best new deals |
> Most deals close after the 5th follow-up. Most agents stop after the 1st.
# Simple CRM Process
Use a Google Sheet or a free CRM (HubSpot free, Zoho Bigin) with these columns:
| Column | Example |
| Lead name & phone | Ali Khan, 0300… |
| Source | FB ad / Zameen / Referral |
| Budget | Rs 1.5–2 crore |
| Area & type | DHA, 10 Marla house |
| Purpose | Living / Investment |
| Timeline | 1–3 months |
| Status | New / Contacted / Visit / Negotiation / Closed / Lost |
| Next follow-up date | 20 Nov |
| Notes | Wants corner, near school |
# Building Authority
- Weekly YouTube/Reel: "Rates update in [Society]", "Plot vs house: which is better?"
- Area guides: schools, hospitals, mosques, markets near each society.
- Client testimonials after successful deals (with permission).
- Referral reward for past clients who send new buyers.
- Professional profile: logo, visiting card, Google Business Profile, WhatsApp catalogue.
"""
