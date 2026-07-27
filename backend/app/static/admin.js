const adminLoginShell = document.getElementById("admin-login-shell");
const adminDashboard = document.getElementById("admin-dashboard");
const adminLoginForm = document.getElementById("admin-login-form");
const adminLoginInput = document.getElementById("admin-login");
const adminPasswordInput = document.getElementById("admin-password");
const adminLoginStatus = document.getElementById("admin-login-status");
const adminSessionChip = document.getElementById("admin-session-chip");
const adminRefresh = document.getElementById("admin-refresh");
const adminLogout = document.getElementById("admin-logout");
const adminPricingJson = document.getElementById("admin-pricing-json");
const adminPricingRefresh = document.getElementById("admin-pricing-refresh");
const adminPricingSave = document.getElementById("admin-pricing-save");
const adminPricingStatus = document.getElementById("admin-pricing-status");
const adminPricingAdvancedToggle = document.getElementById("admin-pricing-advanced-toggle");
const adminPricingAdvanced = document.getElementById("admin-pricing-advanced");
const infraOverallChip = document.getElementById("infra-overall-chip");
const infraHealthChip = document.getElementById("infra-health-chip");
const infraRedisStatus = document.getElementById("infra-redis-status");
const infraQueueStatus = document.getElementById("infra-queue-status");
const infraTotalBacklog = document.getElementById("infra-total-backlog");
const infraPostgresStatus = document.getElementById("infra-postgres-status");
const infraQueuesBody = document.getElementById("infra-queues-body");
const infraCutoverCards = document.getElementById("infra-cutover-cards");
const infraConsistencyBody = document.getElementById("infra-consistency-body");
const infraConsistencyChip = document.getElementById("infra-consistency-chip");
const infraStatus = document.getElementById("infra-status");
const infraMetricsBody = document.getElementById("infra-metrics-body");
const infraMetricsChip = document.getElementById("infra-metrics-chip");
const infraAdviceChip = document.getElementById("infra-advice-chip");
const infraAdviceSummary = document.getElementById("infra-advice-summary");
const infraAdviceCards = document.getElementById("infra-advice-cards");

const priceImg2img = document.getElementById("price-img2img");
const priceMaterials = document.getElementById("price-materials");
const priceText2img = document.getElementById("price-text2img");
const priceInfluencer = document.getElementById("price-influencer");
const priceChat = document.getElementById("price-chat");
const priceChatImage = document.getElementById("price-chat-image");
const priceMusic8 = document.getElementById("price-music-8");
const priceMusic15 = document.getElementById("price-music-15");
const priceMusic30 = document.getElementById("price-music-30");
const priceMusic60 = document.getElementById("price-music-60");
const priceMusic120 = document.getElementById("price-music-120");
const priceMusic180 = document.getElementById("price-music-180");
const priceI2vKling5 = document.getElementById("price-i2v-kling-5");
const priceI2vKling8 = document.getElementById("price-i2v-kling-8");
const priceI2vKling15 = document.getElementById("price-i2v-kling-15");
const priceI2vWan225 = document.getElementById("price-i2v-wan22-5");
const priceI2vWan228 = document.getElementById("price-i2v-wan22-8");
const priceI2vWan2215 = document.getElementById("price-i2v-wan22-15");
const priceI2vWan255 = document.getElementById("price-i2v-wan25-5");
const priceI2vWan258 = document.getElementById("price-i2v-wan25-8");
const priceI2vWan2515 = document.getElementById("price-i2v-wan25-15");
const priceI2vMinimax5 = document.getElementById("price-i2v-minimax-5");
const priceI2vMinimax8 = document.getElementById("price-i2v-minimax-8");
const priceI2vMinimax15 = document.getElementById("price-i2v-minimax-15");
const adminSearch = document.getElementById("admin-search");
const adminUsersBody = document.getElementById("admin-users-body");
const metricUsers = document.getElementById("metric-users");
const metricBalance = document.getElementById("metric-balance");
const metricGenerations = document.getElementById("metric-generations");
const metricModules = document.getElementById("metric-modules");
const adminSelectedId = document.getElementById("admin-selected-id");
const adminDetailEmpty = document.getElementById("admin-detail-empty");
const adminDetailPanel = document.getElementById("admin-detail-panel");
const adminDetailName = document.getElementById("admin-detail-name");
const adminDetailEmail = document.getElementById("admin-detail-email");
const adminDetailMeta = document.getElementById("admin-detail-meta");
const adminDetailBalance = document.getElementById("admin-detail-balance");
const adminDetailTotal = document.getElementById("admin-detail-total");
const adminDetailModules = document.getElementById("admin-detail-modules");
const adminBalanceForm = document.getElementById("admin-balance-form");
const adminBalanceInput = document.getElementById("admin-balance-input");
const adminBalanceNote = document.getElementById("admin-balance-note");
const adminDetailGenerations = document.getElementById("admin-detail-generations");
const adminHistoryCount = document.getElementById("admin-detail-history-count");

