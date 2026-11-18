"""10 AI Workflow products (No. 26–35). Each workflow is rendered with the same proven structure."""

STD_INTRO = """
## How every Skillstack workflow is built
Each workflow comes in **two levels** so you can start today and automate later:
- **Level 1 — Assisted (free / no-code):** you run the steps yourself with AI tools. Works from day one, costs almost nothing.
- **Level 2 — Automated:** the same steps connected with Make.com or n8n so they run on their own.
> Start with Level 1 for at least a week. Automating a process you haven't tested by hand just makes mistakes faster.
"""

STD_RULES = """
## Ground rules for using AI in business
- **Check before you send.** AI can be wrong about prices, laws, platform rules and facts. A human approves anything customer-facing until the workflow is proven.
- **Protect customer data.** Don't paste CNIC numbers, card details or passwords into AI tools. Use first names and order IDs.
- **Follow platform rules.** WhatsApp, Meta, Upwork, Fiverr and Daraz all have policies on automation and messaging. When in doubt, keep a human in the loop.
- **Prices change.** Tool prices in this guide were checked in late 2026 and are approximate; confirm on each tool's website.
"""


def render(w):
    out = [f"# What You'll Build", w["what"], STD_INTRO]
    out.append("## The workflow at a glance")
    out.append("| Step | Tool | What happens |")
    out += [f"| {i} | {t} | {d} |" for i, (t, d) in enumerate(w["flow"], 1)]
    out.append("")
    out.append("## Who it's for")
    out += [f"- {x}" for x in w["for"]]
    out.append("")
    out.append("# Tools & Costs")
    out.append("| Tool | Used for | Cost (approx.) |")
    out += [f"| {a} | {b} | {c} |" for a, b, c in w["tools"]]
    out.append("")
    out.append(w.get("cost_note", "> You can run Level 1 entirely on free plans. Pay for a tool only when the free limit becomes the bottleneck."))
    out.append("# Level 1 — Set Up the Assisted Workflow")
    for title, steps in w["setup"]:
        out.append(f"## {title}")
        out += [f"{i}. {s}" for i, s in enumerate(steps, 1)]
        out.append("")
    out.append("# Copy-Paste Prompts")
    out.append("Replace everything in [BRACKETS]. Save these in a ChatGPT Project / Claude Project / Gemini Gem so the instructions are always loaded.")
    for title, prompt in w["prompts"]:
        out.append(f"## {title}")
        out.append("```")
        out += _wrap_code(prompt)
        out.append("```")
    if w.get("code"):
        title, intro, code = w["code"]
        out.append(f"# {title}")
        out.append(intro)
        out.append("```")
        out += code.strip("\n").splitlines()
        out.append("```")
    out.append("# Level 2 — Automate It")
    out.append(w["auto_intro"])
    out.append("| # | Module / node | Settings |")
    out += [f"| {i} | {a} | {b} |" for i, (a, b) in enumerate(w["auto"], 1)]
    out.append("")
    out += [f"> {x}" for x in w.get("auto_tips", [])]
    out.append("# Test, Launch & Measure")
    out.append("## Testing checklist")
    out += [f"[ ] {x}" for x in w["tests"]]
    out.append("")
    out.append("## Numbers to track")
    out.append("| Metric | Why it matters | Good sign |")
    out += [f"| {a} | {b} | {c} |" for a, b, c in w["metrics"]]
    out.append("")
    out.append("## Common problems & fixes")
    out.append("| Problem | Fix |")
    out += [f"| {a} | {b} |" for a, b in w["fixes"]]
    out.append("")
    out.append("# Sell This Workflow as a Service")
    out.append(w["sell_intro"])
    out.append("| Package | What you deliver | Price (PKR) | Price (USD, Fiverr/Upwork) |")
    out += [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in w["packages"]]
    out.append("")
    out.append("## Pitch message")
    out.append(w["pitch"])
    out.append(STD_RULES)
    return "\n".join(out)


def _wrap_code(text, width=96):
    lines = []
    for para in text.split("\n"):
        while len(para) > width:
            cut = para.rfind(" ", 0, width)
            cut = cut if cut > 0 else width
            lines.append(para[:cut])
            para = "  " + para[cut:].lstrip()
        lines.append(para)
    return lines


W = {}

