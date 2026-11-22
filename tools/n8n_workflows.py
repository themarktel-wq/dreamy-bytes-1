"""Build the 10 Skillstack AI Workflows as importable n8n workflow files (+ Google Sheets template).

Output: ai-workflows/  (n8n JSON files, sheet template, README)
Validate with: node <n8n-validator> ai-workflows/*.json
"""
import json
import os
import uuid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "ai-workflows")

SHEET = {"__rl": True, "mode": "list", "value": ""}  # pick your sheet from the list after importing
OPENAI_URL = "https://api.openai.com/v1/chat/completions"

SETTINGS_JS = """// ⚙️ SETTINGS — edit these values once.
const config = {
  model: 'gpt-4.1-mini',            // any current OpenAI chat model
  businessName: 'Your Business',
  ownerEmail: 'you@example.com',     // where alerts / summaries are sent
__EXTRA__};
return $input.all().map(item => ({ json: { ...item.json, config }, pairedItem: item.pairedItem }));"""

PARSE_AI_JS = """// Turns the AI's JSON answer into normal fields.
return $input.all().map((item, i) => {
  let ai = {};
  try { ai = JSON.parse(item.json.choices[0].message.content); }
  catch (e) { ai = { error: 'AI response was not valid JSON', raw: item.json }; }
  return { json: ai, pairedItem: { item: i } };
});"""


class WF:
    def __init__(self, name):
        self.name, self.nodes, self.conn, self.x = name, [], {}, 0

    def add(self, name, typ, ver, params, pos, **extra):
        n = {"parameters": params, "id": str(uuid.uuid4()), "name": name, "type": "n8n-nodes-base." + typ, "typeVersion": ver, "position": pos}
        n.update(extra)
        self.nodes.append(n)
        return name

    def link(self, a, b, out=0):
        self.conn.setdefault(a, {"main": []})
        while len(self.conn[a]["main"]) <= out:
            self.conn[a]["main"].append([])
        self.conn[a]["main"][out].append({"node": b, "type": "main", "index": 0})

    def chain(self, *names):
        for a, b in zip(names, names[1:]):
            self.link(a, b)

    def note(self, text, pos, w=420, h=300, color=5):
        self.nodes.append({"parameters": {"content": text, "height": h, "width": w, "color": color}, "id": str(uuid.uuid4()),
                           "name": f"Note {sum(1 for n in self.nodes if n['type'].endswith('stickyNote')) + 1}",
                           "type": "n8n-nodes-base.stickyNote", "typeVersion": 1, "position": pos})

    def dump(self, fname, tags):
        wf = {"name": self.name, "nodes": self.nodes, "connections": self.conn, "active": False,
              "settings": {"executionOrder": "v1", "timezone": "Asia/Karachi"}, "pinData": {},
              "meta": {"templateCredsSetupCompleted": False}, "tags": []}
        with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
            json.dump(wf, f, indent=2, ensure_ascii=False)


# ---------- node helpers ----------
def code(w, name, js, pos, each=False):
    p = {"jsCode": js}
    if each:
        p = {"mode": "runOnceForEachItem", "jsCode": js}
    return w.add(name, "code", 2, p, pos)


def settings(w, pos, extra=""):
    return code(w, "Settings", SETTINGS_JS.replace("__EXTRA__", extra), pos)


def openai(w, name, pos):
    """HTTP Request to OpenAI chat completions. The previous Code node builds $json.body."""
    return w.add(name, "httpRequest", 4.2, {
        "method": "POST", "url": OPENAI_URL, "authentication": "predefinedCredentialType", "nodeCredentialType": "openAiApi",
        "sendBody": True, "specifyBody": "json", "jsonBody": "={{ JSON.stringify($json.body) }}", "options": {"timeout": 120000}}, pos)


def sheet_read(w, name, tab, pos, once=True):
    extra = {"executeOnce": True} if once else {}
    return w.add(name, "googleSheets", 4.5, {"documentId": SHEET, "sheetName": {"__rl": True, "mode": "name", "value": tab}, "options": {}}, pos,
                 alwaysOutputData=True, **extra)


def sheet_append(w, name, tab, pos):
    return w.add(name, "googleSheets", 4.5, {"operation": "append", "documentId": SHEET, "sheetName": {"__rl": True, "mode": "name", "value": tab},
                                              "columns": {"mappingMode": "autoMapInputData", "value": {}, "matchingColumns": [], "schema": []}, "options": {}}, pos)


def sheet_update(w, name, tab, key, pos):
    return w.add(name, "googleSheets", 4.5, {"operation": "update", "documentId": SHEET, "sheetName": {"__rl": True, "mode": "name", "value": tab},
                                              "columns": {"mappingMode": "autoMapInputData", "value": {}, "matchingColumns": [key], "schema": []}, "options": {}}, pos)


def gmail_send(w, name, to, subject, message, pos, html=False):
    p = {"sendTo": to, "subject": subject, "message": message, "options": {"appendAttribution": False}}
    if not html:
        p["emailType"] = "text"
    return w.add(name, "gmail", 2.1, p, pos)


def form(w, name, title, desc, fields, pos, path):
    ff = []
    for f in fields:
        d = {"fieldLabel": f[0]}
        if len(f) > 1 and f[1]:
            d["fieldType"] = f[1]
        if len(f) > 2:
            d.update(f[2])
        ff.append(d)
    return w.add(name, "formTrigger", 2.2, {"formTitle": title, "formDescription": desc, "formFields": {"values": ff}, "options": {"path": path}}, pos,
                 webhookId=str(uuid.uuid4()))


def if_true(w, name, left, pos):
    return w.add(name, "if", 2.2, {"conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose", "version": 2},
                                                  "conditions": [{"id": str(uuid.uuid4()), "leftValue": left, "rightValue": "",
                                                                  "operator": {"type": "boolean", "operation": "true", "singleValue": True}}],
                                                  "combinator": "and"}, "options": {}}, pos)


def manual(w, pos):
    return w.add("Run manually", "manualTrigger", 1, {}, pos)


def schedule(w, name, hour, pos, every_hours=None):
    if every_hours:
        rule = {"interval": [{"field": "hours", "hoursInterval": every_hours}]}
    else:
        rule = {"interval": [{"triggerAtHour": hour}]}
    return w.add(name, "scheduleTrigger", 1.2, {"rule": rule}, pos)


