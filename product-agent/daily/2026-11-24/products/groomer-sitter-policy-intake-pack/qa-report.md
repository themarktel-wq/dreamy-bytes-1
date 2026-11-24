# QA report: Groomer & Sitter Policy and Intake Pack (2026-11-24)
## Tested
- Generated 6 .docx files with python-docx (`tools/docs/d20261124_policy_pack.py`); all re-opened with python-docx without error.
- Scripted check: every file has the footer "Template only, not legal advice; check local rules", contains bracketed fields (counts: 2/38/28/27/15/17), and has no lorem/TODO/XXX/undefined/template-syntax text.
- Converted all 6 to PDF with LibreOffice (all succeeded; policy is 2 pages) and visually checked the rendering of the intake form page: headings, tables and footer render correctly.
## NOT tested
- Not opened in Microsoft Word or Google Docs (only LibreOffice).
- Not reviewed by a lawyer; clauses are generic templates and may be unenforceable or insufficient in some jurisdictions. No jurisdiction-specific content.
- Policy content structure is based on a few public shop policy pages (research P8), not a survey.