W["ai-whatsapp-sales-assistant"] = dict(
    what="An AI assistant that answers WhatsApp inquiries in seconds: greets the customer, answers price, size and delivery questions from **your** product information, handles common objections, collects order details and hands complex chats to a human. Most Pakistani sales start on WhatsApp, and the business that replies first usually wins the order.",
    flow=[("WhatsApp Business", "Customer sends a message"), ("Knowledge sheet", "Your products, prices, policies and FAQs in one Google Sheet"),
          ("ChatGPT / Claude Project", "Drafts a reply using only your knowledge sheet"), ("You (Level 1) or automation (Level 2)", "Reply is sent; order details collected"),
          ("Orders sheet", "Confirmed order logged with name, city, items, total")],
    **{"for": ["Online stores, home businesses and service providers getting 20+ WhatsApp chats a day", "Teams where replies are slow at night or on weekends", "Freelancers who want to sell this setup to local businesses"]},
    tools=[("WhatsApp Business app", "Labels, quick replies, catalogue (Level 1)", "Free"),
           ("ChatGPT / Claude / Gemini", "Drafting replies from your knowledge", "Free tier or ~$20/month"),
           ("Google Sheets", "Knowledge base + orders log", "Free"),
           ("WhatsApp Cloud API (Meta)", "Automated sending (Level 2)", "Service conversations within 24h are free or low-cost; template messages are charged per Meta's rate card for Pakistan"),
           ("Make.com or n8n", "Connects WhatsApp, AI and Sheets", "Make free tier; n8n self-hosted free"),
           ("OpenAI / Anthropic API", "AI replies in automation", "Usually Rs 1–5 per conversation at typical lengths")],
    setup=[("Build your knowledge sheet", ["Create a Google Sheet called **Knowledge** with tabs: Products, Policies, FAQs, Tone.",
            "Products tab columns: Name · Price (Rs) · Variants/sizes · In stock (Y/N) · 1-line benefit · Photo link.",
            "Policies tab: delivery time by city, delivery charges, COD rules, exchange/refund policy, payment accounts.",
            "FAQs tab: copy the 20 questions you get most from your WhatsApp history, with your best answer.",
            "Tone tab: 5 example replies you're proud of. The AI will copy this style."]),
           ("Set up WhatsApp Business properly", ["Add catalogue, business hours, address and a greeting message.",
            "Create labels: New lead · Price sent · Waiting payment · Confirmed · Dispatched · Complaint.",
            "Save quick replies for /price /order /pay /track /review (see product No. 14 for scripts)."]),
           ("Create the AI assistant", ["In ChatGPT (Projects), Claude (Projects) or Gemini (Gems) create **WhatsApp Assistant**.",
            "Paste the System Prompt from the next chapter as the instructions.",
            "Upload or paste your Knowledge sheet (export as CSV). Re-upload whenever prices change.",
            "Daily use: copy the customer's message → paste → copy the reply → check → send. About 15 seconds per chat."])],
    prompts=[("System prompt (assistant instructions)", "You are the WhatsApp sales assistant for [BUSINESS], which sells [WHAT] in Pakistan.\nUse ONLY the attached knowledge (products, prices, policies, FAQs). If the answer isn't there, say a team member will confirm shortly. Never invent prices, stock or delivery dates.\nReply in the customer's language (English, Roman Urdu or Urdu). Keep replies under 60 words, friendly, 1 emoji max.\nAlways end with one clear next step (choose a size, share address, confirm order).\nTo take an order collect: name, full address with city, phone, item + variant + quantity. Then show a summary with total and ask them to reply YES.\nIf the customer is angry, asks for a refund, or mentions a problem with an order, reply politely and write [HANDOFF] at the start so a human takes over."),
             ("Objection handler", "Customer said: \"[MESSAGE]\". Using our policies, write 3 short replies that keep the sale alive without discounting. Mention COD, exchange policy or quality proof where relevant."),
             ("Order summary", "Turn this chat into an order row: Name | City | Address | Phone | Items | Qty | Total | Payment method. Chat: [PASTE]"),
             ("Weekly improvement", "Here are this week's chats where we lost the sale: [PASTE]. What were the top 3 reasons? Suggest new FAQ answers to add to the knowledge sheet.")],
    auto_intro="Level 2 uses the official **WhatsApp Cloud API** (via Meta Business). You need a phone number that is not already active on the WhatsApp app, a verified Meta Business account, and approved message templates for messages you start outside the 24-hour customer-service window.",
    auto=[("Webhook: WhatsApp Cloud API → Watch messages", "Trigger on every incoming customer message"),
          ("Google Sheets → Search rows", "Load Products, Policies and FAQs (cache them; refresh hourly)"),
          ("Data store / Sheets → Get last 10 messages", "Gives the AI the conversation history for this phone number"),
          ("OpenAI / Anthropic → Create completion", "System prompt + knowledge + history + new message"),
          ("Router", "If reply starts with [HANDOFF] → notify a human (email/Slack/WhatsApp group) and send a holding reply"),
          ("WhatsApp Cloud API → Send message", "Send the AI reply (free-form text is only allowed within 24h of the customer's last message)"),
          ("Google Sheets → Add row", "If the customer replied YES to an order summary, log the order")],
    auto_tips=["Run in **shadow mode** first: the AI writes replies into a sheet and a human sends them. Switch to auto-send only after 100 good replies.",
               "Ready-made option: tools like WATI, Interakt or ManyChat (WhatsApp) provide the API connection and an AI-agent builder if you don't want to build in Make/n8n."],
    tests=["20 real past questions answered correctly from the knowledge sheet", "Out-of-stock item → assistant says so and suggests an alternative",
           "Question not in knowledge → assistant hands off, doesn't invent", "Angry customer message → [HANDOFF] triggered",
           "Roman Urdu question → Roman Urdu reply", "Order summary total matches your price list"],
    metrics=[("First reply time", "Speed wins sales", "Under 2 minutes"), ("Chat → order rate", "Is the assistant selling?", "Rising week on week"),
             ("Handoff rate", "How often a human is needed", "Under 20% after month 1"), ("Wrong answers / week", "Quality", "Zero after week 2")],
    fixes=[("AI invents a price", "Add 'never invent prices' to the prompt and make sure the product is in the sheet with the exact name customers use"),
           ("Replies too long", "Lower the word limit to 40 and add 2 short example replies to the Tone tab"),
           ("Template message rejected by Meta", "Remove promotional language from utility templates; follow Meta's template guidelines")],
    sell_intro="Small businesses in Pakistan lose orders to slow replies. Set this up for them.",
    packages=[("Starter", "Knowledge sheet + AI Project + quick replies + 1h training", "15,000–25,000", "$80–150"),
              ("Automated", "Cloud API + Make/n8n flow + shadow mode + handoff", "40,000–80,000", "$250–500"),
              ("Monthly care", "Update knowledge, review chats, improve prompts", "10,000–20,000 / month", "$60–120 / month")],
    pitch="\"Assalam o Alaikum! I noticed it took a few hours to get a reply from [BUSINESS] on WhatsApp. I set up AI-assisted WhatsApp replies for small businesses so every customer gets an answer in under 2 minutes, using your own prices and policies, with a human approving anything sensitive. Can I show you a 5-minute demo with your products?\"",
)

W["ai-content-calendar-machine"] = dict(
    what="A system that produces **30 days of social media posts in about 2 hours**: ideas, hooks and captions from AI, designs auto-filled from a spreadsheet with Canva Bulk Create, and everything scheduled in Meta Business Suite. Consistency is the biggest problem for small brands, and this workflow solves it.",
    flow=[("ChatGPT / Claude", "30 post ideas across 4 content pillars"), ("Google Sheets", "Headline, sub-text, caption, CTA, hashtags per post"),
          ("Canva Bulk Create", "One template + the sheet = 30 designed posts"), ("Meta Business Suite", "Schedule to Instagram & Facebook"),
          ("Insights review", "Monthly: double down on what worked")],
    **{"for": ["Small businesses posting irregularly", "Social media managers handling 3+ clients", "Personal brands and coaches"]},
    tools=[("ChatGPT / Claude / Gemini", "Ideas, hooks, captions", "Free or ~$20/month"), ("Google Sheets", "Content database", "Free"),
           ("Canva Pro", "Bulk Create (fills templates from data)", "Canva Pro subscription (check current PKR price)"),
           ("Meta Business Suite", "Scheduling for FB + IG", "Free"), ("CapCut (optional)", "Turning posts into Reels", "Free tier")],
    setup=[("Define your pillars (once)", ["Pick 4 pillars: Teach (35%), Relate (25%), Prove (20%), Sell (20%).",
            "Write 3 example posts you like for each pillar — the AI will match them.", "Note your brand voice in 5 words (e.g. friendly, practical, local, honest, short)."]),
           ("Generate the month", ["Run the 'Monthly plan' prompt → paste the table into Google Sheets.",
            "Columns needed for Canva: Headline · Subtext · Highlight · CTA. Keep headlines under 8 words.",
            "Run the 'Caption writer' prompt on the sheet to fill Caption + Hashtags columns.",
            "Read every row. Delete weak ideas, fix facts, add local details (prices, cities, festivals)."]),
           ("Design 30 posts at once", ["In Canva create one post template with text boxes for Headline, Subtext, CTA.",
            "Apps → Bulk Create → upload the sheet as CSV → connect each column to its text box.",
            "Generate → review all designs → fix any text overflow → download as PNG (zip)."]),
           ("Schedule", ["Meta Business Suite → Planner → create post → upload image + caption → schedule.",
            "Best starting times for Pakistan: 1–2 pm and 8–11 pm PKT — then use your own Insights.",
            "Block 30 minutes daily to reply to comments (engagement boosts reach)."])],
    prompts=[("Monthly plan", "Act as a social media strategist for [BRAND], a [BUSINESS TYPE] in [CITY], Pakistan, targeting [AUDIENCE].\nCreate a 30-day plan as a table with columns: Day | Pillar | Format (static/carousel/Reel) | Headline (max 8 words) | Subtext (max 15 words) | Highlight word | CTA.\nPillar mix: Teach 35%, Relate 25%, Prove 20%, Sell 20%. Include [OCCASIONS THIS MONTH]. Mix English and Roman Urdu naturally. No fake statistics."),
             ("Caption writer", "For each row below write: a caption (hook first line, 40–80 words, 1–2 emojis, CTA at end) and 4 relevant hashtags (mix broad + Pakistani niche). Return as a table: Day | Caption | Hashtags.\n[PASTE ROWS]"),
             ("Reel converter", "Turn this post into a 20-second Reel script: 2-second hook text, 3 quick shots with on-screen text, CTA. Post: [PASTE]"),
             ("Monthly review", "Here are last month's post stats (reach, saves, shares, comments, DMs): [PASTE]. Which pillars and formats performed best? Give me 5 ideas for next month based on the winners.")],
    auto_intro="Level 2 removes copy-pasting: a sheet row marked 'Approved' becomes a scheduled post automatically.",
    auto=[("Google Sheets → Watch rows", "Trigger when Status = Approved"), ("OpenAI → Create completion", "Generate caption + hashtags if empty"),
          ("Canva Connect API or image generator (optional)", "Or keep Canva Bulk Create manual and upload PNGs to a Drive folder named by Day"),
          ("Google Drive → Search file", "Find the PNG for that Day"), ("Instagram for Business → Create a photo post", "Publish at the scheduled time (Make supports IG business accounts)"),
          ("Google Sheets → Update row", "Status = Published + post URL")],
    auto_tips=["Keep a human approval column. Brands get into trouble when AI posts something tone-deaf during sensitive news events."],
    tests=["30 rows have no headline over 8 words (fits the template)", "No duplicated ideas", "Every Sell post has a clear CTA and price",
           "Occasions/festivals on correct dates", "Bulk Create preview checked for overflow", "Scheduled times in PKT"],
    metrics=[("Posts published / month", "Consistency", "20+"), ("Saves + shares per post", "Content value", "Rising"),
             ("Profile visits → follows", "Profile strength", "10%+"), ("DMs / link clicks", "Sales intent", "Rising")],
    fixes=[("Captions sound robotic", "Add 3 of your best real captions to the prompt as style examples"),
           ("Canva text overflows", "Set max characters in the prompt; enable auto-resize text in the template"),
           ("Same ideas every month", "Feed last month's best posts and ask for new angles, not new topics")],
    sell_intro="Content creation is the most requested service by Pakistani small businesses.",
    packages=[("Content pack", "30 designed posts + captions (client posts them)", "12,000–25,000", "$80–150"),
              ("Managed", "30 posts + scheduling + monthly report", "25,000–45,000 / month", "$150–300 / month"),
              ("Setup only", "Templates + sheet + training for in-house team", "20,000–35,000", "$120–200")],
    pitch="\"Hi [Name], I love your products but noticed your last post was [X] weeks ago. I can deliver 30 on-brand posts with captions every month, ready to schedule, so your page stays active without taking your time. Want to see 3 free sample posts for [BRAND]?\"",
)

