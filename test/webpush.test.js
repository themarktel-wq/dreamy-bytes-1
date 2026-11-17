/* Web Push encryption against the RFC 8291 §5 example, plus a VAPID signature check. Run: node test/webpush.test.js */
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs'), os = require('node:os'), path = require('node:path');
const { encrypt, loadVapid, vapidHeader } = require('../server/webpush.js');

const out = encrypt('When I grow up, I want to be a watermelon',
  'BCVxsr7N_eNgVRqvHtD0zTZsEc6-VV-JvLexhqUzORcxaOzi6-AYWXvTBHm4bjyPjs7Vd8pZGH6SRpkNtoIAiw4',
  'BTBZMqHH6r4Tts7J_aSIgg',
  { asPrivate: Buffer.from('yfWPiYE-n46HLnH0KqZOF1fJJU3MYrct3AELtAQ-oRw', 'base64url'), salt: Buffer.from('DGv6ra1nlYgDCS1FRnbzlw', 'base64url') });
assert.equal(out.toString('base64url'),
  'DGv6ra1nlYgDCS1FRnbzlwAAEABBBP4z9KsN6nGRTbVYI_c7VJSPQTBtkgcy27mlmlMoZIIgDll6e3vCYLocInmYWAmS6TlzAC8wEqKK6PBru3jl7A_yl95bQpu6cVPTpK4Mqgkf1CXztLVBSt2Ks3oZwbuwXPXLWyouBWLVWGNWQexSgSxsj_Qulcy4a-fN');
console.log('  ✓ matches the RFC 8291 test vector');

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'vapid-'));
const v = loadVapid(path.join(dir, 'vapid.json'));
const again = loadVapid(path.join(dir, 'vapid.json'));
assert.equal(v.publicKeyB64, again.publicKeyB64, 'key pair is persisted');
const h = vapidHeader('https://fcm.googleapis.com/fcm/send/abc', v, 'mailto:owner@example.com');
const [, jwt] = /t=([^,]+)/.exec(h); const [hd, cl, sig] = jwt.split('.');
const pub = crypto.createPublicKey({ key: { kty: 'EC', crv: 'P-256', x: Buffer.from(v.publicKey.subarray(1, 33)).toString('base64url'), y: Buffer.from(v.publicKey.subarray(33)).toString('base64url') }, format: 'jwk' });
assert.ok(crypto.verify('sha256', Buffer.from(`${hd}.${cl}`), { key: pub, dsaEncoding: 'ieee-p1363' }, Buffer.from(sig, 'base64url')));
assert.equal(JSON.parse(Buffer.from(cl, 'base64url')).aud, 'https://fcm.googleapis.com');
fs.rmSync(dir, { recursive: true });
console.log('  ✓ VAPID JWT is a valid ES256 signature for the push service origin');
