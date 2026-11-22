// Skillstack access system — shared helpers (Netlify Functions v2, Node 18+).
import { readFile, writeFile, mkdir, access } from "node:fs/promises";
import { constants } from "node:fs";
import { createHash, randomBytes, timingSafeEqual } from "node:crypto";
import path from "node:path";
import { fileURLToPath } from "node:url";
import CATALOG from "./catalog.mjs";

export { CATALOG };

const HERE = path.dirname(fileURLToPath(import.meta.url));

// ---------- storage: Netlify Blobs in production, a local JSON folder for testing ----------
let _store;
export async function store() {
  if (_store) return _store;
  const local = process.env.SK_LOCAL_STORE;
  if (local) {
    await mkdir(local, { recursive: true });
    const f = (k) => path.join(local, encodeURIComponent(k) + ".json");
    _store = {
      async get(k) { try { return JSON.parse(await readFile(f(k), "utf8")); } catch { return null; } },
      async set(k, v) { await writeFile(f(k), JSON.stringify(v)); },
    };
  } else {
    const { getStore } = await import("@netlify/blobs");
    const s = getStore({ name: "skillstack-access", consistency: "strong" });
    _store = { get: (k) => s.get(k, { type: "json" }), set: (k, v) => s.setJSON(k, v) };
  }
  return _store;
}

// Codes are stored individually; an index keeps the admin list fast.
export async function getCode(code) { return (await store()).get("code:" + code); }
export async function saveCode(rec) {
  const s = await store();
  await s.set("code:" + rec.code, rec);
  const idx = (await s.get("index")) || [];
  const i = idx.findIndex((x) => x.code === rec.code);
  const row = { code: rec.code, name: rec.name, contact: rec.contact, all: rec.all, count: rec.all ? CATALOG.length : rec.products.length,
                active: rec.active, created: rec.created, downloads: rec.downloads || 0 };
  if (i >= 0) idx[i] = row; else idx.unshift(row);
  await s.set("index", idx.slice(0, 2000));
}
export async function listCodes() { return (await store()).get("index").then((x) => x || []); }

export function newCode() {
  const A = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"; // no 0/O/1/I to avoid confusion
  const b = randomBytes(8);
  let s = "";
  for (let i = 0; i < 8; i++) s += A[b[i] % A.length];
  return `SK-${s.slice(0, 4)}-${s.slice(4)}`;
}
export const normCode = (c) => String(c || "").toUpperCase().replace(/[^A-Z0-9-]/g, "").slice(0, 20);

// ---------- admin auth ----------
export function isAdmin(req) {
  const want = process.env.ADMIN_PASSWORD || "";
  const got = req.headers.get("x-admin-password") || "";
  if (want.length < 8) return false; // refuse to run with no / weak password
  const a = createHash("sha256").update(want).digest(), b = createHash("sha256").update(got).digest();
  return timingSafeEqual(a, b);
}

// ---------- products ----------
export function productsFor(rec) {
  return rec.all ? CATALOG : CATALOG.filter((p) => rec.products.includes(p.slug));
}

export async function productFilePath(file) {
  const candidates = [
    path.join(process.cwd(), "products", file),
    path.join(HERE, "..", "..", "products", file),
    path.join(HERE, "..", "..", "..", "products", file),
    path.join("/var/task", "products", file),
  ];
  for (const c of candidates) {
    try { await access(c, constants.R_OK); return c; } catch {}
  }
  return null;
}

export const json = (data, status = 200) =>
  new Response(JSON.stringify(data), { status, headers: { "content-type": "application/json", "cache-control": "no-store" } });
