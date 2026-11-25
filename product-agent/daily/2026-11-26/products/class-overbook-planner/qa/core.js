// ---- CORE (pure functions, unit-tested in Node). Model: each booked person independently attends with probability q = 1 - noShowRate. ----
function logChoose(n, k) { var s = 0, i; if (k > n - k) k = n - k; for (i = 1; i <= k; i++) s += Math.log(n - k + i) - Math.log(i); return s; }
function binomPmf(n, q) { // array pmf[0..n] of attendees
  var out = [], k;
  if (!(n >= 0) || n !== Math.floor(n)) return [1];
  q = Math.min(1, Math.max(0, q));
  for (k = 0; k <= n; k++) {
    if (q === 0) out.push(k === 0 ? 1 : 0); else if (q === 1) out.push(k === n ? 1 : 0);
    else out.push(Math.exp(logChoose(n, k) + k * Math.log(q) + (n - k) * Math.log(1 - q)));
  }
  return out;
}
function metrics(bookings, cap, noShow, price, turnAwayCost) {
  var q = 1 - noShow, pmf = binomPmf(bookings, q), pOver = 0, eTurn = 0, eEmpty = 0, eServed = 0, eAtt = 0, pFull = 0, k;
  for (k = 0; k < pmf.length; k++) {
    var p = pmf[k]; eAtt += k * p; eServed += Math.min(k, cap) * p;
    if (k > cap) { pOver += p; eTurn += (k - cap) * p; } else { eEmpty += (cap - k) * p; }
    if (k >= cap) pFull += p;
  }
  var net = price * eServed - turnAwayCost * eTurn;
  return { bookings: bookings, pOver: pOver, pFull: pFull, eTurn: eTurn, eEmpty: eEmpty, eServed: eServed, eAttend: eAtt, revenue: price * eServed, turnCost: turnAwayCost * eTurn, net: net, pmf: pmf };
}
function compare(cap, noShow, price, turnAwayCost, maxExtra) {
  var rows = [], e; for (e = 0; e <= maxExtra; e++) { var m = metrics(cap + e, cap, noShow, price, turnAwayCost); m.extra = e; rows.push(m); }
  var best = rows[0]; rows.forEach(function (r) { if (r.net > best.net + 1e-9) best = r; }); return { rows: rows, bestExtra: best.extra };
}
function policyText(o) { // o: {studio, cap, bookings, noShowPct, pOverPct, remedy}
  return (o.studio || 'Our studio') + ' booking policy\n\nThis class has ' + o.cap + ' spots. Because some booked people do not attend (about ' + o.noShowPct + '% of bookings, based on our own records), we accept up to ' + o.bookings + ' bookings. In the unlikely event that more than ' + o.cap + ' people arrive, ' + (o.remedy || 'the last people to check in will be offered a spot in the next class and a class credit') + '. Cancel at least [CANCELLATION WINDOW] before the class to release your spot.';
}
if (typeof module !== 'undefined') module.exports = { binomPmf: binomPmf, metrics: metrics, compare: compare, policyText: policyText };
