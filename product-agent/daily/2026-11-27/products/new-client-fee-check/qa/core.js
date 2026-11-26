// ---- CORE (pure functions, unit-tested in Node) ----
function num(v, d) { var n = Number(v); return (v === '' || v === null || v === undefined || !isFinite(n)) ? (d === undefined ? 0 : d) : n; }
function expectedVisits(rebookPct, repeatVisits) { var r = Math.min(100, Math.max(0, num(rebookPct))) / 100; return 1 + r * Math.max(0, num(repeatVisits)); }
function firstVisitFee(ticket, feePct, minFee) { var f = Math.max(0, num(feePct)), m = Math.max(0, num(minFee)); if (f === 0 && m === 0) return 0; return Math.max(m, f / 100 * Math.max(0, num(ticket))); }
// inp: {ticket, marginPct, rebookPct, repeatVisits, newPerMonth, anywayPct}; pf: {name, monthly, feePct, minFee}
function evaluate(pf, inp) {
  var ticket = Math.max(0, num(inp.ticket)), margin = Math.min(100, Math.max(0, num(inp.marginPct, 100))) / 100, n = Math.max(0, num(pf.newPerMonth !== undefined && pf.newPerMonth !== '' ? pf.newPerMonth : inp.newPerMonth)), any = Math.min(100, Math.max(0, num(inp.anywayPct))) / 100;
  var visits = expectedVisits(inp.rebookPct, inp.repeatVisits), fee = firstVisitFee(ticket, pf.feePct, pf.minFee), sub = Math.max(0, num(pf.monthly));
  var perVisit = ticket * margin, value = perVisit * visits;            // 12-month contribution from one new client
  var allIn = n > 0 ? fee + sub / n : fee;                                // fee plus subscription spread over the new clients per month
  var trulyNew = n * (1 - any);
  var costPerTrulyNew = trulyNew > 0 ? (n * fee + sub) / trulyNew : null; // what each genuinely new client costs
  var monthlyNet = trulyNew * value - n * fee - sub;
  var be = perVisit > 0 ? allIn / perVisit : null;                        // visits (incl. the first) needed to cover the all-in cost
  var beRebook = null, beNote = '';
  if (be === null) beNote = 'No margin per visit';
  else if (be <= 1) beNote = 'First visit already covers it';
  else { var rv = Math.max(0, num(inp.repeatVisits)); if (rv === 0) beNote = 'Needs repeat visits'; else { beRebook = (be - 1) / rv * 100; beNote = beRebook > 100 ? 'Not reachable at these inputs' : ''; } }
  return { name: pf.name, fee: fee, sub: sub, visits: visits, value: value, allIn: allIn, costPerTrulyNew: costPerTrulyNew, netPerClient: value - allIn, monthlyNet: monthlyNet, feePctOfValue: value > 0 ? fee / value * 100 : null, breakEvenVisits: be, breakEvenRebookPct: beRebook, breakEvenNote: beNote };
}
function evaluateAll(platforms, inp) { var rows = platforms.filter(function (p) { return p.name !== ''; }).map(function (p) { return evaluate(p, inp); }); var best = -1; rows.forEach(function (r, i) { if (best < 0 || r.monthlyNet > rows[best].monthlyNet + 1e-9) best = i; }); return { rows: rows, bestIndex: best }; }
if (typeof module !== 'undefined') module.exports = { num: num, expectedVisits: expectedVisits, firstVisitFee: firstVisitFee, evaluate: evaluate, evaluateAll: evaluateAll };
