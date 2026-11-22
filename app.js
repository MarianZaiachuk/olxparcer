const I18N = {
  uk: {
    title: "OLX Deal Sniper — Web Demo",
    subtitle: "Симуляція фільтрації, оцінки ринку, зниження ціни та Telegram-карток на тестових оголошеннях",
    simPriceDrop: "Знизити ціну (демо)",
    resetDemo: "Скинути",
    passed: "Пройшли",
    skipped: "Відсіяно",
    favorites: "Обране",
    filtersHeading: "Фільтри",
    priorityRegion: "Пріоритетний регіон",
    minPrice: "Мін. грн",
    maxPrice: "Макс. грн",
    skipAboveMarket: "Пропускати дорожче медіани ринку",
    minDiscount: "Мін. знижка %",
    stopWordsHeading: "Стоп-слова",
    stopPlaceholder: "Додати стоп-слово...",
    whitelistHeading: "Білий список (опц.)",
    wlPlaceholder: "Обов'язкове слово...",
    add: "Додати",
    catAll: "Усі",
    tabTelegram: "Telegram-картка",
    tabFavorites: "Обране",
    tabStats: "/stats",
    statsPlaceholder: "Модель (напр. iphone 14)",
    runStats: "Оцінити",
    passLabel: "ПРОЙШЛО",
    skipLabel: "ПРОПУСК",
    localLabel: "ЛОКАЛЬНО",
    dropLabel: "ЗНИЖКА",
    favEmpty: "Список обраного порожній. Натисніть «В обране» на картці Telegram.",
    statsLow: "Замало даних для запиту (потрібно хоча б 2 оголошення).",
    openOlx: "Відкрити на OLX",
    addFav: "В обране",
    inFav: "В обраному",
    marketBtn: "Ринкова ціна",
    remove: "Прибрати",
  },
  en: {
    title: "OLX Deal Sniper — Web Demo",
    subtitle: "Interactive simulation of DealFilter, market valuation, price-drop alerts, and Telegram cards",
    simPriceDrop: "Simulate price drop",
    resetDemo: "Reset",
    passed: "Passed",
    skipped: "Skipped",
    favorites: "Favorites",
    filtersHeading: "Filter Rules",
    priorityRegion: "Priority region",
    minPrice: "Min UAH",
    maxPrice: "Max UAH",
    skipAboveMarket: "Skip offers above market median",
    minDiscount: "Min discount %",
    stopWordsHeading: "Stop-words",
    stopPlaceholder: "Add stop-word...",
    whitelistHeading: "Whitelist (optional)",
    wlPlaceholder: "Required keyword...",
    add: "Add",
    catAll: "All",
    tabTelegram: "Telegram Card",
    tabFavorites: "Favorites",
    tabStats: "/stats",
    statsPlaceholder: "Model (e.g. iphone 14)",
    runStats: "Check",
    passLabel: "PASS",
    skipLabel: "SKIP",
    localLabel: "LOCAL",
    dropLabel: "PRICE DROP",
    favEmpty: "Favorites list is empty. Click 'Add to Favorites' on a Telegram card.",
    statsLow: "Not enough sample ads for this query (need at least 2).",
    openOlx: "Open on OLX",
    addFav: "Add to Favorites",
    inFav: "Saved",
    marketBtn: "Market Price",
    remove: "Remove",
  },
};

