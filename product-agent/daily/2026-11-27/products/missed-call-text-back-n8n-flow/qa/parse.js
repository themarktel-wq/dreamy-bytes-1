const c = $('Config').first().json, b = $('Normalize').first().json;
const text = String(b.text || '').trim().slice(0, 1000), lower = text.toLowerCase();
const now = /^\d{4}-\d{2}-\d{2}/.test(String(c.testNow || '')) ? new Date(c.testNow).toISOString() : new Date().toISOString();
if (/^\s*(stop|stopall|unsubscribe|cancel|end|quit)\s*$/i.test(text)) return [{ json: { optOut: true, row: { received_at: now, phone: b.from, name: '', address: '', job_type: '', details: text, urgency: '', status: 'opted_out' } } }];
const parts = text.split(/(?:^|\s)([1-4])[).:\-]\s*/), f = {};
for (let i = 1; i + 1 < parts.length; i += 2) f[parts[i]] = parts[i + 1].trim();
const words = String(c.urgentWords || 'emergency,flood,flooding,burst,no heat,no hot water,gas smell,gas leak,sparks,smoke,asap,urgent').split(',').map(s => s.trim().toLowerCase()).filter(Boolean);
const yes = /^(y|yes|yeah|urgent|asap)\b/i.test(f['4'] || '');
const urgent = yes || words.some(w => lower.includes(w));
const jobText = f['3'] || text;
const groups = { Plumbing: ['leak', 'pipe', 'drain', 'clog', 'toilet', 'faucet', 'tap', 'water heater', 'sewer', 'sink'], HVAC: ['heat', 'furnace', 'a/c', 'air condition', 'cooling', 'thermostat', 'boiler', ' ac '], Electrical: ['outlet', 'breaker', 'wiring', 'power', 'panel', 'sparks'] };
let job = 'Other'; const jl = (' ' + jobText.toLowerCase() + ' ');
for (const [k, ws] of Object.entries(groups)) { if (ws.some(w => jl.includes(w))) { job = k; break; } }
const row = { received_at: now, phone: b.from, name: f['1'] || '', address: f['2'] || '', job_type: job, details: jobText.slice(0, 300), urgency: urgent ? 'URGENT' : 'normal', status: Object.keys(f).length ? 'Reply received' : 'Reply received (unstructured)' };
return [{ json: { optOut: false, row } }];
