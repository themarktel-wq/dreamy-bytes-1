// /api/admin — create, list, revoke and restore access codes (password protected).
import { isAdmin, json, newCode, getCode, saveCode, listCodes, CATALOG } from "../lib/core.mjs";

export default async (req) => {
  if (!isAdmin(req)) return json({ error: "Wrong admin password" }, 401);
  const url = new URL(req.url);

  if (req.method === "GET") {
    return json({ codes: await listCodes(), products: CATALOG.map(({ slug, name, cat }) => ({ slug, name, cat })) });
  }
  if (req.method !== "POST") return json({ error: "Method not allowed" }, 405);

  let body = {};
  try { body = await req.json(); } catch { return json({ error: "Invalid JSON" }, 400); }
  const action = body.action || url.searchParams.get("action");

  if (action === "create") {
    const name = String(body.name || "").trim().slice(0, 80);
    const contact = String(body.contact || "").trim().slice(0, 80);
    const all = !!body.all;
    const valid = new Set(CATALOG.map((p) => p.slug));
    const products = all ? [] : [...new Set((body.products || []).filter((s) => valid.has(s)))];
    if (!name) return json({ error: "Customer name is required" }, 400);
    if (!all && !products.length) return json({ error: "Choose at least one product or All-Access" }, 400);
    let code;
    for (let i = 0; i < 5; i++) { code = newCode(); if (!(await getCode(code))) break; }
    const rec = { code, name, contact, all, products, active: true, created: new Date().toISOString(),
                  note: String(body.note || "").slice(0, 200), downloads: 0 };
    await saveCode(rec);
    return json({ ok: true, code: rec });
  }

  if (action === "revoke" || action === "restore") {
    const rec = await getCode(String(body.code || ""));
    if (!rec) return json({ error: "Code not found" }, 404);
    rec.active = action === "restore";
    await saveCode(rec);
    return json({ ok: true, code: rec });
  }

  if (action === "add-products") {
    const rec = await getCode(String(body.code || ""));
    if (!rec) return json({ error: "Code not found" }, 404);
    const valid = new Set(CATALOG.map((p) => p.slug));
    if (body.all) rec.all = true;
    rec.products = [...new Set([...(rec.products || []), ...(body.products || []).filter((s) => valid.has(s))])];
    await saveCode(rec);
    return json({ ok: true, code: rec });
  }

  return json({ error: "Unknown action" }, 400);
};

export const config = { path: "/api/admin" };
