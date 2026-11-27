# QA report: Lead Clock (2026-11-28)
Result: PASS (tested items below).

## Tested (automated, run on this build)
- `qa/test-core.js` (node, 14 tests): wait minutes from local timestamps; band boundaries (15 / 16 / 60 / 61 minutes) and custom limits; queue holds only uncontacted, non-lost leads; ordering (red first, then source priority, then longest wait; amber; green); same band and priority sorted by wait; unknown source priority; response minutes and median (10, 50, 20, 30 = 25); 7-day window excludes older and future leads; per-source stats; empty data; minute formatting; script placeholders; CSV rows and quoting.
- `qa/test-browser.js` (Playwright Chromium, 375 px and 1280 px, clock fixed to 2026-06-20 12:00): no horizontal overflow, no "undefined"/"NaN"/unfilled placeholders; sample queue shows 95 min red, 40 min amber and 8 min green in that order; KPIs; after fast-forwarding the clock 30 minutes the amber lead turns red and its timer text updates; "I contacted them" removes the lead and records the response time in the log; adding an inquiry with an explicit time and with the default (now); scripts preview with first name; weekly stats; tightening the colour limits in settings changes the bands; CSV download; persistence after reload; sample removal; zero console errors.
- Wording fix during QA: the scripts tab note named placeholders in a confusing way; replaced with a plain sentence.

## Not tested
- Safari, Firefox, real phones; clipboard permission paths; JSON restore with a real file.
- Time zone or daylight-saving edge cases (times are the browser's local time); business-hours-only timing is not offered.
- Real agents: no agent has used it; sample leads are fictional. No effect on response speed or conversion is measured or claimed.
