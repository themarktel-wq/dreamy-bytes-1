# Lahore Mobile Wholesale

A wholesale ordering and back-office app for a mobile accessories supplier in Lahore. Retail shops in nearby markets install it on their phones, sign in, see trade prices and live stock, place orders on cash or khata, and chat with the store. The owner runs everything from the admin panel: orders, counter sales, inventory, purchases, shop accounts, khata, warranty claims and reports.

It is an installable web app (PWA) with a small Node.js server. It has no external dependencies, needs only Node 22 or newer, and keeps its data in a single SQLite file.

## What shops get

- **Registration and approval**: a shop signs up with its mobile number, and the owner approves it and sets a price tier and credit limit. Until then, prices stay hidden.
- **Catalogue**: search by name, SKU or phone model (for example "A15" or "iPhone 11"), with filters for category, grade (Original / OLED / Incell / TFT), brand and stock. Each product shows the shop's own tier price, the suggested retail price and the shop's margin.
- **Ordering rules**: pack sizes and minimum order quantities are enforced.
- **Cart and checkout**: pay by khata (credit), cash or bank. The credit limit is checked before the order goes through.
- **Orders**: each order shows a status timeline. Shops can cancel while an order is pending, order the same items again with one tap, and copy the invoice.
- **Warranty claims**: report a faulty item from an order, and the store credits the khata or sends a replacement.
- **Khata**: a statement with a running balance and the store's payment details.
- **Messages**: chat with the store, with product references and live updates.
- **Other**: stock requests ("Notify me" when out of stock), saved items, and announcements from the store.

## What the owner gets

- **Dashboard**: today's and this month's sales and profit, receivables, new orders, unread messages, claims, low stock, a 14-day chart, and the top products and shops.
- **Orders**: confirm, pack, dispatch and deliver. Confirming takes the stock and adds the order to the shop's khata. You can edit quantities and give a discount before confirming. You can override the credit limit (owner only). When an order is delivered you can record that the cash was collected.
- **Counter sale (POS)**: sell to walk-in customers or registered shops at the shop's tier price, with partial payment going on khata.
- **Inventory**: products with photos, SKU, compatible models, grade, pack size, minimum order, reorder level and cost price. Stock adjustments (count, damage, return) and the full stock history per product are recorded. Products that appear in past orders are archived instead of deleted.
- **Purchases**: receive stock from suppliers. The average cost updates automatically, and you can post a "new stock" announcement.
- **Shops**: approve or block shops, set tiers and credit limits, reset passwords, view each shop's khata and orders, record payments, make adjustments, and send WhatsApp reminders.
- **Khata**: everything owed, with each shop's last payment date.
- **Claims and requests**: approve a claim with a khata credit or a replacement, or reject it. Track faulty stock to send back to suppliers.
- **Announcements**: posted to every shop's home screen. Price drops are announced automatically.
- **Reports**: sales and profit by day, product, category and shop; stock value; days of stock left; slow movers.
- **Settings**: business details, price tiers, market list, staff accounts, and backup/restore.
- **Staff accounts**: staff can handle orders, sales, messages, payments and stock counts. They cannot see cost, profit or reports, edit products, or change credit limits.

## Added in version 2

