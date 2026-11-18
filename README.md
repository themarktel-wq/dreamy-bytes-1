# Lahore Mobile Wholesale

A wholesale ordering and back-office app for a mobile accessories supplier in Lahore. Retail shops in nearby markets install it on their phones, sign in, see trade prices and live stock, place orders on cash or khata, and chat with the store. The owner runs everything from the admin panel: orders, counter sales, inventory, purchases, shop accounts, khata, warranty claims and reports.

It is an installable web app (PWA) with a small Node.js server. It has no external dependencies, needs only Node 22 or newer, and keeps its data in a single SQLite file.

## What shops get

- **Registration and approval**: a shop signs up with its mobile number, and the owner approves it. Until then, prices stay hidden.
- **Catalogue**: search by name, SKU or phone model (for example "A15" or "iPhone 11"), with filters for category, grade (Original / OLED / Incell / TFT), brand and stock. Every shop sees the same wholesale price, plus the suggested retail price and its margin.
- **Ordering rules**: pack sizes and minimum order quantities are enforced.
- **Cart and checkout**: pay cash (on delivery or pickup) or by bank / JazzCash / Easypaisa.
- **Orders**: each order shows a status timeline. Shops can cancel while an order is pending, order the same items again with one tap, and copy the invoice.
- **Warranty claims**: report a faulty item from an order, and the store sends a replacement or gives a refund.
- **Messages**: chat with the store, with product references and live updates.
- **Other**: stock requests ("Notify me" when out of stock), saved items, and announcements from the store.

## What the owner gets

- **Dashboard**: today's and this month's sales and profit, average order, new orders, unread messages, claims, low stock, a 14-day chart, and the top products and shops.
- **Orders**: confirm, pack, dispatch and deliver. Confirming takes the stock. You can edit quantities and give a discount before confirming.
- **Counter sale (POS)**: sell to walk-in customers or registered shops, always paid in full.
- **Inventory**: products with photos, SKU, compatible models, grade, pack size, minimum order, reorder level and cost price. Stock adjustments (count, damage, return) and the full stock history per product are recorded. Products that appear in past orders are archived instead of deleted.
- **Purchases**: receive stock from suppliers. The average cost updates automatically, and you can post a "new stock" announcement.
- **Shops**: approve or block shops, set special prices, reset passwords, and view each shop's orders.
- **Claims and requests**: approve a claim with a refund or a replacement, or reject it. Track faulty stock to send back to suppliers.
- **Announcements**: posted to every shop's home screen. Price drops are announced automatically.
- **Reports**: sales and profit by day, product, category and shop; stock value; days of stock left; slow movers.
- **Settings**: business details (address, Google Maps link, phone, WhatsApp), market list, staff accounts, and backup/restore.
- **Staff accounts**: staff can handle orders, sales, messages and stock counts. They cannot see cost, profit or reports, or edit products.

## Added in version 2

- **Phone notifications** (Web Push, no third-party service): new orders, messages, order status, flash deals and claims reach phones even when the app is closed. Each user turns them on under **Account**. They need HTTPS. On iPhone, the app must first be added to the Home Screen (iOS 16.4+).
- **Barcode / QR**: products have a barcode field. **Counter sale** and **Inventory → Stock count** accept USB or Bluetooth scanners (type and press Enter), or the camera on Chrome for Android. **Inventory → QR labels** prints shelf labels; the QR library loads from cdnjs, and without internet the labels show the code as text.
- **Printing**: invoices in A4 or 80 mm thermal format. Use the browser's print dialog, or choose "Save as PDF". Bluetooth thermal printers work through the phone's print service (for example the RawBT app on Android).
- **Supplier khata**: purchases are added to what you owe each supplier, and payments to suppliers are recorded. Faulty stock you return to a supplier is credited at cost.
- **Special prices**: set fixed rates per shop per product on the shop's page.
- **Flash deals**: a deal price with a countdown and an optional limit per shop. Starting a deal notifies every shop.
- **Faulty rate by supplier**: the share of units that came back as warranty claims, per supplier and per product, in **Reports** and on each supplier's page.

## Added in version 3

- **App content editor** (**Admin → App content**, owner only): edit the home banner slides (photo, label, heading, text, button and link), the highlights strip, categories (rename, reorder, photo, hide, add), which home sections show, the featured category, ticker lines, a home-page notice, the Urdu name, the "At the shop" note and the footer line. Saved changes reach every open app at once.
- **Products from Excel** (**Inventory → Excel sheet**): download all products as a CSV sheet, edit it in Excel or Google Sheets, and import it back. Rows match by SKU; new SKUs become new products; empty cells keep the current value; a bad row stops the whole import and names the row.
- **Automatic updates**: the server stamps `sw.js` with a hash of the app files. When you deploy new files, every installed app picks up the new version the next time it is opened (or within 10 minutes while open) and reloads itself when nothing is being typed. Nobody reinstalls anything. Products, prices and content are live data and never need an update.
- **Automatic backups**: the server saves a copy of the database every day to `DATA_DIR/backups/` and keeps the last 14 days.
- **Logo**: the "L-frame" mark (the L of Lahore holding a phone). Files are in `brand/` (SVG and PNG), with a one-page brand sheet in `brand/brand-sheet.html`.

## Added for go-live

