// /api/download?code=SK-XXXX-XXXX&p=<slug> — streams a purchased product file.
import { readFile } from "node:fs/promises";
import { json, getCode, saveCode, normCode, productsFor, productFilePath } from "../lib/core.mjs";

const MIME = {
  pdf: "application/pdf",
  xlsx: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  docx: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
};

export default async (req) => {
  const u = new URL(req.url);
  const code = normCode(u.searchParams.get("code"));
  const slug = String(u.searchParams.get("p") || "");
  const rec = code && (await getCode(code));
  if (!rec || !rec.active) return json({ error: "Access code not valid" }, 403);
  const prod = productsFor(rec).find((p) => p.slug === slug);
  if (!prod) return json({ error: "This product is not included in your access" }, 403);
  const file = await productFilePath(prod.file);
  if (!file) return json({ error: "File temporarily unavailable. Please contact support." }, 500);
  const data = await readFile(file);
  rec.downloads = (rec.downloads || 0) + 1;
  rec.lastDownload = new Date().toISOString();
  await saveCode(rec);
  return new Response(data, {
    headers: {
      "content-type": MIME[prod.fmt] || "application/octet-stream",
      "content-disposition": `attachment; filename="Skillstack-${prod.file}"`,
      "cache-control": "private, no-store",
    },
  });
};

export const config = { path: "/api/download" };
