# QA report: Wedding Photography Contract + Client Guide Pack (d20261124-11)
Date: 2026-11-24. Everything listed under Tested was actually run.

## Tested
- All 4 DOCX files re-opened with python-docx and converted to PDF with LibreOffice without error (pages: contract 3, guide 2, questionnaire 2, emails 2).
- Automated scan (`qa/qa.py`): brackets balanced in every file; no TODO, lorem, XXX, TBD, FIXME, {{ }}, "None" or "undefined" text; every remaining [BRACKET] is an intentional fill-in field (contract 54 field uses, 48 unique; guide 23; emails 36).
- Contract footer contains "Template only, not legal advice; have a lawyer review for your jurisdiction"; client documents have a template footer.
- Contract page 1 checked by eye in the rendered PDF (fields highlighted yellow, table layout fine).
- Features from the plan present: delivery window, gallery access months, image count range, style notes, copyright/usage fields; client questionnaire; client timeline and expectations guide; delivery email set (on time, delayed, late apology, on-track); gallery expiry reminders (2).

## Not tested
- Opening in Microsoft Word itself or Google Docs (LibreOffice and python-docx only).
- Legal sufficiency or enforceability in any jurisdiction. Not reviewed by a lawyer. The pack says so and tells buyers to have it reviewed.
- Pages 2 and 3 of the contract, and the other three documents, were checked by text scan but not all page images inspected by eye.
- No market testing.

Result: PASS (shippable as a template pack, with the legal-review disclaimer).