const INITIAL_OFFERS = [
  { id: 1001, cat: "iphone", title: "iPhone 14 Pro 128GB Space Black Neverlock", price: 21500, oldPrice: null, city: "Івано-Франківськ", region: "Івано-Франківська область", url: "https://www.olx.ua/" },
  { id: 1002, cat: "iphone", title: "iPhone 14 128GB Midnight стан 9/10", price: 16200, oldPrice: 19500, city: "Калуш", region: "Івано-Франківська область", url: "https://www.olx.ua/" },
  { id: 1003, cat: "iphone", title: "iPhone 14 128GB Blue Neverlock", price: 20500, oldPrice: null, city: "Київ", region: "Київська область", url: "https://www.olx.ua/" },
  { id: 1004, cat: "iphone", title: "iPhone 14 256GB Starlight повний комплект", price: 22500, oldPrice: null, city: "Львів", region: "Львівська область", url: "https://www.olx.ua/" },
  { id: 1005, cat: "iphone", title: "iPhone 14 128GB ідеал терміново", price: 26500, oldPrice: null, city: "Одеса", region: "Одеська область", url: "https://www.olx.ua/" },
  { id: 1006, cat: "iphone", title: "Оригінальний чохол MagSafe iPhone 14 Pro", price: 950, oldPrice: null, city: "Київ", region: "Київська область", url: "https://www.olx.ua/" },
  { id: 1007, cat: "iphone", title: "iPhone 14 Pro на запчастини iCloud lock", price: 8000, oldPrice: null, city: "Харків", region: "Харківська область", url: "https://www.olx.ua/" },
  { id: 2001, cat: "macbook", title: "Apple MacBook Air M2 16/256GB Midnight", price: 29500, oldPrice: null, city: "Львів", region: "Львівська область", url: "https://www.olx.ua/" },
  { id: 2002, cat: "macbook", title: "MacBook Air M2 8/256GB Space Gray", price: 34500, oldPrice: null, city: "Київ", region: "Київська область", url: "https://www.olx.ua/" },
  { id: 2003, cat: "macbook", title: "MacBook Air M2 256GB ідеальний стан", price: 37000, oldPrice: null, city: "Дніпро", region: "Дніпропетровська область", url: "https://www.olx.ua/" },
  { id: 2004, cat: "macbook", title: "MacBook Air M1 256GB розбита матриця дефект", price: 14500, oldPrice: null, city: "Київ", region: "Київська область", url: "https://www.olx.ua/" },
  { id: 3001, cat: "console", title: "Sony PlayStation 5 Slim 1TB + 2 геймпади", price: 15800, oldPrice: null, city: "Коломия", region: "Івано-Франківська область", url: "https://www.olx.ua/" },
  { id: 3002, cat: "console", title: "PlayStation 5 Disc Edition", price: 19200, oldPrice: null, city: "Київ", region: "Київська область", url: "https://www.olx.ua/" },
  { id: 3003, cat: "console", title: "PlayStation 5 стандартна версія 825GB", price: 20500, oldPrice: null, city: "Львів", region: "Львівська область", url: "https://www.olx.ua/" },
  { id: 4001, cat: "ecoflow", title: "Зарядна станція EcoFlow Delta 2 1024Wh", price: 24500, oldPrice: null, city: "Івано-Франківськ", region: "Івано-Франківська область", url: "https://www.olx.ua/" },
  { id: 4002, cat: "ecoflow", title: "EcoFlow Delta 2 нова в коробці", price: 31000, oldPrice: null, city: "Київ", region: "Київська область", url: "https://www.olx.ua/" },
  { id: 4003, cat: "ecoflow", title: "Зарядна станція EcoFlow Delta 2", price: 32500, oldPrice: null, city: "Львів", region: "Львівська область", url: "https://www.olx.ua/" },
];

const LIQUIDITY_PATTERNS = [
  { re: /\biphone\s*(1[3-7])\b/i, score: 9.6, label: "Дуже висока (1-2 дні)" },
  { re: /\bplaystation\s*5\b|\bps5\b/i, score: 9.5, label: "Дуже висока (1-3 дні)" },
  { re: /\bmacbook\s*(air|pro)?\s*(m[1-4])\b/i, score: 9.1, label: "Висока (2-5 днів)" },
  { re: /\becoflow\b|\bbluetti\b/i, score: 9.3, label: "Дуже висока (1-3 дні)" },
];

const REGION_CITIES = {
  "Івано-Франківськ": ["івано-франківськ", "калуш", "коломия", "надвірна"],
  "Львів": ["львів", "дрогобич", "стрий"],
  "Київ": ["київ", "бровари", "ірпінь", "буча"],
};

function createInitialState() {
  return {
    lang: "uk",
    category: "all",
    sideTab: "telegram",
    priorityRegion: "Івано-Франківськ",
    minPrice: 5000,
    maxPrice: 50000,
    skipAboveMarket: true,
    minDiscountPct: 0,
    stopWords: ["на запчастини", "icloud", "дефект", "чохол", "розбит"],
    whitelist: [],
    offers: JSON.parse(JSON.stringify(INITIAL_OFFERS)),
    favorites: [],
    selectedId: 1002,
  };
}

