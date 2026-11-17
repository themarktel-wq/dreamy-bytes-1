# Lahore Mobile — Phones & Accessories PWA

An installable web app (PWA) for a mobile phone and accessories shop in Lahore. It installs from Chrome on Android or Safari on iPhone (Add to Home Screen) and keeps working offline. It is plain HTML/CSS/JS with no build step.

## Features that set it apart

| Feature | What it does | Route |
|---|---|---|
| **Mera Phone Matcher** | The customer picks their phone once. Every cover, glass, cable, charger and watch is then marked "fits / doesn't fit", and chargers show their real charging speed (for example, "Full speed: 45W"). | `#/myphone` |
| **Smart Kit Builder** | Builds a bundle (phone, cover, glass, charger and extras) that fits the chosen phone. 3 or more accessories get an automatic combo discount. | `#/kit` |
| **Trade-in Estimator** | A 6-question condition check gives an estimated value. The customer can apply it as credit in the cart or confirm it on WhatsApp. | `#/tradein` |
| **Warranty Vault** | Every order creates a digital warranty card with the IMEI, an expiry countdown and a one-tap claim on WhatsApp. | `#/warranty` |
| **Price Tracker + Drop Alerts** | Each product shows a 90-day price chart and a "lowest price" badge. Customers can set a target price and get notified. | product page |
| **Shopping Assistant** | Understands Roman Urdu and English ("50k tak gaming phone", "A56 ke liye charger"). It runs on the device, so it needs no API key and works offline. | AI button |
| **PTA clarity** | Every phone shows a PTA or Non-PTA badge. Non-PTA phones also show an estimated PTA tax and the total including tax. | product page |

## Design

The design is clean white and navy blue, set in Inter, with real product photography and subtle motion only (fades, image zoom, slide progress). The layout follows a standard retail structure: an announcement bar, a header with search, a category bar, a hero with promo tiles, a trust strip, shop-by-category tiles, product grids, services, brands, reviews, a store block and the footer.

## Photos

`assets/img/` contains free stock photos from [Unsplash](https://unsplash.com/license), which can be used commercially without attribution. They are placeholders: some show older phone models, and products in the same category share one photo. Replace them with your own photos from **Admin → Products → Photo** (square images look best).

## Also included

- Photo hero carousel (swipe, auto-play, progress bars), scroll reveal, image zoom on product pages
- Search with typo tolerance, voice search, recent and trending searches; filters for category, brand, price, PTA, in stock and "fits my phone"; 7 sort options
- Suggestions based on what the customer viewed or saved and on their phone
- Compare up to 3 products, wishlist, product reviews
- Qist calculator (3/6/12 months), checkout on WhatsApp (delivery or shop pickup), free-delivery threshold
- Community page: WhatsApp channel, Facebook, Instagram, TikTok and YouTube links, a Q&A wall and referral sharing
- Live "Open now / Closed" status
- **Admin panel** (`#/admin`, default PIN `1234`): dashboard charts, product CRUD with photo upload, stock editing, banners, orders with status updates and a WhatsApp reply button, phone models, all settings, JSON backup/restore, CSV export

## Run locally

```bash
python3 -m http.server 8080
```

Then open http://localhost:8080. The service worker needs `http://localhost` or HTTPS, so opening the file directly won't work.

## Deploy (free)

Push this folder to **GitHub Pages**, **Netlify** or **Vercel**; any static host works. The site must be served over HTTPS for the install button to appear. On every deploy, change `VERSION` in `sw.js` so customers get the update.

## First things to change (Admin → Settings)

1. Real WhatsApp number (`92XXXXXXXXXX`), phone, address and Google Maps link
2. Admin PIN
3. Social media links
4. Products: all prices in the seed data are **sample prices**. Edit them from Admin → Products and upload real photos.

## Important limitation

Admin edits and orders are saved in **that browser's storage** (localStorage). When the owner edits products on their phone, customers will **not** see the change. Use Admin → Backup to move data between devices. For a real live store where admin changes reach every customer, the next step is a backend such as **Firebase** or **Supabase**. The data layer (`DB` in `js/app.js`) is kept in one place so it can be swapped out.

## Files

```
index.html            app shell
css/style.css         design system + animations
js/data.js            seed products, phone models, banners, settings
js/ui.js              icons, logo, product illustrations, helpers
js/app.js             state, compatibility engine, cart
js/pages.js           router, home, shop, product, cart, checkout
js/features.js        Mera Phone, Kit, Trade-in, Warranty, Compare, Community, Store
js/ai.js              Lahori AI helper (offline NLU)
js/admin.js           admin panel
js/main.js            boot, search, voice, install prompt, service worker
sw.js                 offline cache
manifest.webmanifest  PWA manifest
```
