/* Web Push without dependencies: VAPID (RFC 8292) + aes128gcm payload encryption (RFC 8291 / RFC 8188). */
'use strict';
const crypto = require('node:crypto');
const fs = require('node:fs');

const b64u = (buf) => Buffer.from(buf).toString('base64url');
const fromB64u = (s) => Buffer.from(String(s), 'base64url');

/* Load or create the server's VAPID key pair (kept in DATA_DIR so subscriptions stay valid). */
function loadVapid(file) {
  let jwk;
  try { jwk = JSON.parse(fs.readFileSync(file, 'utf8')); } catch {
    jwk = newVapidJwk();
    fs.writeFileSync(file, JSON.stringify(jwk), { mode: 0o600 });
  }
  return vapidFromJwk(jwk);
}
function newVapidJwk() { return crypto.generateKeyPairSync('ec', { namedCurve: 'P-256' }).privateKey.export({ format: 'jwk' }); }
function vapidFromJwk(jwk) {
  const privateKey = crypto.createPrivateKey({ key: jwk, format: 'jwk' });
  const publicKey = Buffer.concat([Buffer.from([4]), fromB64u(jwk.x), fromB64u(jwk.y)]); // uncompressed P-256 point
  return { privateKey, publicKey, publicKeyB64: b64u(publicKey) };
}

function vapidHeader(endpoint, vapid, subject) {
  const aud = new URL(endpoint).origin;
  const header = b64u(JSON.stringify({ typ: 'JWT', alg: 'ES256' }));
  const claims = b64u(JSON.stringify({ aud, exp: Math.floor(Date.now() / 1000) + 12 * 3600, sub: subject }));
  const sig = crypto.sign('sha256', Buffer.from(`${header}.${claims}`), { key: vapid.privateKey, dsaEncoding: 'ieee-p1363' });
  return `vapid t=${header}.${claims}.${b64u(sig)}, k=${vapid.publicKeyB64}`;
}

/* RFC 8291 encryption. `asPrivate` and `salt` are only passed by the test (RFC test vector). */
function encrypt(payload, uaPublicB64, authB64, { asPrivate, salt } = {}) {
  const uaPublic = fromB64u(uaPublicB64), auth = fromB64u(authB64);
  const ecdh = crypto.createECDH('prime256v1');
  if (asPrivate) ecdh.setPrivateKey(asPrivate); else ecdh.generateKeys();
  const asPublic = ecdh.getPublicKey();
  const shared = ecdh.computeSecret(uaPublic);
  salt = salt || crypto.randomBytes(16);
  const keyInfo = Buffer.concat([Buffer.from('WebPush: info\0'), uaPublic, asPublic]);
  const ikm = Buffer.from(crypto.hkdfSync('sha256', shared, auth, keyInfo, 32));
  const cek = Buffer.from(crypto.hkdfSync('sha256', ikm, salt, Buffer.from('Content-Encoding: aes128gcm\0'), 16));
  const nonce = Buffer.from(crypto.hkdfSync('sha256', ikm, salt, Buffer.from('Content-Encoding: nonce\0'), 12));
  const cipher = crypto.createCipheriv('aes-128-gcm', cek, nonce);
  const body = Buffer.concat([cipher.update(Buffer.concat([Buffer.from(payload), Buffer.from([2])])), cipher.final(), cipher.getAuthTag()]);
  const rs = Buffer.alloc(4); rs.writeUInt32BE(4096);
  return Buffer.concat([salt, rs, Buffer.from([asPublic.length]), asPublic, body]);
}

/* Send one notification. Resolves { ok, gone } — gone means the subscription expired and should be deleted. */
async function send(sub, data, vapid, subject) {
  const body = encrypt(JSON.stringify(data), sub.keys.p256dh, sub.keys.auth);
  try {
    const r = await fetch(sub.endpoint, {
      method: 'POST',
      headers: { TTL: '86400', Urgency: 'high', 'Content-Encoding': 'aes128gcm', 'Content-Type': 'application/octet-stream', Authorization: vapidHeader(sub.endpoint, vapid, subject) },
      body,
    });
    return { ok: r.ok, gone: r.status === 404 || r.status === 410, status: r.status };
  } catch (e) { return { ok: false, gone: false, error: e.message }; }
}

module.exports = { loadVapid, newVapidJwk, vapidFromJwk, encrypt, send, vapidHeader };
