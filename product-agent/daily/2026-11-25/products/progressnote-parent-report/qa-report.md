# QA report: ProgressNote (2026-11-25)
## Tested
- `tools/tests/progressnote.test.js`: 25 checks PASSED.
- Unit (node): month/student filtering with malformed dates; attendance counts by hand (3 held, 1 cancelled by student, 1 no-show); case-insensitive topic de-duplication; cancelled lessons excluded from topics/wins; goals and next-steps trimming; attendance sentence wording; report text; empty report and invalid month; colour sanitising.
- Browser (Playwright Chromium, 390x844): no horizontal page overflow; example report matches hand calculation; HTML in user text escaped; add student / empty-name rejection; log lessons / missing-date rejection; per-student isolation; month with no lessons; copy as text; brand name, colour and logo reach the report; persistence after reload; print view and PDF generation; backup export/restore and invalid-file rejection; deleting a student; no-students state (a real bug where the report area disappeared after the last student was deleted was found by this test and fixed); reset; works with localStorage blocked; zero console errors. Viewed the report screenshot.
## NOT tested
- Only Chromium; not Safari, Firefox, a real phone or printer.
- Print layout verified by emulation and PDF smoke test only.
- No claim is made that parents want or pay for this (evidence Low).
