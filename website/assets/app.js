/* Hunarly storefront — cart, checkout, animations. No dependencies. */
(function () {
  const CFG = window.HUNARLY || {};
  const PRODUCTS = CFG.products || [];
  const BY_SLUG = Object.fromEntries(PRODUCTS.map(p => [p.slug, p]));
  const KEY = "hunarly_cart_v1";
  const px = (ev, data) => { try { if (window.fbq) window.fbq("track", ev, data); } catch (e) {} };
  const fmt = n => "Rs " + Number(n).toLocaleString("en-PK");

  // ---------- storage (safe) ----------
  const store = {
    get() { try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch (e) { return []; } },
    set(v) { try { localStorage.setItem(KEY, JSON.stringify(v)); } catch (e) {} }
  };
  let cart = store.get().filter(s => BY_SLUG[s]);

  function save() { store.set(cart); renderCount(); document.dispatchEvent(new Event("cart")); }
  function add(slug) {
    if (slug === CFG.bundle.slug) { cart = [slug]; }
    else {
      if (cart.includes(CFG.bundle.slug)) { toast("All-Access Pass already includes every product ✨", true); return; }
      if (!cart.includes(slug)) cart.push(slug);
    }
    save();
    px("AddToCart", { content_ids: [slug], value: BY_SLUG[slug].price, currency: "PKR" });
    toast(`<b>${BY_SLUG[slug].name}</b> added to cart`, true);
  }
  function remove(slug) { cart = cart.filter(s => s !== slug); save(); }
  function totals() {
    const items = cart.map(s => BY_SLUG[s]);
    const subtotal = items.reduce((a, p) => a + p.price, 0);
    const mrp = items.reduce((a, p) => a + p.mrp, 0);
    return { items, subtotal, mrp, total: subtotal };
  }

  // ---------- UI helpers ----------
  function renderCount() {
    document.querySelectorAll(".cart-count").forEach(el => {
      el.textContent = cart.length;
      el.classList.toggle("show", cart.length > 0);
    });
  }
  let toastTimer;
  function toast(html, withLink) {
    let t = document.querySelector(".toast");
    if (!t) { t = document.createElement("div"); t.className = "toast"; document.body.appendChild(t); }
    t.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg><span>${html}</span>` + (withLink ? `<a href="${CFG.root}cart.html">View cart →</a>` : "");
    requestAnimationFrame(() => t.classList.add("show"));
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => t.classList.remove("show"), 3200);
  }

  document.addEventListener("click", e => {
    const a = e.target.closest("[data-add]");
    if (a) { e.preventDefault(); add(a.dataset.add); }
    const b = e.target.closest("[data-buy]");
    if (b) { e.preventDefault(); add(b.dataset.buy); location.href = CFG.root + "cart.html"; }
    const r = e.target.closest("[data-remove]");
    if (r) { e.preventDefault(); remove(r.dataset.remove); }
    const m = e.target.closest(".menu-btn");
    if (m) document.querySelector(".mobile-nav").classList.toggle("open");
  });

  // ---------- reveal on scroll ----------
  const io = "IntersectionObserver" in window ? new IntersectionObserver(es => {
    es.forEach(en => { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
  }, { threshold: 0.12 }) : null;
  document.querySelectorAll(".reveal").forEach(el => io ? io.observe(el) : el.classList.add("in"));

  // ---------- counters ----------
  document.querySelectorAll("[data-count]").forEach(el => {
    const end = +el.dataset.count, pre = el.dataset.pre || "", suf = el.dataset.suf || "";
    const run = () => {
      const t0 = performance.now(), d = 1600;
      const step = t => {
        const k = Math.min(1, (t - t0) / d), v = Math.round(end * (1 - Math.pow(1 - k, 3)));
        el.textContent = pre + v.toLocaleString("en-PK") + suf;
        if (k < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    };
    if (!io) return run();
    const o = new IntersectionObserver(es => { if (es[0].isIntersecting) { run(); o.disconnect(); } });
    o.observe(el);
  });

  // ---------- word rotator ----------
  const rot = document.querySelector(".rotator");
  if (rot) {
    const words = rot.dataset.words.split("|"); let i = 0;
    setInterval(() => { i = (i + 1) % words.length; rot.innerHTML = `<span class="grad-text">${words[i]}</span>`; }, 2400);
  }

  // ---------- 3D tilt ----------
  if (matchMedia("(hover:hover)").matches && !matchMedia("(prefers-reduced-motion:reduce)").matches) {
    document.querySelectorAll("[data-tilt]").forEach(el => {
      el.addEventListener("mousemove", e => {
        const r = el.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
        el.style.transform = `perspective(900px) rotateY(${x * 8}deg) rotateX(${-y * 8}deg) translateY(-6px)`;
      });
      el.addEventListener("mouseleave", () => { el.style.transform = ""; });
    });
  }

  // ---------- sticky buy bar (product page) ----------
  const sticky = document.querySelector(".sticky-buy"), anchor = document.querySelector(".pdp-buy");
  if (sticky && anchor && io) {
    new IntersectionObserver(es => sticky.classList.toggle("show", !es[0].isIntersecting && es[0].boundingClientRect.top < 0)).observe(anchor);
  }

  // ---------- shop filter ----------
  const shop = document.querySelector("#shop-grid");
  if (shop) {
    const chips = document.querySelectorAll(".chip"), q = document.querySelector("#q"), sort = document.querySelector("#sort");
    let cat = new URLSearchParams(location.search).get("cat") || "all";
    const apply = () => {
      const term = (q.value || "").toLowerCase().trim();
      const cards = [...shop.querySelectorAll(".card")];
      let shown = 0;
      cards.forEach(c => {
        const ok = (cat === "all" || c.dataset.cat === cat) && (!term || c.dataset.search.includes(term));
        c.style.display = ok ? "" : "none"; if (ok) shown++;
      });
      const s = sort.value;
      cards.sort((a, b) => s === "low" ? a.dataset.price - b.dataset.price : s === "high" ? b.dataset.price - a.dataset.price : a.dataset.order - b.dataset.order)
        .forEach(c => shop.appendChild(c));
      shop.querySelector(".empty").style.display = shown ? "none" : "";
      chips.forEach(c => c.classList.toggle("on", c.dataset.cat === cat));
    };
    chips.forEach(c => c.addEventListener("click", () => { cat = c.dataset.cat; apply(); }));
    q.addEventListener("input", apply); sort.addEventListener("change", apply);
    apply();
  }

  // ---------- cart page ----------
  const cartEl = document.querySelector("#cart-lines");
  if (cartEl) {
    const form = document.querySelector("#checkout-form");
    const draw = () => {
      const { items, subtotal, mrp, total } = totals();
      cartEl.innerHTML = items.length ? items.map(p => `
        <div class="line-item">
          <div class="cover" style="--c1:${p.c1};--c2:${p.c2}">${p.icon}</div>
          <div><h4>${p.name}</h4><span class="muted" style="font-size:13px">${p.fmt}</span><br><a href="#" class="remove" data-remove="${p.slug}">Remove</a></div>
          <div style="text-align:right"><b>${fmt(p.price)}</b><br><span class="mrp">${fmt(p.mrp)}</span></div>
        </div>`).join("") : `<div class="empty">Your cart is empty. <a href="${CFG.root}shop.html" class="grad-text" style="font-weight:700">Browse products →</a></div>`;
      document.querySelector("#sum-sub").textContent = fmt(mrp);
      document.querySelector("#sum-save").textContent = "− " + fmt(mrp - subtotal);
      document.querySelector("#sum-total").textContent = fmt(total);
      const up = document.querySelector("#bundle-upsell");
      if (up) up.style.display = (items.length >= 2 && !cart.includes(CFG.bundle.slug) && subtotal > CFG.bundle.price * 0.5) ? "" : "none";
      form.querySelector("button[type=submit]").disabled = !items.length;
    };
    document.addEventListener("cart", draw); draw();

    form.addEventListener("submit", e => {
      e.preventDefault();
      const { items, total } = totals();
      if (!items.length) return;
      const d = Object.fromEntries(new FormData(form));
      const id = "HN-" + Date.now().toString(36).toUpperCase().slice(-6);
      const lines = items.map((p, i) => `${i + 1}. ${p.name} — ${fmt(p.price)}`).join("\n");
      const msg = `Assalam o Alaikum Hunarly! 👋\nI want to place an order.\n\n🧾 Order ID: ${id}\n${lines}\n\n💰 Total: ${fmt(total)}\n💳 Payment: ${d.payment}\n\n👤 Name: ${d.name}\n📱 WhatsApp: ${d.phone}\n📧 Email: ${d.email}\n🏙️ City: ${d.city}\n\nI will send the payment screenshot here.`;
      try { sessionStorage.setItem("hunarly_last_order", JSON.stringify({ id, total, payment: d.payment })); } catch (e) {}
      px("InitiateCheckout", { content_ids: cart.slice(), value: total, currency: "PKR", num_items: items.length });
      const url = `https://wa.me/${CFG.whatsapp}?text=${encodeURIComponent(msg)}`;
      window.open(url, "_blank", "noopener");
      cart = []; save();
      location.href = CFG.root + "thank-you.html";
    });
  }

  // ---------- thank-you ----------
  const ty = document.querySelector("#ty-order");
  if (ty) {
    try {
      const o = JSON.parse(sessionStorage.getItem("hunarly_last_order"));
      if (o) ty.innerHTML = `Order <b>${o.id}</b> · ${fmt(o.total)} · ${o.payment}`;
    } catch (e) {}
  }

  const pdp = document.querySelector(".pdp [data-buy]");
  if (pdp) px("ViewContent", { content_ids: [pdp.dataset.buy], value: (BY_SLUG[pdp.dataset.buy] || {}).price, currency: "PKR" });
  renderCount();
})();