W["ai-faceless-reels-factory"] = dict(
    what="A production line for **faceless short videos** (Reels, TikTok, YouTube Shorts): AI-assisted research and scripts, natural voiceover, stock or screen-recorded visuals, auto captions and batch scheduling. Make 10 videos in one sitting, without showing your face.",
    flow=[("ChatGPT / Claude", "Topic research + 10 scripts with hooks"), ("ElevenLabs or CapCut text-to-speech", "Voiceover"),
          ("Pexels / Pixabay / screen recordings", "Visuals"), ("CapCut", "Edit, auto-captions, template"), ("Meta Business Suite / TikTok / YouTube Studio", "Schedule")],
    **{"for": ["Faceless educational pages (tech, finance basics, history, study tips)", "Businesses that want Reels without filming people", "Video editors selling short-form packages"]},
    tools=[("ChatGPT / Claude", "Research & scripts", "Free or ~$20/month"), ("ElevenLabs", "Natural voiceover", "Free tier; paid from ~$5/month"),
           ("CapCut", "Editing, captions, TTS", "Free tier; Pro optional"), ("Pexels / Pixabay", "Free stock video", "Free"),
           ("Canva (optional)", "Thumbnails / covers", "Free or Pro")],
    setup=[("Pick a niche and format", ["Choose one niche and one repeatable format (e.g. '3 AI tools for students', 'One Excel trick a day').",
            "Study 10 top videos in your niche: note hook style, length (aim 20–40s), and caption style.", "Create a CapCut template: fonts, caption style, logo, intro sting (1s max)."]),
           ("Batch scripts", ["Run the 'Script batch' prompt for 10 topics.", "Fact-check every claim; add one personal or local detail per script.",
            "Read each script aloud and time it. Cut anything over 40 seconds."]),
           ("Produce in batches", ["Generate all 10 voiceovers in one session; name files 01–10.",
            "Collect 4–6 clips per video from Pexels or record your screen.", "Import into the CapCut template → Auto captions → fix any wrong words (especially Urdu names).",
            "Export 1080×1920, 30fps. Create a cover frame with the hook text."]),
           ("Publish", ["Post 1 per day at your best time; same video can go to Reels, TikTok and Shorts.",
            "Use platform AI-disclosure labels where required (e.g. realistic AI-generated people or voices).",
            "Pin a comment with the CTA."])],
    prompts=[("Script batch", "Write 10 faceless short-video scripts for a [NICHE] page aimed at Pakistani [AUDIENCE].\nFor each: Title | Hook (spoken, under 8 words, creates curiosity) | 4–6 short spoken lines | On-screen text for each line | B-roll idea for each line | CTA.\nLength 25–35 seconds when spoken. Simple English with light Roman Urdu. No made-up statistics; mark any fact I should verify with [VERIFY]."),
             ("Hook upgrader", "Here are 10 hooks: [PASTE]. Rewrite each 3 ways: question, bold claim, and 'stop doing X'. Keep under 8 words."),
             ("Repurpose long video", "Here is a transcript: [PASTE]. Find the 5 most interesting 30-second moments and write a hook + caption for each."),
             ("Caption & hashtags", "Write a caption (max 40 words, curiosity + CTA) and 4 hashtags for this video script: [PASTE]")],
    auto_intro="Level 2 automates the boring parts: scripts and voiceovers are generated from a topic list and dropped in a Drive folder ready for editing.",
    auto=[("Google Sheets → Watch rows", "New topic added with Status = Ready"), ("OpenAI → Create completion", "Generate script using the Script prompt"),
          ("ElevenLabs → Text to speech (HTTP module)", "Create the voiceover MP3"), ("Google Drive → Upload file", "Save script.txt + voice.mp3 in /Reels/[Topic]"),
          ("Google Sheets → Update row", "Status = Script ready; editor is notified")],
    auto_tips=["Editing stays human. Fully auto-generated slideshow videos tend to get low reach, and on YouTube they can be refused monetisation as 'repetitious' content."],
    tests=["Every fact verified", "Captions spelled correctly (names, places)", "Audio levels even; music under voice", "Hook appears as text in first second",
           "Copyright-safe music (platform library or royalty-free)", "AI disclosure applied where required"],
    metrics=[("3-second hold rate", "Is the hook working?", "60%+"), ("Average watch %", "Retention", "50%+ for 30s videos"),
             ("Shares + saves", "Value", "Rising"), ("Follows per 1,000 views", "Page growth", "5+")],
    fixes=[("Robotic voice", "Try another voice, add punctuation for pauses, or record your own voice"), ("Low reach", "Rewrite hooks first; it's usually the first 2 seconds"),
           ("Muted audio", "You used copyrighted music; switch to the platform's music library")],
    sell_intro="Brands want Reels but don't want to be on camera. Faceless packages are easy to sell.",
    packages=[("10 Reels", "Scripts + voice + edit + captions", "15,000–30,000", "$80–200"),
              ("30 Reels / month", "Full production + posting plan", "40,000–80,000 / month", "$250–600 / month"),
              ("Channel setup", "Niche, template, first 10 videos, training", "30,000–50,000", "$200–350")],
    pitch="\"Hi [Name], short videos get the most reach on Instagram and TikTok in Pakistan, but filming takes time. I produce faceless Reels for [BUSINESS TYPE] (script, voice, editing, captions) so you can post daily without being on camera. Here are 2 samples I made for your niche: [link].\"",
)

