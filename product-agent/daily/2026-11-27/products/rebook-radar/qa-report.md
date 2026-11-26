# QA report: Rebook Radar (2026-11-27)
## Tested
- `tools/tests/rebookradar.test.js`: 29 checks PASSED.
- Unit (node), against hand calculation with a fixed date: date maths; expected return = last visit + interval weeks; status classification (overdue / due now / due soon / ok / no visit) and grace-day boundaries; overdue list sorted (18, 14 days) and due-soon list; rebook % (Alex 4/6, Sam 4/5, overall 8/11, invalid-date visit ignored); month filter and empty period; target comparison boundaries; logging a visit updates the last visit only when newer; message placeholders; CSV escaping and formula-injection guard.
- Browser (Playwright Chromium, 390x844): no horizontal page overflow; example data (2 overdue, 2 due soon; Alex 66.7%, Sam 75.0%, overall 70.0%) matches hand calculation; copy message; target flags; logging a visit changes the overdue list and rebook % (7/11 = 63.6%); add client with HTML escaping and blank rejection; grace days and salon name settings; persistence after reload; CSV download; JSON backup/restore with a real invalid-file dialog; delete; reset and empty state without NaN/undefined; works with localStorage blocked; zero console errors. Viewed the overdue screenshot.
- Fixtures in my own test file had arithmetic slips that were corrected in the tests (not the product).
## NOT tested
- Only Chromium; not Safari, Firefox or a real phone.
- Uses the device's local date; time zones near midnight not tested.
- Vendor benchmark text is taken from the research card (S3), not re-verified today; no outcome claims are made.
