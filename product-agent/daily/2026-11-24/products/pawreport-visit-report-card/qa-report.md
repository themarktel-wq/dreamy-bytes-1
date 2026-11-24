# QA report: PawReport (2026-11-24)
## Tested
- `tools/tests/pawreport.test.js`: 21 checks PASSED. Unit tests: date formatting (incl. 12 AM / 12 PM), WhatsApp text content and order, empty report without undefined/null, text wrapping, photo downscale dimensions, colour sanitising.
- Browser (Playwright Chromium, 390x844 phone viewport): tabs without horizontal overflow; brand name/colour/footer/logo reach the preview; HTML typed in notes is escaped; 3 photos load and are downscaled to <=900px; a non-image file is rejected with a message; Copy text puts the expected text on the clipboard (clipboard permission granted in the test browser); history save / reopen / delete; brand, logo and history persist after reload; backup export/restore and rejection of an invalid backup; print view shows only the report card and print-to-PDF produces a valid PDF; app still works with localStorage blocked; zero console errors.
- PNG export verified independently with PIL: 1080 px wide, header colour equals the chosen accent, logo and red/green/blue photo thumbnails present in the right area, text present. Viewed the exported image and the phone screenshot.
## NOT tested
- Only Chromium; not Safari, Firefox, a real phone or a real WhatsApp paste. Clipboard fallback (older browsers) not exercised.
- Emoji appearance depends on the device font; canvas export of emoji was seen only in this container's font.
- Large photos from real phone cameras (e.g. 12 MP HEIC) not tested; HEIC may not load in some browsers.
- localStorage quota exhaustion with very large history (200 entries limit, text only) not tested.