let adminSession = null;
let usersCache = [];
let selectedUserId = null;
let selectedUserDetail = null;
let pricingCache = null;
let infraCache = null;

function formatCop(value) {
  const amount = Number(value || 0);
  return new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 0,
  }).format(amount);
}

function formatDate(value) {
  if (!value) return "--";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "--";
  return date.toLocaleString("es-CO");
}

async function readApiError(response) {
  const text = await response.text();
  if (!text) return "Error inesperado";
  try {
    const parsed = JSON.parse(text);
    if (parsed && typeof parsed.detail === "string") return parsed.detail;
    return text;
  } catch {
    return text;
  }
}

function setLoginStatus(text, state = "idle") {
  if (!adminLoginStatus) return;
  adminLoginStatus.textContent = text;
  adminLoginStatus.dataset.state = state;
}

function setPricingStatus(text, state = "idle") {
  if (!adminPricingStatus) return;
  adminPricingStatus.textContent = text;
  adminPricingStatus.dataset.state = state;
}

function setInfraStatus(text, state = "idle") {
  if (!infraStatus) return;
  infraStatus.textContent = text;
  infraStatus.dataset.state = state;
}

function formatPricingJson(pricing) {
  return JSON.stringify(pricing || {}, null, 2);
}

function safeNumber(value, fallback = 0) {
  const n = Number(value);
  return Number.isFinite(n) ? n : fallback;
}

function copToUsd(copPrice, pricing) {
  const usdToCop = safeNumber(pricing?.usd_to_cop, 3602.817479);
  const margin = safeNumber(pricing?.pricing_margin_multiplier, 1.5);
  const plans = Array.isArray(pricing?.recharge_plans) && pricing.recharge_plans.length
    ? pricing.recharge_plans.map((v) => safeNumber(v, 0)).filter((v) => v > 0)
    : [5000, 10000, 15000, 20000, 25000, 30000, 35000, 40000, 45000, 50000];
  const wompiPercent = safeNumber(pricing?.wompi_percent, 0.0265);
  const wompiFixed = safeNumber(pricing?.wompi_fixed_fee, 700);
  const wompiIva = safeNumber(pricing?.wompi_iva_rate, 0.19);

  let factorSum = 0;
  for (const amount of plans) {
    const fee = amount * wompiPercent + wompiFixed;
    const net = amount - fee * (1 + wompiIva);
    factorSum += net > 0 ? amount / net : 1;
  }
  const coverage = factorSum / plans.length;
  const denominator = usdToCop * margin * coverage;
  if (!Number.isFinite(denominator) || denominator <= 0) return 0;
  return safeNumber(copPrice, 0) / denominator;
}

function setInputValue(el, value) {
  if (!el) return;
  el.value = String(Math.max(0, Math.round(safeNumber(value, 0))));
}

function parseCopInput(el) {
  return Math.max(0, Math.round(safeNumber(el?.value, 0)));
}

function statusLabel(ok, positive = "Operativo", negative = "Atención") {
  return ok ? positive : negative;
}

function coverageLabel(value) {
  const numeric = Number(value || 0);
  if (!Number.isFinite(numeric)) return "0%";
  return `${numeric.toFixed(numeric % 1 === 0 ? 0 : 2)}%`;
}

function renderQueuesTable(queues) {
  if (!infraQueuesBody) return;
  infraQueuesBody.innerHTML = "";

  const rows = Array.isArray(queues) ? queues : [];
  if (!rows.length) {
    const row = document.createElement("tr");
    row.innerHTML = '<td colspan="5">No hay colas reportadas.</td>';
    infraQueuesBody.appendChild(row);
    return;
  }

  for (const item of rows) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${item.name || "-"}</td>
      <td>${Number(item.queued || 0)}</td>
      <td>${Number(item.started || 0)}</td>
      <td>${Number(item.failed || 0)}</td>
      <td>${Number(item.scheduled || 0)}</td>
    `;
    infraQueuesBody.appendChild(row);
  }
}

function renderCutoverCards(modules) {
  if (!infraCutoverCards) return;
  infraCutoverCards.innerHTML = "";

  const rows = Array.isArray(modules) ? modules : [];
  if (!rows.length) {
    infraCutoverCards.innerHTML = '<div class="detail-empty">No hay configuración de cutover disponible.</div>';
    return;
  }

  for (const item of rows) {
    const article = document.createElement("article");
    article.className = "cutover-card";
    const enabled = Boolean(item.enabled);
    const percent = Number(item.percent || 0);
    const fallback = Boolean(item.sqlite_fallback_enabled);
    article.innerHTML = `
      <div class="cutover-card__head">
        <strong>${item.module || "modulo"}</strong>
        <span class="badge ${enabled ? "badge--ok" : "badge--muted"}">${enabled ? "Activo" : "Apagado"}</span>
      </div>
      <div class="cutover-meter">
        <div class="cutover-meter__bar"><span style="width:${Math.max(0, Math.min(100, percent))}%"></span></div>
        <span>${percent}%</span>
      </div>
      <p class="admin-note">Fallback SQLite: ${fallback ? "habilitado" : "deshabilitado"}</p>
    `;
    infraCutoverCards.appendChild(article);
  }
}

function renderConsistencyTable(metrics) {
  if (!infraConsistencyBody) return;
  infraConsistencyBody.innerHTML = "";

  const entries = Object.entries(metrics || {});
  if (!entries.length) {
    const row = document.createElement("tr");
    row.innerHTML = '<td colspan="5">No hay métricas de consistencia disponibles.</td>';
    infraConsistencyBody.appendChild(row);
    return;
  }

  for (const [name, item] of entries) {
    const match = Boolean(item?.match);
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${name}</td>
      <td>${Number(item?.sqlite || 0)}</td>
      <td>${Number(item?.postgres || 0)}</td>
      <td>${coverageLabel(item?.coverage_pct)}</td>
      <td><span class="badge ${match ? "badge--ok" : "badge--warn"}">${match ? "Verde" : "Revisar"}</span></td>
    `;
    infraConsistencyBody.appendChild(row);
  }
}

