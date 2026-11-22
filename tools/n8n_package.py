"""Package the Skillstack AI Workflows: n8n JSONs + Google Sheets template + chat widget + Apps Script + README."""
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(__file__))
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
import n8n_workflows

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WF = os.path.join(ROOT, "ai-workflows")

TABS = {
    "Knowledge": (["Type", "Item", "Details", "Price (Rs)"],
                  [["Product", "Lawn suit 3-piece", "Sizes S–XL · 2 colours · cotton", 3500], ["Policy", "Delivery", "2–4 working days all over Pakistan · Rs 200 (free above Rs 5,000)", ""],
                   ["Policy", "Payment", "COD, JazzCash, Easypaisa, bank transfer", ""], ["FAQ", "Exchange", "7-day exchange if unused with tags", ""]]),
    "Chats": (["Time", "Phone", "Name", "Customer message", "AI reply", "Needs human", "Order confirmed", "Order summary"], []),
    "Content Calendar": (["Day", "Date", "Pillar", "Format", "Headline", "Subtext", "Highlight", "CTA", "Caption", "Hashtags", "Reel idea", "Status"], []),
    "Reels": (["ID", "Topic", "Status", "Hook", "Script", "On-screen text", "Caption", "Hashtags", "Voice file"],
              [["R1", "3 free AI tools every student should use", "Ready"], ["R2", "How to get paid as a freelancer in Pakistan", "Ready"]]),
    "Leads": (["ID", "Business", "Website", "Email", "Notes", "Status", "Personal line", "Subject", "Follow-up day 3", "Follow-up day 7", "Follow-up 1 date", "Follow-up 2 date"],
              [["L1", "Example Cafe", "example.com", "hello@example.com", "No Reels posted in 30 days", "New"]]),
    "FAQ": (["Question", "Answer"], [["How long is delivery?", "2–4 working days all over Pakistan."], ["How can I pay?", "JazzCash, Easypaisa, bank transfer or Cash on Delivery."]]),
    "Chatbot Leads": (["Time", "Name", "Phone", "Email", "Last message"], []),
    "Products": (["SKU", "Product type", "Brand", "Material", "Size", "Colours", "Price (Rs)", "Photo URL", "Status", "Title", "Highlights", "Description", "Specs", "Keywords"],
                 [["SKU-001", "Kitchen organiser rack", "GharPlus", "Stainless steel", "3-tier, 40×25×60 cm", "Silver", 2499, "https://", "To-do"]]),
    "About Me": (["Section", "Item", "Details"],
                 [["Profile", "Role", "Shopify developer, 4 years, Pakistan (GMT+5)"], ["Case study", "Store speed", "Cut a skincare store's load time from 6s to 1.8s; conversion +22%"],
                  ["Rates", "Hourly", "$25/hour; fixed projects from $150"], ["Portfolio", "Speed case study link", "https://"]]),
    "Proposal Tracker": (["Date", "Platform", "Score", "Client goal", "Red flags", "Proposal", "Portfolio to attach", "Screening answers", "Job post", "Reply", "Hired"], []),
    "Invoices": (["Invoice No", "Date", "Customer", "Email", "Phone", "Item", "Qty", "Unit price", "Delivery", "Total", "Payment method", "Status"], []),
    "Ad Ideas": (["Date", "Product", "Ad name", "Angle", "Core message", "Format", "Hook 1", "Hook 2", "Hook 3", "Image headline", "Primary text", "Image prompt", "Status"], []),
}

USED_BY = {"Knowledge": "26", "Chats": "26", "Content Calendar": "27", "Reels": "28", "Leads": "29", "FAQ": "30", "Chatbot Leads": "30",
           "Products": "31", "About Me": "32", "Proposal Tracker": "32", "Invoices": "33", "Ad Ideas": "34"}


def sheets_template(path):
    wb = Workbook()
    st = wb.active
    st.title = "README"
    st["A1"] = "Skillstack AI Workflows — Google Sheets template"
    st["A1"].font = Font(bold=True, size=16, color="5B2EFF")
    lines = ["1. Upload this file to Google Drive → right-click → Open with Google Sheets (File → Save as Google Sheets).",
             "2. Keep the tab names and the header row exactly as they are (the workflows use these names).",
             "3. Replace the sample rows with your own data. In n8n, pick this sheet + the right tab in each Google Sheets node.", "",
             "Tab → used by workflow"] + [f"   {t}  →  workflow {n}" for t, n in USED_BY.items()]
    for i, l in enumerate(lines, 3):
        st.cell(row=i, column=1, value=l)
    st.column_dimensions["A"].width = 110
    for tab, (cols, rows) in TABS.items():
        ws = wb.create_sheet(tab)
        for j, c in enumerate(cols, 1):
            cell = ws.cell(row=1, column=j, value=c)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="111018")
            cell.alignment = Alignment(vertical="center")
            ws.column_dimensions[cell.column_letter].width = max(14, min(40, len(c) + 6))
        for i, r in enumerate(rows, 2):
            for j, v in enumerate(r, 1):
                ws.cell(row=i, column=j, value=v)
        ws.freeze_panes = "A2"
    wb.save(path)


