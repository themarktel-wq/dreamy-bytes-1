# DetailQuote: Size x Condition x Add-On Quote Builder

A single-file quote builder for auto detailers. Pick the vehicle size, package and condition, tick the add-ons, and get a clean printable quote with the deposit and your cancellation notice on it. Work that depends on the paint (paint correction, ceramic coating) is flagged "quoted after inspection" with a range you type, instead of a made-up fixed price. Open `index.html` in any browser. No install, no account, works offline.

## What you get
- Vehicle size tiers and package prices you set yourself (4 sizes x 3 packages to start; rename and edit everything).
- Condition surcharge (light / normal / heavy) as a % you choose.
- Add-on list (headlights, engine bay, odor removal, pet hair, clay bar and more) with your own prices and an optional "market reference" note.
- Inspection-required items: shown on the quote with your price range, never added to the total.
- Deposit % (shown as an amount), mobile / travel fee, tax, quote validity and cancellation notice hours.
- Printable quote (browser print or save as PDF) and copy-as-text for messaging; saved quotes list; JSON backup and restore.

## How the quote is calculated
`total = package price for size x (1 + condition %) + add-ons + travel fee (+ tax)`; `deposit = deposit % x total`. Inspection items are listed separately and are not part of the total.

## Who it is for
Solo and mobile detailers who quote by guesswork, lose money on scope creep, and want the add-ons offered as clear upgrades.

## Good to know
- Starting prices are examples, not advice. Market reference ranges (for example headlight restoration $50-150, paint correction $200-1,000, ceramic coating $500-2,000) come from public marketing guides, vary by region, and are shown for orientation only.
- The terms text is a template, not legal advice. Adapt it to your local rules.
- Tested in Chromium at desktop and 375 px phone width; not tested in Safari or Firefox. Back up with Export JSON before clearing browser data.

Price: Rs 9,800 (USD 35)
