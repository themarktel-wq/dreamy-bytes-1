# QA report: Small Landlord Notice + Addendum Pack (2026-11-25)
## Tested
- Generated 7 .docx with python-docx (`tools/docs/d20261125_landlord_pack.py`); all reopened without error.
- Scripted check: every file has the legal-notice footer and the boxed top notice ("varies by state"), has bracketed fields (counts 1/27/26/82/19/52/25), no lorem/TODO/XXX/undefined text.
- Converted all to PDF with LibreOffice (1-2 pages each) and viewed the condition-form page: layout, tables, notice box, footer render correctly.
- Content review: no document states a legal notice period, fee cap or deposit deadline; all are fields.
## NOT tested
- Not opened in Microsoft Word or Google Docs.
- Not reviewed by a lawyer; templates may not satisfy local requirements anywhere. No state-specific versions.