function renderMetricsTable(items) {
  if (!infraMetricsBody) return;
  infraMetricsBody.innerHTML = "";

  const rows = Array.isArray(items) ? items : [];
  if (!rows.length) {
    const row = document.createElement("tr");
    row.innerHTML = '<td colspan="9">No hay métricas operativas disponibles todavía.</td>';
    infraMetricsBody.appendChild(row);
    return;
  }

  for (const item of rows) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${item.module || "-"}</td>
      <td>${Number(item.api_requests_total || 0)}</td>
      <td>${Number(item.api_avg_duration_ms || 0).toFixed(2)}</td>
      <td>${Number(item.api_errors_5xx || 0)}</td>
      <td>${Number(item.jobs_total || 0)}</td>
      <td>${Number(item.jobs_completed || 0)}</td>
      <td>${Number(item.jobs_failed || 0)}</td>
      <td>${Number(item.jobs_rejected || 0)}</td>
      <td>${Number(item.job_avg_duration_seconds || 0).toFixed(2)}</td>
    `;
    infraMetricsBody.appendChild(row);
  }
}

function renderAdviceCards(items, summary) {
  if (infraAdviceSummary) {
    infraAdviceSummary.textContent = summary || "Sin evaluación.";
  }
  if (!infraAdviceCards) return;
  infraAdviceCards.innerHTML = "";

  const rows = Array.isArray(items) ? items : [];
  if (!rows.length) {
    infraAdviceCards.innerHTML = '<div class="detail-empty">No hay recomendaciones disponibles.</div>';
    return;
  }

  for (const item of rows) {
    const toneClass = item.status === "critical" ? "badge--warn" : item.status === "warn" ? "badge--warn" : "badge--ok";
    const article = document.createElement("article");
    article.className = "cutover-card";
    article.innerHTML = `
      <div class="cutover-card__head">
        <strong>${item.module || "modulo"}</strong>
        <span class="badge ${toneClass}">${item.status || "ok"}</span>
      </div>
      <p class="admin-note"><strong>Acción:</strong> ${item.action || "Mantener"}</p>
      <p class="admin-note">Backlog: ${Number(item.backlog || 0)} · Latencia: ${Number(item.latency_ms || 0).toFixed(2)} ms · Rechazos: ${Number(item.rejections || 0)}</p>
      <p class="admin-note">${Array.isArray(item.reasons) ? item.reasons.join(" | ") : ""}</p>
    `;
    infraAdviceCards.appendChild(article);
  }
}

function renderInfrastructure(payload) {
  infraCache = payload || {};
  const health = infraCache.health || {};
  const queue = health.queue || {};
  const postgres = health.postgres_mirror || {};
  const cutoverModules = infraCache.cutover?.modules || [];
  const consistency = infraCache.consistency || {};
  const metrics = infraCache.metrics || {};
  const advice = infraCache.advice || {};
  const consistencyOk = Boolean(consistency.ok);
  const healthOk = Boolean(health.ok);

  if (infraOverallChip) {
    infraOverallChip.textContent = healthOk && consistencyOk ? "Infra en verde" : healthOk ? "Operativa con revisión" : "Atención requerida";
  }
  if (infraHealthChip) {
    infraHealthChip.textContent = statusLabel(healthOk, "Operativa", "Incidencias");
  }
  if (infraRedisStatus) {
    infraRedisStatus.textContent = statusLabel(Boolean(queue.redis_ok), "OK", "Fallo");
  }
  if (infraQueueStatus) {
    infraQueueStatus.textContent = statusLabel(Boolean(queue.queue_enabled), "Distribuida", "Fallback local");
  }
  if (infraTotalBacklog) {
    infraTotalBacklog.textContent = String(Number(queue.total_backlog || 0));
  }
  if (infraPostgresStatus) {
    infraPostgresStatus.textContent = statusLabel(Boolean(postgres.ok), "OK", "Pendiente");
  }
  if (infraConsistencyChip) {
    infraConsistencyChip.textContent = consistencyOk ? "Verde" : "Revisión necesaria";
  }
  if (infraMetricsChip) {
    infraMetricsChip.textContent = Array.isArray(metrics.modules) && metrics.modules.length ? "Activo" : "Sin tráfico";
  }
  if (infraAdviceChip) {
    infraAdviceChip.textContent = advice.status === "critical" ? "Crítico" : advice.status === "warn" ? "Precaución" : "Estable";
  }

  renderQueuesTable(queue.queues || []);
  renderCutoverCards(cutoverModules);
  renderConsistencyTable(consistency.metrics || {});
  renderMetricsTable(metrics.modules || []);
  renderAdviceCards(advice.modules || [], advice.summary || "");
  setInfraStatus("Infraestructura actualizada.", "completed");
}

function fillCopPricingForm(pricing) {
  if (!pricing) return;
  const moduleUsd = pricing.module_usd || {};
  const moduleCop = pricing.module_price_cop || {};
  const musicUsd = pricing.music_duration_usd || {};
  const musicCop = pricing.music_duration_cop || {};
  const videoUsd = pricing.video_engine_usd_per_second || {};
  const videoCop = pricing.video_price_cop || {};

  const toCop = (usd) => {
    const base = safeNumber(usd, 0);
    const usdToCop = safeNumber(pricing.usd_to_cop, 3602.817479);
    const margin = safeNumber(pricing.pricing_margin_multiplier, 1.5);
    const plans = Array.isArray(pricing.recharge_plans) && pricing.recharge_plans.length
      ? pricing.recharge_plans.map((v) => safeNumber(v, 0)).filter((v) => v > 0)
      : [5000, 10000, 15000, 20000, 25000, 30000, 35000, 40000, 45000, 50000];
    const wompiPercent = safeNumber(pricing.wompi_percent, 0.0265);
    const wompiFixed = safeNumber(pricing.wompi_fixed_fee, 700);
    const wompiIva = safeNumber(pricing.wompi_iva_rate, 0.19);
    let factorSum = 0;
    for (const amount of plans) {
      const fee = amount * wompiPercent + wompiFixed;
      const net = amount - fee * (1 + wompiIva);
      factorSum += net > 0 ? amount / net : 1;
    }
    const coverage = factorSum / plans.length;
    return Math.max(0, Math.round(base * usdToCop * margin * coverage));
  };

  setInputValue(priceImg2img, moduleCop.img2img ?? toCop(moduleUsd.img2img));
  setInputValue(priceMaterials, moduleCop.materials ?? toCop(moduleUsd.materials));
  setInputValue(priceText2img, moduleCop.text2img ?? toCop(moduleUsd.text2img));
  setInputValue(priceInfluencer, moduleCop.influencer ?? toCop(moduleUsd.influencer));
  setInputValue(priceChat, moduleCop.chat ?? toCop(moduleUsd.chat));
  setInputValue(priceChatImage, moduleCop.chat_image ?? toCop(moduleUsd.chat_image));
  setInputValue(priceMusic8, musicCop["8"] ?? toCop(musicUsd["8"]));
  setInputValue(priceMusic15, musicCop["15"] ?? toCop(musicUsd["15"]));
  setInputValue(priceMusic30, musicCop["30"] ?? toCop(musicUsd["30"]));
  setInputValue(priceMusic60, musicCop["60"] ?? toCop(musicUsd["60"]));
  setInputValue(priceMusic120, musicCop["120"] ?? toCop(musicUsd["120"]));
  setInputValue(priceMusic180, musicCop["180"] ?? toCop(musicUsd["180"]));

  setInputValue(priceI2vKling5, videoCop["kwaivgi/kling-v3-video"]?.["5"] ?? toCop(safeNumber(videoUsd["kwaivgi/kling-v3-video"]) * 5));
  setInputValue(priceI2vKling8, videoCop["kwaivgi/kling-v3-video"]?.["8"] ?? toCop(safeNumber(videoUsd["kwaivgi/kling-v3-video"]) * 8));
  setInputValue(priceI2vKling15, videoCop["kwaivgi/kling-v3-video"]?.["15"] ?? toCop(safeNumber(videoUsd["kwaivgi/kling-v3-video"]) * 15));
  setInputValue(priceI2vWan225, videoCop["wan-video/wan-2.2-i2v-fast"]?.["5"] ?? toCop(safeNumber(videoUsd["wan-video/wan-2.2-i2v-fast"]) * 5));
  setInputValue(priceI2vWan228, videoCop["wan-video/wan-2.2-i2v-fast"]?.["8"] ?? toCop(safeNumber(videoUsd["wan-video/wan-2.2-i2v-fast"]) * 8));
  setInputValue(priceI2vWan2215, videoCop["wan-video/wan-2.2-i2v-fast"]?.["15"] ?? toCop(safeNumber(videoUsd["wan-video/wan-2.2-i2v-fast"]) * 15));
  setInputValue(priceI2vWan255, videoCop["wan-video/wan-2.5-i2v-fast"]?.["5"] ?? toCop(safeNumber(videoUsd["wan-video/wan-2.5-i2v-fast"]) * 5));
  setInputValue(priceI2vWan258, videoCop["wan-video/wan-2.5-i2v-fast"]?.["8"] ?? toCop(safeNumber(videoUsd["wan-video/wan-2.5-i2v-fast"]) * 8));
  setInputValue(priceI2vWan2515, videoCop["wan-video/wan-2.5-i2v-fast"]?.["15"] ?? toCop(safeNumber(videoUsd["wan-video/wan-2.5-i2v-fast"]) * 15));
  setInputValue(priceI2vMinimax5, videoCop["minimax/video-01-live"]?.["5"] ?? toCop(safeNumber(videoUsd["minimax/video-01-live"]) * 5));
  setInputValue(priceI2vMinimax8, videoCop["minimax/video-01-live"]?.["8"] ?? toCop(safeNumber(videoUsd["minimax/video-01-live"]) * 8));
  setInputValue(priceI2vMinimax15, videoCop["minimax/video-01-live"]?.["15"] ?? toCop(safeNumber(videoUsd["minimax/video-01-live"]) * 15));
}

function buildPricingFromCopForm() {
  const base = pricingCache ? JSON.parse(JSON.stringify(pricingCache)) : {};
  base.module_usd = base.module_usd || {};
  base.module_price_cop = {};
  base.music_duration_usd = base.music_duration_usd || {};
  base.music_duration_cop = {};
  base.video_engine_usd_per_second = base.video_engine_usd_per_second || {};
  base.video_price_cop = {};

  const moduleCop = {
    img2img: parseCopInput(priceImg2img),
    materials: parseCopInput(priceMaterials),
    text2img: parseCopInput(priceText2img),
    influencer: parseCopInput(priceInfluencer),
    chat: parseCopInput(priceChat),
    chat_image: parseCopInput(priceChatImage),
  };
  base.module_price_cop = moduleCop;
  base.module_usd.img2img = copToUsd(moduleCop.img2img, base);
  base.module_usd.materials = copToUsd(moduleCop.materials, base);
  base.module_usd.text2img = copToUsd(moduleCop.text2img, base);
  base.module_usd.influencer = copToUsd(moduleCop.influencer, base);
  base.module_usd.chat = copToUsd(moduleCop.chat, base);
  base.module_usd.chat_image = copToUsd(moduleCop.chat_image, base);

  const musicCop = {
    "8": parseCopInput(priceMusic8),
    "15": parseCopInput(priceMusic15),
    "30": parseCopInput(priceMusic30),
    "60": parseCopInput(priceMusic60),
    "120": parseCopInput(priceMusic120),
    "180": parseCopInput(priceMusic180),
  };
  base.music_duration_cop = musicCop;
  base.music_duration_usd["8"] = copToUsd(musicCop["8"], base);
  base.music_duration_usd["15"] = copToUsd(musicCop["15"], base);
  base.music_duration_usd["30"] = copToUsd(musicCop["30"], base);
  base.music_duration_usd["60"] = copToUsd(musicCop["60"], base);
  base.music_duration_usd["120"] = copToUsd(musicCop["120"], base);
  base.music_duration_usd["180"] = copToUsd(musicCop["180"], base);

  const videoCop = {
    "kwaivgi/kling-v3-video": {
      "5": parseCopInput(priceI2vKling5),
      "8": parseCopInput(priceI2vKling8),
      "15": parseCopInput(priceI2vKling15),
    },
    "wan-video/wan-2.2-i2v-fast": {
      "5": parseCopInput(priceI2vWan225),
      "8": parseCopInput(priceI2vWan228),
      "15": parseCopInput(priceI2vWan2215),
    },
    "wan-video/wan-2.5-i2v-fast": {
      "5": parseCopInput(priceI2vWan255),
      "8": parseCopInput(priceI2vWan258),
      "15": parseCopInput(priceI2vWan2515),
    },
    "minimax/video-01-live": {
      "5": parseCopInput(priceI2vMinimax5),
      "8": parseCopInput(priceI2vMinimax8),
      "15": parseCopInput(priceI2vMinimax15),
    },
  };
  base.video_price_cop = videoCop;

  const averagePerSecond = (engineKey) => {
    const durations = videoCop[engineKey] || {};
    const values = ["5", "8", "15"].map((seconds) => safeNumber(durations[seconds], 0));
    const usdValues = [
      copToUsd(values[0], base) / 5,
      copToUsd(values[1], base) / 8,
      copToUsd(values[2], base) / 15,
    ].filter((v) => Number.isFinite(v) && v > 0);
    if (!usdValues.length) return 0;
    return usdValues.reduce((sum, value) => sum + value, 0) / usdValues.length;
  };

  base.video_engine_usd_per_second["kwaivgi/kling-v3-video"] = averagePerSecond("kwaivgi/kling-v3-video");
  base.video_engine_usd_per_second["wan-video/wan-2.2-i2v-fast"] = averagePerSecond("wan-video/wan-2.2-i2v-fast");
  base.video_engine_usd_per_second["wan-video/wan-2.5-i2v-fast"] = averagePerSecond("wan-video/wan-2.5-i2v-fast");
  base.video_engine_usd_per_second["minimax/video-01-live"] = averagePerSecond("minimax/video-01-live");

  return base;
}

function setDashboardVisible(visible) {
  if (adminLoginShell) adminLoginShell.hidden = visible;
  if (adminDashboard) adminDashboard.hidden = !visible;
  if (adminLogout) adminLogout.hidden = !visible;
  if (adminRefresh) adminRefresh.hidden = !visible;
  if (adminSessionChip) adminSessionChip.hidden = !visible;
}

function buildModuleBadges(summary) {
  if (!adminDetailModules) return;
  adminDetailModules.innerHTML = "";
  const entries = Object.entries(summary || {});
  if (!entries.length) {
    adminDetailModules.innerHTML = '<span class="badge">Sin generaciones</span>';
    return;
  }

  for (const [moduleName, count] of entries) {
    const badge = document.createElement("span");
    badge.className = "badge";
    badge.textContent = `${moduleName}: ${count}`;
    adminDetailModules.appendChild(badge);
  }
}

function renderDetailGenerations(items) {
  if (!adminDetailGenerations) return;
  adminDetailGenerations.innerHTML = "";

  const rows = Array.isArray(items) ? items : [];
  if (adminHistoryCount) {
    adminHistoryCount.textContent = `${rows.length} registros`;
  }

  if (!rows.length) {
    const row = document.createElement("tr");
    row.innerHTML = '<td colspan="4">No hay generaciones registradas.</td>';
    adminDetailGenerations.appendChild(row);
    return;
  }

  for (const item of rows) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${formatDate(item.updated_at || item.created_at)}</td>
      <td>${item.module || "-"}</td>
      <td>${item.status || "-"}</td>
      <td>${formatCop(item.amount_cop || 0)}</td>
    `;
    adminDetailGenerations.appendChild(row);
  }
}

