# QuoteSweep: Margin-Safe Cleaning Quote Calculator

A single-file quote calculator for house-cleaning owners. Instead of adding up line items, QuoteSweep works backwards from your own labor cost, overhead and target margin, so every quote leaves the profit you chose. Open `index.html` in any browser. No install, no account, no monthly fee, works offline.

## What you get
- Cost settings: labor $/hr, overhead $/hr, target margin %, lowest margin you accept, sales tax %, minimum job price, setup minutes.
- Room-by-room task minutes (bedroom, bathroom, kitchen, sq ft of common areas), all editable.
- Condition multipliers (light / normal / heavy), pets multiplier, editable add-on list (oven, fridge, windows, cabinets, laundry).
- Live numbers: labor hours, on-site time for your crew size, cost, price, profit, margin.
- Recurring plans (one-time, monthly, bi-weekly, weekly) with your own discount %: new price and the margin you keep, flagged on target / thin / too low.
- Client estimate page (your business name, rooms included, price, tax, total) that never shows your costs or margin. Print or save as PDF from the browser, or copy as text for WhatsApp / SMS.
- Saved quotes list, JSON export and import for backup. Everything is stored in your browser only.

## How the price is calculated
`price = cost / (1 - target margin)` where `cost = labor hours x (labor $/hr + overhead $/hr)`. This is margin on price, not markup on cost. Example: $18 labor + $20 overhead at a 25% margin = $50.67 per labor hour.

## Who it is for
Solo cleaners and small maid-service owners (1-8 people) who quote by gut feel or phone call and want a fast, defensible price.

## Good to know
- The starting minutes, multipliers and discounts are examples, not industry standards. Time a few real jobs and replace them with your own numbers.
- Not accounting or tax advice. Data lives in this browser; use Export JSON before clearing browser data.
- Tested in Chromium (desktop and 375 px phone width). Not tested in Safari or Firefox.

Price: Rs 10,920 (USD 39)
