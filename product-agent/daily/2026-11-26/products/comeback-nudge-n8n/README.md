# Comeback Nudge: Ghosted-Client Re-engagement Flow (n8n)

Stop quiet clients slipping away without extra software. Two importable n8n workflows read a simple Google Sheet of your clients and send polite, escalating check-ins when someone has not trained for a while, a renewal message when a session pack is almost used up, and a Monday digest to you listing who needs a personal follow-up. When a client trains again, their counters reset automatically. Email-first, with optional SMS through your own Twilio account.

**What you get**
- 2 n8n workflow files (daily nudges, weekly digest)
- Clients sheet template (CSV) and step-by-step SETUP.md
- Editable message wording

**Features**
- Three-step check-in at day thresholds you set (defaults 14, 21, 35), then it stops
- Renewal message once when the pack balance reaches your threshold; link to YOUR pack/payment page
- Auto-reset when last_session is updated; paused or archived clients are skipped
- Monday owner digest: quiet clients (with check-ins sent) and low packs; nothing sent if all is well

**Who it is for:** solo personal trainers and small studios who track clients in a sheet and want consistent follow-up.

**Needs:** an n8n instance, Google account, email account; Twilio optional. Tested in a local simulator only, not against live email, SMS or Google (see setup notes). Get client permission to message them.

Price: Rs 12,600 PKR (about $45 USD)