function renderUsersTable(filterText = "") {
  if (!adminUsersBody) return;
  const query = filterText.trim().toLowerCase();
  const rows = usersCache.filter((item) => {
    if (!query) return true;
    const user = item.user || {};
    return [user.username, user.email, user.first_name, user.last_name]
      .filter(Boolean)
      .some((value) => String(value).toLowerCase().includes(query));
  });

  adminUsersBody.innerHTML = "";
  if (!rows.length) {
    const tr = document.createElement("tr");
    tr.innerHTML = '<td colspan="6">No se encontraron usuarios.</td>';
    adminUsersBody.appendChild(tr);
    return;
  }

  for (const item of rows) {
    const user = item.user || {};
    const tr = document.createElement("tr");
    tr.dataset.userId = String(user.user_id || "");
    if (String(user.user_id) === String(selectedUserId)) {
      tr.classList.add("is-selected");
    }
    const moduleSummary = Object.entries(item.generation_by_module || {})
      .map(([moduleName, count]) => `${moduleName} ${count}`)
      .join(" · ");
    tr.innerHTML = `
      <td>
        <strong>${user.username || "-"}</strong><br />
        <span>${user.first_name || ""} ${user.last_name || ""}</span>
      </td>
      <td>${user.email || "-"}</td>
      <td>${formatCop(item.balance_cop || 0)}</td>
      <td>${item.generation_total || 0}</td>
      <td>${moduleSummary || "-"}</td>
      <td><button type="button" class="admin-btn admin-btn--ghost" data-open-user="${user.user_id || ""}">Ver</button></td>
    `;
    adminUsersBody.appendChild(tr);
  }
}