W["ai-lead-gen-outreach-system"] = dict(
    what="A system to find businesses that need your service, research each one, write **personalised** outreach in seconds with AI, and track replies in one sheet. Built for freelancers and agencies who want clients without depending only on Fiverr or Upwork.",
    flow=[("Google Maps / LinkedIn / Instagram", "Find businesses in your niche & city"), ("Google Sheets", "Lead list: name, website, Instagram, email, notes"),
          ("ChatGPT / GPT for Sheets", "1–2 personalised lines per lead based on their website/page"), ("Gmail / LinkedIn", "Send outreach + 2 follow-ups"),
          ("Pipeline sheet", "Track replies → calls → clients")],
    **{"for": ["Freelancers (design, web, ads, content, video)", "Small agencies", "B2B sellers (packaging, printing, software)"]},
    tools=[("Google Maps / LinkedIn", "Finding leads", "Free"), ("Google Sheets", "CRM / pipeline", "Free"),
           ("ChatGPT / Claude", "Research + personalisation", "Free or ~$20/month"), ("GPT for Sheets add-on (optional)", "Run AI inside Sheets", "Pay-as-you-go"),
           ("Gmail + mail-merge add-on (e.g. YAMM)", "Sending personalised emails", "Free daily limit"), ("Hunter.io (optional)", "Finding public business emails", "Free tier")],
    setup=[("Define your ideal client", ["Niche + city + size + visible problem. Example: 'Lahore restaurants with outdated Instagram (no Reels in 30 days).'",
            "Write your offer in one line with a result: 'I make 12 Reels a month that show your food at its best.'"]),
           ("Build the lead list (50 leads)", ["Search Google Maps: '[niche] in [city]'. Open each listing.",
            "Record: Business · Website · Instagram · Public email/WhatsApp (business listings only) · What you noticed (the problem).",
            "Only collect publicly listed business contacts. Never buy personal number lists."]),
           ("Personalise with AI", ["For each lead paste what you noticed + their website text into the 'Personal line' prompt.",
            "Paste the line into the sheet. Read it; it must mention something real about them.",
            "Use the 'Outreach email' prompt to merge your offer + personal line."]),
           ("Send & follow up", ["Send 10–20 emails/day from a professional Gmail. Follow up on day 3 and day 7.",
            "On LinkedIn: connect with a note (no pitch), then message after accepting.",
            "WhatsApp: only for businesses that list WhatsApp publicly for inquiries, one message, no bulk blasting (bulk messages get numbers banned)."])],
    prompts=[("Personal line", "Here is information about a business: [WEBSITE TEXT / INSTAGRAM BIO / WHAT I NOTICED].\nWrite ONE sentence (max 25 words) that shows I looked at their business specifically and points to an opportunity related to [MY SERVICE]. Friendly, not salesy, no flattery clichés."),
             ("Outreach email", "Write a cold email under 90 words. Structure: personal line → the opportunity → one result I achieved for a similar client ([RESULT]) → low-pressure CTA (a 10-minute call or a free sample).\nPersonal line: [LINE]. My service: [SERVICE]. Give 3 subject lines under 6 words."),
             ("Follow-ups", "Write two follow-ups for this email: day 3 (add one new useful idea) and day 7 (polite close-the-loop). Each under 50 words. Email: [PASTE]"),
             ("Reply handler", "A lead replied: \"[REPLY]\". Write a response that answers them and moves to a call or a clear price. Under 70 words.")],
    auto_intro="Level 2 enriches and drafts automatically; **you still press send**, which keeps quality high and protects your email reputation.",
    auto=[("Google Sheets → Watch rows", "New lead with Website filled"), ("HTTP → Get website", "Fetch homepage text (respect robots.txt)"),
          ("OpenAI → Create completion", "Write personal line + email draft"), ("Gmail → Create a draft", "Draft appears in your Gmail for review"),
          ("Google Sheets → Update row", "Status = Draft ready; follow-up dates set (+3, +7 days)")],
    auto_tips=["Warm up a new email domain slowly (10/day, then increase). Mass sending from a fresh address lands in spam.",
               "Include your real name, business name and an opt-out line in cold emails."],
    tests=["Every personal line mentions something specific & true", "Spelling of business names correct", "Links in signature work",
           "Opt-out line included", "Follow-up dates calculated", "Sending limit under 30/day initially"],
    metrics=[("Reply rate", "Message quality", "8–15%"), ("Positive replies → calls", "Offer strength", "40%+"),
             ("Calls → clients", "Sales skill", "20–30%"), ("Leads added / week", "Activity", "50+")],
    fixes=[("No replies", "Make the offer more specific and the CTA smaller (free sample)"), ("Emails in spam", "Fewer links, no attachments, slower volume, set up SPF/DKIM on your domain"),
           ("AI lines feel generic", "Give the AI more raw input: a specific post, review or page section")],
    sell_intro="Agencies and B2B businesses pay well for qualified leads and outreach systems.",
    packages=[("Lead list", "100 researched leads with notes + personal lines", "10,000–20,000", "$60–150"),
              ("Outreach setup", "Sheet CRM + templates + automation + training", "30,000–60,000", "$200–400"),
              ("Done-for-you outreach", "Monthly leads + sending + reply handling", "50,000+ / month", "$400+ / month")],
    pitch="\"Hi [Name], I help [NICHE] businesses get new clients with personalised outreach rather than spam. I build a list of businesses that fit your ideal customer, research each one, and set up a simple system so you follow up consistently. Shall I send you 10 sample leads for free?\"",
)

W["ai-website-support-chatbot"] = dict(
    what="A customer-support chatbot on your website, trained on **your** FAQs, policies and product pages. It answers 24/7, captures leads, and hands over to WhatsApp or email when a human is needed.",
    flow=[("Your content", "FAQs, policies, product pages collected in one doc"), ("Chatbot builder (Chatbase / Tidio / Voiceflow)", "Trains the bot on your content"),
          ("Website widget", "Bot appears on every page"), ("Lead capture", "Name + WhatsApp/email collected when relevant"), ("Handoff", "Button to WhatsApp or ticket to email")],
    **{"for": ["Online stores and service businesses with repeat questions", "Clinics, schools, travel agents, real estate", "Freelance web developers adding a high-value upsell"]},
    tools=[("Chatbase", "Chatbot trained on docs/website", "Free tier; paid plans for more messages"), ("Tidio (Lyro AI)", "Live chat + AI agent", "Free tier; AI conversations limited"),
           ("Voiceflow", "Advanced flows & integrations", "Free tier"), ("Google Docs", "Knowledge document", "Free"), ("WhatsApp click-to-chat link", "Human handoff", "Free")],
    setup=[("Write the knowledge doc", ["Collect: About, products/services + prices, delivery/turnaround, payment methods, refund policy, opening hours, contact.",
            "Add the 30 most common customer questions with clear answers.", "Write in short paragraphs with headings. Bots answer better from clean text."]),
           ("Build the bot", ["Create a bot in your chosen tool → add the knowledge doc and your website URL as sources.",
            "Paste the System Prompt (next chapter) into the bot's instructions.", "Set the welcome message and 3 suggested questions (e.g. 'Delivery time?', 'Prices', 'Talk to a human').",
            "Enable lead capture: ask for name + WhatsApp/email only when the customer wants a quote or callback."]),
           ("Install & test", ["Copy the embed script → paste before </body> on your site (or use the WordPress/Shopify plugin).",
            "Ask 30 test questions, including tricky ones. Correct wrong answers by improving the knowledge doc.",
            "Add the handoff button: 'Chat on WhatsApp' → wa.me/92XXXXXXXXXX."])],
    prompts=[("Bot instructions", "You are the support assistant for [BUSINESS] on its website. Answer only from the provided knowledge. If unsure, say: 'Let me connect you with our team' and offer the WhatsApp button.\nBe warm, concise (max 3 sentences), and use bullet points for lists. Answer in the user's language (English or Roman Urdu).\nNever discuss competitors, never give medical/legal/financial advice, never promise discounts.\nWhen someone asks for a quote or callback, ask for their name and WhatsApp number."),
             ("FAQ generator", "Here is my website text and 50 customer messages: [PASTE]. Write 30 FAQ questions customers actually ask, with clear answers based only on this information. Mark missing info with [ADD]."),
             ("Gap finder", "Here are this week's chatbot conversations: [PASTE]. List questions the bot couldn't answer well, and draft knowledge-doc additions for each.")],
    auto_intro="Level 2 connects the chatbot to your tools so leads and tickets are never lost.",
    auto=[("Chatbot webhook / integration → New lead", "Fires when name + contact captured"), ("Google Sheets → Add row", "Leads sheet: date, name, contact, question, page"),
          ("Gmail / WhatsApp notification", "Alert the sales person instantly"), ("Weekly scheduler", "Export transcripts → AI 'Gap finder' prompt → email summary to owner")],
    auto_tips=["Show a clear notice that the visitor is chatting with an AI assistant and how to reach a human."],
    tests=["30 test questions answered correctly", "Unknown question → handoff offered", "Lead capture works and arrives in sheet",
           "Widget loads on mobile and doesn't cover checkout buttons", "Roman Urdu question handled", "Bot never quotes a price that isn't in the knowledge doc"],
    metrics=[("Resolution rate", "Questions answered without a human", "60–80%"), ("Leads captured / week", "Sales value", "Rising"),
             ("Handoffs", "Gaps in knowledge", "Falling month on month"), ("Wrong answers", "Trust", "Zero tolerance")],
    fixes=[("Bot gives outdated prices", "Update the knowledge doc and retrain; avoid putting prices in many places"), ("Bot too chatty", "Set max 3 sentences in instructions"),
           ("Widget slows the site", "Load the script with 'defer' or on user interaction")],
    sell_intro="Web developers and freelancers can add this to every website project as a premium upsell.",
    packages=[("Basic bot", "Knowledge doc + bot + install", "15,000–30,000", "$100–200"),
              ("Bot + leads", "Lead capture + Sheets + alerts + training", "35,000–60,000", "$250–400"),
              ("Monthly optimisation", "Review chats, update knowledge", "8,000–15,000 / month", "$50–100 / month")],
    pitch="\"Hi [Name], your website gets visitors at night when nobody is available to answer. I can add an AI assistant trained only on your services and policies. It answers common questions instantly and sends you hot leads on WhatsApp. Want to try a demo version on your site?\"",
)

