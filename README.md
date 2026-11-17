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

**Back up `DATA_DIR`.** It holds all your business data. The app also has **Settings → Backup**.

## Deploy

Any server that runs Node 22 works: a small VPS (Hostinger, DigitalOcean or a local Pakistani host, roughly Rs 1,500–3,000 per month), Railway, or Fly.io. The hosting must keep a **persistent disk** for `DATA_DIR`; free tiers that wipe the disk on restart will lose your data. Put it behind HTTPS (Caddy or Nginx with Let's Encrypt), set `COOKIE_SECURE=1`, and point a domain such as `lahoremobile.pk` at it. Once it is on HTTPS, shops can install it from Chrome or Safari.

## Demo mode

If no server is reachable (for example on static hosting, or in the claude.ai artifact preview), the same business logic runs inside the browser on sample data saved in that browser. A yellow bar marks demo mode. Use it to show the app; it is not for real use.

## Tests

```bash
node test/core.test.js
```

Runs 23 business-rule tests: pricing, MOQ, stock, credit limits, khata, claims, rollback, permissions and lockout.

```bash
node test/server.test.js
```

Tests HTTP, cookies, live events, uploads and persistence across restarts.

## Code layout

```
core/core.js         all business rules and the API (shared by server and demo)
core/memstore.js     transactional in-memory store
server/server.js     HTTP server, SQLite persistence, sessions, live updates, uploads
js/api.js            client: server mode or in-browser demo mode
js/router.js         navigation, cart, helpers
js/shop.js           shop-facing screens
js/admin.js          admin panel
js/main.js           header, tabs, live refresh, install prompt
tools/build-artifact.py   single-page demo build for claude.ai artifacts
```

## Photos

`assets/img/` has free stock photos from Unsplash used as placeholders. Upload real product photos from **Inventory → product → Upload photo**.