function renderMetrics() {
  const totalUsers = usersCache.length;
  const totalBalance = usersCache.reduce((sum, item) => sum + Number(item.balance_cop || 0), 0);
  const totalGenerations = usersCache.reduce((sum, item) => sum + Number(item.generation_total || 0), 0);
  const modules = new Set();
  for (const item of usersCache) {
    for (const moduleName of Object.keys(item.generation_by_module || {})) {
      modules.add(moduleName);
    }
  }

  if (metricUsers) metricUsers.textContent = String(totalUsers);
  if (metricBalance) metricBalance.textContent = formatCop(totalBalance);
  if (metricGenerations) metricGenerations.textContent = String(totalGenerations);
  if (metricModules) metricModules.textContent = String(modules.size);
}

function clearDetailState() {
  selectedUserDetail = null;
  selectedUserId = null;
  if (adminSelectedId) adminSelectedId.textContent = "Sin selección";
  if (adminDetailEmpty) adminDetailEmpty.hidden = false;
  if (adminDetailPanel) adminDetailPanel.hidden = true;
}

function renderSelectedUser(detail) {
  selectedUserDetail = detail;
  const user = detail?.user || {};
  const summary = detail?.generation_by_module || {};
  const generations = Array.isArray(detail?.generations) ? detail.generations : [];
  selectedUserId = Number(user.user_id || 0);

  if (adminSelectedId) adminSelectedId.textContent = `ID ${selectedUserId}`;
  if (adminDetailEmpty) adminDetailEmpty.hidden = true;
  if (adminDetailPanel) adminDetailPanel.hidden = false;
  if (adminDetailName) {
    adminDetailName.textContent = `${user.first_name || ""} ${user.last_name || ""}`.trim() || user.username || "Usuario";
  }
  if (adminDetailEmail) adminDetailEmail.textContent = user.email || "-";
  if (adminDetailMeta) {
    adminDetailMeta.textContent = `${user.username || "-"} · ${user.phone || "sin teléfono"} · creado ${formatDate(user.created_at)}`;
  }
  if (adminDetailBalance) adminDetailBalance.textContent = formatCop(detail?.balance_cop || 0);
  if (adminDetailTotal) adminDetailTotal.textContent = String(detail?.generation_total || 0);
  if (adminBalanceInput) adminBalanceInput.value = String(detail?.balance_cop || 0);
  if (adminBalanceNote) adminBalanceNote.value = "Saldo ajustado por administrador";
  buildModuleBadges(summary);
  renderDetailGenerations(generations);
}

