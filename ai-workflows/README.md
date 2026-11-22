# Skillstack AI Workflows (No. 26–35)

**10 ready-to-import n8n automations.** Har file n8n mein *Import from File* karte hi poora workflow ban jati hai: nodes, AI prompts, connections aur andar setup notes.

## Folder mein kya hai
| File | Kya hai |
|---|---|
| `26 … 35 *.json` | 10 n8n workflows (import karne wali files) |
| `Skillstack-AI-Workflows-Sheets.xlsx` | Google Sheets template: har workflow ke liye tab, sahi columns + sample rows |
| `30-chat-widget.html` | Website chatbot ka widget (workflow 30 ke sath) |
| `33-invoice-apps-script.gs` | Optional: PDF invoices banane wala Google Apps Script (workflow 33 ka alternative) |
| `previews/` | Har workflow ki n8n screenshot |

## 10 workflows
| # | Workflow | Kya karta hai | Kya chahiye |
|---|---|---|---|
| 26 | AI WhatsApp Sales Assistant | WhatsApp par har message ka AI jawab (sirf aap ki product sheet se), chat log, human handoff email | WhatsApp Cloud API, OpenAI, Sheets, Gmail |
| 27 | AI Content Calendar Machine | Form bharein → 30 din ke posts (hooks, captions, hashtags, Reel ideas) sheet mein | OpenAI, Sheets |
| 28 | AI Faceless Reels Factory | Topic → script + hook + caption → ElevenLabs voiceover MP3 Drive mein | OpenAI, ElevenLabs, Drive, Sheets |
| 29 | AI Lead Gen & Outreach | Lead ki website parh kar personal email + 2 follow-ups → Gmail draft | OpenAI, Sheets, Gmail |
| 30 | AI Website Support Chatbot | Website chat jo FAQ se jawab de, leads sheet mein save kare, WhatsApp handoff | OpenAI, Sheets (+ widget) |
| 31 | AI Product Listing Generator | Photo + facts → Daraz/Shopify SEO title, highlights, description, specs | OpenAI, Sheets |
| 32 | AI Proposal Writer | Job post form → fit score, red flags, proposal (sirf aap ke facts se) → email + tracker | OpenAI, Sheets, Gmail |
| 33 | Invoice & Order Automation | Order form → invoice number, total, branded HTML invoice email → Invoices sheet | Gmail, Sheets |
| 34 | AI Ad Creative Factory | Product + customer words → 6 ad angles (hooks, headline, primary text, image prompt) | OpenAI, Sheets (+ Drive optional) |
| 35 | AI Voice Notes → Tasks | Drive folder mein voice note → transcription (Urdu/English) → Google Tasks + summary email | OpenAI, Drive, Google Tasks, Gmail |

## Setup (har workflow ke liye ek dafa)
1. **n8n account:** n8n.io par cloud account banayein, ya apne server par self-host karein. Yeh files n8n 2.x mein import test ki gayi hain.
2. **Sheet template:** `Skillstack-AI-Workflows-Sheets.xlsx` ko Google Drive par upload karein → *Open with Google Sheets* → *File → Save as Google Sheets*. Tabs ke naam aur pehli row (headers) na badlein.
3. **Import:** n8n → *Workflows* → **⋯ → Import from File** → `.json` file chunein.
4. **Settings node:** har workflow mein pehla **Settings** node kholein, aur apna business name, email aur baqi values likhein.
5. **Credentials** (jin nodes par ⚠️ ho, unhein khol kar *Create new credential*):
   - **OpenAI:** platform.openai.com → API keys → nayi key → n8n mein *OpenAI* credential (HTTP Request nodes isi ko use karte hain).
   - **Google Sheets / Gmail / Drive / Tasks:** *Sign in with Google* (n8n cloud par ek click; self-hosted par Google Cloud OAuth client chahiye, n8n docs dekhein).
   - **WhatsApp (26):** Meta Business → WhatsApp → Cloud API. *WhatsApp Trigger* ke liye App ID + Secret, *Send* ke liye access token. Number WhatsApp app par active nahi hona chahiye.
   - **ElevenLabs (28):** *Header Auth* credential: Name `xi-api-key`, Value = aap ki ElevenLabs API key.
6. **Sheet chunein:** har Google Sheets node mein *Document* = apni sheet, *Sheet* = sahi tab (node par tab ka naam likha hai).
7. **Test:** *Execute workflow* dabayein (form wale workflows mein form khulega). Sab theek ho to upar **Publish / Active** on karein.

## Har workflow ke khaas notes
- **26:** pehle *shadow mode* mein chalayein: *Send WhatsApp reply* node ko deactivate kar ke kuch din `Chats` tab mein AI ke jawab parhein. Theek lagein to on karein. Customer ne 24 ghante se message na kiya ho to WhatsApp sirf approved template messages allow karta hai.
- **27:** sheet ke Headline / Subtext / CTA columns Canva **Bulk Create** se connect karke 30 designs ek sath banayein.
- **28:** Settings mein `elevenLabsVoiceId` daalein. *Save MP3 to Drive* mein folder chunein. Editing CapCut mein khud karein; poori tarah auto-generated videos ki reach kam hoti hai.
- **29:** emails khud **review kar ke send** karein (Gmail Drafts). Roz 10–20 se zyada na bhejein. Sirf public business contacts use karein.
- **30:** workflow **Active** karein → *Chat message (webhook)* node se **Production URL** copy karein → `30-chat-widget.html` mein `WEBHOOK_URL` ki jagah paste karein → widget ka code website ke `</body>` se pehle lagayein.
- **31:** Photo URL public hona chahiye (Google Drive link ko "Anyone with link" share karein, ya website image link). Specs hamesha asal product se check karein.
- **32:** `About Me` tab mein sirf **sach** likhein. AI sirf wahi facts use karta hai. Proposal khud bhejein; bots se Upwork/Fiverr par bhejna mana hai.
- **33:** Settings mein payment details aur brand color badlein. PDF invoice chahiye to `33-invoice-apps-script.gs` use karein (instructions file ke andar).
- **34:** grey (disabled) nodes enable karein to har angle ki draft image bhi ban jati hai (OpenAI image model + Drive node add karein).
- **35:** phone se voice note Google Drive ke **VoiceNotes** folder mein save karein. Trigger har minute check karta hai.

## Kharcha (andaza)
n8n cloud ka plan, ya self-hosting ka server. OpenAI API pay-as-you-go: ek AI jawab aam taur par chand paisay se kuch rupay tak. ElevenLabs ka free tier shuru ke liye kaafi hai. WhatsApp Cloud API: Meta ki Pakistan wali rates (customer ki taraf se shuru hui chat ke andar jawab aam taur par sasta/free). Asal prices har service ki website par check karein.

## Masle
| Masla | Hal |
|---|---|
| Google Sheets node: "column not found" | Tab ki pehli row ke headers template jaise hi rakhein (spelling / spaces) |
| Update node kuch update nahi karta | Row mein `ID` (28, 29) ya `SKU` (31) column bhara hona chahiye |
| OpenAI: 401 / 429 | API key ghalat hai, ya OpenAI account mein balance nahi |
| AI "not valid JSON" | Settings mein model ko kisi naye OpenAI chat model par set karein |
| WhatsApp jawab nahi jata | Phone Number ID / access token check karein; template rules (24 ghante) |
| Chat widget kaam nahi karta | Workflow Active hai? Widget mein **Production** URL (test URL nahi) hai? |
