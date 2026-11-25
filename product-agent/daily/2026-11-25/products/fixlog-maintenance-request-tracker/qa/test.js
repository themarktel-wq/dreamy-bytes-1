const C = require('./core.js'); let n = 0, bad = 0;
function eq(a, b, m) { n++; if (JSON.stringify(a) !== JSON.stringify(b)) { bad++; console.log('FAIL', m, '\n  got     ', JSON.stringify(a), '\n  expected', JSON.stringify(b)); } }
const units = [{ id: 'u1', name: '1A', tenant: 'Ana', tenantEmail: 'ana@example.com', tenantPhone: '+1 555-0101' }, { id: 'u2', name: '2B', tenant: 'Ben' }];
const R = [
 { id: 'r1', unitId: 'u1', title: 'Leaking tap', priority: 'normal', status: 'new', opened: '2026-11-01', cost: '' },
 { id: 'r2', unitId: 'u1', title: 'No heat', priority: 'urgent', status: 'in_progress', opened: '2026-11-20', cost: 150 },
 { id: 'r3', unitId: 'u2', title: 'Broken lock', priority: 'high', status: 'done', opened: '2026-03-02', completed: '2026-03-04', cost: 85.5, vendor: 'Locksmith' },
 { id: 'r4', unitId: 'u2', title: 'Old job', priority: 'low', status: 'done', opened: '2025-12-30', completed: '2026-01-03', cost: 40 },
 { id: 'r5', unitId: 'u1', title: 'Paint', priority: 'low', status: 'scheduled', opened: '2026-11-24', scheduled: '2026-12-01' }];
eq(C.ageDays(R[0], '2026-11-25'), 24, 'age 24 days'); eq(C.ageDays({ opened: 'bad' }, '2026-11-25'), 0, 'bad date age 0');
eq(C.isOverdue(R[0], '2026-11-25'), true, 'normal open 24 days > 14 overdue'); eq(C.isOverdue(R[1], '2026-11-25'), true, 'urgent 5 days > 2 overdue'); eq(C.isOverdue(R[1], '2026-11-22'), false, 'urgent 2 days is not over limit 2');
eq(C.isOverdue(R[2], '2026-11-25'), false, 'done never overdue'); eq(C.isOverdue(R[4], '2026-11-25'), false, 'low 1 day fine');
eq(C.isOverdue(R[0], '2026-11-25', { normal: 30 }), false, 'custom limit respected');
eq(C.openList(R, '2026-11-25').map(r => r.id), ['r2', 'r1', 'r5'], 'open sorted by priority then age; done excluded');
const s = C.annualSummary(R, units, 2026);
eq(s.rows.find(r => r.unitId === 'u1'), { unitId: 'u1', name: '1A', count: 3, cost: 150 }, 'unit 1A 2026: 3 requests, cost 150 (blank cost counts as 0)');
eq(s.rows.find(r => r.unitId === 'u2'), { unitId: 'u2', name: '2B', count: 2, cost: 125.5 }, 'unit 2B 2026: locksmith 85.5 + old job completed 2026-01-03 40');
eq(s.total, { count: 5, cost: 275.5 }, 'total 2026'); eq(C.annualSummary(R, units, 2025).total, { count: 0, cost: 0 }, 'job opened 2025 but completed 2026 counts in 2026 only');
eq(C.annualSummary([{ unitId: 'zz', opened: '2026-01-01', cost: 9 }], units, 2026).total, { count: 0, cost: 0 }, 'unknown unit ignored');
eq(C.annualSummary([{ unitId: 'u1', opened: '2026-01-01', cost: '0.1' }, { unitId: 'u1', opened: '2026-01-02', cost: '0.2' }], units, 2026).total.cost, 0.3, 'cent rounding 0.1+0.2');
eq(C.unitHistory(R, 'u1').map(r => r.id), ['r5', 'r2', 'r1'], 'history newest first');
// CSV
eq(C.csvCell('a,b'), '"a,b"', 'comma quoted'); eq(C.csvCell('say "hi"'), '"say ""hi"""', 'quote doubled'); eq(C.csvCell('=1+1'), "'=1+1", 'formula injection guarded'); eq(C.csvCell('line1\nline2'), '"line1\nline2"', 'newline quoted'); eq(C.csvCell(null), '', 'null empty'); eq(C.csvCell(85.5), '85.5', 'number');
const csv = C.toCsv(R.slice(2, 3), units); eq(csv.split('\r\n').length, 2, 'header + 1 row'); eq(csv.split('\r\n')[1].startsWith('2B,Broken lock'), true, 'row starts with unit name and title');
// links
eq(C.mailtoLink('a@x.com', 'Fix & go', 'Line 1\nLine 2'), 'mailto:a@x.com?subject=Fix%20%26%20go&body=Line%201%0ALine%202', 'mailto encoding');
eq(C.whatsappLink('+1 (555) 010-0101', 'Hi there'), 'https://wa.me/15550100101?text=Hi%20there', 'whatsapp digits only');
// messages
const set = { landlord: 'Sam' };
eq(C.statusMessage('scheduled', R[2], units[1], set).includes('Locksmith') && C.statusMessage('scheduled', Object.assign({}, R[4], { scheduled: '2026-12-01' }), units[0], set).includes('Dec 1, 2026'), true, 'scheduled message names vendor and pretty date');
eq(C.statusMessage('completed', R[2], units[1], set).includes('Mar 4, 2026'), true, 'completed date');
eq(C.statusMessage('scheduled', { title: 'x' }, units[0], set).includes('to be confirmed'), true, 'missing date handled');
eq(C.statusMessage('delayed', Object.assign({}, R[0], { notes: 'waiting on parts' }), units[0], set).includes('waiting on parts'), true, 'delayed includes note');
eq(['received', 'scheduled', 'delayed', 'completed'].every(k => !/undefined|NaN|\[object/.test(C.statusMessage(k, R[0], units[0], set))), true, 'no undefined in any message');
eq(C.tenantRequestText(units[0], set).includes('1A') && C.tenantRequestText(units[0], set).includes('Sam'), true, 'request text has unit and landlord');
console.log(n + ' assertions, ' + bad + ' failed'); process.exit(bad ? 1 : 0);
