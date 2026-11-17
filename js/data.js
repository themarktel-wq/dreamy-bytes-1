/* Lahore Mobile — seed data.
   Everything here is SAMPLE data. The shop owner edits it from the Admin panel (#/admin);
   edits are saved in the browser (localStorage) and override this seed. */

const LM_SEED_VERSION = 4;

/* Phone models a customer can pick in "Mera Phone" (compatibility engine).
   connector: charging port. maxW: max wired charging the phone accepts. tradeBase: used price (PKR) in good condition. */
const LM_MODELS = [
  { id: 'ip17pm', name: 'iPhone 17 Pro Max', brand: 'Apple', connector: 'usb-c', maxW: 40, tradeBase: 420000 },
  { id: 'ip17', name: 'iPhone 17', brand: 'Apple', connector: 'usb-c', maxW: 40, tradeBase: 255000 },
  { id: 'ip16', name: 'iPhone 16', brand: 'Apple', connector: 'usb-c', maxW: 27, tradeBase: 205000 },
  { id: 'ip15', name: 'iPhone 15', brand: 'Apple', connector: 'usb-c', maxW: 27, tradeBase: 170000 },
  { id: 'ip13', name: 'iPhone 13', brand: 'Apple', connector: 'lightning', maxW: 20, tradeBase: 105000 },
  { id: 'ip11', name: 'iPhone 11', brand: 'Apple', connector: 'lightning', maxW: 18, tradeBase: 62000 },
  { id: 's25u', name: 'Galaxy S25 Ultra', brand: 'Samsung', connector: 'usb-c', maxW: 45, tradeBase: 280000 },
  { id: 'a56', name: 'Galaxy A56', brand: 'Samsung', connector: 'usb-c', maxW: 45, tradeBase: 98000 },
  { id: 'a16', name: 'Galaxy A16', brand: 'Samsung', connector: 'usb-c', maxW: 25, tradeBase: 38000 },
  { id: 'rn14p', name: 'Redmi Note 14 Pro', brand: 'Xiaomi', connector: 'usb-c', maxW: 45, tradeBase: 62000 },
  { id: 'inx50p', name: 'Infinix Note 50 Pro', brand: 'Infinix', connector: 'usb-c', maxW: 90, tradeBase: 48000 },
  { id: 'tc40p', name: 'Tecno Camon 40 Pro', brand: 'Tecno', connector: 'usb-c', maxW: 45, tradeBase: 50000 },
  { id: 'vy29', name: 'Vivo Y29', brand: 'Vivo', connector: 'usb-c', maxW: 44, tradeBase: 36000 },
  { id: 'reno13', name: 'Oppo Reno 13', brand: 'Oppo', connector: 'usb-c', maxW: 80, tradeBase: 88000 },
  { id: 'px9', name: 'Pixel 9', brand: 'Google', connector: 'usb-c', maxW: 27, tradeBase: 135000 },
];

const LM_CATEGORIES = [
  { id: 'phone', name: 'Phones', ur: 'موبائل', icon: 'phone' },
  { id: 'case', name: 'Covers & Cases', ur: 'کور', icon: 'case' },
  { id: 'protector', name: 'Screen Protectors', ur: 'گلاس', icon: 'shield' },
  { id: 'charger', name: 'Chargers', ur: 'چارجر', icon: 'bolt' },
  { id: 'cable', name: 'Cables', ur: 'کیبل', icon: 'cable' },
  { id: 'audio', name: 'Earbuds & Audio', ur: 'ایئربڈز', icon: 'audio' },
  { id: 'powerbank', name: 'Power Banks', ur: 'پاور بینک', icon: 'battery' },
  { id: 'watch', name: 'Smart Watches', ur: 'واچ', icon: 'watch' },
];

function lmHistory(price, drops) {
  // 6 points over ~90 days ending at current price
  const pts = [];
  let p = Math.round(price * (1 + drops));
  for (let i = 0; i < 5; i++) {
    pts.push(p);
    p = Math.round(p - (p - price) * (0.25 + (i % 2) * 0.2));
  }
  pts.push(price);
  return pts;
}

