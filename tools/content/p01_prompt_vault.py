"""AI Prompt Vault — 250+ prompts in 12 categories."""

FORMULA = """
# The Prompt Formula
Most people type one line into ChatGPT and get a generic answer. Professionals give the AI the same brief they would give a human expert. Use the **R-C-T-F-E** formula:
| Letter | Meaning | Example |
| R | Role — who should the AI act as? | "Act as a senior Facebook ads strategist for Pakistani e-commerce brands." |
| C | Context — what is the situation? | "I sell women's lawn suits online, price Rs 3,500–6,000, COD across Pakistan." |
| T | Task — what exactly do you want? | "Write 5 ad primary texts for our Eid collection." |
| F | Format — how should it look? | "Each under 80 words, with 1 emoji, and a CTA to order on WhatsApp." |
| E | Examples / limits — what to avoid? | "Avoid the words 'best quality'. Tone: elegant, not pushy." |
> Every prompt in this vault has [BRACKETS]. Replace them with your details — the more specific you are, the better the result.
## 5 rules for better AI output
1. **Ask for options.** "Give me 10 versions" beats "write one".
2. **Iterate.** Reply with "make version 3 shorter and more emotional".
3. **Give samples.** Paste a caption you like and say "match this style".
4. **Ask it to ask you.** End with "Ask me 5 questions before you start."
5. **Verify facts.** AI can be confidently wrong — check numbers, laws and prices.
## Getting Urdu / Roman Urdu output
- Add: "Write in simple Roman Urdu, the way young Pakistanis text on WhatsApp."
- For Urdu script: "Write in Urdu (Nastaliq script), formal tone, short sentences."
- Mixed: "Write in English but add 1–2 natural Roman Urdu phrases per post."
"""

