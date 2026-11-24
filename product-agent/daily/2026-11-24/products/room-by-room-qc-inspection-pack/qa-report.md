# QA report: Room-by-Room QC Inspection Pack (2026-11-24)
Result: PASS (documents). No market validation.

## Tested (`qa/test.py`, run on this build)
- All 8 DOCX files open with python-docx; each has a matching PDF with extractable text and the title present.
- Scorecards meet the spec: Standard 8 rooms, Deep 10 rooms, Move-Out 10 rooms; every room has 6-10 checks (counts checked from the tables); numbering starts at 1; scoring formula text present.
- No stray placeholder text (lorem, TODO, TBD, XXX, {{ }}, undefined, NaN). Intentional blanks are underscores or [bracketed fields].
- Worked example arithmetic verified: 80.0%, 87.5%, 100.0% rows and 21/(21+3) = 87.5%.
- Footer "Adapt to your local rules" present on every file.
- Visual check of page renders (scorecard, visit slip, photo sheet) at 50 dpi after fixing column widths; page counts: 1-3 pages per file.

## Not tested
- Opening in Microsoft Word or Google Docs (only python-docx and LibreOffice were used).
- Print on real printers (slip cut line and margins looked right in the PDF only).
- Whether the check wording suits any specific market; no cleaners reviewed it.