W["ai-product-listing-generator"] = dict(
    what="Turn product photos and a few facts into **complete, SEO-ready listings for Daraz and Shopify** in minutes: clean images, keyword-rich titles, highlights, descriptions and specs, exported in bulk-upload format.",
    flow=[("Phone photos", "Shoot product on any background"), ("Photoroom / remove.bg", "White background + consistent size"),
          ("ChatGPT (with image upload)", "Reads the photo + your facts → title, bullets, description, specs"), ("Google Sheets", "Listing database"),
          ("Daraz Bulk Manager / Shopify CSV import", "Upload many products at once")],
    **{"for": ["Daraz and Shopify sellers with 20+ products", "Virtual assistants offering listing services", "Wholesalers moving online"]},
    tools=[("ChatGPT / Gemini / Claude (vision)", "Reads photos, writes listings", "Free tier or ~$20/month"), ("Photoroom or remove.bg", "Background removal", "Free tier; paid for bulk"),
           ("Google Sheets", "Listing database", "Free"), ("Daraz Seller Center (Bulk Manager)", "Bulk upload template", "Free for sellers"),
           ("Shopify", "Product CSV import", "Part of your Shopify plan")],
    setup=[("Photos", ["Shoot in daylight near a window: front, back, close-up, in-use, with a hand for scale.",
            "Batch-remove backgrounds → white, 1:1 square, product fills ~80% of frame.", "Name files SKU-1.jpg, SKU-2.jpg …"]),
           ("Facts sheet", ["For each product note: SKU · Product type · Material · Size/dimensions · Colours · Price · What's in the box · Target buyer.",
            "Search the product on Daraz; note the words in top listings' titles and the autocomplete suggestions."]),
           ("Generate listings", ["Upload 1–2 photos + paste the facts into the 'Listing writer' prompt.",
            "Paste the output into your Listings sheet with columns matching the platform template.",
            "Check every spec against the real product. Never let AI guess material or size."]),
           ("Bulk upload", ["Daraz: Seller Center → Products → Bulk Manager → download the category template → paste columns → upload.",
            "Shopify: Products → Import → use Shopify's sample CSV format (Handle, Title, Body (HTML), Vendor, Type, Tags, Variant Price, Image Src…).",
            "Upload 5 first, check how they look on mobile, then upload the rest."])],
    prompts=[("Listing writer", "You are an e-commerce copywriter for [PLATFORM: Daraz / Shopify] in Pakistan. Using the photo and these facts: [FACTS], write:\n1) Title (max [120] characters): Brand + product type + key feature + size/variant + use case, using words Pakistani buyers search.\n2) 5 highlight bullets, each starting with a benefit.\n3) Description (120–180 words): who it's for, how to use, materials, care, what's in the box.\n4) Specs table.\n5) 10 search keywords.\nDo not invent any fact not given; write [CHECK] where info is missing."),
             ("Variant naming", "Create clean variant names (colour/size) and SKU codes for: [LIST]. Format: SKU | Variant | Option1 | Option2."),
             ("Title A/B", "Give 3 alternative titles for this listing optimised for different search terms: [TITLE]"),
             ("Review miner", "Here are competitor reviews: [PASTE]. What do buyers praise and complain about? Add 2 bullets to my listing that answer the complaints honestly.")],
    auto_intro="Level 2: drop photos in a Drive folder and get listing drafts in your sheet automatically.",
    auto=[("Google Drive → Watch files", "New photo in /Listings/To-do (file name = SKU)"), ("Google Sheets → Search rows", "Get the facts for that SKU"),
          ("OpenAI (vision) → Analyze image + completion", "Listing writer prompt with photo + facts"), ("Google Sheets → Update row", "Fill Title, Bullets, Description, Keywords; Status = Review"),
          ("Google Drive → Move file", "Move photo to /Listings/Done")],
    auto_tips=["Keep 'Status = Review' until a human checks specs. Wrong specs are the #1 cause of returns and bad reviews."],
    tests=["Titles within platform character limits", "No invented materials/sizes", "Images 1:1, white background, ≥ 800 px", "Bulk file uploads with zero errors",
           "Listings checked on mobile app", "Keywords appear naturally (no stuffing)"],
    metrics=[("Time per listing", "Efficiency", "Under 5 minutes"), ("Search impressions", "SEO", "Rising after 2 weeks"),
             ("Click-to-order rate", "Listing quality", "Rising"), ("Returns due to 'not as described'", "Accuracy", "Near zero")],
    fixes=[("Bulk upload errors", "Use the exact template for your category; don't rename columns"), ("Titles too long", "State the platform's limit in the prompt"),
           ("Generic descriptions", "Give more facts and the target buyer; ask for one real use-case scenario")],
    sell_intro="Sellers with big catalogues hate writing listings. This is a fast, repeatable service.",
    packages=[("20 listings", "Photos edited + full listings + bulk file", "8,000–15,000", "$50–100"),
              ("100 listings", "Full catalogue + keyword research", "30,000–55,000", "$200–350"),
              ("Store launch", "Listings + store setup + banners", "45,000–80,000", "$300–500")],
    pitch="\"Hi [Name], I saw your store on Daraz. Your products are great, but some titles are missing the words buyers search for. I write SEO listings and edit product photos in bulk. Can I rewrite 3 of your listings for free so you can compare?\"",
)