CATS = {
"Marketing & Advertising": [
"Act as a direct-response copywriter. Write 10 Facebook ad headlines for [PRODUCT] aimed at [AUDIENCE] in Pakistan. Mix curiosity, benefit and urgency angles.",
"Write 5 primary texts for a Meta ad selling [PRODUCT] at Rs [PRICE]. Use the Problem-Agitate-Solution structure. Under 90 words each, CTA to order on WhatsApp.",
"List 20 pain points and 20 desires of [AUDIENCE] related to [PRODUCT/SERVICE]. Group them by emotional vs practical.",
"Create a 3-angle ad testing plan for [PRODUCT]: one emotional, one logical, one social-proof angle. Give a hook, body and CTA for each.",
"Write a 30-second UGC-style video script for [PRODUCT] — a customer talking to camera. Include the first 3-second hook, problem, demo and CTA.",
"Generate 15 scroll-stopping hooks for Reels about [TOPIC]. Each under 10 words.",
"Write a limited-time offer announcement for [OFFER] ending on [DATE]. Create urgency without sounding fake.",
"Rewrite this ad copy to be clearer and more persuasive, keeping it under 70 words: [PASTE COPY]",
"Suggest 10 creative concepts for an Eid campaign for [BRAND] that sells [PRODUCT]. Include visual idea and caption.",
"Create a customer avatar for [BUSINESS]: age, city, income, daily routine, objections, where they spend time online, and what words they use.",
"Write 8 ad variations for 11.11 / Black Friday sale of [STORE] with [DISCOUNT]% off.",
"Turn these product features into benefits that a [AUDIENCE] cares about: [FEATURES].",
"Write a lead-magnet ad offering a free [GUIDE/CHECKLIST] about [TOPIC] to collect WhatsApp numbers.",
"Give me 10 unique selling proposition (USP) statements for [BUSINESS] competing against [COMPETITOR TYPE].",
"Analyse this competitor ad and tell me its angle, hook, offer and weaknesses, then write a better version: [PASTE AD]",
"Write a retargeting ad for people who visited our [PRODUCT] page but didn't buy. Address the top 3 objections.",
"Create a 7-day launch ad calendar for [NEW PRODUCT] — what to post/advertise each day and why.",
"Write 5 testimonial-style ad scripts based on these real reviews: [PASTE REVIEWS]. Do not invent new claims.",
"Suggest 10 names and taglines for a [TYPE] brand targeting [AUDIENCE] in Pakistan. Check they're easy to say in Urdu.",
"Write the text for a carousel ad with 5 cards explaining why [PRODUCT] is better than [ALTERNATIVE].",
"Create a brand voice guide for [BRAND]: 5 personality traits, words we use, words we avoid, and 3 sample captions.",
],
"Social Media Content": [
"Create a 30-day Instagram content plan for [BUSINESS] with 4 content pillars. Include format (Reel/carousel/static) and caption idea for each day.",
"Write 10 Instagram captions for [PRODUCT] with a hook in the first line, value in the middle and a CTA at the end.",
"Turn this blog post into a 7-slide carousel. Give the headline for each slide: [PASTE TEXT]",
"Give me 20 Reel ideas for a [NICHE] account that can be filmed with just a phone at home.",
"Write a 'day in the life' Reel script for the owner of [BUSINESS], 30 seconds, with on-screen text.",
"Suggest 30 relevant hashtags for [NICHE] in Pakistan: 10 big, 10 medium, 10 small/niche.",
"Write an engaging 'This or That' poll story sequence for [BRAND] to increase interaction.",
"Write a LinkedIn post about [ACHIEVEMENT/LESSON] in a story format. Short lines, no buzzwords, end with a question.",
"Rewrite this caption in Roman Urdu, friendly and fun: [PASTE CAPTION]",
"Create 10 'myth vs fact' post ideas for [INDUSTRY].",
"Write a Facebook group post that starts a discussion about [TOPIC] without sounding promotional.",
"Give me 15 TikTok trends/formats and explain how [BUSINESS] can use each.",
"Write 5 bio options for an Instagram account that sells [PRODUCT]. Under 150 characters, include a CTA.",
"Plan Instagram story highlights for [BRAND] and write the content for each highlight.",
"Write a behind-the-scenes caption showing how we [MAKE/PACK/DELIVER] our products.",
"Create a giveaway post for [BRAND] with rules that grow followers and follow Instagram guidelines.",
"Write 10 replies to common comments like 'price?', 'location?' and 'DM details' that move people to WhatsApp politely.",
"Repurpose this YouTube video transcript into 5 tweets/X posts, 3 Instagram captions and 1 LinkedIn post: [PASTE]",
"Write 10 relatable meme caption ideas for [NICHE] audience in Pakistan.",
"Create a weekly content batching routine for a solo business owner who has 3 hours per week.",
"Write captions for a 'customer of the week' feature series for [BRAND].",
],
"Sales & Customer Service": [
"Write a WhatsApp greeting message for [BUSINESS] that introduces us and asks what the customer needs.",
"A customer says '[OBJECTION, e.g. price zyada hai]'. Give 5 polite responses that keep the sale alive.",
"Write a COD order confirmation message asking the customer to confirm name, address and phone.",
"Write a follow-up message for a customer who asked the price 2 days ago but didn't reply.",
"Create a sales script for a phone call selling [SERVICE] to [CLIENT TYPE], including discovery questions.",
"Write a polite reply to a 1-star review that says '[REVIEW]'. Take responsibility and offer a solution.",
"Write an upsell message offering [ADD-ON] to a customer who just bought [PRODUCT].",
"Create an FAQ section (10 Q&As) for [BUSINESS] covering delivery, payment, returns and sizing.",
"Write a refund/exchange policy for [BUSINESS] that is fair but protects us from abuse.",
"Draft a message asking happy customers for a review/photo, with a small incentive.",
"Write a win-back message for customers who haven't bought in 90 days.",
"Write 10 WhatsApp quick replies for common questions at [BUSINESS].",
"Create a B2B cold email to [COMPANY TYPE] offering [SERVICE]. Under 120 words, one clear CTA.",
"Role-play as a difficult customer for [PRODUCT] so I can practise handling objections. Start now.",
"Write a delay apology message for orders delayed due to [REASON] with a goodwill gesture.",
"Write a quotation/proposal message for [SERVICE] with 3 package options.",
"Create a lead qualification checklist for [SERVICE] — questions to ask before giving a price.",
"Write a payment reminder for an invoice that is [X] days overdue — friendly, then firm version.",
"Write a thank-you message to send with every order, including how to reorder.",
"Suggest 10 ways to increase average order value for [STORE].",
],
"Freelancing": [
"Act as a Fiverr expert. Suggest 10 profitable gig ideas for someone skilled in [SKILL], with demand level and competition.",
"Write an SEO-optimised Fiverr gig title (max 80 characters) for [SERVICE]. Give 5 options.",
"Write a Fiverr gig description for [SERVICE] with sections: intro, what you get, why me, process, FAQ.",
"Create 3 package tiers (Basic/Standard/Premium) for [SERVICE] with deliverables, delivery days and prices in USD.",
"Write an Upwork proposal for this job post. Start with a hook about their problem, not about me: [PASTE JOB]",
"Write my Upwork profile overview as a [ROLE] with [X] years of experience. First 2 lines must hook the client.",
"Write a cold outreach message to a [BUSINESS TYPE] on LinkedIn offering [SERVICE]. Under 80 words.",
"A client asks for extra work outside scope. Write a polite message explaining it costs $[X] extra.",
"Write a message to ask a client for a 5-star review and testimonial after completing the project.",
"Create a client onboarding questionnaire for [SERVICE].",
"Suggest a portfolio project I can create for free to show skills in [SKILL]. Give the brief.",
"Write a project kickoff message with timeline, milestones and communication rules.",
"Turn my experience into 5 strong portfolio case-study descriptions: [PASTE EXPERIENCE]",
"Write 10 Fiverr gig tags and search keywords for [SERVICE].",
"Write a reply to a client who says my price is too high, without reducing price.",
"Create a weekly routine for a beginner freelancer to get their first order in 30 days.",
"Write a professional message to decline a project politely.",
"Suggest how to niche down from '[GENERAL SKILL]' to a specialised, higher-paying service.",
"Write a revision-request response that clarifies exactly what the client wants changed.",
"Create a LinkedIn headline and About section for a freelance [ROLE].",
],
"Content Writing & Blogging": [
"Act as an SEO content strategist. Give me 20 blog topics about [NICHE] with search intent and a target keyword for each.",
"Create a detailed outline for a blog post titled '[TITLE]', with H2/H3 headings and key points.",
"Write a 300-word introduction for '[TITLE]' that hooks the reader with a relatable problem.",
"Rewrite this paragraph to sound more human and conversational, removing AI-sounding phrases: [PASTE]",
"Write a meta title (under 60 characters) and meta description (under 155 characters) for an article about [TOPIC].",
"Generate 10 FAQ questions people ask about [TOPIC] with short answers for an FAQ section.",
"Proofread this text, fix grammar, and list every change you made: [PASTE]",
"Write a product description for [PRODUCT] for an online store — features, benefits, specs and care instructions.",
"Summarise this article into 5 bullet points and a one-line takeaway: [PASTE]",
"Write a newsletter edition about [TOPIC] with a personal story, 3 tips and a CTA.",
"Turn these notes into a well-structured article: [PASTE NOTES]",
"Write 10 headline variations for '[TITLE]' using numbers, questions and how-to formats.",
"Create a content brief for a writer covering [TOPIC]: audience, keyword, outline, word count, sources to check.",
"Write a comparison article outline: '[PRODUCT A] vs [PRODUCT B]' for Pakistani buyers.",
"Write a 'How to [TASK]' step-by-step guide for beginners with numbered steps.",
"Simplify this technical text for a 14-year-old reader: [PASTE]",
"Suggest internal linking opportunities between these article titles: [LIST]",
"Write a press release announcing [NEWS] for [COMPANY].",
"Write a website About Us page for [BUSINESS], telling our founder story authentically.",
"Write homepage copy for [BUSINESS]: headline, sub-headline, 3 benefits, social proof section and CTA.",
"Write a YouTube video description with timestamps placeholder, keywords and links section for '[VIDEO TITLE]'.",
],
"YouTube & Video": [
"Give me 20 faceless YouTube channel niche ideas with high CPM and low competition for 2026.",
"Write a 6-minute YouTube script on '[TOPIC]' with a strong 15-second hook, 3 main sections and an outro CTA.",
"Write 10 click-worthy but honest YouTube titles for a video about [TOPIC].",
"Describe 5 thumbnail concepts for '[VIDEO TITLE]': main image, text (max 4 words), colours, emotion.",
"Turn this script into a shot list with B-roll suggestions for each line: [PASTE]",
"Write a YouTube Shorts script (under 45 seconds) teaching one quick tip about [TOPIC].",
"Analyse why these 3 competitor videos performed well and give me 5 video ideas inspired by them: [TITLES]",
"Write a channel description and channel keywords for a channel about [NICHE].",
"Create a 12-week upload plan for a new [NICHE] channel, 2 videos per week.",
"Write a pinned comment that drives engagement on my video about [TOPIC].",
"Suggest 10 video series ideas for [NICHE] that build binge-watching.",
"Rewrite this script to improve retention: shorter sentences, open loops, pattern interrupts: [PASTE]",
"Write a sponsorship pitch email to [BRAND] for my [NICHE] channel with [X] subscribers.",
"Write a podcast episode outline about [TOPIC] with 10 interview questions for [GUEST TYPE].",
"Create a voiceover-friendly version of this script with pauses marked: [PASTE]",
"List the best royalty-free music and stock footage sources and explain how to stay copyright-safe.",
"Write 5 video intros under 10 seconds for a channel about [NICHE].",
],
"E-commerce & Online Store": [
"Act as an e-commerce analyst. Suggest 20 trending product ideas to sell online in Pakistan under Rs [PRICE], with reasons.",
"Write a Daraz product title for [PRODUCT] using keywords buyers search for. Give 5 options under 120 characters.",
"Write 5 bullet-point highlights for a Daraz/Shopify listing of [PRODUCT].",
"Calculate the selling price for a product that costs Rs [COST], with [X]% marketplace commission, Rs [SHIPPING] shipping, and a target [Y]% profit margin. Show the working.",
"Write a size guide and care instructions for [CLOTHING ITEM].",
"Write an abandoned cart message sequence (3 messages) for [STORE].",
"Suggest 10 bundle offers for a store selling [PRODUCTS] to increase order value.",
"Write a Shopify homepage section structure for a [NICHE] store with copy for each section.",
"Create a supplier inquiry message asking for MOQ, wholesale price, delivery time and samples for [PRODUCT].",
"Give me a checklist to reduce COD return rates for an online store in Pakistan.",
"Write a return-policy page for [STORE], clear and customer-friendly.",
"Suggest a collection structure (categories) for a store selling [PRODUCTS].",
"Write a product launch announcement for our new [PRODUCT] for Instagram, WhatsApp broadcast and email.",
"Write a 'Why buy from us' section that builds trust for a new online store in Pakistan.",
"Analyse these customer reviews and tell me the top 3 complaints and top 3 praises: [PASTE REVIEWS]",
"Create a 11.11 campaign plan for [STORE]: offers, timeline, content and ad budget split.",
"Write image alt-text and file names for these product photos: [DESCRIBE]",
"Write 10 Google Shopping / search keywords that buyers of [PRODUCT] would use.",
"Write a shipping policy covering delivery times by city, charges and tracking.",
"Suggest 5 loyalty program ideas for a small online store.",
],
"Business & Strategy": [
"Act as a business consultant. Analyse this business idea for the Pakistani market: [IDEA]. Give SWOT, target customer, pricing and first 3 steps.",
"Create a one-page business plan for [BUSINESS] with problem, solution, customers, revenue model, costs and marketing.",
"Suggest 10 low-investment business ideas under Rs [BUDGET] for [CITY/SITUATION].",
"Do a competitor analysis framework for [BUSINESS]: what to compare and where to find the information.",
"Write a pricing strategy for [PRODUCT/SERVICE]: cost-plus, value-based and competitor-based options compared.",
"Create a 90-day growth plan for [BUSINESS] with weekly goals.",
"Give me 10 questions to interview potential customers to validate [IDEA].",
"Write standard operating procedure (SOP) steps for [PROCESS] in my business.",
"Draft a job post for hiring a [ROLE] for my small business, including responsibilities and requirements.",
"Write an interview question list for hiring a [ROLE].",
"Create a simple KPI dashboard list for [BUSINESS] — what to track weekly and monthly.",
"Suggest ways to reduce costs in [BUSINESS] without hurting quality.",
"Write a partnership proposal to [BUSINESS TYPE] for cross-promotion.",
"Help me decide between [OPTION A] and [OPTION B] using a decision matrix.",
"Write a mission, vision and 3 core values for [BUSINESS].",
"Create a customer journey map for [BUSINESS] from discovery to repeat purchase.",
"List the legal and registration steps to formalise a small business in Pakistan (FBR NTN, SECP, etc.) and tell me which to verify with a professional.",
"Write a pitch for [BUSINESS] I can say in 60 seconds to an investor or partner.",
"Create a weekly planning template for a business owner who also has a job.",
"Brainstorm 15 ways to get the first 10 customers for [BUSINESS] with zero ad budget.",
],
"Excel, Data & Productivity": [
"Write an Excel formula to [TASK, e.g. sum sales where city is Lahore]. Explain how it works.",
"Explain VLOOKUP vs XLOOKUP vs INDEX-MATCH with a simple example.",
"Create a table structure for tracking [DATA] in Google Sheets with column names and data types.",
"Write a Google Sheets formula to remove duplicates and sort this list automatically.",
"Help me create a pivot table to summarise sales by month and product. Give steps.",
"Write an Apps Script that sends me an email when a new row is added to my Google Sheet.",
"Convert this messy data into a clean table: [PASTE DATA]",
"Create a daily to-do system using the Eisenhower matrix for my tasks: [LIST]",
"Turn this long email into 3 clear action items with owners and deadlines: [PASTE]",
"Write meeting minutes from these notes: [PASTE NOTES]",
"Plan my week with time blocks: work hours [X], tasks [LIST], priorities [LIST].",
"Write a professional email to [PERSON] about [SUBJECT]. Tone: [polite/firm/friendly].",
"Explain this chart/data and give 3 insights: [PASTE DATA]",
"Create a conditional formatting rule to highlight overdue dates in red.",
"Build a simple invoice template layout for Google Sheets with auto-total and tax.",
"Suggest a folder and file-naming system for my [BUSINESS/FREELANCE] files.",
"Summarise this PDF/document into a one-page brief: [PASTE TEXT]",
"Write a formula to calculate monthly instalments for a loan of Rs [AMOUNT] at [X]% for [N] months.",
"Create a habit tracker layout in Google Sheets with a progress percentage.",
"Explain how to automate [REPETITIVE TASK] using free tools like Zapier, Make or Google Apps Script.",
],
"Career & Jobs": [
"Rewrite my CV bullet points to be achievement-focused with numbers: [PASTE BULLETS]",
"Tailor my CV to this job description. Tell me which keywords are missing: [CV] [JOB DESCRIPTION]",
"Write a cover letter for [ROLE] at [COMPANY] using my experience: [EXPERIENCE]. Under 250 words.",
"Act as an interviewer for a [ROLE] position. Ask me 10 questions one by one and give feedback on each answer.",
"Help me answer 'Tell me about yourself' for a [ROLE] interview in under 90 seconds.",
"Write a LinkedIn summary for a [ROLE] who wants to move into [NEW FIELD].",
"Give me a 3-month learning plan to become job-ready in [SKILL] using free resources.",
"Write a polite salary negotiation email asking for Rs [AMOUNT] instead of the offered Rs [OFFER].",
"Write a resignation letter that keeps a good relationship with my employer.",
"Write a message to a senior on LinkedIn asking for career advice, not a job.",
"Prepare STAR-method answers for: teamwork, conflict, failure and leadership, based on: [EXPERIENCE]",
"List 10 remote job websites and how to stand out on each.",
"Write a follow-up email after an interview for [ROLE].",
"Help me create a personal brand statement for [FIELD].",
"Explain [CONCEPT] as if preparing me for a technical interview, then quiz me.",
"Write an internship application email for a student studying [DEGREE].",
"Create a job-search tracker table with columns I should track.",
],
"Education & Study": [
"Explain [TOPIC] in simple words with an everyday Pakistani example, then give 5 quiz questions.",
"Create a 4-week study timetable for [EXAM] with [X] hours per day, including revision days.",
"Make flashcards (question/answer) from these notes: [PASTE]",
"Summarise this chapter into key points I can revise in 10 minutes: [PASTE]",
"Give me 10 MCQs on [TOPIC] with answers and explanations.",
"Explain the mistakes in my solution and how to fix them: [PASTE]",
"Teach me [SKILL] like a tutor. Start with a diagnostic question to check my level.",
"Create a mind-map structure for [TOPIC].",
"Write an essay outline on '[TOPIC]' with thesis, arguments and counter-arguments.",
"Give me mnemonics to remember [LIST].",
"Translate and explain this English paragraph in simple Urdu: [PASTE]",
"Help me improve my English speaking: give me 10 daily phrases for [SITUATION] with Urdu meaning.",
"Correct my English writing and explain each grammar mistake: [PASTE]",
"Create a research plan for my assignment on [TOPIC] including what sources to look for.",
"Suggest 10 final-year project ideas for [DEGREE] students that solve a local problem.",
"Explain this code line by line for a beginner: [PASTE CODE]",
],
"Personal Growth & Daily Life": [
"Create a monthly budget for a salary of Rs [AMOUNT] for a family of [N] in [CITY], with savings target.",
"Plan healthy, budget-friendly Pakistani meals for 7 days for [N] people.",
"Give me a morning routine to be productive while working from home.",
"Help me set 3 SMART goals for the next 90 days in [AREA].",
"Write a polite message to say no to [REQUEST] without hurting the relationship.",
"Suggest 10 skills I can learn online in 3 months to start earning, based on my interests: [INTERESTS]",
"Make a packing checklist for a [N]-day trip to [PLACE].",
"Help me plan a small family event for [OCCASION] within Rs [BUDGET].",
"Give me a 30-day reading plan to build the habit, with book suggestions on [TOPIC].",
"Write a journaling prompt for each day of the week for reflection and gratitude.",
"Compare [PHONE/LAPTOP A] vs [B] for [USE CASE] — and tell me what to verify before buying.",
"Explain how compound savings works with an example of saving Rs [AMOUNT] monthly.",
"Create a simple home workout plan with no equipment for beginners.",
"Help me write a heartfelt message for [PERSON] on [OCCASION].",
"Create a digital detox plan to reduce my screen time from [X] hours to [Y] hours.",
],
}


