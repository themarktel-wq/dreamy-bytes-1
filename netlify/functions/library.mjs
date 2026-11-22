// /api/library?code=SK-XXXX-XXXX — returns the products a customer can download.
import { json, getCode, normCode, productsFor } from "../lib/core.mjs";

export default async (req) => {
  const code = normCode(new URL(req.url).searchParams.get("code"));
  if (!code) return json({ error: "Enter your access code" }, 400);
  const rec = await getCode(code);
  if (!rec) return json({ error: "This access code was not found. Check it and try again, or message us on WhatsApp." }, 404);
  if (!rec.active) return json({ error: "This access code is no longer active. Please contact support on WhatsApp." }, 403);
  return json({
    name: rec.name, all: rec.all, code: rec.code,
    products: productsFor(rec).map(({ slug, name, cat, catName, fmt, fmtLabel, tagline, id }) => ({ slug, name, cat, catName, fmt, fmtLabel, tagline, id })),
  });
};

export const config = { path: "/api/library" };