W["ai-proposal-writer-system"] = dict(
    what="A personal AI proposal writer for Fiverr and Upwork, loaded with your profile, portfolio and best proposals, so you send **personalised, high-quality proposals in under 3 minutes** and track which ones win.",
    flow=[("Job post", "Copy the client's post"), ("Proposal Project (ChatGPT / Claude)", "Already knows your skills, samples, rates and winning style"),
          ("You", "Edit the first line, check facts, send manually"), ("Proposal tracker sheet", "Log job, connects, reply, hire"), ("Weekly review", "AI finds patterns in what wins")],
    **{"for": ["Upwork freelancers spending too long on proposals", "Fiverr sellers answering buyer requests and messages", "Agencies with several bidders"]},
    tools=[("ChatGPT Projects / Claude Projects / Gemini Gems", "Your proposal brain", "Free tier or ~$20/month"), ("Google Sheets", "Proposal tracker", "Free"),
           ("Google Docs", "Portfolio + case studies doc", "Free")],
    setup=[("Create your 'About me' pack", ["One doc with: your niche, services, 5 case studies (problem → what you did → result), tools, rates, availability, time zone (PKT, GMT+5).",
            "Add your 3 best-performing proposals (ones that got replies).", "List portfolio links with one line each on when to use them."]),
           ("Create the Proposal Project", ["New Project → paste the System Prompt → upload your About-me pack.",
            "Test with 5 old job posts; compare with what you actually sent."]),
           ("Daily routine", ["Filter jobs: payment verified, < 20 proposals, clear description, fits your niche.",
            "Paste job → get proposal → rewrite the first line yourself → check every claim → send.",
            "Log it in the tracker. Upwork does not allow bots to submit proposals; always send them yourself."])],
    prompts=[("System prompt", "You write proposals for me, a [ROLE] from Pakistan with [X] years' experience. Use ONLY the facts in my About-me pack; never invent clients, numbers or skills.\nFormat: Hook (1–2 lines about THEIR problem, quoting a detail from the post) → Proof (one relevant case study + link) → Plan (3 short numbered steps) → Question CTA.\nMax 150 words. Natural, confident, no clichés ('I am a hardworking…', 'Dear Sir'). Also suggest which portfolio link to attach and 2 questions to answer if the post has screening questions."),
             ("Job analyser", "Analyse this job post: [PASTE]. Give: client's real goal, red flags, budget fit for my rates ([RATE]), and whether I should apply (score 1–10)."),
             ("Fiverr buyer message", "A buyer messaged: [PASTE]. Reply in under 80 words: confirm understanding, ask 2 questions, suggest the right package or a custom offer."),
             ("Weekly review", "Here is my proposal tracker for the last 2 weeks: [PASTE]. Which job types, hooks and portfolio items got replies? What should I change?")],
    auto_intro="Level 2 speeds up research and logging. Sending stays manual to respect platform rules.",
    auto=[("Browser extension / form", "You paste a job link + text into a Google Form"), ("OpenAI → Create completion", "Job analyser + proposal draft"),
          ("Google Sheets → Add row", "Tracker row with draft, score and date"), ("Gmail → Send email to self", "Draft arrives on your phone for quick copy-paste")],
    auto_tips=["Never use tools that auto-submit proposals or scrape Upwork. They violate the terms of service and can get your account suspended."],
    tests=["5 old jobs → drafts better than what you sent", "No invented facts", "Under 150 words", "Correct portfolio suggested", "Tracker logs every proposal"],
    metrics=[("Reply rate", "Proposal quality", "10%+ (Upwork), rising"), ("Interview → hire", "Sales calls", "25%+"),
             ("Connects per hire", "Efficiency", "Falling"), ("Time per proposal", "Speed", "Under 3 minutes")],
    fixes=[("All proposals sound the same", "Write the first line yourself from a detail in the post"), ("Low replies", "Apply earlier (first hour) and to better-fit jobs; check the score"),
           ("Too long", "Set 120 words and ask for no bullet lists")],
    sell_intro="Agencies and busy freelancers will pay for a tuned proposal system.",
    packages=[("Profile + system", "Profile rewrite + Proposal Project + tracker", "10,000–20,000", "$60–120"),
              ("Agency setup", "Projects for 3 bidders + templates + training", "30,000–50,000", "$200–350"),
              ("Coaching", "Weekly proposal review for a month", "15,000–25,000", "$100–150")],
    pitch="\"Hi [Name], I help freelancers increase their Upwork reply rate with a personal AI proposal system trained on their own case studies, so every proposal is specific and fast. Want me to review your last 5 proposals for free?\"",
)