const LM_PRODUCTS_SEED = [
  // ---------- Phones ----------
  { id: 'p-ip17pm', cat: 'phone', name: 'iPhone 17 Pro Max', brand: 'Apple', model: 'ip17pm', price: 589999, oldPrice: 619999, pta: true, ptaTax: 0, stock: 4, rating: 4.9, reviews: 38, hue: 28,
    colors: ['Cosmic Orange', 'Deep Blue', 'Silver'], storage: ['256GB', '512GB', '1TB'], featured: true, isNew: true,
    tags: ['camera', 'flagship', 'gaming', 'video'], specs: { Display: '6.9" ProMotion 120Hz', Chip: 'A19 Pro', Camera: '48+48+48MP', Battery: 'All-day', Charging: '40W USB-C', Warranty: '1 Year Official' },
    desc: 'The most powerful iPhone yet. PTA approved with official warranty.' },
  { id: 'p-ip16', cat: 'phone', name: 'iPhone 16', brand: 'Apple', model: 'ip16', price: 279999, oldPrice: 299999, pta: false, ptaTax: 122000, stock: 6, rating: 4.7, reviews: 54, hue: 210,
    colors: ['Ultramarine', 'Teal', 'Black'], storage: ['128GB', '256GB'], featured: true,
    tags: ['camera', 'video'], specs: { Display: '6.1" OLED', Chip: 'A18', Camera: '48+12MP', Charging: '27W USB-C', Warranty: '6 Month Shop' },
    desc: 'Non-PTA unit. See the estimated PTA tax below to register it for SIM use.' },
  { id: 'p-ip13', cat: 'phone', name: 'iPhone 13 (Used, 10/10)', brand: 'Apple', model: 'ip13', price: 112000, oldPrice: 125000, pta: true, ptaTax: 0, stock: 3, rating: 4.6, reviews: 91, hue: 340,
    colors: ['Pink', 'Midnight'], storage: ['128GB'], used: true, batteryHealth: 89,
    tags: ['budget', 'camera'], specs: { Display: '6.1" OLED', Chip: 'A15', 'Battery Health': '89%', Charging: '20W Lightning', Warranty: '1 Month Checking' },
    desc: 'Pre-owned and shop-inspected, with a 30-point inspection report.' },
  { id: 'p-s25u', cat: 'phone', name: 'Galaxy S25 Ultra', brand: 'Samsung', model: 's25u', price: 419999, oldPrice: 449999, pta: true, ptaTax: 0, stock: 5, rating: 4.8, reviews: 47, hue: 260,
    colors: ['Titanium Silverblue', 'Titanium Black'], storage: ['256GB', '512GB'], featured: true,
    tags: ['camera', 'flagship', 'gaming', 'pen'], specs: { Display: '6.9" QHD+ 120Hz', Chip: 'Snapdragon 8 Elite', Camera: '200MP Quad', Battery: '5000mAh', Charging: '45W', Warranty: '1 Year Samsung PK' },
    desc: 'S Pen, Galaxy AI and a 200MP camera. Official Samsung Pakistan warranty.' },
  { id: 'p-a56', cat: 'phone', name: 'Galaxy A56 5G', brand: 'Samsung', model: 'a56', price: 129999, oldPrice: 139999, pta: true, ptaTax: 0, stock: 12, rating: 4.5, reviews: 120, hue: 150,
    colors: ['Awesome Olive', 'Graphite', 'Pink'], storage: ['256GB'], isNew: true,
    tags: ['camera', 'battery', 'midrange'], specs: { Display: '6.7" AMOLED 120Hz', Chip: 'Exynos 1580', Camera: '50MP OIS', Battery: '5000mAh', Charging: '45W', Warranty: '1 Year Samsung PK' },
    desc: 'The best all-rounder in its class, with 6 years of updates.' },
  { id: 'p-a16', cat: 'phone', name: 'Galaxy A16', brand: 'Samsung', model: 'a16', price: 49999, oldPrice: 54999, pta: true, ptaTax: 0, stock: 20, rating: 4.3, reviews: 210, hue: 190,
    colors: ['Black', 'Light Green'], storage: ['128GB'],
    tags: ['budget', 'battery'], specs: { Display: '6.7" AMOLED', Battery: '5000mAh', Charging: '25W', Warranty: '1 Year Samsung PK' },
    desc: 'AMOLED display and 6 years of updates at an entry price.' },
  { id: 'p-rn14p', cat: 'phone', name: 'Redmi Note 14 Pro', brand: 'Xiaomi', model: 'rn14p', price: 79999, oldPrice: 86999, pta: true, ptaTax: 0, stock: 9, rating: 4.5, reviews: 88, hue: 0,
    colors: ['Midnight Black', 'Coral Green'], storage: ['256GB'], featured: true,
    tags: ['camera', 'gaming', 'midrange'], specs: { Display: '6.67" AMOLED 120Hz', Camera: '200MP', Battery: '5500mAh', Charging: '45W', Warranty: '1 Year Official' },
    desc: '200MP camera and IP68 protection. Outstanding value.' },
  { id: 'p-inx50p', cat: 'phone', name: 'Infinix Note 50 Pro', brand: 'Infinix', model: 'inx50p', price: 62999, oldPrice: 67999, pta: true, ptaTax: 0, stock: 15, rating: 4.4, reviews: 142, hue: 45,
    colors: ['Titanium Grey', 'Racing Edition'], storage: ['256GB'],
    tags: ['gaming', 'battery', 'fastcharge', 'budget'], specs: { Display: '6.78" AMOLED 144Hz', Chip: 'Helio G100 Ultimate', Battery: '5200mAh', Charging: '90W', Warranty: '1 Year Official' },
    desc: '90W charging gets you to full in about 30 minutes. Built for gaming.' },
  { id: 'p-tc40p', cat: 'phone', name: 'Tecno Camon 40 Pro', brand: 'Tecno', model: 'tc40p', price: 64999, oldPrice: 69999, pta: true, ptaTax: 0, stock: 8, rating: 4.3, reviews: 64, hue: 300,
    colors: ['Emerald Lake Green', 'Galaxy Black'], storage: ['256GB'],
    tags: ['camera', 'selfie', 'midrange'], specs: { Display: '6.78" AMOLED 144Hz', Camera: '50MP + 50MP Selfie', Battery: '5100mAh', Charging: '45W', Warranty: '1 Year Official' },
    desc: 'A 50MP front camera made for creators.' },
  { id: 'p-reno13', cat: 'phone', name: 'Oppo Reno 13 5G', brand: 'Oppo', model: 'reno13', price: 134999, oldPrice: 144999, pta: true, ptaTax: 0, stock: 0, rating: 4.6, reviews: 33, hue: 175,
    colors: ['Luminous Blue', 'Plum Purple'], storage: ['256GB'],
    tags: ['camera', 'selfie', 'fastcharge'], specs: { Display: '6.59" AMOLED', Camera: '50MP + 50MP Selfie', Battery: '5600mAh', Charging: '80W SUPERVOOC', Warranty: '1 Year Official' },
    desc: 'Underwater photography and 80W charging. Restocking soon.' },
  { id: 'p-px9', cat: 'phone', name: 'Google Pixel 9', brand: 'Google', model: 'px9', price: 189999, oldPrice: 205000, pta: false, ptaTax: 95000, stock: 2, rating: 4.7, reviews: 21, hue: 95,
    colors: ['Obsidian', 'Wintergreen'], storage: ['128GB'],
    tags: ['camera', 'flagship'], specs: { Display: '6.3" Actua', Chip: 'Tensor G4', Camera: '50+48MP', Charging: '27W', Warranty: '6 Month Shop' },
    desc: 'Pure Android and class-leading photo processing. Non-PTA.' },

  // ---------- Cases ----------
  { id: 'a-case-ip17pm-mag', cat: 'case', name: 'MagSafe Clear Case — iPhone 17 Pro Max', brand: 'Lahore Mobile', compat: ['ip17pm'], price: 3499, oldPrice: 4500, stock: 30, rating: 4.6, reviews: 75, hue: 200,
    tags: ['magsafe', 'clear'], specs: { Material: 'Polycarbonate + TPU', Magnet: 'N52 MagSafe', 'Drop Test': '2m' }, desc: 'Anti-yellowing clear case with a 6-month guarantee.' },
  { id: 'a-case-ip16-sil', cat: 'case', name: 'Silicone Soft Case — iPhone 16', brand: 'Lahore Mobile', compat: ['ip16', 'ip15'], price: 1999, oldPrice: 2500, stock: 45, rating: 4.4, reviews: 61, hue: 10,
    tags: ['silicone'], specs: { Material: 'Liquid Silicone', Inside: 'Microfiber' }, desc: 'Soft-touch finish with raised camera protection. Also fits iPhone 15.' },
  { id: 'a-case-ip13-arm', cat: 'case', name: 'Armor Rugged Case — iPhone 13/14', brand: 'Spigen', compat: ['ip13'], price: 4299, stock: 12, rating: 4.7, reviews: 40, hue: 220,
    tags: ['rugged'], specs: { 'Drop Test': 'Military Grade', Kickstand: 'Yes' }, desc: 'Genuine Spigen Tough Armor.' },
  { id: 'a-case-s25u', cat: 'case', name: 'Carbon Fibre Case — S25 Ultra', brand: 'Lahore Mobile', compat: ['s25u'], price: 2799, oldPrice: 3500, stock: 25, rating: 4.5, reviews: 29, hue: 250,
    tags: ['slim'], specs: { Material: 'Aramid fibre look', Thickness: '0.8mm' }, desc: 'Ultra-slim with S Pen access.' },
  { id: 'a-case-a56', cat: 'case', name: 'Shockproof Case — Galaxy A56', brand: 'Lahore Mobile', compat: ['a56'], price: 1299, stock: 40, rating: 4.3, reviews: 52, hue: 140,
    tags: ['clear', 'budget'], specs: { Corners: 'Air-cushion' }, desc: 'Air-cushioned corners for drop protection.' },
  { id: 'a-case-a16', cat: 'case', name: 'Leather Flip Cover — Galaxy A16', brand: 'Lahore Mobile', compat: ['a16'], price: 1499, stock: 35, rating: 4.2, reviews: 88, hue: 30,
    tags: ['flip'], specs: { Slots: '2 card slots' }, desc: 'Flip cover with card slots.' },
  { id: 'a-case-rn14p', cat: 'case', name: 'Gaming Cooling Case — Redmi Note 14 Pro', brand: 'Lahore Mobile', compat: ['rn14p'], price: 1799, stock: 22, rating: 4.4, reviews: 19, hue: 0,
    tags: ['gaming'], specs: { Design: 'Heat dissipation mesh' }, desc: 'Ventilated back keeps your phone cool while gaming.' },
  { id: 'a-case-inx50p', cat: 'case', name: 'Racing Edition Case — Infinix Note 50 Pro', brand: 'Lahore Mobile', compat: ['inx50p'], price: 1499, stock: 28, rating: 4.3, reviews: 23, hue: 45,
    tags: ['gaming'], specs: { Finish: 'Matte' }, desc: 'Matte, fingerprint-resistant finish.' },

  // ---------- Protectors ----------
  { id: 'a-gl-ip17pm', cat: 'protector', name: 'Privacy Glass — iPhone 17 Pro Max', brand: 'Lahore Mobile', compat: ['ip17pm'], price: 1499, oldPrice: 2000, stock: 60, rating: 4.6, reviews: 110, hue: 190,
    tags: ['privacy'], specs: { Hardness: '9H', Type: 'Privacy 28°' }, desc: 'Keeps your screen private from side angles. Free in-store installation.' },
  { id: 'a-gl-ip16', cat: 'protector', name: 'Full Glue 9D Glass — iPhone 15/16', brand: 'Lahore Mobile', compat: ['ip16', 'ip15'], price: 799, stock: 80, rating: 4.5, reviews: 160, hue: 205,
    tags: ['9d'], specs: { Hardness: '9H', Edge: 'Full glue' }, desc: 'Bubble-free fit with oleophobic coating.' },
  { id: 'a-gl-ip13', cat: 'protector', name: 'Full Glue 9D Glass — iPhone 13/14', brand: 'Lahore Mobile', compat: ['ip13'], price: 599, stock: 70, rating: 4.4, reviews: 130, hue: 215,
    tags: ['9d'], specs: { Hardness: '9H' }, desc: '' },
  { id: 'a-gl-s25u', cat: 'protector', name: 'UV Curved Glass — S25 Ultra', brand: 'Whitestone', compat: ['s25u'], price: 3999, stock: 15, rating: 4.7, reviews: 26, hue: 255,
    tags: ['uv'], specs: { Type: 'UV liquid glue', Fingerprint: 'Supported' }, desc: 'Full curved coverage with ultrasonic fingerprint support.' },
  { id: 'a-gl-uni-a', cat: 'protector', name: 'Matte Gaming Glass — A56 / A16 / Note 14 Pro', brand: 'Lahore Mobile', compat: ['a56', 'a16', 'rn14p'], price: 899, stock: 90, rating: 4.3, reviews: 77, hue: 120,
    tags: ['matte', 'gaming'], specs: { Finish: 'Anti-glare matte' }, desc: 'Smooth matte touch for gaming.' },
  { id: 'a-gl-inx', cat: 'protector', name: 'Curved Hydrogel — Infinix / Tecno / Reno', brand: 'Lahore Mobile', compat: ['inx50p', 'tc40p', 'reno13', 'vy29'], price: 699, stock: 100, rating: 4.1, reviews: 45, hue: 60,
    tags: ['hydrogel'], specs: { Type: 'Self-healing hydrogel' }, desc: 'Precision-cut and installed in store.' },

  // ---------- Chargers (compat by connector/watts) ----------
  { id: 'a-ch-anker-30', cat: 'charger', name: 'Anker Nano 30W USB-C', brand: 'Anker', watts: 30, port: 'usb-c', price: 5499, oldPrice: 6500, stock: 18, rating: 4.8, reviews: 95, hue: 200, featured: true,
    tags: ['gan', 'fast'], specs: { Output: '30W PD', Tech: 'GaN', Ports: '1x USB-C' }, desc: 'Compact fast charger for iPhone and Samsung.' },
  { id: 'a-ch-sam-45', cat: 'charger', name: 'Samsung 45W Super Fast Charger', brand: 'Samsung', watts: 45, port: 'usb-c', price: 7999, stock: 10, rating: 4.7, reviews: 58, hue: 230,
    tags: ['fast', 'original'], specs: { Output: '45W PPS', Cable: 'C-to-C 5A included' }, desc: 'Genuine, boxed. Charges the S25 Ultra and A56 at full speed.' },
  { id: 'a-ch-ugreen-65', cat: 'charger', name: 'UGREEN Nexode 65W 3-Port GaN', brand: 'UGREEN', watts: 65, port: 'usb-c', price: 9499, oldPrice: 11000, stock: 7, rating: 4.8, reviews: 36, hue: 160,
    tags: ['gan', 'laptop'], specs: { Output: '65W', Ports: '2x C + 1x A' }, desc: 'Charge your laptop, phone and earbuds at once.' },
  { id: 'a-ch-apple-20', cat: 'charger', name: 'Apple 20W USB-C Adapter (Original)', brand: 'Apple', watts: 20, port: 'usb-c', price: 5999, stock: 14, rating: 4.6, reviews: 120, hue: 0,
    tags: ['original'], specs: { Output: '20W PD' }, desc: 'Genuine Apple, sealed.' },
  { id: 'a-ch-infinix-90', cat: 'charger', name: 'Infinix 90W All-Round FastCharge Kit', brand: 'Infinix', watts: 90, port: 'usb-a', price: 4499, stock: 9, rating: 4.4, reviews: 22, hue: 50, brandLock: 'Infinix',
    tags: ['fast'], specs: { Output: '90W (Infinix protocol)', Cable: 'A-to-C 6A' }, desc: 'Full 90W on Infinix phones only; standard speed on others.' },

  // ---------- Cables ----------
  { id: 'a-cb-cc-100', cat: 'cable', name: 'Braided USB-C to C 100W (1.5m)', brand: 'Baseus', connector: 'usb-c', watts: 100, price: 1499, oldPrice: 1999, stock: 70, rating: 4.6, reviews: 140, hue: 280,
    tags: ['braided'], specs: { Length: '1.5m', Power: '100W', Data: '480Mbps' }, desc: 'Nylon-braided, tested to 20,000 bends.' },
  { id: 'a-cb-cl-mfi', cat: 'cable', name: 'MFi USB-C to Lightning (1m)', brand: 'Anker', connector: 'lightning', watts: 20, price: 2499, stock: 40, rating: 4.7, reviews: 85, hue: 15,
    tags: ['mfi'], specs: { Certified: 'Apple MFi', Length: '1m' }, desc: 'Fast-charging cable for iPhone 11–14.' },
  { id: 'a-cb-magnetic', cat: 'cable', name: '3-in-1 Magnetic Cable (C / Lightning / Micro)', brand: 'Lahore Mobile', connector: 'any', watts: 15, price: 999, stock: 55, rating: 4.0, reviews: 66, hue: 100,
    tags: ['universal'], specs: { Tips: '3 magnetic tips' }, desc: 'One cable for every phone in the house.' },

  // ---------- Audio (universal) ----------
  { id: 'a-au-airpods4', cat: 'audio', name: 'AirPods 4 (ANC)', brand: 'Apple', price: 52999, oldPrice: 57999, stock: 6, rating: 4.7, reviews: 44, hue: 0, featured: true, universal: true,
    tags: ['anc', 'iphone'], specs: { ANC: 'Yes', Battery: '30h with case', Charging: 'USB-C' }, desc: 'Genuine Apple with 1-year warranty.' },
  { id: 'a-au-buds3', cat: 'audio', name: 'Galaxy Buds 3 FE', brand: 'Samsung', price: 17999, oldPrice: 21999, stock: 11, rating: 4.5, reviews: 39, hue: 220, universal: true,
    tags: ['anc'], specs: { ANC: 'Yes', Battery: '30h' }, desc: '' },
  { id: 'a-au-r50i', cat: 'audio', name: 'Soundcore R50i NC', brand: 'Anker', price: 5999, oldPrice: 7499, stock: 34, rating: 4.4, reviews: 210, hue: 260, universal: true, isNew: true,
    tags: ['budget', 'anc', 'gaming'], specs: { ANC: 'Yes (-42dB)', Latency: 'Game mode', Battery: '45h' }, desc: 'Active noise cancelling at an entry price. A best seller.' },
  { id: 'a-au-handsfree', cat: 'audio', name: 'Type-C Wired Handsfree (Hi-Res)', brand: 'Lahore Mobile', price: 699, stock: 120, rating: 4.1, reviews: 300, hue: 330, connector: 'usb-c',
    tags: ['budget', 'wired'], specs: { Mic: 'Yes', Plug: 'USB-C' }, desc: '' },

  // ---------- Power banks ----------
  { id: 'a-pb-anker-20k', cat: 'powerbank', name: 'Anker 20,000mAh 22.5W', brand: 'Anker', watts: 22.5, price: 8499, oldPrice: 9999, stock: 16, rating: 4.7, reviews: 120, hue: 200, universal: true,
    tags: ['travel'], specs: { Capacity: '20,000mAh', Output: '22.5W', Ports: 'C + A' }, desc: 'Charges a phone up to 4 times.' },
  { id: 'a-pb-mag-10k', cat: 'powerbank', name: 'MagSafe Power Bank 10,000mAh', brand: 'Baseus', watts: 20, price: 6999, stock: 13, rating: 4.4, reviews: 58, hue: 170, magsafe: true,
    tags: ['magsafe'], specs: { Capacity: '10,000mAh', Wireless: '15W magnetic' }, desc: 'Snaps magnetically to iPhone 13 and later.' },

  // ---------- Watches ----------
  { id: 'a-w-gw8', cat: 'watch', name: 'Galaxy Watch 8 (44mm)', brand: 'Samsung', price: 79999, oldPrice: 89999, stock: 4, rating: 4.6, reviews: 18, hue: 230, os: 'android', isNew: true,
    tags: ['health'], specs: { OS: 'Wear OS', Sensors: 'BP, ECG, SpO2' }, desc: 'Works with Android phones only.' },
  { id: 'a-w-zero', cat: 'watch', name: 'Zero Luna Pro Smart Watch', brand: 'Zero', price: 9999, oldPrice: 12999, stock: 25, rating: 4.2, reviews: 140, hue: 40, universal: true,
    tags: ['budget'], specs: { Display: 'AMOLED', Calling: 'Bluetooth' }, desc: 'Bluetooth calling, 1-year local warranty.' },
];

