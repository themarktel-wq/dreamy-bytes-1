/* Skillstack — admin panel: create access codes after payment, send them on WhatsApp, revoke/restore. */
(function () {
  const PKEY = "skillstack_admin_pw";
  const $ = (s) => document.querySelector(s);
  const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  let PW = (() => { try { return sessionStorage.getItem(PKEY) || ""; } catch (e) { return ""; } })();
  let PRODUCTS = [];
  const SITE = location.origin;

  async function api(method, body) {
    const r = await fetch("/api/admin", { method, headers: { "content-type": "application/json", "x-admin-password": PW }, body: body ? JSON.stringify(body) : undefined });
    const d = await r.json().catch(() => ({}));
    if (r.status === 401) { logout(); throw new Error(d.error || "Wrong password"); }
    if (!r.ok) throw new Error(d.error || "Request failed");
    return d;
  }

  function logout() { PW = ""; try { sessionStorage.removeItem(PKEY); } catch (e) {} $("#panel").hidden = true; $("#login").hidden = false; }

  async function load() {
    const d = await api("GET");
    $("#login").hidden = true; $("#panel").hidden = false;
    if (!PRODUCTS.length) {
      PRODUCTS = d.products;
      const groups = {};
      PRODUCTS.forEach((p) => (groups[p.cat] = groups[p.cat] || []).push(p));
      $("#prod-list").innerHTML = Object.values(groups).map((g) => g.map((p) =>
        `<label class="pick"><input type="checkbox" value="${esc(p.slug)}"> ${esc(p.name)}</label>`).join("")).join("");
    }
    const rows = d.codes;
    $("#stat-codes").textContent = rows.length;
    $("#stat-active").textContent = rows.filter((r) => r.active).length;
    $("#stat-dl").textContent = rows.reduce((a, r) => a + (r.downloads || 0), 0);
    $("#codes").innerHTML = rows.length ? rows.map((r) => `
      <tr class="${r.active ? "" : "off"}">
        <td><b>${esc(r.name)}</b><br><small>${esc(r.contact)}</small></td>
        <td><code>${esc(r.code)}</code></td>
        <td>${r.all ? "All-Access" : r.count + " product" + (r.count > 1 ? "s" : "")}</td>
        <td>${new Date(r.created).toLocaleDateString("en-PK", { day: "numeric", month: "short" })}</td>
        <td>${r.downloads || 0}</td>
        <td class="acts">${r.active ? `<button data-wa="${esc(r.code)}" data-name="${esc(r.name)}" data-contact="${esc(r.contact)}">WhatsApp</button><button data-revoke="${esc(r.code)}">Revoke</button>` : `<button data-restore="${esc(r.code)}">Restore</button>`}</td>
      </tr>`).join("") : '<tr><td colspan="6" class="muted">No access codes yet. Create the first one above.</td></tr>';
  }

  function waLink(contact, name, code) {
    const link = `${SITE}/access.html?code=${encodeURIComponent(code)}`;
    const msg = `Assalam o Alaikum ${name}! 💚 Payment received, shukriya.\n\nYour Skillstack library is ready:\n${link}\n\nAccess code: ${code}\n\nOpen the link on your phone or laptop and tap Download on any product. Keep this code safe, it's your personal access.`;
    let num = String(contact || "").replace(/[^0-9]/g, "");
    if (num.startsWith("0")) num = "92" + num.slice(1);
    return `https://wa.me/${num.length >= 11 ? num : ""}?text=${encodeURIComponent(msg)}`;
  }

  $("#login-form").addEventListener("submit", async (e) => {
    e.preventDefault(); PW = $("#pw").value; $("#login-msg").textContent = "";
    try { await load(); try { sessionStorage.setItem(PKEY, PW); } catch (e) {} }
    catch (err) { $("#login-msg").textContent = err.message; }
  });

  $("#all").addEventListener("change", (e) => { $("#prod-list").classList.toggle("disabled", e.target.checked); });

  $("#create").addEventListener("submit", async (e) => {
    e.preventDefault();
    const out = $("#result"); out.hidden = true;
    const all = $("#all").checked;
    const products = [...document.querySelectorAll("#prod-list input:checked")].map((i) => i.value);
    try {
      const d = await api("POST", { action: "create", name: $("#c-name").value, contact: $("#c-contact").value, all, products, note: $("#c-note").value });
      const c = d.code;
      out.innerHTML = `<b>Access created ✓</b><div class="big-code">${esc(c.code)}</div>
        <p>Library link: <a href="/access.html?code=${encodeURIComponent(c.code)}" target="_blank">${SITE}/access.html?code=${esc(c.code)}</a></p>
        <a class="btn btn-wa" target="_blank" rel="noopener" href="${waLink(c.contact, c.name, c.code)}">Send on WhatsApp</a>`;
      out.hidden = false;
      $("#create").reset(); $("#prod-list").classList.remove("disabled");
      load();
    } catch (err) { out.innerHTML = `<span class="err">${esc(err.message)}</span>`; out.hidden = false; }
  });

  $("#codes").addEventListener("click", async (e) => {
    const b = e.target.closest("button"); if (!b) return;
    try {
      if (b.dataset.wa) window.open(waLink(b.dataset.contact, b.dataset.name, b.dataset.wa), "_blank", "noopener");
      if (b.dataset.revoke && confirm("Revoke access for this code? The customer will no longer be able to download.")) { await api("POST", { action: "revoke", code: b.dataset.revoke }); load(); }
      if (b.dataset.restore) { await api("POST", { action: "restore", code: b.dataset.restore }); load(); }
    } catch (err) { alert(err.message); }
  });
  $("#search").addEventListener("input", (e) => {
    const t = e.target.value.toLowerCase();
    document.querySelectorAll("#codes tr").forEach((tr) => { tr.style.display = tr.textContent.toLowerCase().includes(t) ? "" : "none"; });
  });
  $("#logout").addEventListener("click", (e) => { e.preventDefault(); logout(); });

  if (PW) load().catch(() => logout());
})();
