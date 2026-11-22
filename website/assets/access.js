/* Skillstack — customer library: enter access code, see & download purchased products. */
(function () {
  const KEY = "skillstack_access_code";
  const form = document.querySelector("#access-form");
  const input = document.querySelector("#access-code");
  const msg = document.querySelector("#access-msg");
  const lib = document.querySelector("#library");
  const gate = document.querySelector("#gate");
  const COV = (window.SKILLSTACK_COVERS || {});
  const get = (k) => { try { return localStorage.getItem(k); } catch (e) { return null; } };
  const set = (k, v) => { try { v ? localStorage.setItem(k, v) : localStorage.removeItem(k); } catch (e) {} };
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  async function open(code) {
    msg.textContent = "Checking your code…"; msg.className = "notice";
    try {
      const r = await fetch("/api/library?code=" + encodeURIComponent(code));
      const d = await r.json();
      if (!r.ok) throw new Error(d.error || "Something went wrong");
      set(KEY, d.code);
      render(d);
    } catch (e) {
      msg.textContent = e.message; msg.className = "notice err";
      lib.hidden = true; gate.hidden = false;
    }
  }

  function render(d) {
    gate.hidden = true; lib.hidden = false;
    document.querySelector("#lib-name").textContent = d.name.split(" ")[0];
    document.querySelector("#lib-count").textContent = d.products.length + (d.all ? " products · All-Access" : d.products.length === 1 ? " product" : " products");
    document.querySelector("#lib-code").textContent = d.code;
    const q = document.querySelector("#lib-q");
    const draw = () => {
      const t = (q.value || "").toLowerCase();
      const items = d.products.filter((p) => !t || (p.name + " " + p.catName).toLowerCase().includes(t));
      document.querySelector("#lib-grid").innerHTML = items.map((p) => `
        <article class="card lib-card">
          <div class="card-media">${COV[p.slug] || ""}</div>
          <div class="card-body">
            <span class="card-cat">${esc(p.catName)}</span>
            <h3>${esc(p.name)}</h3>
            <p>${esc(p.tagline)}</p>
            <a class="btn btn-primary btn-block" href="/api/download?code=${encodeURIComponent(d.code)}&p=${encodeURIComponent(p.slug)}">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
              Download ${({ pdf: "PDF", xlsx: "Excel", docx: "Word" })[p.fmt] || "file"}</a>
          </div>
        </article>`).join("") || '<div class="empty">No products match your search.</div>';
    };
    q.oninput = draw; draw();
  }

  form.addEventListener("submit", (e) => { e.preventDefault(); const c = input.value.trim(); if (c) open(c); });
  document.querySelector("#lib-logout").addEventListener("click", (e) => {
    e.preventDefault(); set(KEY, null); lib.hidden = true; gate.hidden = false; input.value = ""; msg.textContent = ""; msg.className = "";
  });

  const fromUrl = new URLSearchParams(location.search).get("code");
  const saved = fromUrl || get(KEY);
  if (saved) { input.value = saved; open(saved); }
})();