LM_PRODUCTS_SEED.forEach((p, i) => {
  p.history = p.history || lmHistory(p.price, 0.04 + (i % 5) * 0.025);
});

const LM_BANNERS_SEED = [
  { id: 'b1', title: 'iPhone 17 Pro Max is here.', sub: 'PTA approved with official warranty. 0% installments for 3 months.', cta: 'Shop now', link: '#/p/p-ip17pm', hue: 220, tag: 'New arrival' },
  { id: 'b2', title: 'Accessories that fit. Guaranteed.', sub: 'Tell us your phone and we show only the covers, glass and chargers made for it.', cta: 'Select your phone', link: '#/myphone', hue: 220, tag: 'Phone Match' },
  { id: 'b3', title: 'Trade in. Trade up.', sub: 'Get an instant estimate for your old phone and use it as credit on a new one.', cta: 'Get an estimate', link: '#/tradein', hue: 220, tag: 'Trade-in' },
  { id: 'b4', title: 'Build your kit. Save 15%.', sub: 'Cover, screen protector and charger matched to your phone, at a bundle price.', cta: 'Build a kit', link: '#/kit', hue: 220, tag: 'Bundle offer' },
];

const LM_SETTINGS_SEED = {
  shopName: 'Lahore Mobile',
  tagline: 'Phones · Accessories · Trust',
  whatsapp: '923000000000',            // replace with real number (country code, no +)
  phone: '+92 300 0000000',
  address: 'Shop #12, Hafeez Centre, Gulberg III, Lahore',
  mapUrl: 'https://maps.google.com/?q=Hafeez+Centre+Lahore',
  openHour: 11, closeHour: 22, closedDay: 5, // Friday prayer break handled as note
  note: 'Jumma: 1pm – 3pm band',
  social: {
    whatsappChannel: 'https://whatsapp.com/channel/',
    facebook: 'https://facebook.com/',
    instagram: 'https://instagram.com/',
    tiktok: 'https://tiktok.com/',
    youtube: 'https://youtube.com/',
  },
  installments: { 3: 0, 6: 8, 12: 18 }, // markup % per tenure
  kitDiscount: 15,
  adminPin: '1234',
  deliveryFee: 250,
  freeDeliveryOver: 5000,
};