let state = createInitialState();

function escapeRegExp(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function hasWord(text, word) {
  const esc = escapeRegExp(word.trim().toLowerCase());
  if (!esc) return false;
  const re = new RegExp(`(?:^|[^\\p{L}\\p{N}_])${esc}(?:$|[^\\p{L}\\p{N}_])`, "iu");
  return re.test(text);
}

function cleanTitleForStats(title) {
  const words = title.toLowerCase().replace(/[^\p{L}\p{N}\s]/gu, " ").split(/\s+/).filter(Boolean);
  const stop = new Set(["продам", "новий", "бу", "нова", "стан", "ідеал", "гарний", "терміново", "торг", "чохол"]);
  const meaningful = words.filter((w) => !stop.has(w));
  return (meaningful.length ? meaningful.slice(0, 3).join(" ") : title.slice(0, 20));
}

function computeStats(query) {
  const words = query.toLowerCase().split(/\s+/).filter((w) => w.length >= 2);
  if (!words.length) return null;
  const prices = state.offers
    .filter((o) => words.every((w) => o.title.toLowerCase().includes(w)) && o.price > 100)
    .map((o) => o.price)
    .sort((a, b) => a - b);

  if (prices.length < 2) return null;
  const n = prices.length;
  const median = n % 2 === 1 ? prices[(n - 1) / 2] : Math.round((prices[n / 2 - 1] + prices[n / 2]) / 2);
  const avg = Math.round(prices.reduce((acc, p) => acc + p, 0) / n);
  const targetBuy = Math.round(median * 0.82);
  return {
    query,
    count: n,
    min: prices[0],
    max: prices[n - 1],
    avg,
    median,
    quickResale: Math.round(median * 0.94),
    targetBuy,
    margin: Math.max(0, median - targetBuy),
  };
}

function estimateLiquidity(title) {
  for (const item of LIQUIDITY_PATTERNS) {
    if (item.re.test(title)) return item;
  }
  return { score: 7.0, label: "Помірна (1-2 тижні)" };
}

function evaluateOffer(offer) {
  const titleLower = offer.title.toLowerCase();
  if (offer.price < state.minPrice) {
    return { pass: false, reason: `${offer.price} < ${state.minPrice} грн` };
  }
  if (offer.price > state.maxPrice) {
    return { pass: false, reason: `${offer.price} > ${state.maxPrice} грн` };
  }
  for (const sw of state.stopWords) {
    if (hasWord(titleLower, sw)) {
      return { pass: false, reason: `stop-word: '${sw}'` };
    }
  }
  if (state.whitelist.length > 0 && !state.whitelist.some((w) => hasWord(titleLower, w))) {
    return { pass: false, reason: "no whitelist match" };
  }

  const stats = computeStats(cleanTitleForStats(offer.title));
  let valuation = null;
  if (stats && stats.count >= 3) {
    const discountPct = Number((((stats.median - offer.price) / stats.median) * 100).toFixed(1));
    const quickResale = Math.round(stats.median * 0.94);
    const profit = quickResale - offer.price;
    const liq = estimateLiquidity(offer.title);
    let verdict = "По ринку або вище";
    if (discountPct >= 20 && profit >= 2500) verdict = "ТОП ПРОПОЗИЦІЯ";
    else if (discountPct >= 12 && profit >= 1500) verdict = "ВИГІДНА ЦІНА";
    else if (discountPct > 0) verdict = "Трохи дешевше ринку";
    valuation = { median: stats.median, discountPct, quickResale, profit, liq, verdict };

    if (state.skipAboveMarket && discountPct < state.minDiscountPct) {
      return {
        pass: false,
        reason: `${offer.price} > медіани ${stats.median} грн (${discountPct}%)`,
        valuation,
      };
    }
  }

  const cities = REGION_CITIES[state.priorityRegion] || [];
  const isLocal =
    offer.region.toLowerCase().includes(state.priorityRegion.toLowerCase()) ||
    cities.some((c) => offer.city.toLowerCase().includes(c));

  return { pass: true, reason: "OK", isLocal, valuation };
}

function fmt(num) {
  return Number(num).toLocaleString("uk-UA").replace(/,/g, " ");
}

function t(key) {
  return I18N[state.lang][key] || I18N.en[key] || key;
}

function renderTags(containerId, list, onRemove) {
  const box = document.getElementById(containerId);
  box.innerHTML = "";
  for (const val of list) {
    const span = document.createElement("span");
    span.className = "tag";
    const txt = document.createElement("span");
    txt.textContent = val;
    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = "×";
    btn.addEventListener("click", () => onRemove(val));
    span.append(txt, btn);
    box.appendChild(span);
  }
}

function renderTelegramPreview(offer, evalRes) {
  const panel = document.getElementById("side-telegram");
  if (!offer) {
    panel.innerHTML = "";
    return;
  }

  const lines = [];
  if (evalRes.isLocal) {
    lines.push(`[ЛОКАЛЬНО: ${state.priorityRegion.toUpperCase()} / ОБЛАСТЬ]`);
  }
  if (offer.oldPrice && offer.price < offer.oldPrice) {
    const pct = (((offer.oldPrice - offer.price) / offer.oldPrice) * 100).toFixed(1);
    lines.push(`ЦІНУ ЗНИЖЕНО НА ${pct}%!`);
    lines.push(`Було: ${fmt(offer.oldPrice)} грн -> Стало: ${fmt(offer.price)} грн`);
  } else {
    lines.push("НОВЕ ОГОЛОШЕННЯ");
    lines.push(`Ціна: ${fmt(offer.price)} грн`);
  }
  lines.push("");
  lines.push(offer.title);
  lines.push(`Локація: ${offer.city} (${offer.region})`);

  if (evalRes.valuation) {
    const v = evalRes.valuation;
    const sign = v.discountPct > 0 ? "-" : "+";
    lines.push("");
    lines.push(`--- ${v.verdict} ---`);
    lines.push(`Медіана ринку: ~${fmt(v.median)} грн (${sign}${Math.abs(v.discountPct)}%)`);
    lines.push(`Швидкий перепродаж: ~${fmt(v.quickResale)} грн`);
    if (v.profit > 0) lines.push(`Орієнтовний профіт: ~+${fmt(v.profit)} грн`);
    lines.push(`Ліквідність: ${v.liq.label}`);
  }

  const card = document.createElement("div");
  card.className = "tg-card";
  card.textContent = lines.join("\n");

  const btns = document.createElement("div");
  btns.className = "tg-buttons";

  const openLink = document.createElement("a");
  openLink.className = "tg-btn full";
  openLink.href = offer.url;
  openLink.target = "_blank";
  openLink.rel = "noopener noreferrer";
  openLink.textContent = t("openOlx");

  const isFav = state.favorites.includes(offer.id);
  const favBtn = document.createElement("button");
  favBtn.type = "button";
  favBtn.className = "tg-btn";
  favBtn.textContent = isFav ? t("inFav") : t("addFav");
  favBtn.addEventListener("click", () => {
    if (isFav) {
      state.favorites = state.favorites.filter((id) => id !== offer.id);
    } else {
      state.favorites.push(offer.id);
    }
    renderAll();
  });

  const statsBtn = document.createElement("button");
  statsBtn.type = "button";
  statsBtn.className = "tg-btn";
  statsBtn.textContent = t("marketBtn");
  statsBtn.addEventListener("click", () => {
    state.sideTab = "stats";
    document.getElementById("stats-input").value = cleanTitleForStats(offer.title);
    renderAll();
  });

  btns.append(openLink, favBtn, statsBtn);
  panel.innerHTML = "";
  panel.append(card, btns);
}

function renderFavorites() {
  const box = document.getElementById("side-favorites");
  box.innerHTML = "";
  if (state.favorites.length === 0) {
    const p = document.createElement("p");
    p.className = "subtitle";
    p.textContent = t("favEmpty");
    box.appendChild(p);
    return;
  }
  for (const id of state.favorites) {
    const o = state.offers.find((item) => item.id === id);
    if (!o) continue;
    const row = document.createElement("div");
    row.className = "fav-item";
    const title = document.createElement("strong");
    title.textContent = o.title;
    const meta = document.createElement("span");
    meta.className = "subtitle";
    meta.textContent = `${fmt(o.price)} грн · ${o.city}`;
    const rm = document.createElement("button");
    rm.type = "button";
    rm.className = "btn-secondary";
    rm.textContent = t("remove");
    rm.addEventListener("click", () => {
      state.favorites = state.favorites.filter((fid) => fid !== id);
      renderAll();
    });
    row.append(title, meta, rm);
    box.appendChild(row);
  }
}

function renderStats() {
  const query = document.getElementById("stats-input").value.trim();
  const out = document.getElementById("stats-output");
  const stats = computeStats(query);
  if (!stats) {
    out.textContent = t("statsLow");
    return;
  }
  const liq = estimateLiquidity(query);
  out.textContent = [
    `РИНКОВА АНАЛІТИКА: ${stats.query}`,
    `Проаналізовано оголошень: ${stats.count}`,
    `Середня ціна: ${fmt(stats.avg)} грн`,
    `Медіана ринку: ${fmt(stats.median)} грн`,
    `Діапазон: ${fmt(stats.min)} — ${fmt(stats.max)} грн`,
    `Швидкий перепродаж: ~${fmt(stats.quickResale)} грн`,
    `Рекомендований викуп: до ${fmt(stats.targetBuy)} грн`,
    `Орієнтовний профіт: ~${fmt(stats.margin)} грн`,
    `Ліквідність: ${liq.label}`,
  ].join("\n");
}

function renderAll() {
  document.documentElement.lang = state.lang;
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
    node.placeholder = t(node.dataset.i18nPlaceholder);
  });
  document.querySelectorAll(".lang-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.lang === state.lang);
  });

  document.getElementById("select-region").value = state.priorityRegion;
  document.getElementById("input-min-price").value = state.minPrice;
  document.getElementById("input-max-price").value = state.maxPrice;
  document.getElementById("toggle-skip-market").checked = state.skipAboveMarket;
  document.getElementById("input-min-discount").value = state.minDiscountPct;

  document.querySelectorAll("[data-cat]").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.cat === state.category);
  });
  document.querySelectorAll("[data-side]").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.side === state.sideTab);
  });

  document.getElementById("side-telegram").hidden = state.sideTab !== "telegram";
  document.getElementById("side-favorites").hidden = state.sideTab !== "favorites";
  document.getElementById("side-stats").hidden = state.sideTab !== "stats";

  renderTags("stop-tags", state.stopWords, (w) => {
    state.stopWords = state.stopWords.filter((x) => x !== w);
    renderAll();
  });
  renderTags("wl-tags", state.whitelist, (w) => {
    state.whitelist = state.whitelist.filter((x) => x !== w);
    renderAll();
  });

  const visibleOffers =
    state.category === "all"
      ? state.offers
      : state.offers.filter((o) => o.cat === state.category);

  const listEl = document.getElementById("offers-list");
  listEl.innerHTML = "";
  let passed = 0;
  let skipped = 0;
  let selectedEval = null;
  let selectedOffer = null;

  for (const offer of visibleOffers) {
    const res = evaluateOffer(offer);
    if (res.pass) passed += 1;
    else skipped += 1;

    if (offer.id === state.selectedId) {
      selectedOffer = offer;
      selectedEval = res;
    }

    const card = document.createElement("article");
    card.className = `offer-card ${res.pass ? "" : "skipped"} ${offer.id === state.selectedId ? "selected" : ""}`;
    card.addEventListener("click", () => {
      state.selectedId = offer.id;
      state.sideTab = "telegram";
      renderAll();
    });

    const top = document.createElement("div");
    top.className = "offer-top";
    const badges = document.createElement("div");
    badges.className = "badges";

    const statusPill = document.createElement("span");
    statusPill.className = `pill ${res.pass ? "pill-pass" : "pill-skip"}`;
    statusPill.textContent = res.pass ? t("passLabel") : t("skipLabel");
    badges.appendChild(statusPill);

    if (res.isLocal) {
      const locPill = document.createElement("span");
      locPill.className = "pill pill-local";
      locPill.textContent = t("localLabel");
      badges.appendChild(locPill);
    }

    if (offer.oldPrice && offer.price < offer.oldPrice) {
      const dropPill = document.createElement("span");
      dropPill.className = "pill pill-drop";
      dropPill.textContent = t("dropLabel");
      badges.appendChild(dropPill);
    }

    const priceEl = document.createElement("div");
    priceEl.className = "offer-price";
    if (offer.oldPrice && offer.price < offer.oldPrice) {
      const oldS = document.createElement("s");
      oldS.textContent = `${fmt(offer.oldPrice)}`;
      priceEl.appendChild(oldS);
    }
    priceEl.append(document.createTextNode(`${fmt(offer.price)} грн`));

    top.append(badges, priceEl);

    const titleEl = document.createElement("div");
    titleEl.className = "offer-title";
    titleEl.textContent = offer.title;

    const metaEl = document.createElement("div");
    metaEl.className = "offer-meta";
    metaEl.textContent = `${offer.city} · ${offer.region}`;

    card.append(top, titleEl, metaEl);

    if (res.pass && res.valuation) {
      const v = document.createElement("div");
      v.className = "offer-verdict";
      v.textContent = `${vText(res.valuation)}`;
      card.appendChild(v);
    } else if (!res.pass) {
      const r = document.createElement("div");
      r.className = "skip-reason";
      r.textContent = res.reason;
      card.appendChild(r);
    }

    listEl.appendChild(card);
  }

  function vText(v) {
    return `${v.verdict} · медіана ${fmt(v.median)} грн (${v.discountPct >= 0 ? "-" : "+"}${Math.abs(v.discountPct)}%)`;
  }

  if (!selectedOffer && visibleOffers.length > 0) {
    selectedOffer = visibleOffers[0];
    selectedEval = evaluateOffer(selectedOffer);
  }

  document.getElementById("stat-passed").textContent = String(passed);
  document.getElementById("stat-skipped").textContent = String(skipped);
  document.getElementById("stat-favs").textContent = String(state.favorites.length);

  renderTelegramPreview(selectedOffer, selectedEval || { pass: false });
  renderFavorites();
  renderStats();
}