WIDGET = """<!-- Skillstack AI chat widget — paste before </body> on your website.
     1) In n8n open workflow 30, click the "Chat message (webhook)" node, copy the PRODUCTION URL and paste it below.
     2) Activate the workflow. -->
<script>
(function () {
  var WEBHOOK_URL = "PASTE_N8N_PRODUCTION_WEBHOOK_URL_HERE";
  var COLOR = "#5B2EFF", TITLE = "Ask us anything", HELLO = "Assalam o Alaikum! 👋 How can we help you today?";
  var css = "#skc-btn{position:fixed;right:20px;bottom:20px;width:58px;height:58px;border-radius:50%;background:" + COLOR + ";color:#fff;border:0;font-size:26px;cursor:pointer;box-shadow:0 10px 30px rgba(0,0,0,.25);z-index:99998}" +
    "#skc-box{position:fixed;right:20px;bottom:90px;width:340px;max-width:calc(100vw - 40px);height:460px;max-height:70vh;background:#fff;border-radius:18px;box-shadow:0 20px 60px rgba(0,0,0,.25);display:none;flex-direction:column;overflow:hidden;z-index:99999;font-family:system-ui,sans-serif}" +
    "#skc-box.open{display:flex}#skc-head{background:" + COLOR + ";color:#fff;padding:14px 16px;font-weight:700}#skc-log{flex:1;overflow:auto;padding:12px;background:#f7f7f9}" +
    ".skc-m{max-width:82%;padding:9px 12px;border-radius:14px;margin:6px 0;font-size:14px;line-height:1.4;white-space:pre-wrap}.skc-u{background:" + COLOR + ";color:#fff;margin-left:auto}.skc-a{background:#fff;border:1px solid #eee}" +
    ".skc-wa{display:inline-block;margin-top:6px;background:#25D366;color:#06210F;padding:6px 10px;border-radius:99px;text-decoration:none;font-weight:700;font-size:13px}" +
    "#skc-form{display:flex;border-top:1px solid #eee}#skc-in{flex:1;border:0;padding:12px;font-size:14px;outline:none}#skc-send{border:0;background:#fff;color:" + COLOR + ";font-weight:700;padding:0 14px;cursor:pointer}";
  var s = document.createElement("style"); s.textContent = css; document.head.appendChild(s);
  var btn = document.createElement("button"); btn.id = "skc-btn"; btn.setAttribute("aria-label", "Chat"); btn.textContent = "💬";
  var box = document.createElement("div"); box.id = "skc-box";
  box.innerHTML = '<div id="skc-head">' + TITLE + '</div><div id="skc-log"></div><form id="skc-form"><input id="skc-in" placeholder="Type your question…" autocomplete="off"><button id="skc-send">Send</button></form>';
  document.body.appendChild(btn); document.body.appendChild(box);
  var log = box.querySelector("#skc-log"), input = box.querySelector("#skc-in"), history = [];
  var sid = "s" + Math.random().toString(36).slice(2);
  function add(text, who, wa) {
    var d = document.createElement("div"); d.className = "skc-m " + (who === "u" ? "skc-u" : "skc-a"); d.textContent = text;
    if (wa) { var a = document.createElement("a"); a.href = wa; a.target = "_blank"; a.className = "skc-wa"; a.textContent = "Chat on WhatsApp"; d.appendChild(document.createElement("br")); d.appendChild(a); }
    log.appendChild(d); log.scrollTop = log.scrollHeight;
  }
  btn.onclick = function () { box.classList.toggle("open"); if (!log.children.length) add(HELLO, "a"); input.focus(); };
  box.querySelector("#skc-form").onsubmit = function (e) {
    e.preventDefault(); var msg = input.value.trim(); if (!msg) return; input.value = ""; add(msg, "u");
    var typing = document.createElement("div"); typing.className = "skc-m skc-a"; typing.textContent = "…"; log.appendChild(typing);
    fetch(WEBHOOK_URL, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ message: msg, history: history, sessionId: sid }) })
      .then(function (r) { return r.json(); })
      .then(function (d) { typing.remove(); add(d.reply || "Sorry, please try again.", "a", d.whatsapp); history.push({ role: "user", content: msg }, { role: "assistant", content: d.reply || "" }); history = history.slice(-8); })
      .catch(function () { typing.remove(); add("Sorry, something went wrong. Please try again.", "a"); });
  };
})();
</script>
"""

README = """# Skillstack AI Workflows (No. 26–35)

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
"""


def main():
    n8n_workflows.build()
    sheets_template(os.path.join(WF, "Skillstack-AI-Workflows-Sheets.xlsx"))
    with open(os.path.join(WF, "30-chat-widget.html"), "w", encoding="utf-8") as f:
        f.write(WIDGET)
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "content"))
    from content.workflows import W
    title, intro, gs = W["ai-invoice-order-automation"]["code"]
    steps = W["ai-invoice-order-automation"]["setup"]
    head = "// OPTIONAL: PDF invoices with Google Forms + Docs + Gmail (alternative to n8n workflow 33)\n// SETUP\n" + "\n".join(
        f"//  {t}: " + " | ".join(re.sub(r"\*\*", "", x) for x in s) for t, s in steps) + "\n\n"
    with open(os.path.join(WF, "33-invoice-apps-script.gs"), "w", encoding="utf-8") as f:
        f.write(head + gs.strip() + "\n")
    with open(os.path.join(WF, "README.md"), "w", encoding="utf-8") as f:
        f.write(README)
    prev = os.path.join(ROOT, "ai-workflows", "previews")
    os.makedirs(prev, exist_ok=True)
    print("packaged", sorted(os.listdir(WF)))


if __name__ == "__main__":
    main()