- **Phone notifications** (Web Push, no third-party service): new orders, messages, order status, flash deals, payments, claims and reminders reach phones even when the app is closed. Each user turns them on under **Account**. They need HTTPS. On iPhone, the app must first be added to the Home Screen (iOS 16.4+).
- **Riders**: add riders under **Settings → Staff & riders**, then assign them on the order page. Riders mark orders "Picked up" and "Delivered" and enter the cash they collected. That cash is recorded on the shop's khata and shown as the rider's cash in hand, which you clear with **Riders → Receive cash**.
- **Barcode / QR**: products have a barcode field. **Counter sale** and **Inventory → Stock count** accept USB or Bluetooth scanners (type and press Enter), or the camera on Chrome for Android. **Inventory → QR labels** prints shelf labels; the QR library loads from cdnjs, and without internet the labels show the code as text.
- **Printing**: invoices in A4 or 80 mm thermal format, and khata statements. Use the browser's print dialog, or choose "Save as PDF". Bluetooth thermal printers work through the phone's print service (for example the RawBT app on Android).
- **Supplier khata**: purchases are added to what you owe each supplier, and payments to suppliers are recorded. Faulty stock you return to a supplier is credited at cost.
- **Special prices**: set fixed rates per shop per product on the shop's page.
- **Khata aging**: dues are split into 0–30, 31–60, 61–90 and 90+ days, with payments settling the oldest orders first. You can send reminders as an in-app message plus a notification (automatically every N days, set in Settings) or open WhatsApp with the message ready. Fully automatic WhatsApp messages would need the paid WhatsApp Business API.
- **Flash deals**: a deal price with a countdown and an optional limit per shop. Starting a deal notifies every shop.
- **Faulty rate by supplier**: the share of units that came back as warranty claims, per supplier and per product, in **Reports** and on each supplier's page.

## Run it

```bash
node --no-warnings server/server.js
```

Open http://localhost:8080. On first run the server prints the owner's login: mobile `03000000000` and a random password. Change it in **Account → Change password**.

Options (environment variables):

| Variable | Default | Meaning |
|---|---|---|
| `PORT` | `8080` | Port to listen on |
| `DATA_DIR` | `./data` | Where the database (`lahore-mobile.db`) and uploaded photos are kept |
| `ADMIN_PHONE` / `ADMIN_PASSWORD` | `03000000000` / random | Owner account created on first run |
| `DEMO` | off | `DEMO=1` adds sample shops, orders, khata and messages (all shops' password: `shop123`) |
| `COOKIE_SECURE` | off | Set to `1` when served over HTTPS |
| `VAPID_SUBJECT` | `mailto:admin@example.com` | Contact for push services; set it to your own email, e.g. `mailto:you@yourdomain.pk` |

**Back up `DATA_DIR`.** It holds all your business data. The app also has **Settings → Backup**.

## Deploy

Any server that runs Node 22 works: a small VPS (Hostinger, DigitalOcean or a local Pakistani host, roughly Rs 1,500–3,000 per month), Railway, or Fly.io. The hosting must keep a **persistent disk** for `DATA_DIR`; free tiers that wipe the disk on restart will lose your data. Put it behind HTTPS (Caddy or Nginx with Let's Encrypt), set `COOKIE_SECURE=1`, and point a domain such as `lahoremobile.pk` at it. Once it is on HTTPS, shops can install it from Chrome or Safari.

## Demo mode

If no server is reachable (for example on static hosting, or in the claude.ai artifact preview), the same business logic runs inside the browser on sample data saved in that browser. A yellow bar marks demo mode. Use it to show the app; it is not for real use.

## Tests

```bash
node test/core.test.js
```

Runs 32 business-rule tests: pricing, MOQ, stock, credit limits, khata, claims, rollback, permissions, lockout, special prices, flash deals, suppliers, riders, aging, reminders, barcodes and push targeting.

```bash
node test/webpush.test.js
```

Checks the push encryption against the RFC 8291 test vector and the VAPID signature.

```bash
node test/server.test.js
```

Tests HTTP, cookies, live events, uploads, push delivery (decrypted by a fake push service) and persistence across restarts.

## Code layout

```
core/core.js         all business rules and the API (shared by server and demo)
core/memstore.js     transactional in-memory store
server/server.js     HTTP server, SQLite persistence, sessions, live updates, uploads, reminder schedule
server/webpush.js    Web Push (VAPID + aes128gcm), no dependencies
js/extras.js         notifications, deals, riders, suppliers, aging, scanning, printing
js/api.js            client: server mode or in-browser demo mode
js/router.js         navigation, cart, helpers
js/shop.js           shop-facing screens
js/admin.js          admin panel
js/main.js           header, tabs, live refresh, install prompt
tools/build-artifact.py   single-page demo build for claude.ai artifacts
```

## Photos

`assets/img/` has free stock photos from Unsplash used as placeholders. Upload real product photos from **Inventory → product → Upload photo**.