document.querySelectorAll(".lang-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    state.lang = btn.dataset.lang;
    renderAll();
  });
});

document.getElementById("btn-reset").addEventListener("click", () => {
  state = createInitialState();
  renderAll();
});

document.getElementById("btn-price-drop").addEventListener("click", () => {
  const candidate = state.offers.find((o) => o.id === 1003);
  if (candidate) {
    if (!candidate.oldPrice) candidate.oldPrice = candidate.price;
    candidate.price = Math.max(5000, Math.round(candidate.price * 0.8));
    state.selectedId = candidate.id;
    state.sideTab = "telegram";
    renderAll();
  }
});

document.getElementById("select-region").addEventListener("change", (e) => {
  state.priorityRegion = e.target.value;
  renderAll();
});

document.getElementById("input-min-price").addEventListener("change", (e) => {
  state.minPrice = Number(e.target.value) || 0;
  renderAll();
});

document.getElementById("input-max-price").addEventListener("change", (e) => {
  state.maxPrice = Number(e.target.value) || 999999;
  renderAll();
});

document.getElementById("toggle-skip-market").addEventListener("change", (e) => {
  state.skipAboveMarket = e.target.checked;
  renderAll();
});

document.getElementById("input-min-discount").addEventListener("change", (e) => {
  state.minDiscountPct = Number(e.target.value) || 0;
  renderAll();
});

document.getElementById("stop-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const inp = document.getElementById("stop-input");
  const val = inp.value.trim().toLowerCase();
  if (val && !state.stopWords.includes(val)) {
    state.stopWords.push(val);
  }
  inp.value = "";
  renderAll();
});

document.getElementById("wl-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const inp = document.getElementById("wl-input");
  const val = inp.value.trim().toLowerCase();
  if (val && !state.whitelist.includes(val)) {
    state.whitelist.push(val);
  }
  inp.value = "";
  renderAll();
});

document.getElementById("cat-tabs").addEventListener("click", (e) => {
  const btn = e.target.closest("[data-cat]");
  if (!btn) return;
  state.category = btn.dataset.cat;
  renderAll();
});

document.querySelector(".preview-col .tabs").addEventListener("click", (e) => {
  const btn = e.target.closest("[data-side]");
  if (!btn) return;
  state.sideTab = btn.dataset.side;
  renderAll();
});

document.getElementById("stats-form").addEventListener("submit", (e) => {
  e.preventDefault();
  renderStats();
});

renderAll();
