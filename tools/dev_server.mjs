// Local test server: serves website/ and runs the Netlify functions for /api/* (no Netlify CLI needed).
// Usage: ADMIN_PASSWORD=testpass123 SK_LOCAL_STORE=.local-store node tools/dev_server.mjs [port]
import http from "node:http";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
process.chdir(ROOT); // like Netlify: functions run from the repo root, products/ is included
process.env.SK_LOCAL_STORE ||= path.join(ROOT, ".local-store");
const PORT = Number(process.argv[2] || 8888);
const fns = {
  "/api/admin": (await import("../netlify/functions/admin.mjs")).default,
  "/api/library": (await import("../netlify/functions/library.mjs")).default,
  "/api/download": (await import("../netlify/functions/download.mjs")).default,
};
const TYPES = { ".html": "text/html", ".css": "text/css", ".js": "text/javascript", ".svg": "image/svg+xml", ".png": "image/png", ".xml": "application/xml", ".txt": "text/plain" };

http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);
  const fn = fns[url.pathname];
  if (fn) {
    const chunks = [];
    for await (const c of req) chunks.push(c);
    const r = await fn(new Request(url, { method: req.method, headers: req.headers, body: ["GET", "HEAD"].includes(req.method) ? undefined : Buffer.concat(chunks) }));
    res.writeHead(r.status, Object.fromEntries(r.headers));
    res.end(Buffer.from(await r.arrayBuffer()));
    return;
  }
  let p = url.pathname === "/" ? "/index.html" : url.pathname;
  if (p === "/admin" || p === "/access") p += ".html";
  try {
    const data = await readFile(path.join(ROOT, "website", path.normalize(p)));
    res.writeHead(200, { "content-type": TYPES[path.extname(p)] || "application/octet-stream" });
    res.end(data);
  } catch { res.writeHead(404); res.end("Not found"); }
}).listen(PORT, () => console.log(`Skillstack dev server: http://localhost:${PORT}  (admin: /admin)`));