/* Product photos (free stock photos from Unsplash, stored locally in assets/img).
   Replace with your own shop photos from Admin → Products → Photo. */
const LM_IMG = {
  'p-ip17pm': 'ip17pm', 'p-ip16': 'ip16', 'p-ip13': 'ip13', 'p-s25u': 's25u', 'p-a56': 'a56', 'p-a16': 'a16', 'p-rn14p': 'rn14p',
  'p-inx50p': 'inx50p', 'p-tc40p': 'tc40p', 'p-reno13': 'reno13', 'p-px9': 'px9',
  'a-case-ip17pm-mag': 'case-leather', 'a-case-ip16-sil': 'case-carbon', 'a-case-ip13-arm': 'case-leather', 'a-case-s25u': 'case-carbon',
  'a-case-a56': 'case-carbon', 'a-case-a16': 'case-leather', 'a-case-rn14p': 'case-carbon', 'a-case-inx50p': 'case-leather',
  'a-gl-ip17pm': 'glass1', 'a-gl-ip16': 'glass3', 'a-gl-ip13': 'glass2', 'a-gl-s25u': 'glass1', 'a-gl-uni-a': 'glass2', 'a-gl-inx': 'glass3',
  'a-ch-anker-30': 'charger', 'a-ch-sam-45': 'charger', 'a-ch-ugreen-65': 'charger', 'a-ch-apple-20': 'charger', 'a-ch-infinix-90': 'charger',
  'a-cb-cc-100': 'cables', 'a-cb-cl-mfi': 'cables', 'a-cb-magnetic': 'cables',
  'a-au-airpods4': 'airpods', 'a-au-buds3': 'buds', 'a-au-r50i': 'earbuds-blue', 'a-au-handsfree': 'earbuds-dark',
  'a-pb-anker-20k': 'magsafe', 'a-pb-mag-10k': 'magsafe', 'a-w-gw8': 'watch-black', 'a-w-zero': 'watch-classic',
};
LM_PRODUCTS_SEED.forEach((p) => { if (LM_IMG[p.id]) p.img = 'assets/img/' + LM_IMG[p.id] + '.jpg'; });
LM_BANNERS_SEED[0].img = 'assets/img/hero-iphones.jpg';
LM_BANNERS_SEED[1].img = 'assets/img/hero-accessories.jpg';
LM_BANNERS_SEED[2].img = 'assets/img/hero-trade.jpg';
LM_BANNERS_SEED[3].img = 'assets/img/hero-audio.jpg';
