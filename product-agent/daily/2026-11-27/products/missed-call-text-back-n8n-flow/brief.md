# Brief: Missed Call Text-Back n8n Flow (d20261127-03)
- Niche: trades (HVAC / plumbing). Persona: solo / small contractor.
- Concept: missed-call text-back on the contractor's own Twilio account with lead logging, keyword classification, owner alert and weekly summary. Call-answering and CRM services charge monthly; this is a one-time flow plus Twilio usage.
- Evidence: H5 only (vendor and trade-press claims such as "27% of inbound calls unanswered, about $75k a year lost" are vendor-sourced; Low). Do NOT quote those numbers as facts in marketing.
- Scope notes: built as three workflows (missed call, reply intake, weekly summary). SMS owner alert included but disabled by default. Reply parsing uses deterministic keywords, not AI, so there are no AI claims.
- Compliance: README warns that texting rules vary (consent, opt-out, quiet hours, carrier registration); opt-out handling and a cooldown are built in; no legal advice.
