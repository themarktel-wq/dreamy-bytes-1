# 50 n8n automations (US small-business, 2026)

Importable workflow files for [n8n](https://n8n.io) (self-hosted or cloud). See `CATALOG.md` for the list and `RESEARCH.md` for why these were chosen and how to sell them.

## Use one
1. n8n > Workflows > Import from file > pick a file in `workflows/`.
2. Open the **Config** node and replace the placeholder values (Slack webhook, sheet ID, email, business name, links).
3. Attach credentials on the nodes that show a warning icon:
   - **AI API key**: HTTP Header Auth, header `Authorization`, value `Bearer sk-...`. Works with OpenAI or any OpenAI-compatible endpoint; change `aiBaseUrl` and `aiModel` in Config.
   - **SMTP account** for email nodes, **Google Sheets OAuth2** for sheet nodes, **Twilio / Stripe / GitHub** Header or Basic Auth where used.
4. Read the sticky note on the canvas (setup steps and sheet column names), click **Execute workflow** on a test input, then activate.

Webhook workflows: copy the Production URL from the Webhook node and POST JSON like the sample in `tests.json`.

## What has been tested
`node sim.js` runs every workflow in a small local simulator with mocked services: it follows the real connections, evaluates every `{{ }}` expression, runs every Code node, checks each IF branch against sample data, and fails on undefined/NaN/[object Object] in emails or Slack text, invalid JSON bodies or broken links. 50 of 50 pass.

## What has NOT been tested
- Not run inside a real n8n instance, and no live Slack, Stripe, Twilio, Google, GitHub or AI calls were made. Node parameter formats follow n8n's current node versions but a node may ask you to re-select a field on import.
- AI responses were mocked; check prompts with your own model and keep a human reviewing anything customer-facing (refunds, hiring, public review replies).
- Sheet column names and API field names in webhook payloads must match your tools; adapt the **Normalize** node at the start of each flow.

## Regenerate
```bash
python3 build_all.py   # writes workflows/*.json and tests.json from src/s_*.py
node sim.js            # simulated run of all 50
python3 catalog.py     # refreshes CATALOG.md
```