W["ai-invoice-order-automation"] = dict(
    what="An order-to-invoice system built entirely on free Google tools: orders come in through a Google Form (or your team fills it), an invoice PDF is generated from your branded template, emailed to the customer and saved to Drive, and everything is logged in Sheets. No more manual invoices.",
    flow=[("Google Form", "Order entered (customer or staff)"), ("Google Sheets", "Response row created"),
          ("Apps Script (included)", "Copies the Docs invoice template, fills it, saves PDF"), ("Gmail", "Invoice emailed to customer"), ("Sheets", "Invoice number written back on the row")],
    **{"for": ["Small businesses, wholesalers and freelancers sending invoices by hand", "Anyone who wants a free alternative to paid invoicing software", "Freelancers who can sell this setup to local businesses"]},
    tools=[("Google Forms + Sheets + Docs + Drive + Gmail", "The whole system", "Free with a Google account"),
           ("Apps Script", "The automation (code included)", "Free; Gmail free accounts can send about 100 emails/day by script"),
           ("ChatGPT / Claude (optional)", "Customising the script, writing email text", "Free tier")],
    setup=[("Create the form", ["Google Forms → new form with questions titled exactly: **Customer name**, **Email**, **Product**, **Quantity**, **Unit price**.",
            "Responses → Link to Sheets → create a new spreadsheet.", "In the sheet, add a header **Invoice No** in the first empty column after the form columns."]),
           ("Create the invoice template", ["Google Docs → design your invoice (logo, business name, address, bank/JazzCash details).",
            "Type these placeholders where values should go: ##INVOICE## ##DATE## ##NAME## ##ITEM## ##QTY## ##PRICE## ##TOTAL##",
            "Copy the template's ID from its URL (the long code between /d/ and /edit).", "Create a Drive folder 'Invoices' and copy its ID from the URL."]),
           ("Install the script", ["In the response sheet: Extensions → Apps Script → paste the code from the next chapter.",
            "Replace TEMPLATE_ID, FOLDER_ID and BUSINESS at the top. Save.",
            "Triggers (clock icon) → Add trigger → function onFormSubmit → event source: From spreadsheet → event type: On form submit → Save → allow permissions.",
            "Submit a test order with your own email. You should receive the PDF within a minute."])],
    prompts=[("Customise the script", "Here is my Google Apps Script for invoices: [PASTE]. Modify it to also [ADD 5% TAX / ADD DELIVERY CHARGE / SUPPORT 3 PRODUCTS PER ORDER / SEND A WHATSAPP LINK]. Explain each change and keep my placeholders."),
             ("Email text", "Write a short, professional invoice email for [BUSINESS] in English with one Roman Urdu line of thanks. Include payment methods: [ACCOUNTS] and a polite due date."),
             ("Debug helper", "My Apps Script shows this error: [ERROR] on line [N]. Here is the code: [PASTE]. What's wrong and what is the fix?")],
    code=("The Apps Script (copy exactly)", "Paste into Extensions → Apps Script. Lines starting with // are comments.", """
// Skillstack - Order to Invoice automation (Google Apps Script)
const TEMPLATE_ID = 'PASTE_YOUR_GOOGLE_DOC_TEMPLATE_ID';
const FOLDER_ID   = 'PASTE_YOUR_INVOICES_FOLDER_ID';
const BUSINESS    = 'Your Business Name';
const TZ          = 'Asia/Karachi';

function onFormSubmit(e) {
  const v = e.namedValues;
  const name  = v['Customer name'][0];
  const email = v['Email'][0];
  const item  = v['Product'][0];
  const qty   = Number(v['Quantity'][0]);
  const price = Number(v['Unit price'][0]);
  const total = qty * price;
  const now   = new Date();
  const invNo = 'INV-' + Utilities.formatDate(now, TZ, 'yyMMdd-HHmmss');

  // 1) Copy the template and fill the placeholders
  const folder = DriveApp.getFolderById(FOLDER_ID);
  const copy = DriveApp.getFileById(TEMPLATE_ID).makeCopy(invNo, folder);
  const doc = DocumentApp.openById(copy.getId());
  const body = doc.getBody();
  const values = {
    '##INVOICE##': invNo,
    '##DATE##': Utilities.formatDate(now, TZ, 'dd MMM yyyy'),
    '##NAME##': name,
    '##ITEM##': item,
    '##QTY##': String(qty),
    '##PRICE##': 'Rs ' + price.toLocaleString(),
    '##TOTAL##': 'Rs ' + total.toLocaleString()
  };
  Object.keys(values).forEach(function (k) { body.replaceText(k, values[k]); });
  doc.saveAndClose();

  // 2) Save as PDF and email it
  const pdf = copy.getAs(MimeType.PDF).setName(invNo + '.pdf');
  folder.createFile(pdf);
  GmailApp.sendEmail(email, 'Invoice ' + invNo + ' from ' + BUSINESS,
    'Dear ' + name + ',\\n\\nThank you for your order. Your invoice is attached.\\n' +
    'Total: Rs ' + total.toLocaleString() + '\\n\\nShukriya,\\n' + BUSINESS,
    { attachments: [pdf], name: BUSINESS });

  // 3) Write the invoice number next to the response
  const sheet = e.range.getSheet();
  sheet.getRange(e.range.getRow(), e.range.getLastColumn() + 1).setValue(invNo);
}
"""),
    auto_intro="The script above is already Level 2. Here is how to extend it with Make/n8n if you need WhatsApp or accounting tools.",
    auto=[("Google Sheets → Watch rows", "New row with Invoice No filled"), ("Google Drive → Search file", "Find [Invoice No].pdf"),
          ("WhatsApp Cloud API → Send template", "Approved 'invoice ready' template with PDF link (needs Meta template approval)"),
          ("Sheets → Update row", "Mark 'Sent on WhatsApp'"), ("Monthly scheduler + OpenAI", "Summarise month: revenue, top products, unpaid invoices")],
    auto_tips=["Keep the template's placeholders exactly the same as in the script, including the ## signs.",
               "Gmail sending limits apply to scripts (roughly 100/day on free Gmail, more on Google Workspace)."],
    tests=["Test order creates a Doc + PDF in the folder", "Email arrives with correct PDF", "Totals correct for quantity > 1",
           "Invoice No written in the right column", "Template placeholders all replaced", "Works when a second order comes in a minute later"],
    metrics=[("Time per invoice", "Efficiency", "0 minutes (automatic)"), ("Invoices with errors", "Accuracy", "Zero"),
             ("Days to payment", "Cash flow", "Falling"), ("Unpaid invoices", "Follow-up", "Reviewed weekly")],
    fixes=[("'Exception: Cannot read properties of undefined'", "A form question title doesn't match the script exactly (check spelling and capitals)"),
           ("No email received", "Check the trigger exists and permissions were allowed; look at Apps Script → Executions for errors"),
           ("Placeholder not replaced", "The text in the Doc must match exactly, with no extra spaces or formatting splits; retype it")],
    sell_intro="Many Pakistani SMEs still write invoices by hand or in Excel. A free, automatic system is an easy sell.",
    packages=[("Basic", "Form + branded template + script + training", "10,000–20,000", "$60–120"),
              ("Business", "Multi-product orders, tax/delivery, WhatsApp link, monthly report", "25,000–45,000", "$150–300"),
              ("Support", "Changes and fixes for 3 months", "5,000 / month", "$30 / month")],
    pitch="\"Hi [Name], I set up free automatic invoicing for small businesses using Google tools you already have. Each order creates a branded PDF invoice and emails it to the customer, so you never type an invoice again and there's no monthly software fee. Can I show you a 3-minute demo?\"",
)

W["ai-ad-creative-factory"] = dict(
    what="A repeatable system to produce **20+ Meta ad variations a week**: AI-generated angles and hooks, on-brand designs in Canva, and a simple testing structure that finds winners fast. In 2026 the creative does most of the targeting, so more good creatives means cheaper results.",
    flow=[("Customer research", "Reviews, DMs, comments → pains & desires"), ("ChatGPT / Claude", "Angles → hooks → primary texts"),
          ("Canva / AI image tools", "Statics, carousels, and simple video edits"), ("Meta Ads Manager", "Testing campaign: 3–6 ads per angle"),
          ("Weekly review", "Kill losers, iterate winners")],
    **{"for": ["Store owners running Meta ads", "Media buyers & freelancers managing ads", "Agencies needing creative volume"]},
    tools=[("ChatGPT / Claude", "Angles, hooks, copy", "Free or ~$20/month"), ("Canva", "Design templates", "Free or Pro"),
           ("Ideogram / Adobe Firefly", "AI images (incl. text in image)", "Free tiers"), ("CapCut", "Video ads, captions", "Free tier"),
           ("Meta Ads Library", "Competitor research", "Free"), ("Meta Ads Manager", "Testing", "Your ad budget")],
    setup=[("Research (once a month)", ["Collect 50 real customer phrases: reviews, DMs, comments ('delivery fast thi', 'size perfect').",
            "Search competitors in Meta Ads Library (country: Pakistan). Screenshot ads running 30+ days: these are likely profitable.",
            "Run the 'Angle finder' prompt with your research."]),
           ("Produce (weekly, ~2 hours)", ["Pick 3 angles. For each: 3 hooks × 2 formats (static + video/carousel) = 18 ads.",
            "Build 3 Canva templates (problem/solution, testimonial, offer). Duplicate and swap text and images.",
            "For video: product demo clips + captions in CapCut, hook text in first second.", "Name every ad: Angle_Hook_Format_Date (e.g. Price_Q1_Static_1118)."]),
           ("Test", ["Testing campaign: 1 ad set per angle, broad audience, 3–6 ads each, Rs 1,000–2,000/day.",
            "Wait 3 days. Kill ads with spend > 2× target CPA and zero results.", "Winners → duplicate into scaling campaign; make 3 new variations of each winner."])],
    prompts=[("Angle finder", "Here is research on my customers for [PRODUCT] (Rs [PRICE], Pakistan): [PASTE REVIEWS, DMs, COMPETITOR ADS].\nGive 8 distinct ad angles (problem, desire, objection, social proof, comparison, offer, identity, curiosity). For each: the core message, the customer phrase it uses, and the best format."),
             ("Hook batch", "For angle [ANGLE], write 10 hooks for the first line of the ad and 10 on-image headlines (max 6 words). Mix English and Roman Urdu. No income or health guarantees."),
             ("Primary text", "Write 3 primary texts (50–90 words) for this hook: [HOOK]. Structure: hook → benefit → proof → offer → CTA (order on WhatsApp / Shop now). Follow Meta advertising policies."),
             ("Image prompt", "Write a prompt for an AI image tool to create a clean product ad image: [PRODUCT] on [BACKGROUND], bold headline '[HEADLINE]' at top, lots of empty space, 4:5 ratio, photographic, natural light."),
             ("Weekly review", "Here are this week's ad results: [PASTE name, spend, CTR, CPC, results, CPA]. Which angles and hooks win? Suggest 6 new variations of the top 2 ads.")],
    auto_intro="Level 2: one sheet row per ad idea becomes copy + image drafts automatically, ready for you to finish in Canva.",
    auto=[("Google Sheets → Watch rows", "New row: Product · Angle · Format"), ("OpenAI → Create completion", "Hooks + primary texts + image prompt"),
          ("OpenAI / Ideogram API → Generate image", "Draft visual (optional)"), ("Google Drive → Upload", "Save image drafts by ad name"),
          ("Sheets → Update row", "Status = Ready for design review")],
    auto_tips=["Use AI images for backgrounds and concepts; use real product photos for the product itself. Buyers trust what's real, and misleading product images cause returns."],
    tests=["Each ad named with the convention", "No policy-risky claims (guarantees, before/after, personal attributes)", "Text readable on a phone",
           "Hook visible in first second (video)", "Correct price and offer", "Landing page / WhatsApp link works"],
    metrics=[("Hook rate (3s views / impressions)", "Video hook strength", "25%+"), ("Link CTR", "Creative relevance", "1%+"),
             ("Cost per result", "Profitability", "Below break-even"), ("Winners per 20 ads", "Research quality", "2–4")],
    fixes=[("All ads have similar results", "Your angles are too similar. Test truly different messages"), ("High CTR, no sales", "Fix landing page, price clarity or offer"),
           ("Ad rejected", "Remove claims, read the policy reason, edit, request review once")],
    sell_intro="Brands always need fresh creatives. Creative packages are easier to sell than full ad management.",
    packages=[("Creative pack", "12 static + 3 video ads with copy", "15,000–30,000", "$100–200"),
              ("Monthly creative", "40 ads/month + testing report", "45,000–90,000 / month", "$300–600 / month"),
              ("Research sprint", "Customer & competitor research + 8 angles", "10,000–20,000", "$60–150")],
    pitch="\"Hi [Name], I noticed you're running the same 2 ads for a while. Ads usually get more expensive once people have seen them a few times. I make fresh ad creatives every week from your customers' own words, plus a simple report on what's winning. Can I make 3 free test ads for [BRAND]?\"",
)