- **Sign-up under the owner's control**: in **Settings → Shop sign-up** choose "shops register, I approve each one" or "only I create accounts". New registrations alert the owner (phone notification + badge) and appear under **Shops → Needs your action** with **Approve** and **Reject**. An approved shop gets a notification.
- **Forgot password**: the login page sends a request to the owner, who sets a new password from **Shops** and sends it on WhatsApp in one tap.
- **Invite shops** (**Shops → Invite shops**): a printable A4 poster with a QR code to the site, and a ready WhatsApp invite message.
- **Remove sample products** (**Inventory**): clears the starter catalogue before real shops start ordering.
- **Owner password rescue**: set `OWNER_RESET_PASSWORD` in the hosting settings, redeploy or restart, sign in with it, then delete the variable. It is applied once per value.
- **Go-live guide**: `docs/Lahore-Mobile-Go-Live-Guide.pdf` (Roman Urdu), step by step from deploy to daily use.

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
| `DEMO` | off | `DEMO=1` adds sample shops, orders and messages (all shops' password: `shop123`) |
| `COOKIE_SECURE` | off | Set to `1` when served over HTTPS |
| `VAPID_SUBJECT` | `mailto:admin@example.com` | Contact for push services; set it to your own email, e.g. `mailto:you@yourdomain.pk` |

**Back up `DATA_DIR`.** It holds all your business data. The server keeps 14 daily copies in `DATA_DIR/backups/`, and **Settings → Backup** downloads a full copy you can keep elsewhere. To go back to a daily copy, stop the server, copy that file over `DATA_DIR/lahore-mobile.db`, and start it again.

## Deploy on Netlify (recommended, no server to look after)

Netlify serves the app and runs the backend as one function (`netlify/functions/api.mjs`). Data and photos are kept in **Netlify Blobs**, which comes with every Netlify site, so there is no database to set up.

1. On [app.netlify.com](https://app.netlify.com): **Add new site → Import an existing project → GitHub**, and pick this repository and branch. The build settings come from `netlify.toml`; leave them as they are.
2. Before the first deploy, open **Site configuration → Environment variables** and add:
   - `ADMIN_PHONE`: the owner's mobile number, e.g. `03036603409`
   - `ADMIN_PASSWORD`: the owner's first password (6+ characters; change it later from the app)
   - optional `VAPID_SUBJECT`: `mailto:` + an email address, used for phone notifications
   - only if the owner password is lost: `OWNER_RESET_PASSWORD` (see above)
3. Deploy. Open the site, sign in with that number and password, and edit everything else from the admin panel.
4. Optional: **Domain management** to connect your own domain (e.g. `lahoremobile.pk`). HTTPS is automatic.

Every later `git push` redeploys the site, and installed apps update themselves.

Differences from the Node server: live updates arrive by checking every 30 seconds instead of instantly, and backups are the **Settings → Backup** download (Netlify Blobs has no daily copies of its own, so save a backup each week). Netlify's free plan has monthly usage limits; a few dozen shops fit comfortably, and the usage page in Netlify shows where you stand.

## Deploy on your own server

Any server that runs Node 22 works: a small VPS (Hostinger, DigitalOcean or a local Pakistani host, roughly Rs 1,500–3,000 per month), Railway, or Fly.io. The hosting must keep a **persistent disk** for `DATA_DIR`; free tiers that wipe the disk on restart will lose your data. Put it behind HTTPS (Caddy or Nginx with Let's Encrypt), set `COOKIE_SECURE=1`, and point a domain such as `lahoremobile.pk` at it. Once it is on HTTPS, shops can install it from Chrome or Safari.

**Updating the app later:** copy the new files over the old ones (or `git pull`) and restart the server. That is all: installed apps update themselves. Do not delete `DATA_DIR`.

## Demo mode

If no server is reachable (for example on static hosting, or in the claude.ai artifact preview), the same business logic runs inside the browser on sample data saved in that browser. A yellow bar marks demo mode. Use it to show the app; it is not for real use.

## Tests

```bash
node test/core.test.js
```

Runs 30 business-rule tests: pricing, MOQ, stock, payments, claims, rollback, permissions, lockout, special prices, flash deals, suppliers, barcodes, push targeting, app content editing and spreadsheet import.

```bash
node test/webpush.test.js
```

Checks the push encryption against the RFC 8291 test vector and the VAPID signature.

```bash
node test/server.test.js
node test/netlify.test.js
```

The first tests HTTP, cookies, live events, uploads, push delivery (decrypted by a fake push service), the update stamp on `sw.js`, cache revalidation and persistence across restarts. The second runs the Netlify function against an in-memory imitation of Netlify Blobs, including racing writes.

## Code layout

```
core/core.js         all business rules and the API (shared by server and demo)
core/memstore.js     transactional in-memory store
server/server.js     HTTP server, SQLite persistence, sessions, live updates, uploads, daily backups, update stamp
server/webpush.js    Web Push (VAPID + aes128gcm), no dependencies
netlify/functions/api.mjs  the same backend as a Netlify Function, data in Netlify Blobs
netlify.toml, tools/netlify-build.js   Netlify build: copies the app to dist/ and stamps the version
js/extras.js         notifications, deals, suppliers, scanning, printing
js/site-editor.js    app content editor, Excel (CSV) import and export
js/api.js            client: server mode or in-browser demo mode
js/router.js         navigation, cart, helpers
js/shop.js           shop-facing screens
js/admin.js          admin panel
js/main.js           header, tabs, live refresh, install prompt, automatic updates
sw.js                offline cache; its version changes with every deploy
brand/               logo files and brand sheet
tools/build-artifact.py   single-page demo build for claude.ai artifacts
```

## Photos

`assets/img/` has free stock photos from Unsplash used as placeholders. Upload real product photos from **Inventory → product → Upload photo**.