COMMON_NOTE = ("**Setup (once)**\n1. Import this file: n8n → *Workflows* → *⋯* → **Import from File**.\n"
               "2. Open **Settings** and fill in your details.\n3. Connect credentials on the nodes with a ⚠️ (OpenAI, Google Sheets, Gmail…).\n"
               "4. In every Google Sheets node pick your sheet + tab (template: *Skillstack-AI-Workflows-Sheets.xlsx*).\n5. **Test workflow**, then switch **Active** on.")


def build():
    os.makedirs(OUT, exist_ok=True)
    built = []

    # ===== 26 WhatsApp AI Sales Assistant =====
    w = WF("Skillstack 26 · AI WhatsApp Sales Assistant")
    w.note("## 🤖 AI WhatsApp Sales Assistant\nReplies to every WhatsApp message in seconds using ONLY your product sheet (no invented prices), "
           "logs every chat, and emails you when a human is needed.\n\n**Needs:** WhatsApp Business Cloud API (Meta), OpenAI key, Google Sheets, Gmail.\n"
           "**Sheet tabs:** `Knowledge`, `Chats`.\n\n" + COMMON_NOTE, [-80, -460], 560, 420, 4)
    w.add("WhatsApp message received", "whatsAppTrigger", 1, {"updates": ["messages"], "options": {}}, [0, 0], webhookId=str(uuid.uuid4()))
    code(w, "Get text message", """// Keep only real text messages from customers (skip delivery/read receipts).
const out = [];
for (const item of $input.all()) {
  const v = item.json;
  const msg = (v.messages || [])[0];
  if (!msg || msg.type !== 'text') continue;
  const contact = (v.contacts || [])[0] || {};
  out.push({ json: { from: msg.from, name: (contact.profile || {}).name || '', text: msg.text.body,
                     phoneNumberId: (v.metadata || {}).phone_number_id, time: new Date().toISOString() } });
}
return out;""", [240, 0])
    settings(w, [480, 0], "  // WhatsApp phone number ID is read from the incoming message automatically.\n")
    sheet_read(w, "Load knowledge", "Knowledge", [720, 0])
    sheet_read(w, "Load chat history", "Chats", [960, 0])
    code(w, "Build AI request", """// Builds the prompt from your Knowledge tab + this customer's last messages.
const cfg = $('Settings').first().json.config;
const knowledge = $('Load knowledge').all().map(i => i.json).filter(r => Object.keys(r).length)
  .map(r => `- ${r.Type || ''}: ${r.Item || ''} | ${r.Details || ''} | ${r['Price (Rs)'] ? 'Rs ' + r['Price (Rs)'] : ''}`).join('\\n');
const history = $('Load chat history').all().map(i => i.json);
return $('Settings').all().map((item, i) => {
  const c = item.json;
  const past = history.filter(h => String(h.Phone) === String(c.from)).slice(-8)
    .flatMap(h => [{ role: 'user', content: String(h['Customer message'] || '') }, { role: 'assistant', content: String(h['AI reply'] || '') }]);
  const system = `You are the WhatsApp sales assistant for ${cfg.businessName} in Pakistan.
Use ONLY this knowledge (products, prices, policies, FAQs):
${knowledge}
Rules: never invent prices, stock or delivery dates; if the answer is not in the knowledge, say a team member will confirm.
Reply in the customer's language (English, Roman Urdu or Urdu), under 60 words, friendly, max 1 emoji, end with one clear next step.
To take an order collect: name, full address with city, phone, item + variant + quantity, then show a summary with total and ask them to reply YES.
If the customer is angry, asks for a refund, reports a problem, or asks for a human, set needs_human true.
Return JSON: {"reply": string, "needs_human": boolean, "order_confirmed": boolean, "order_summary": string}`;
  return { json: { ...c, body: { model: cfg.model, response_format: { type: 'json_object' }, temperature: 0.4,
    messages: [{ role: 'system', content: system }, ...past, { role: 'user', content: c.text }] } }, pairedItem: { item: i } };
});""", [1200, 0])
    openai(w, "AI writes reply", [1440, 0])
    code(w, "Read AI reply", """// Combine the AI answer with the customer details.
return $input.all().map((item, i) => {
  const c = $('Build AI request').all()[i].json;
  let ai = {};
  try { ai = JSON.parse(item.json.choices[0].message.content); } catch (e) { ai = { reply: 'Thank you! A team member will reply shortly.', needs_human: true }; }
  return { json: { to: c.from, name: c.name, phoneNumberId: c.phoneNumberId, text: c.text, reply: ai.reply,
                   needs_human: !!ai.needs_human, order_confirmed: !!ai.order_confirmed, order_summary: ai.order_summary || '' }, pairedItem: { item: i } };
});""", [1680, 0])
    w.add("Send WhatsApp reply", "whatsApp", 1, {"operation": "send", "phoneNumberId": "={{ $json.phoneNumberId }}",
                                                 "recipientPhoneNumber": "={{ $json.to }}", "textBody": "={{ $json.reply }}", "additionalFields": {}}, [1920, -160])
    code(w, "Prepare chat log", """return $('Read AI reply').all().map((item, i) => ({ json: {
  Time: new Date().toLocaleString('en-PK', { timeZone: 'Asia/Karachi' }), Phone: item.json.to, Name: item.json.name,
  'Customer message': item.json.text, 'AI reply': item.json.reply, 'Needs human': item.json.needs_human ? 'YES' : '',
  'Order confirmed': item.json.order_confirmed ? 'YES' : '', 'Order summary': item.json.order_summary }, pairedItem: { item: i } }));""", [1920, 20])
    sheet_append(w, "Log chat", "Chats", [2160, 20])
    if_true(w, "Needs a human?", "={{ $json.needs_human }}", [1920, 200])
    gmail_send(w, "Alert owner", "={{ $('Settings').first().json.config.ownerEmail }}", "=⚠️ WhatsApp chat needs you: {{ $json.name || $json.to }}",
               "=Customer: {{ $json.name }} ({{ $json.to }})\nMessage: {{ $json.text }}\nAI replied: {{ $json.reply }}\n\nOpen WhatsApp Business to take over.", [2160, 200])
    w.chain("WhatsApp message received", "Get text message", "Settings", "Load knowledge", "Load chat history", "Build AI request", "AI writes reply", "Read AI reply")
    for t in ("Send WhatsApp reply", "Prepare chat log", "Needs a human?"):
        w.link("Read AI reply", t)
    w.link("Prepare chat log", "Log chat")
    w.link("Needs a human?", "Alert owner")
    w.note("**Tip:** run in *shadow mode* first: disable **Send WhatsApp reply** (right-click → Deactivate) for a few days and read the `Chats` tab. "
           "Switch it on when replies are consistently right.", [1880, -420], 380, 200, 6)
    w.dump("26-ai-whatsapp-sales-assistant.json", ["whatsapp"]); built.append(w.name)

    # ===== 27 Content Calendar Machine =====
    w = WF("Skillstack 27 · AI Content Calendar Machine")
    w.note("## 🗓️ AI Content Calendar Machine\nFill a short form → AI plans **30 days of posts** (pillars, hooks, captions, hashtags, Reel ideas) → rows land in your `Content Calendar` tab, "
           "ready for Canva **Bulk Create** (Headline / Subtext / CTA columns).\n\n**Needs:** OpenAI, Google Sheets.\n\n" + COMMON_NOTE, [-80, -460], 560, 400, 4)
    form(w, "Content brief form", "30-day content plan", "Tell the AI about your brand. The plan appears in your Google Sheet in about a minute.",
         [("Brand name", None, {"requiredField": True}), ("What you sell", None, {"requiredField": True}), ("City / country", None, {"placeholder": "Lahore, Pakistan"}),
          ("Target audience", "textarea", {"requiredField": True}), ("Occasions this month", None, {"placeholder": "e.g. 11.11 sale, winter launch"}),
          ("Tone", "dropdown", {"fieldOptions": {"values": [{"option": "Friendly & fun"}, {"option": "Premium & elegant"}, {"option": "Bold & energetic"}, {"option": "Professional"}]}}),
          ("Language mix", "dropdown", {"fieldOptions": {"values": [{"option": "English + Roman Urdu"}, {"option": "English only"}, {"option": "Roman Urdu"}]}})],
         [0, 0], "content-plan")
    settings(w, [240, 0])
    code(w, "Build AI request", """const f = $json; const cfg = f.config;
const prompt = `Create a 30-day social media plan for ${f['Brand name']}, which sells ${f['What you sell']} in ${f['City / country'] || 'Pakistan'}.
Audience: ${f['Target audience']}. Occasions: ${f['Occasions this month'] || 'none'}. Tone: ${f['Tone']}. Language: ${f['Language mix']}.
Pillar mix: Teach 35%, Relate 25%, Prove 20%, Sell 20%. Formats: static, carousel, Reel. No made-up statistics, no income claims.
Return JSON {"posts":[{"day":1,"pillar":"","format":"","headline":"max 8 words","subtext":"max 15 words","highlight":"1-3 words from headline","cta":"","caption":"40-80 words, hook first line","hashtags":"4 hashtags","reel_idea":"one line"}]} with exactly 30 posts.`;
return { json: { body: { model: cfg.model, response_format: { type: 'json_object' }, temperature: 0.8,
  messages: [{ role: 'system', content: 'You are an expert social media strategist for Pakistani small businesses.' }, { role: 'user', content: prompt }] } } };""", [480, 0], each=True)
    openai(w, "AI plans the month", [720, 0])
    code(w, "One row per post", """let posts = [];
try { posts = JSON.parse($json.choices[0].message.content).posts || []; } catch (e) {}
const start = new Date();
return posts.map((p, i) => {
  const d = new Date(start); d.setDate(d.getDate() + i);
  return { json: { Day: p.day || i + 1, Date: d.toISOString().slice(0, 10), Pillar: p.pillar, Format: p.format, Headline: p.headline,
    Subtext: p.subtext, Highlight: p.highlight, CTA: p.cta, Caption: p.caption, Hashtags: p.hashtags, 'Reel idea': p.reel_idea, Status: 'Draft' } };
});""", [960, 0])
    sheet_append(w, "Save to Content Calendar", "Content Calendar", [1200, 0])
    w.chain("Content brief form", "Settings", "Build AI request", "AI plans the month", "One row per post", "Save to Content Calendar")
    w.note("**Next:** Canva → Apps → **Bulk Create** → upload the sheet (CSV) → connect Headline / Subtext / CTA to your template → generate 30 designs.", [900, 200], 420, 160, 6)
    w.dump("27-ai-content-calendar-machine.json", []); built.append(w.name)

    # ===== 28 Faceless Reels Factory =====
    w = WF("Skillstack 28 · AI Faceless Reels Factory")
    w.note("## 🎬 AI Faceless Reels Factory\nAdd topics to the `Reels` tab with Status **Ready** → every hour the AI writes a 30-second script, hook & caption, "
           "ElevenLabs creates the voiceover, the MP3 is saved to Google Drive and the row is updated. You just edit in CapCut.\n\n"
           "**Needs:** OpenAI, ElevenLabs (Header Auth credential: name `xi-api-key`, value = your key), Google Drive, Google Sheets.\n\n" + COMMON_NOTE, [-80, -480], 600, 440, 4)
    schedule(w, "Every hour", 0, [0, -100], every_hours=1)
    manual(w, [0, 100])
    settings(w, [240, 0], "  niche: 'AI tools for students in Pakistan',\n  elevenLabsVoiceId: 'PASTE_VOICE_ID',  // ElevenLabs → Voices → copy ID\n  maxPerRun: 5,\n")
    sheet_read(w, "Read Reels tab", "Reels", [480, 0])
    code(w, "Pick Ready topics", """const cfg = $('Settings').first().json.config;
return $input.all().filter(i => String(i.json.Status || '').trim().toLowerCase() === 'ready' && i.json.Topic).slice(0, cfg.maxPerRun)
  .map(i => ({ json: { ID: i.json.ID, Topic: i.json.Topic, body: { model: cfg.model, response_format: { type: 'json_object' }, temperature: 0.8,
    messages: [{ role: 'system', content: `You write faceless short-video scripts for a ${cfg.niche} page. Simple English with light Roman Urdu. No made-up statistics; mark facts to check with [VERIFY].` },
      { role: 'user', content: `Topic: ${i.json.Topic}. Return JSON {"hook":"under 8 words","script":"25-35 seconds spoken, short lines","on_screen_text":"one line per script line, separated by |","caption":"max 40 words with CTA","hashtags":"4 hashtags"}` }] } } }));""", [720, 0])
    openai(w, "AI writes script", [960, 0])
    code(w, "Read script", """return $input.all().map((item, i) => {
  const src = $('Pick Ready topics').all()[i].json; let ai = {};
  try { ai = JSON.parse(item.json.choices[0].message.content); } catch (e) {}
  return { json: { ID: src.ID, Topic: src.Topic, ...ai, voiceText: `${ai.hook || ''}. ${ai.script || ''}` }, pairedItem: { item: i } };
});""", [1200, 0])
    w.add("ElevenLabs voiceover", "httpRequest", 4.2, {
        "method": "POST", "url": "=https://api.elevenlabs.io/v1/text-to-speech/{{ $('Settings').first().json.config.elevenLabsVoiceId }}",
        "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "sendBody": True, "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify({ text: $json.voiceText, model_id: 'eleven_multilingual_v2' }) }}",
        "options": {"response": {"response": {"responseFormat": "file"}}}}, [1440, 0])
    w.add("Save MP3 to Drive", "googleDrive", 3, {"name": "={{ $('Read script').item.json.ID }} - {{ $('Read script').item.json.Topic }}.mp3",
                                                  "driveId": {"__rl": True, "mode": "list", "value": "My Drive"},
                                                  "folderId": {"__rl": True, "mode": "list", "value": ""}, "options": {}}, [1680, 0])
    code(w, "Row update", """return $input.all().map((item, i) => {
  const s = $('Read script').all()[i].json;
  return { json: { ID: s.ID, Hook: s.hook, Script: s.script, 'On-screen text': s.on_screen_text, Caption: s.caption, Hashtags: s.hashtags,
    'Voice file': item.json.webViewLink || item.json.id, Status: 'Voice ready' }, pairedItem: { item: i } };
});""", [1920, 0])
    sheet_update(w, "Update Reels tab", "Reels", "ID", [2160, 0])
    w.link("Every hour", "Settings"); w.link("Run manually", "Settings")
    w.chain("Settings", "Read Reels tab", "Pick Ready topics", "AI writes script", "Read script", "ElevenLabs voiceover", "Save MP3 to Drive", "Row update", "Update Reels tab")
    w.dump("28-ai-faceless-reels-factory.json", []); built.append(w.name)

    # ===== 29 Lead Gen & Outreach =====
    w = WF("Skillstack 29 · AI Lead Gen & Outreach System")
    w.note("## 🎯 AI Lead Gen & Outreach\nAdd businesses to the `Leads` tab (Status **New**, with Website) → the workflow reads each website, writes a **personal first line**, "
           "a short cold email + 2 follow-ups, and saves a **Gmail draft** for you to review and send. Nothing is sent automatically.\n\n"
           "**Needs:** OpenAI, Google Sheets, Gmail.\n\n" + COMMON_NOTE, [-80, -480], 600, 420, 4)
    schedule(w, "Every morning", 10, [0, -100])
    manual(w, [0, 100])
    settings(w, [240, 0], "  myService: 'Instagram Reels editing for restaurants',\n  myResult: 'helped a Lahore cafe grow reach 3x in 2 months',  // a REAL result\n  myName: 'Your Name',\n  maxPerRun: 15,\n")
    sheet_read(w, "Read Leads tab", "Leads", [480, 0])
    code(w, "Pick new leads", """const cfg = $('Settings').first().json.config;
return $input.all().filter(i => String(i.json.Status || '').trim().toLowerCase() === 'new' && i.json.Website).slice(0, cfg.maxPerRun)
  .map(i => ({ json: i.json }));""", [720, 0])
    w.add("Fetch website", "httpRequest", 4.2, {"url": "={{ $json.Website.startsWith('http') ? $json.Website : 'https://' + $json.Website }}",
                                                 "options": {"response": {"response": {"responseFormat": "text"}}, "timeout": 15000}}, [960, 0],
          onError="continueRegularOutput")
    code(w, "Build AI request", """const cfg = $('Settings').first().json.config;
const lead = $('Pick new leads').item.json;
const html = String($json.data || '');
const text = html.replace(/<script[\\s\\S]*?<\\/script>|<style[\\s\\S]*?<\\/style>/gi, ' ').replace(/<[^>]+>/g, ' ').replace(/\\s+/g, ' ').slice(0, 3500);
return { json: { lead, body: { model: cfg.model, response_format: { type: 'json_object' }, temperature: 0.6, messages: [
  { role: 'system', content: 'You write short, honest, personalised B2B cold emails. No flattery cliches, no fake claims.' },
  { role: 'user', content: `Business: ${lead.Business}. Notes: ${lead.Notes || ''}. Website text: ${text || '(not available)'}
My service: ${cfg.myService}. My real result: ${cfg.myResult}. Sign as ${cfg.myName}.
Return JSON {"personal_line":"one specific sentence max 25 words","subject":"under 6 words","email":"under 90 words: personal line, opportunity, my result, low-pressure CTA, opt-out line","followup_day3":"under 50 words","followup_day7":"under 50 words"}` }] } } };""", [1200, 0], each=True)
    openai(w, "AI writes outreach", [1440, 0])
    code(w, "Read outreach", """return $input.all().map((item, i) => {
  const lead = $('Build AI request').all()[i].json.lead; let ai = {};
  try { ai = JSON.parse(item.json.choices[0].message.content); } catch (e) {}
  return { json: { ...lead, ai }, pairedItem: { item: i } };
});""", [1680, 0])
    w.add("Create Gmail draft", "gmail", 2.1, {"resource": "draft", "subject": "={{ $json.ai.subject }}", "message": "={{ $json.ai.email }}",
                                                "options": {"sendTo": "={{ $json.Email }}"}}, [1920, 0])
    code(w, "Row update", """const fmt = d => d.toISOString().slice(0, 10);
return $('Read outreach').all().map((item, i) => {
  const l = item.json; const d3 = new Date(); d3.setDate(d3.getDate() + 3); const d7 = new Date(); d7.setDate(d7.getDate() + 7);
  return { json: { ID: l.ID, 'Personal line': l.ai.personal_line, Subject: l.ai.subject, 'Follow-up day 3': l.ai.followup_day3,
    'Follow-up day 7': l.ai.followup_day7, 'Follow-up 1 date': fmt(d3), 'Follow-up 2 date': fmt(d7), Status: 'Draft ready' }, pairedItem: { item: i } };
});""", [2160, 0])
    sheet_update(w, "Update Leads tab", "Leads", "ID", [2400, 0])
    w.link("Every morning", "Settings"); w.link("Run manually", "Settings")
    w.chain("Settings", "Read Leads tab", "Pick new leads", "Fetch website", "Build AI request", "AI writes outreach", "Read outreach", "Create Gmail draft", "Row update", "Update Leads tab")
    w.note("Only collect **publicly listed business** contacts. Send 10–20 emails a day from your own Gmail, and never bulk-message on WhatsApp (numbers get banned).", [1840, 200], 420, 150, 3)
    w.dump("29-ai-lead-gen-outreach-system.json", []); built.append(w.name)

    # ===== 30 Website Support Chatbot =====
    w = WF("Skillstack 30 · AI Website Support Chatbot")
    w.note("## 💬 AI Website Support Chatbot\nA chat API for your website: answers from your `FAQ` tab only, captures leads (name + WhatsApp/email) into `Chatbot Leads`, "
           "and offers WhatsApp handoff.\n\nPaste **chat-widget.html** (in this folder) into your website and put this workflow's **Production URL** in it.\n\n"
           "**Needs:** OpenAI, Google Sheets.\n\n" + COMMON_NOTE, [-80, -480], 600, 440, 4)
    w.add("Chat message (webhook)", "webhook", 2, {"httpMethod": "POST", "path": "skillstack-chat", "responseMode": "responseNode", "options": {"allowedOrigins": "*"}},
          [0, 0], webhookId=str(uuid.uuid4()))
    settings(w, [240, 0], "  whatsappNumber: '923000000000',  // for the 'talk to a human' link\n")
    sheet_read(w, "Load FAQ", "FAQ", [480, 0])
    code(w, "Build AI request", """const s = $('Settings').first().json; const cfg = s.config; const body = s.body || {};
const faq = $('Load FAQ').all().map(i => i.json).filter(r => r.Question).map(r => `Q: ${r.Question}\\nA: ${r.Answer}`).join('\\n');
const history = Array.isArray(body.history) ? body.history.slice(-8) : [];
return [{ json: { sessionId: body.sessionId || '', message: String(body.message || '').slice(0, 1000), body: { model: cfg.model, response_format: { type: 'json_object' }, temperature: 0.3,
  messages: [{ role: 'system', content: `You are the website assistant for ${cfg.businessName}. Answer ONLY from this FAQ:\\n${faq}\\n
If unsure, say you'll connect them with the team on WhatsApp. Max 3 short sentences. Reply in the user's language.
If the user shares a name and phone/email or asks for a quote/callback, fill "lead". Return JSON {"reply":"", "show_whatsapp": boolean, "lead": {"name":"","phone":"","email":""} or null}` },
    ...history, { role: 'user', content: String(body.message || '') }] } } }];""", [720, 0])
    openai(w, "AI answers", [960, 0])
    code(w, "Read answer", """const cfg = $('Settings').first().json.config; const src = $('Build AI request').first().json; let ai = {};
try { ai = JSON.parse($input.first().json.choices[0].message.content); } catch (e) { ai = { reply: 'Sorry, something went wrong. Please message us on WhatsApp.', show_whatsapp: true }; }
const lead = ai.lead && (ai.lead.phone || ai.lead.email) ? ai.lead : null;
return [{ json: { reply: ai.reply, whatsapp: ai.show_whatsapp ? `https://wa.me/${cfg.whatsappNumber}` : null, hasLead: !!lead,
  lead: lead ? { Time: new Date().toLocaleString('en-PK', { timeZone: 'Asia/Karachi' }), Name: lead.name || '', Phone: lead.phone || '', Email: lead.email || '', 'Last message': src.message } : null } }];""", [1200, 0])
    w.add("Reply to website", "respondToWebhook", 1.1, {"respondWith": "json", "responseBody": "={{ JSON.stringify({ reply: $json.reply, whatsapp: $json.whatsapp }) }}",
                                                        "options": {"responseHeaders": {"entries": [{"name": "Access-Control-Allow-Origin", "value": "*"}]}}}, [1440, -100])
    if_true(w, "Lead shared?", "={{ $json.hasLead }}", [1440, 120])
    code(w, "Lead row", "return [{ json: $json.lead }];", [1680, 120])
    sheet_append(w, "Save lead", "Chatbot Leads", [1920, 120])
    w.chain("Chat message (webhook)", "Settings", "Load FAQ", "Build AI request", "AI answers", "Read answer")
    w.link("Read answer", "Reply to website"); w.link("Read answer", "Lead shared?")
    w.link("Lead shared?", "Lead row"); w.link("Lead row", "Save lead")
    w.dump("30-ai-website-support-chatbot.json", []); built.append(w.name)

    # ===== 31 Product Listing Generator =====
    w = WF("Skillstack 31 · AI Product Listing Generator")
    w.note("## 🛍️ AI Product Listing Generator (Daraz / Shopify)\nAdd products to the `Products` tab (SKU, facts, public **Photo URL**, Status **To-do**) → AI looks at the photo "
           "and writes an SEO title, 5 highlights, description, specs and keywords → row updated to **Review**.\n\n**Needs:** OpenAI (vision model), Google Sheets.\n\n" + COMMON_NOTE,
           [-80, -460], 600, 420, 4)
    manual(w, [0, 0])
    settings(w, [240, 0], "  platform: 'Daraz',  // or 'Shopify'\n  titleMaxChars: 120,\n  maxPerRun: 20,\n")
    sheet_read(w, "Read Products tab", "Products", [480, 0])
    code(w, "Pick To-do products", """const cfg = $('Settings').first().json.config;
return $input.all().filter(i => String(i.json.Status || '').trim().toLowerCase() === 'to-do' && i.json.SKU).slice(0, cfg.maxPerRun).map(i => {
  const p = i.json; const content = [{ type: 'text', text: `Facts: ${JSON.stringify(p)}.
Write a ${cfg.platform} listing for Pakistani buyers. Title max ${cfg.titleMaxChars} characters (brand + product type + key feature + size/variant + use case).
Do NOT invent materials, sizes or claims not in the facts or clearly visible in the photo; write [CHECK] where unsure.
Return JSON {"title":"","highlights":["5 bullets"],"description":"120-180 words","specs":"key: value; key: value","keywords":"10 comma-separated"}` }];
  if (p['Photo URL']) content.push({ type: 'image_url', image_url: { url: p['Photo URL'] } });
  return { json: { SKU: p.SKU, body: { model: cfg.model, response_format: { type: 'json_object' }, temperature: 0.4,
    messages: [{ role: 'system', content: 'You are an e-commerce copywriter for Pakistani marketplaces.' }, { role: 'user', content }] } } };
});""", [720, 0])
    openai(w, "AI writes listing", [960, 0])
    code(w, "Row update", """return $input.all().map((item, i) => {
  const sku = $('Pick To-do products').all()[i].json.SKU; let ai = {};
  try { ai = JSON.parse(item.json.choices[0].message.content); } catch (e) {}
  return { json: { SKU: sku, Title: ai.title, Highlights: (ai.highlights || []).map(h => '• ' + h).join('\\n'), Description: ai.description,
    Specs: ai.specs, Keywords: ai.keywords, Status: 'Review' }, pairedItem: { item: i } };
});""", [1200, 0])
    sheet_update(w, "Update Products tab", "Products", "SKU", [1440, 0])
    w.chain("Run manually", "Settings", "Read Products tab", "Pick To-do products", "AI writes listing", "Row update", "Update Products tab")
    w.note("**Bulk upload:** copy the reviewed columns into the Daraz Bulk Manager template or Shopify product CSV. Always check specs against the real product.", [1100, 200], 400, 150, 6)
    w.dump("31-ai-product-listing-generator.json", []); built.append(w.name)

    # ===== 32 Proposal Writer =====
    w = WF("Skillstack 32 · AI Proposal Writer System")
    w.note("## ✍️ AI Proposal Writer (Upwork / Fiverr)\nPaste a job post into the form → AI scores the job, flags red flags and writes a proposal using ONLY your `About Me` tab "
           "(skills, case studies, rates) → emailed to you + logged in `Proposal Tracker`. You send it yourself (platform-safe).\n\n**Needs:** OpenAI, Google Sheets, Gmail.\n\n" + COMMON_NOTE,
           [-80, -460], 600, 420, 4)
    form(w, "Job post form", "Write my proposal", "Paste the job post. Your proposal arrives by email in under a minute.",
         [("Platform", "dropdown", {"fieldOptions": {"values": [{"option": "Upwork"}, {"option": "Fiverr"}, {"option": "LinkedIn / direct"}]}}),
          ("Job post", "textarea", {"requiredField": True}), ("Client budget", None, {}), ("My extra notes", "textarea", {})], [0, 0], "proposal")
    settings(w, [240, 0], "  maxWords: 150,\n")
    sheet_read(w, "Load About Me", "About Me", [480, 0])
    code(w, "Build AI request", """const s = $('Settings').first().json; const cfg = s.config;
const me = $('Load About Me').all().map(i => i.json).filter(r => r.Item).map(r => `- ${r.Section}: ${r.Item} — ${r.Details || ''}`).join('\\n');
return [{ json: { job: s['Job post'], platform: s.Platform, body: { model: cfg.model, response_format: { type: 'json_object' }, temperature: 0.6, messages: [
  { role: 'system', content: `You write freelance proposals. Use ONLY these facts about me, never invent clients, numbers or skills:\\n${me}` },
  { role: 'user', content: `Platform: ${s.Platform}. Budget: ${s['Client budget'] || 'n/a'}. Notes: ${s['My extra notes'] || ''}.\\nJob post:\\n${s['Job post']}
Return JSON {"score":1-10,"client_goal":"","red_flags":"","proposal":"max ${cfg.maxWords} words: hook about THEIR problem quoting a detail, one relevant proof, 3-step plan, question CTA","portfolio_to_attach":"","screening_answers":""}` }] } } }];""", [720, 0])
    openai(w, "AI writes proposal", [960, 0])
    code(w, "Read proposal", """let ai = {}; try { ai = JSON.parse($json.choices[0].message.content); } catch (e) {}
const src = $('Build AI request').first().json;
return [{ json: { Date: new Date().toISOString().slice(0, 10), Platform: src.platform, Score: ai.score, 'Client goal': ai.client_goal, 'Red flags': ai.red_flags,
  Proposal: ai.proposal, 'Portfolio to attach': ai.portfolio_to_attach, 'Screening answers': ai.screening_answers, 'Job post': String(src.job).slice(0, 1500),
  Reply: '', Hired: '' } }];""", [1200, 0])
    sheet_append(w, "Log in tracker", "Proposal Tracker", [1440, -100])
    gmail_send(w, "Email me the proposal", "={{ $('Settings').first().json.config.ownerEmail }}", "=Proposal ready ({{ $json.Platform }}) · fit {{ $json.Score }}/10",
               "=FIT SCORE: {{ $json.Score }}/10\nRED FLAGS: {{ $json['Red flags'] }}\nATTACH: {{ $json['Portfolio to attach'] }}\n\n--- PROPOSAL ---\n{{ $json.Proposal }}\n\n--- SCREENING ---\n{{ $json['Screening answers'] }}",
               [1440, 100])
    w.chain("Job post form", "Settings", "Load About Me", "Build AI request", "AI writes proposal", "Read proposal")
    w.link("Read proposal", "Log in tracker"); w.link("Read proposal", "Email me the proposal")
    w.dump("32-ai-proposal-writer-system.json", []); built.append(w.name)

    # ===== 33 Invoice & Order Automation =====
    w = WF("Skillstack 33 · AI Invoice & Order Automation")
    w.note("## 🧾 Invoice & Order Automation\nOrder form → invoice number + totals calculated → a branded **HTML invoice email** goes to the customer → order logged in `Invoices`.\n\n"
           "Edit your logo text, colours and payment accounts in **Settings**. (A Google Apps Script version that creates PDF invoices is also included in this folder.)\n\n"
           "**Needs:** Gmail, Google Sheets.\n\n" + COMMON_NOTE, [-80, -480], 600, 440, 4)
    form(w, "Order form", "New order / invoice", "Fill this for every order. The customer receives the invoice by email instantly.",
         [("Customer name", None, {"requiredField": True}), ("Customer email", "email", {"requiredField": True}), ("Customer phone", None, {}),
          ("Product / service", None, {"requiredField": True}), ("Quantity", "number", {"requiredField": True}), ("Unit price (Rs)", "number", {"requiredField": True}),
          ("Delivery charge (Rs)", "number", {}), ("Payment method", "dropdown", {"fieldOptions": {"values": [{"option": "JazzCash"}, {"option": "Easypaisa"}, {"option": "Bank transfer"}, {"option": "Cash on Delivery"}]}})],
         [0, 0], "new-invoice")
    settings(w, [240, 0], "  brandColor: '#5B2EFF',\n  paymentDetails: 'JazzCash 0300-0000000 (Account Title) · Bank IBAN PK00XXXX',\n  businessAddress: 'City, Pakistan',\n")
    code(w, "Calculate & design invoice", """const f = $json; const cfg = f.config;
const qty = Number(f['Quantity'] || 1), price = Number(f['Unit price (Rs)'] || 0), delivery = Number(f['Delivery charge (Rs)'] || 0);
const subtotal = qty * price, total = subtotal + delivery;
const now = new Date(); const pad = n => String(n).padStart(2, '0');
const invoiceNo = `INV-${String(now.getFullYear()).slice(2)}${pad(now.getMonth() + 1)}${pad(now.getDate())}-${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`;
const rs = n => 'Rs ' + Number(n).toLocaleString('en-PK');
const esc = s => String(s || '').replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
const html = `<div style="font-family:Arial,sans-serif;max-width:560px;margin:auto;border:1px solid #eee;border-radius:12px;overflow:hidden">
<div style="background:${cfg.brandColor};color:#fff;padding:20px 24px"><h2 style="margin:0">${esc(cfg.businessName)}</h2><div style="opacity:.85">${esc(cfg.businessAddress)}</div></div>
<div style="padding:24px"><p><b>Invoice:</b> ${invoiceNo}<br><b>Date:</b> ${now.toLocaleDateString('en-PK', { timeZone: 'Asia/Karachi' })}<br><b>Bill to:</b> ${esc(f['Customer name'])}</p>
<table style="width:100%;border-collapse:collapse"><tr style="background:#f4f4f6"><th align="left" style="padding:8px">Item</th><th style="padding:8px">Qty</th><th align="right" style="padding:8px">Price</th><th align="right" style="padding:8px">Amount</th></tr>
<tr><td style="padding:8px">${esc(f['Product / service'])}</td><td align="center">${qty}</td><td align="right">${rs(price)}</td><td align="right">${rs(subtotal)}</td></tr>
${delivery ? `<tr><td style="padding:8px">Delivery</td><td></td><td></td><td align="right">${rs(delivery)}</td></tr>` : ''}
<tr><td colspan="3" align="right" style="padding:8px"><b>Total</b></td><td align="right" style="padding:8px"><b>${rs(total)}</b></td></tr></table>
<p><b>Payment method:</b> ${esc(f['Payment method'])}<br><b>Pay to:</b> ${esc(cfg.paymentDetails)}</p><p>Shukriya for your order! 💚</p></div></div>`;
return { json: { invoiceNo, html, email: f['Customer email'], name: f['Customer name'], row: { 'Invoice No': invoiceNo, Date: now.toISOString().slice(0, 10),
  Customer: f['Customer name'], Email: f['Customer email'], Phone: f['Customer phone'] || '', Item: f['Product / service'], Qty: qty, 'Unit price': price,
  Delivery: delivery, Total: total, 'Payment method': f['Payment method'], Status: 'Unpaid' } } };""", [480, 0], each=True)
    gmail_send(w, "Email invoice to customer", "={{ $json.email }}", "=Invoice {{ $json.invoiceNo }} from {{ $('Settings').first().json.config.businessName }}",
               "={{ $json.html }}", [720, -100], html=True)
    code(w, "Invoice row", "return $('Calculate & design invoice').all().map((i, n) => ({ json: i.json.row, pairedItem: { item: n } }));", [720, 100])
    sheet_append(w, "Log in Invoices", "Invoices", [960, 100])
    w.chain("Order form", "Settings", "Calculate & design invoice")
    w.link("Calculate & design invoice", "Email invoice to customer"); w.link("Calculate & design invoice", "Invoice row"); w.link("Invoice row", "Log in Invoices")
    w.dump("33-ai-invoice-order-automation.json", []); built.append(w.name)

    # ===== 34 Ad Creative Factory =====
    w = WF("Skillstack 34 · AI Ad Creative Factory")
    w.note("## 📣 AI Ad Creative Factory\nForm with your product + real customer words → AI creates **6 ad angles**, each with 3 hooks, an on-image headline, primary text and an image prompt → saved to `Ad Ideas`.\n\n"
           "Optional: enable the two grey nodes to also generate draft images to Google Drive.\n\n**Needs:** OpenAI, Google Sheets (+ Google Drive for images).\n\n" + COMMON_NOTE, [-80, -480], 600, 440, 4)
    form(w, "Ad brief form", "Generate ad angles", "The more real customer words you paste, the better the ads.",
         [("Product", None, {"requiredField": True}), ("Price (Rs)", None, {}), ("Target customer", "textarea", {"requiredField": True}), ("Current offer", None, {}),
          ("Customer reviews / DMs / comments", "textarea", {}), ("Competitor ads notes", "textarea", {})], [0, 0], "ad-ideas")
    settings(w, [240, 0])
    code(w, "Build AI request", """const f = $json; const cfg = f.config;
return { json: { product: f.Product, body: { model: cfg.model, response_format: { type: 'json_object' }, temperature: 0.9, messages: [
  { role: 'system', content: 'You are a direct-response Meta ads strategist for Pakistan. Follow Meta ad policies: no income or health guarantees, no before/after promises, no personal-attribute callouts.' },
  { role: 'user', content: `Product: ${f.Product} (Rs ${f['Price (Rs)'] || '?'}). Customer: ${f['Target customer']}. Offer: ${f['Current offer'] || 'none'}.
Customer words: ${f['Customer reviews / DMs / comments'] || 'n/a'}. Competitors: ${f['Competitor ads notes'] || 'n/a'}.
Return JSON {"angles":[{"angle":"","core_message":"","format":"static|carousel|video","hook_1":"","hook_2":"","hook_3":"","image_headline":"max 6 words","primary_text":"50-90 words, English + light Roman Urdu, CTA","image_prompt":"for an AI image tool, 4:5, real-looking, product on clean background"}]} with 6 truly different angles.` }] } } };""", [480, 0], each=True)
    openai(w, "AI creates angles", [720, 0])
    code(w, "One row per angle", """let a = []; try { a = JSON.parse($json.choices[0].message.content).angles || []; } catch (e) {}
const product = $('Build AI request').first().json.product; const date = new Date().toISOString().slice(0, 10);
return a.map((x, i) => ({ json: { Date: date, Product: product, 'Ad name': `${product}_${(x.angle || 'angle').replace(/\\s+/g, '-')}_${i + 1}`, Angle: x.angle,
  'Core message': x.core_message, Format: x.format, 'Hook 1': x.hook_1, 'Hook 2': x.hook_2, 'Hook 3': x.hook_3, 'Image headline': x.image_headline,
  'Primary text': x.primary_text, 'Image prompt': x.image_prompt, Status: 'Idea' } }));""", [960, 0])
    sheet_append(w, "Save to Ad Ideas", "Ad Ideas", [1200, -100])
    w.add("Generate draft image (optional)", "httpRequest", 4.2, {
        "method": "POST", "url": "https://api.openai.com/v1/images/generations", "authentication": "predefinedCredentialType", "nodeCredentialType": "openAiApi",
        "sendBody": True, "specifyBody": "json", "jsonBody": "={{ JSON.stringify({ model: 'gpt-image-1', prompt: $json['Image prompt'], size: '1024x1536' }) }}", "options": {}},
        [1200, 140], disabled=True)
    code(w, "Image to file", """// Converts the generated image (base64) into a file for Google Drive.
return $input.all().map((item, i) => {
  const b64 = (item.json.data || [])[0]?.b64_json || '';
  const name = $('One row per angle').all()[i].json['Ad name'];
  return { json: { name }, binary: { data: { data: b64, mimeType: 'image/png', fileName: name + '.png' } }, pairedItem: { item: i } };
});""", [1440, 140])
    w.nodes[-1]["disabled"] = True
    w.chain("Ad brief form", "Settings", "Build AI request", "AI creates angles", "One row per angle")
    w.link("One row per angle", "Save to Ad Ideas"); w.link("One row per angle", "Generate draft image (optional)"); w.link("Generate draft image (optional)", "Image to file")
    w.dump("34-ai-ad-creative-factory.json", []); built.append(w.name)

    # ===== 35 Voice Notes -> Tasks =====
    w = WF("Skillstack 35 · AI Voice Notes → Tasks")
    w.note("## 🎙️ AI Voice Notes → Tasks\nSave a voice note / meeting recording into your Google Drive **VoiceNotes** folder (from your phone) → AI transcribes it (Urdu + English), "
           "extracts tasks with real due dates → creates **Google Tasks** → emails you a summary + a ready follow-up message.\n\n**Needs:** OpenAI, Google Drive, Google Tasks, Gmail.\n\n" + COMMON_NOTE,
           [-80, -480], 600, 440, 4)
    w.add("New voice note in Drive", "googleDriveTrigger", 1, {"pollTimes": {"item": [{"mode": "everyMinute"}]}, "triggerOn": "specificFolder",
                                                              "folderToWatch": {"__rl": True, "mode": "list", "value": ""}, "event": "fileCreated", "options": {}}, [0, 0])
    settings(w, [240, 0], "  taskListId: '@default',  // your default Google Tasks list\n")
    w.add("Download audio", "googleDrive", 3, {"operation": "download", "fileId": {"__rl": True, "mode": "id", "value": "={{ $json.id }}"}, "options": {}}, [480, 0])
    w.add("Transcribe (Whisper)", "httpRequest", 4.2, {
        "method": "POST", "url": "https://api.openai.com/v1/audio/transcriptions", "authentication": "predefinedCredentialType", "nodeCredentialType": "openAiApi",
        "sendBody": True, "contentType": "multipart-form-data",
        "bodyParameters": {"parameters": [{"parameterType": "formBinaryData", "name": "file", "inputDataFieldName": "data"},
                                          {"name": "model", "value": "whisper-1"}]}, "options": {}}, [720, 0])
    code(w, "Build AI request", """const cfg = $('Settings').first().json.config; const today = new Date().toISOString().slice(0, 10);
return { json: { file: $('New voice note in Drive').item.json.name, transcript: $json.text, body: { model: cfg.model, response_format: { type: 'json_object' }, temperature: 0.2, messages: [
  { role: 'system', content: 'You turn voice notes and meeting transcripts (English, Urdu, Roman Urdu mixed) into clear actions.' },
  { role: 'user', content: `Today is ${today}. Convert words like "kal", "parson", "next Monday" into real dates (YYYY-MM-DD).
Transcript: ${$json.text}
Return JSON {"summary":"3 lines","tasks":[{"title":"","due_date":"YYYY-MM-DD or empty","priority":"High|Medium|Low","owner":""}],"decisions":"","followup_message":"Roman Urdu WhatsApp message under 60 words, or empty"} with max 7 tasks.` }] } } };""", [960, 0], each=True)
    openai(w, "AI extracts tasks", [1200, 0])
    code(w, "Read result", """return $input.all().map((item, i) => {
  let ai = {}; try { ai = JSON.parse(item.json.choices[0].message.content); } catch (e) {}
  const src = $('Build AI request').all()[i].json;
  return { json: { file: src.file, transcript: src.transcript, ...ai }, pairedItem: { item: i } };
});""", [1440, 0])
    code(w, "One item per task", """const out = [];
for (const item of $input.all()) for (const t of (item.json.tasks || [])) out.push({ json: { title: `[${t.priority || 'Medium'}] ${t.title}`,
  due: new Date((t.due_date || new Date(Date.now() + 7 * 864e5).toISOString().slice(0, 10)) + 'T09:00:00+05:00').toISOString(), notes: `Owner: ${t.owner || 'me'} · From: ${item.json.file}` } });
return out;""", [1680, -100])
    w.add("Create Google Task", "googleTasks", 1, {"task": "={{ $('Settings').first().json.config.taskListId }}", "title": "={{ $json.title }}",
                                                    "additionalFields": {"dueDate": "={{ $json.due }}", "notes": "={{ $json.notes }}"}}, [1920, -100])
    gmail_send(w, "Email me the summary", "={{ $('Settings').first().json.config.ownerEmail }}", "=🎙️ Voice note processed: {{ $json.file }}",
               "=SUMMARY\n{{ $json.summary }}\n\nDECISIONS\n{{ $json.decisions }}\n\nTASKS\n{{ ($json.tasks || []).map(t => '- ' + t.title + (t.due_date ? ' (due ' + t.due_date + ')' : '')).join('\\n') }}\n\nFOLLOW-UP MESSAGE\n{{ $json.followup_message }}\n\nTRANSCRIPT\n{{ $json.transcript }}",
               [1680, 120])
    w.chain("New voice note in Drive", "Settings", "Download audio", "Transcribe (Whisper)", "Build AI request", "AI extracts tasks", "Read result")
    w.link("Read result", "One item per task"); w.link("One item per task", "Create Google Task"); w.link("Read result", "Email me the summary")
    w.dump("35-ai-voice-notes-to-tasks.json", []); built.append(w.name)
    return built


if __name__ == "__main__":
    for n in build():
        print("✓", n)