W["ai-voice-notes-to-tasks"] = dict(
    what="Turn voice notes, meetings and WhatsApp audio into **clear tasks, summaries and follow-up messages** automatically. For busy owners and freelancers who think out loud and lose track of what they promised.",
    flow=[("Phone voice note / WhatsApp audio / meeting recording", "Capture ideas and calls"), ("Transcription (ChatGPT voice, Whisper, TurboScribe, Google Recorder)", "Speech → text (English, Urdu, mixed)"),
          ("ChatGPT / Claude", "Text → tasks, deadlines, summary, reply drafts"), ("Google Tasks / Notion / Trello", "Tasks land in your to-do system"), ("Daily review", "5-minute morning plan")],
    **{"for": ["Business owners managing teams on WhatsApp", "Freelancers with many client calls", "Students recording lectures"]},
    tools=[("ChatGPT app (voice)", "Record + transcribe + organise in one place", "Free tier"), ("TurboScribe / Whisper", "Long recordings", "Free tier / free (open source)"),
           ("Google Recorder (Pixel) / phone recorder", "Capture", "Free"), ("Notion / Google Tasks / Trello", "Task system", "Free tiers"),
           ("Make.com", "Automation (Level 2)", "Free tier"), ("OpenAI API", "Transcription + organisation in automation", "Low cost per minute of audio")],
    setup=[("Capture habit", ["One place for voice notes: a WhatsApp chat with yourself, or your phone recorder.",
            "Start each note with a label: 'Client Ahmed', 'Shop', 'Idea'. It makes sorting easy.", "For meetings: ask permission to record, then record on your phone."]),
           ("Process (10 minutes/day)", ["Export/share the audio to ChatGPT (or transcribe with TurboScribe for long files).",
            "Run the 'Tasks extractor' prompt on the transcript.", "Copy tasks into Google Tasks/Notion with due dates. Send the follow-up messages drafted by AI after checking them."]),
           ("Weekly review", ["Friday: paste the week's summaries into the 'Weekly review' prompt.", "Move unfinished tasks; archive done ones; note promises made to clients."])],
    prompts=[("Tasks extractor", "Here is a transcript of my voice note/meeting (it may mix English, Urdu and Roman Urdu): [PASTE].\nGive me:\n1) 3-line summary\n2) Tasks table: Task | Owner | Due date (convert phrases like 'kal' or 'next Monday' using today = [DATE]) | Priority\n3) Decisions made\n4) Open questions\n5) Draft follow-up WhatsApp message to [PERSON] (Roman Urdu, under 60 words)."),
             ("Meeting minutes", "Turn this meeting transcript into professional minutes: attendees, agenda points, decisions, action items with owners and dates. [PASTE]"),
             ("Idea organiser", "These are my random voice-note ideas from this week: [PASTE]. Group them into themes, remove duplicates, and rank the top 3 by impact vs effort."),
             ("Weekly review", "Here are this week's summaries and task lists: [PASTE]. What did I complete, what's overdue, what promises did I make to clients, and what are my top 5 priorities next week?")],
    auto_intro="Level 2: save audio to a Drive folder from your phone and tasks appear in Notion automatically.",
    auto=[("Google Drive → Watch files", "New audio in /VoiceNotes"), ("OpenAI → Create transcription", "Speech-to-text (supports Urdu and English)"),
          ("OpenAI → Create completion", "Tasks extractor prompt; return JSON"), ("Iterator", "Loop over tasks"),
          ("Notion → Create database item", "Task, owner, due date, priority, link to audio"), ("Gmail → Send email", "Summary + follow-up drafts to yourself")],
    auto_tips=["Recordings of other people: tell them you record meetings and why. Don't record private calls without consent.",
               "Ask the AI to return JSON with fixed keys so the automation never breaks."],
    tests=["Mixed Urdu/English note transcribed accurately enough", "'Kal' and 'next week' converted to real dates", "Tasks have owners",
           "Duplicate notes don't create duplicate tasks", "Follow-up drafts checked before sending"],
    metrics=[("Tasks captured / week", "Nothing forgotten", "All voice notes processed"), ("Overdue tasks", "Follow-through", "Falling"),
             ("Time to follow up after calls", "Professionalism", "Same day"), ("Minutes spent organising", "Efficiency", "Under 10/day")],
    fixes=[("Poor Urdu transcription", "Speak closer to the mic; try another transcriber; ask AI to fix obvious errors using context"),
           ("Dates wrong", "Always include today's date in the prompt"), ("Too many tiny tasks", "Ask the AI to merge related tasks and keep max 7")],
    sell_intro="Executives, doctors, lawyers and business owners pay for personal productivity systems.",
    packages=[("Personal setup", "Capture habit + prompts + Notion board + training", "8,000–15,000", "$50–100"),
              ("Automated", "Drive → transcription → Notion automation", "20,000–35,000", "$120–250"),
              ("Team version", "Meeting minutes + task assignment for a team", "35,000–60,000", "$250–400")],
    pitch="\"Hi [Name], you probably send and receive dozens of voice notes a day. I set up a simple system that turns voice notes and meetings into a clean task list with due dates and draft follow-ups, so nothing slips. Want to try it on one of your meeting recordings?\"",
)

ORDER = ["ai-whatsapp-sales-assistant", "ai-content-calendar-machine", "ai-faceless-reels-factory", "ai-lead-gen-outreach-system",
         "ai-website-support-chatbot", "ai-product-listing-generator", "ai-proposal-writer-system", "ai-invoice-order-automation",
         "ai-ad-creative-factory", "ai-voice-notes-to-tasks"]

CONTENT = {k: render(v) for k, v in W.items()}