async function loadUsers() {
  const response = await fetch("/admin-api/users");
  if (!response.ok) {
    throw new Error(await readApiError(response));
  }
  const data = await response.json();
  usersCache = Array.isArray(data?.items) ? data.items : [];
  renderMetrics();
  renderUsersTable(adminSearch?.value || "");

  if (!selectedUserId && usersCache.length) {
    await loadUserDetail(usersCache[0].user?.user_id);
  } else if (selectedUserId) {
    const current = usersCache.find((item) => Number(item.user?.user_id || 0) === Number(selectedUserId));
    if (current) {
      await loadUserDetail(selectedUserId);
    }
  }
}

async function loadPricing() {
  const response = await fetch("/admin-api/pricing");
  if (!response.ok) {
    throw new Error(await readApiError(response));
  }
  const data = await response.json();
  pricingCache = data?.pricing || {};
  if (adminPricingJson) {
    adminPricingJson.value = formatPricingJson(pricingCache);
  }
  fillCopPricingForm(pricingCache);
  setPricingStatus("Configuración cargada.", "completed");
}

async function loadInfrastructure() {
  const [healthResponse, cutoverResponse, consistencyResponse, metricsResponse, adviceResponse] = await Promise.all([
    fetch("/admin-api/infra/health"),
    fetch("/admin-api/infra/cutover"),
    fetch("/admin-api/infra/consistency"),
    fetch("/admin-api/infra/metrics"),
    fetch("/admin-api/infra/advice"),
  ]);

  if (!healthResponse.ok) {
    throw new Error(await readApiError(healthResponse));
  }
  if (!cutoverResponse.ok) {
    throw new Error(await readApiError(cutoverResponse));
  }
  if (!consistencyResponse.ok) {
    throw new Error(await readApiError(consistencyResponse));
  }
  if (!metricsResponse.ok) {
    throw new Error(await readApiError(metricsResponse));
  }
  if (!adviceResponse.ok) {
    throw new Error(await readApiError(adviceResponse));
  }

  const [health, cutover, consistency, metrics, advice] = await Promise.all([
    healthResponse.json(),
    cutoverResponse.json(),
    consistencyResponse.json(),
    metricsResponse.json(),
    adviceResponse.json(),
  ]);

  renderInfrastructure({ health, cutover, consistency, metrics, advice });
}