def markup():
    out = [FORMULA]
    n = 0
    for cat, prompts in CATS.items():
        out.append(f"# {cat}")
        out.append(f"{len(prompts)} prompts. Replace everything in [BRACKETS] with your own details.")
        for p in prompts:
            n += 1
            out.append(f"{n}. {p}")
        out.append("")
    out.append("# Prompt Chaining Workflows")
    out.append("Chaining means using the output of one prompt as the input for the next. Here are 4 workflows you can run in one ChatGPT chat:")
    out.append("## Workflow 1 — Product launch in 1 hour")
    out += ["1. Customer avatar prompt (Marketing #10).", "2. Pain points & desires (Marketing #3) using the avatar.",
            "3. 10 hooks using the top 3 pain points.", "4. 5 ad primary texts using the best 2 hooks.", "5. 7-day launch calendar (Marketing #17).", ""]
    out.append("## Workflow 2 — Freelance gig from zero")
    out += ["1. Gig ideas for your skill (Freelancing #1).", "2. Niche down the best idea (Freelancing #18).", "3. Gig title + tags.", "4. Gig description + packages.", "5. Outreach message to 10 prospects.", ""]
    out.append("## Workflow 3 — One blog post, ten pieces of content")
    out += ["1. Blog outline → full draft → humanise.", "2. Carousel from the blog (Social #3).", "3. Reel script from slide 1.", "4. Newsletter edition.", "5. 5 short posts for X/Threads.", ""]
    out.append("## Workflow 4 — Exam prep sprint")
    out += ["1. Study timetable.", "2. Chapter summaries.", "3. Flashcards from summaries.", "4. MCQ quiz daily.", "5. Explain mistakes.", ""]
    out.append("> Save your best prompts in a Google Doc called 'My Prompt Library'. Over time it becomes your most valuable work tool.")
    return "\n".join(out), n