async function refreshPricing() {
  setPricingStatus("Cargando configuración de precios...", "processing");
  try {
    await loadPricing();
  } catch (error) {
    setPricingStatus(error instanceof Error ? error.message : "No se pudo cargar la configuración.", "failed");
  }
}

async function loadUserDetail(userId) {
  if (!userId) {
    clearDetailState();
    renderUsersTable(adminSearch?.value || "");
    return;
  }

  const response = await fetch(`/admin-api/users/${userId}`);
  if (!response.ok) {
    throw new Error(await readApiError(response));
  }
  const data = await response.json();
  renderSelectedUser(data);
  renderUsersTable(adminSearch?.value || "");
}

async function refreshAll() {
  try {
    const response = await fetch("/admin-api/me");
    if (!response.ok) {
      adminSession = null;
      setDashboardVisible(false);
      clearDetailState();
      return;
    }

    const data = await response.json();
    adminSession = data?.admin || null;
    setDashboardVisible(true);
    if (adminSessionChip) {
      adminSessionChip.hidden = false;
      adminSessionChip.textContent = adminSession?.username ? `Admin: ${adminSession.username}` : "Sesión activa";
    }
    setInfraStatus("Cargando infraestructura...", "processing");
    await Promise.all([loadUsers(), loadPricing(), loadInfrastructure()]);
  } catch {
    adminSession = null;
    setDashboardVisible(false);
    clearDetailState();
  }
}

adminLoginForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const login = adminLoginInput?.value.trim() || "";
  const password = adminPasswordInput?.value || "";
  if (!login || !password) {
    setLoginStatus("Completa usuario y contraseña.", "failed");
    return;
  }

  if (adminLoginForm instanceof HTMLFormElement) {
    const submit = adminLoginForm.querySelector("button[type='submit']");
    if (submit instanceof HTMLButtonElement) submit.disabled = true;
  }
  setLoginStatus("Validando acceso...", "processing");

  try {
    const response = await fetch("/admin-api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ login, password }),
    });

    if (!response.ok) {
      const error = await readApiError(response);
      setLoginStatus(error, "failed");
      return;
    }

    setLoginStatus("Acceso concedido.", "completed");
    await refreshAll();
  } catch {
    setLoginStatus("No se pudo iniciar sesión como administrador.", "failed");
  } finally {
    if (adminLoginForm instanceof HTMLFormElement) {
      const submit = adminLoginForm.querySelector("button[type='submit']");
      if (submit instanceof HTMLButtonElement) submit.disabled = false;
    }
  }
});

adminLogout?.addEventListener("click", async () => {
  try {
    await fetch("/admin-api/logout", { method: "POST" });
  } finally {
    adminSession = null;
    usersCache = [];
    setDashboardVisible(false);
    clearDetailState();
    renderUsersTable("");
    setLoginStatus("Sesión cerrada.", "idle");
  }
});

adminRefresh?.addEventListener("click", async () => {
  await refreshAll();
});

adminPricingRefresh?.addEventListener("click", async () => {
  await refreshPricing();
});

adminPricingSave?.addEventListener("click", async () => {
  if (!adminPricingJson) return;
  try {
    const parsed = adminPricingAdvanced && !adminPricingAdvanced.hidden
      ? JSON.parse(adminPricingJson.value || "{}")
      : buildPricingFromCopForm();
    setPricingStatus("Guardando configuración...", "processing");
    const response = await fetch("/admin-api/pricing", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pricing: parsed }),
    });
    if (!response.ok) {
      const error = await readApiError(response);
      setPricingStatus(error, "failed");
      return;
    }
    const data = await response.json();
    pricingCache = data?.pricing || parsed;
    adminPricingJson.value = formatPricingJson(pricingCache);
    fillCopPricingForm(pricingCache);
    setPricingStatus("Precios actualizados. La plataforma usará esta configuración.", "completed");
  } catch (error) {
    setPricingStatus(error instanceof Error ? error.message : "JSON inválido.", "failed");
  }
});

adminPricingAdvancedToggle?.addEventListener("click", () => {
  if (!adminPricingAdvanced) return;
  const nextHidden = !adminPricingAdvanced.hidden;
  adminPricingAdvanced.hidden = nextHidden;
  adminPricingAdvancedToggle.textContent = nextHidden ? "Modo avanzado (JSON)" : "Ocultar modo avanzado";
  if (!nextHidden && adminPricingJson) {
    adminPricingJson.value = formatPricingJson(pricingCache || {});
  }
});

adminSearch?.addEventListener("input", () => {
  renderUsersTable(adminSearch.value || "");
});

adminUsersBody?.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) return;
  const button = target.closest("button[data-open-user]");
  const row = target.closest("tr[data-user-id]");
  const userId = Number(button?.dataset.openUser || row?.dataset.userId || 0);
  if (!userId) return;
  try {
    await loadUserDetail(userId);
  } catch (error) {
    window.alert(error instanceof Error ? error.message : "No se pudo cargar el usuario.");
  }
});

adminBalanceForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!selectedUserId || !selectedUserDetail) {
    window.alert("Selecciona un usuario primero.");
    return;
  }

  const newBalance = Math.max(0, Math.round(Number(adminBalanceInput?.value) || 0));
  const note = (adminBalanceNote?.value || "").trim() || "Saldo ajustado por administrador";
  const submit = adminBalanceForm.querySelector("button[type='submit']");
  if (submit instanceof HTMLButtonElement) submit.disabled = true;

  try {
    const response = await fetch(`/admin-api/users/${selectedUserId}/balance`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ balance_cop: newBalance, note }),
    });

    if (!response.ok) {
      const error = await readApiError(response);
      window.alert(error);
      return;
    }

    await refreshAll();
    await loadUserDetail(selectedUserId);
  } catch {
    window.alert("No se pudo actualizar el saldo.");
  } finally {
    if (submit instanceof HTMLButtonElement) submit.disabled = false;
  }
});

window.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && adminDashboard && !adminDashboard.hidden) {
    adminSearch?.blur();
  }
});

refreshAll();
