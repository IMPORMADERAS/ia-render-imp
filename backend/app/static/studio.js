const form = document.getElementById("render-form");
const textForm = document.getElementById("text-form");
const musicForm = document.getElementById("music-form");
const chatForm = document.getElementById("chat-form");
const influencerForm = document.getElementById("influencer-form");

const inputPreview = document.getElementById("input-preview");
const outputPreview = document.getElementById("output-preview");
const statusEl = document.getElementById("status");
const downloadLink = document.getElementById("download-link");
const submitBtn = document.getElementById("submit-btn");
const textSubmitBtn = document.getElementById("text-submit-btn");

const progressFill = document.getElementById("progress-fill");
const progressText = document.getElementById("progress-text");
const stageEl = document.getElementById("stage");
const etaEl = document.getElementById("eta");

const dropZone = document.getElementById("drop-zone");
const dropZoneInput = document.getElementById("image");
const dropZoneFilename = document.getElementById("drop-zone-filename");
const dropZonePreview = document.getElementById("drop-zone-preview");
const animDropZone = document.getElementById("anim-drop-zone");
const animDropZoneInput = document.getElementById("anim-image");
const animDropZoneFilename = document.getElementById("anim-drop-zone-filename");
const animDropZonePreview = document.getElementById("anim-drop-zone-preview");

const tabImg2Img = document.getElementById("tab-img2img");
const tabImg2Vid = document.getElementById("tab-img2vid");
const tabInfluencer = document.getElementById("tab-influencer");
const tabIntelligent = document.getElementById("tab-intelligent");
const tabTxt2Img = document.getElementById("tab-txt2img");
const tabMusic = document.getElementById("tab-music");
const tabChat = document.getElementById("tab-chat");
const paneImg2Img = document.getElementById("mode-img2img");
const paneImg2Vid = document.getElementById("mode-img2vid");
const paneInfluencer = document.getElementById("mode-influencer");
const paneIntelligent = document.getElementById("mode-intelligent");
const paneTxt2Img = document.getElementById("mode-txt2img");
const paneMusic = document.getElementById("mode-music");
const paneChat = document.getElementById("mode-chat");
const examplesGrid = document.getElementById("examples-grid");

const resultShell = document.getElementById("result-shell");
const musicShell = document.getElementById("music-shell");
const chatShell = document.getElementById("chat-shell");
const chatMessages = document.getElementById("chat-messages");
const chatStatus = document.getElementById("chat-status");
const chatNewConversationBtn = document.getElementById("chat-new-conversation");
const chatHistoryToggle = document.getElementById("chat-history-toggle");
const chatHistoryModal = document.getElementById("chat-history-modal");
const chatHistoryClose = document.getElementById("chat-history-close");
const chatHistoryList = document.getElementById("chat-history-list");
const chatHistoryDetail = document.getElementById("chat-history-detail");
const chatHistoryRefresh = document.getElementById("chat-history-refresh");
const chatInput = document.getElementById("chat-input");
const chatAttachBtn = document.getElementById("chat-attach-btn");
const chatAttachInput = document.getElementById("chat-attach-input");
const chatAttachList = document.getElementById("chat-attach-list");
const chatSendBtn = document.getElementById("chat-send-btn");

const animatePanel = document.getElementById("animate-panel");
const animBtn = document.getElementById("anim-btn");
const animPromptEl = document.getElementById("anim-prompt");
const animModelEl = document.getElementById("anim-model");
const animDurationEl = document.getElementById("anim-duration");
const animStatusEl = document.getElementById("anim-status");
const animProgressWrap = document.getElementById("anim-progress-wrap");
const animProgressFill = document.getElementById("anim-progress-fill");
const animProgressText = document.getElementById("anim-progress-text");
const animStageEl = document.getElementById("anim-stage");
const animVideo = document.getElementById("anim-video");
const animDownload = document.getElementById("anim-download");

const musicTypeEl = document.getElementById("music-type");
const musicDurationEl = document.getElementById("music-duration");
const musicGenreEl = document.getElementById("music-genre");
const musicMoodEl = document.getElementById("music-mood");
const musicBpmEl = document.getElementById("music-bpm");
const musicInstrumentsEl = document.getElementById("music-instruments");
const musicTasteEl = document.getElementById("music-taste");
const musicLanguageEl = document.getElementById("music-language");
const musicThemeEl = document.getElementById("music-theme");
const musicLyricsEl = document.getElementById("music-lyrics");
const musicGenerateBtn = document.getElementById("music-generate-btn");

const musicStatusEl = document.getElementById("music-status");
const musicProgressWrap = document.getElementById("music-progress-wrap");
const musicProgressFill = document.getElementById("music-progress-fill");
const musicProgressText = document.getElementById("music-progress-text");
const musicStageEl = document.getElementById("music-stage");
const musicMetaEl = document.getElementById("music-meta");
const musicPlayer = document.getElementById("music-player");
const musicDownload = document.getElementById("music-download");
const influencerImageZone = document.getElementById("influencer-image-zone");
const influencerImageInput = document.getElementById("influencer-image");
const influencerImageFilename = document.getElementById("influencer-image-filename");
const influencerImagePreview = document.getElementById("influencer-image-preview");
const influencerVideoZone = document.getElementById("influencer-video-zone");
const influencerVideoInput = document.getElementById("influencer-video");
const influencerVideoFilename = document.getElementById("influencer-video-filename");
const influencerVideoPreview = document.getElementById("influencer-video-preview");
const influencerInstruction = document.getElementById("influencer-instruction");
const influencerResolution = document.getElementById("influencer-resolution");
const influencerFps = document.getElementById("influencer-fps");
const influencerConsent = document.getElementById("influencer-consent");
const influencerGenerateBtn = document.getElementById("influencer-generate-btn");
const influencerStatus = document.getElementById("influencer-status");
const influencerProgressWrap = document.getElementById("influencer-progress-wrap");
const influencerProgressFill = document.getElementById("influencer-progress-fill");
const influencerProgressText = document.getElementById("influencer-progress-text");
const influencerStage = document.getElementById("influencer-stage");
const influencerResultVideo = document.getElementById("influencer-result-video");
const influencerDownload = document.getElementById("influencer-download");
const t2iStepsInput = document.getElementById("t2i-steps");
const materialModeEl = document.getElementById("material-mode");
const materialPlanEl = document.getElementById("material-plan");
const materialsToggleEl = document.getElementById("materials-toggle");
const materialsPanelEl = document.getElementById("materials-panel");
const materialsToggleIconEl = document.getElementById("materials-toggle-icon");
const materialsLibraryEl = document.getElementById("materials-library");
const materialsSearchEl = document.getElementById("materials-search");
const materialsSelectedEl = document.getElementById("materials-selected");
const materialsCountEl = document.getElementById("materials-count");
const btnPrices = document.getElementById("btn-prices");
const btnSmartProject = document.getElementById("btn-smart-project");
const btnRecharge = document.getElementById("btn-recharge");
const btnAccount = document.getElementById("btn-account");
const btnStudioImp = document.getElementById("btn-studio-imp");
const btnLogin = document.getElementById("btn-login");
const btnLogout = document.getElementById("btn-logout");
const accountChip = document.getElementById("account-chip");
const pricesModal = document.getElementById("prices-modal");
const pricesClose = document.getElementById("prices-close");
const pricesTableBody = document.getElementById("prices-table-body");
const pricesVideoBody = document.getElementById("prices-video-body");
const pricesMusicBody = document.getElementById("prices-music-body");
const pricesRechargeBody = document.getElementById("prices-recharge-body");
const pricesPlanBanners = document.getElementById("prices-plan-banners");
const pricesNote = document.getElementById("prices-note");
const rechargeModal = document.getElementById("recharge-modal");
const rechargeClose = document.getElementById("recharge-close");
const rechargeForm = document.getElementById("recharge-form");
const rechargeAmount = document.getElementById("recharge-amount");
const rechargePayValue = document.getElementById("recharge-pay-value");
const rechargeCreditValue = document.getElementById("recharge-credit-value");
const rechargeSubmit = document.getElementById("recharge-submit");
const rechargePlanCapacity = document.getElementById("recharge-plan-capacity");
const authModal = document.getElementById("auth-modal");
const authClose = document.getElementById("auth-close");
const authTabLogin = document.getElementById("auth-tab-login");
const authTabRegister = document.getElementById("auth-tab-register");
const authForm = document.getElementById("auth-form");
const authRegisterFields = document.getElementById("auth-register-fields");
const authFirstName = document.getElementById("auth-first-name");
const authLastName = document.getElementById("auth-last-name");
const authEmail = document.getElementById("auth-email");
const authLogin = document.getElementById("auth-login");
const authPassword = document.getElementById("auth-password");
const authPasswordConfirmWrap = document.getElementById("auth-confirm-wrap");
const authPasswordConfirm = document.getElementById("auth-password-confirm");
const authRecoverToggle = document.getElementById("auth-recover-toggle");
const authRecoverWrap = document.getElementById("auth-recover-wrap");
const authRecoverEmail = document.getElementById("auth-recover-email");
const authResetWrap = document.getElementById("auth-reset-wrap");
const authResetToken = document.getElementById("auth-reset-token");
const authResetPassword = document.getElementById("auth-reset-password");
const authResetPasswordConfirm = document.getElementById("auth-reset-password-confirm");
const authSubmit = document.getElementById("auth-submit");
const authStatus = document.getElementById("auth-status");
const accountModal = document.getElementById("account-modal");
const accountClose = document.getElementById("account-close");
const accountDeleteTopBtn = document.getElementById("account-delete-top-btn");
const accountProfileForm = document.getElementById("account-profile-form");
const accountFirstName = document.getElementById("account-first-name");
const accountLastName = document.getElementById("account-last-name");
const accountEmail = document.getElementById("account-email");
const accountPhone = document.getElementById("account-phone");
const accountUsername = document.getElementById("account-username");
const accountProfileSubmit = document.getElementById("account-profile-submit");
const accountProfileStatus = document.getElementById("account-profile-status");
const accountBalance = document.getElementById("account-balance");
const accountPasswordForm = document.getElementById("account-password-form");
const accountCurrentPassword = document.getElementById("account-current-password");
const accountNewPassword = document.getElementById("account-new-password");
const accountConfirmPassword = document.getElementById("account-confirm-password");
const accountPasswordSubmit = document.getElementById("account-password-submit");
const accountPasswordStatus = document.getElementById("account-password-status");
const accountDeleteBtn = document.getElementById("account-delete-btn");
const accountDeleteStatus = document.getElementById("account-delete-status");
const accountGenerationsBody = document.getElementById("account-generations-body");
const accountChatHistoryBody = document.getElementById("account-chat-history-body");

const intelligentForm = document.getElementById("intelligent-form");
const intelligentPromptEl = document.getElementById("intelligent-prompt");
const intelligentIncludeVideoEl = document.getElementById("intelligent-include-video");
const intelligentDurationEl = document.getElementById("intelligent-duration");
const intelligentSubmitBtn = document.getElementById("intelligent-submit-btn");
const intelligentStatusEl = document.getElementById("intelligent-status");
const intelligentLinksEl = document.getElementById("intelligent-links");
const intelligentVideoLinkEl = document.getElementById("intelligent-video-link");
const intelligentReportLinkEl = document.getElementById("intelligent-report-link");
const intelligentQuantitiesEl = document.getElementById("intelligent-quantities");
const intelligentMaterialsToggleEl = document.getElementById("intelligent-materials-toggle");
const intelligentMaterialsPanelEl = document.getElementById("intelligent-materials-panel");
const intelligentMaterialsToggleIconEl = document.getElementById("intelligent-materials-toggle-icon");
const intelligentMaterialsSearchEl = document.getElementById("intelligent-materials-search");
const intelligentMaterialsLibraryEl = document.getElementById("intelligent-materials-library");
const intelligentMaterialsSelectedEl = document.getElementById("intelligent-materials-selected");
const intelligentMaterialsCountEl = document.getElementById("intelligent-materials-count");

let pollingTimer = null;
let currentAnimJobId = null;
let animPollingTimer = null;
let animVisualProgress = 0;
let musicPollingTimer = null;
let musicVisualProgress = 0;
let influencerPollingTimer = null;
let influencerVisualProgress = 0;
let wompiSyncTimer = null;
const chatHistory = [];
let chatHistoryPanelLoaded = false;
let activeConversationId = `conv-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
let chatAttachedFiles = [];
let materialItems = [];
const selectedMaterialNames = [];
let materialSearchQuery = "";
const intelligentSelectedMaterialNames = [];
let intelligentMaterialSearchQuery = "";
let currentMode = "img2img";
let activeRenderJobId = null;
let intelligentPollingTimer = null;
let authMode = "login";
let currentUser = null;
const wompiWatchingRefs = new Set();
let paymentNoticeTimer = null;

const WOMPI_APPROVAL_POLL_MS = 3000;
const WOMPI_APPROVAL_WAIT_MS = 120000;

function hideImageElement(imgEl) {
  if (!imgEl) return;
  imgEl.removeAttribute("src");
  imgEl.style.display = "none";
}

function ensurePaymentNoticeUi() {
  let container = document.getElementById("payment-notice-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "payment-notice-container";
    container.className = "payment-notice-overlay";
    container.setAttribute("aria-live", "polite");
    container.setAttribute("aria-atomic", "true");
    container.addEventListener("click", (event) => {
      if (event.target === container) {
        container.classList.remove("is-open");
        container.innerHTML = "";
      }
    });
    document.body.appendChild(container);
  }

  if (!document.getElementById("payment-notice-styles")) {
    const styles = document.createElement("style");
    styles.id = "payment-notice-styles";
    styles.textContent = `
      #payment-notice-container {
        position: fixed;
        inset: 0;
        z-index: 13000;
        display: none;
        align-items: center;
        justify-content: center;
        padding: 18px;
        background: rgba(4, 9, 7, 0.62);
        backdrop-filter: blur(4px);
        -webkit-backdrop-filter: blur(4px);
      }
      #payment-notice-container.is-open {
        display: flex;
      }
      .payment-notice {
        min-width: 300px;
        max-width: min(560px, calc(100vw - 36px));
        pointer-events: auto;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.16);
        box-shadow: 0 18px 44px rgba(0, 0, 0, 0.4);
        padding: 14px 16px;
        color: #f3fff8;
        font-size: 0.94rem;
        line-height: 1.45;
        animation: paymentNoticeIn 220ms ease-out;
        backdrop-filter: blur(4px);
        -webkit-backdrop-filter: blur(4px);
      }
      .payment-notice--info { background: rgba(17, 28, 47, 0.95); }
      .payment-notice--success { background: rgba(11, 49, 30, 0.95); }
      .payment-notice--warning { background: rgba(71, 49, 10, 0.95); }
      .payment-notice--error { background: rgba(77, 24, 24, 0.95); }
      .payment-notice__head {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
      }
      .payment-notice__title {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        margin: 0;
        font-weight: 700;
      }
      .payment-notice__message {
        margin: 6px 0 0;
        color: #d8efe2;
      }
      .payment-notice__close {
        border: 0;
        border-radius: 999px;
        width: 24px;
        height: 24px;
        cursor: pointer;
        color: #e9fff3;
        background: rgba(255, 255, 255, 0.14);
      }
      @keyframes paymentNoticeIn {
        from { transform: translateY(-10px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
      }
    `;
    document.head.appendChild(styles);
  }

  return container;
}

function showPaymentNotice(message, type = "info", options = {}) {
  const safeMessage = String(message || "").trim();
  if (!safeMessage) return;

  const { durationMs = 5600 } = options;
  const container = ensurePaymentNoticeUi();
  if (!container) return;

  container.innerHTML = "";
  container.classList.add("is-open");

  const titles = {
    info: "Proceso de pago",
    success: "Pago actualizado",
    warning: "Pago pendiente",
    error: "Pago no procesado",
  };
  const icons = {
    info: "•",
    success: "✓",
    warning: "!",
    error: "x",
  };
  const safeType = ["info", "success", "warning", "error"].includes(type) ? type : "info";

  const notice = document.createElement("section");
  notice.className = `payment-notice payment-notice--${safeType}`;
  notice.setAttribute("role", safeType === "error" ? "alert" : "status");
  notice.innerHTML = `
    <div class="payment-notice__head">
      <p class="payment-notice__title"><span aria-hidden="true">${icons[safeType]}</span>${titles[safeType]}</p>
      <button class="payment-notice__close" type="button" aria-label="Cerrar aviso">×</button>
    </div>
    <p class="payment-notice__message"></p>
  `;

  const messageEl = notice.querySelector(".payment-notice__message");
  if (messageEl) {
    messageEl.textContent = safeMessage;
  }

  const closeBtn = notice.querySelector(".payment-notice__close");
  if (closeBtn) {
    closeBtn.addEventListener("click", () => {
      if (paymentNoticeTimer) {
        clearTimeout(paymentNoticeTimer);
        paymentNoticeTimer = null;
      }
      container.classList.remove("is-open");
      notice.remove();
    });
  }

  container.appendChild(notice);

  if (paymentNoticeTimer) {
    clearTimeout(paymentNoticeTimer);
  }
  if (durationMs > 0) {
    paymentNoticeTimer = setTimeout(() => {
      container.classList.remove("is-open");
      notice.remove();
      paymentNoticeTimer = null;
    }, durationMs);
  }
}

const DEFAULT_PRICING = {
  usd_to_cop: 3602.817479,
  pricing_margin_multiplier: 1.5,
  wompi_percent: 0.0265,
  wompi_fixed_fee: 700,
  wompi_iva_rate: 0.19,
  recharge_plans: [5000, 10000, 15000, 20000, 25000, 30000, 35000, 40000, 45000, 50000],
  module_usd: {
    img2img: 0.04,
    materials: 0.039,
    text2img: 0.039,
    influencer: 0.9,
    chat: 0.01,
    intelligent_project: 10.0,
  },
  module_price_cop: {},
  music_duration_usd: { 8: 0.08, 15: 0.15, 30: 0.3, 60: 0.6, 120: 1.2, 180: 1.8 },
  music_duration_cop: {},
  video_engine_usd_per_second: {
    "kwaivgi/kling-v3-video": 0.224,
    "wan-video/wan-2.2-i2v-fast": 0.022,
    "wan-video/wan-2.5-i2v-fast": 0.068,
    "minimax/video-01-live": 0.1,
  },
  video_price_cop: {},
};

let pricingConfig = JSON.parse(JSON.stringify(DEFAULT_PRICING));

const MUSIC_GENRE_PRESETS = {
  salsa_choke_calena: {
    genre: "Salsa choke caleña comercial",
    mood: "energetico, bailable, callejero y pegajoso",
    bpm: "102",
    instruments: "timbal, congas, brass hits, bass groove, percusion urbana, synth support",
    taste: "hook fuerte, sonido de feria y discoteca, mezcla comercial, coros memorables",
    theme: "fiesta, barrio, actitud y celebracion",
    language: "es",
  },
  electronica: {
    genre: "Electronica comercial festivalera",
    mood: "epica, energica, envolvente y moderna",
    bpm: "128",
    instruments: "synth leads, bassline potente, drums punchy, risers, pads atmosfericos",
    taste: "drop contundente, build-up potente, mezcla premium, impacto club y streaming",
    theme: "noche, energia, movimiento y euforia",
    language: "en",
  },
  afrobeat: {
    genre: "Afrobeat comercial moderno",
    mood: "calido, sensual, veraniego y pegajoso",
    bpm: "105",
    instruments: "afro percussion, guitar plucks, deep bass, soft synths, vocal chops",
    taste: "groove internacional, coros faciles de recordar, mezcla limpia, sonido premium",
    theme: "verano, fiesta, baile y carisma",
    language: "es",
  },
  reggaeton: {
    genre: "Regaeton comercial mainstream",
    mood: "agresivo, sensual, urbano y adictivo",
    bpm: "94",
    instruments: "dembow drums, sub bass, synth leads, fx urbanos, pads oscuros",
    taste: "hook viral, beat potente, mezcla radial, pegada comercial y energia urbana",
    theme: "fiesta, deseo, seguridad y calle",
    language: "es",
  },
  house: {
    genre: "House comercial elegante",
    mood: "uplifting, sofisticado, vibrante y elegante",
    bpm: "124",
    instruments: "four-on-the-floor kick, piano house, bass groove, vocal chops, pads",
    taste: "club premium, groove constante, mezcla amplia, feel internacional",
    theme: "lujo, noche, estilo y movimiento",
    language: "en",
  },
  rap_rock: {
    genre: "Rap Rock comercial",
    mood: "intenso, rebelde, poderoso y motivador",
    bpm: "96",
    instruments: "electric guitars, live drums, bass, turntable fx, aggressive synth support",
    taste: "riff memorable, coro fuerte, energia de estadio, mezcla potente y moderna",
    theme: "superacion, fuerza, identidad y resistencia",
    language: "es",
  },
  new_metal: {
    genre: "New Metal moderno",
    mood: "oscuro, agresivo, emocional y explosivo",
    bpm: "92",
    instruments: "heavy guitars, distorted bass, hard drums, atmospheric textures, fx industriales",
    taste: "coro masivo, breakdown potente, mezcla grande, energia extrema y moderna",
    theme: "catarsis, lucha interna, rabia y poder",
    language: "en",
  },
  balada_pop: {
    genre: "Balada pop comercial",
    mood: "emocional, romantica, inspiradora y memorable",
    bpm: "78",
    instruments: "piano, acoustic guitar, strings, soft drums, ambient pads",
    taste: "melodia fuerte, coro inolvidable, produccion limpia, radio-friendly y emocional",
    theme: "amor, nostalgia, esperanza y crecimiento",
    language: "es",
  },
  pop_urbano_comercial: {
    genre: "Pop urbano comercial",
    mood: "fresh, juvenil, pegajoso y aspiracional",
    bpm: "100",
    instruments: "urban drums, synth bass, plucks, ambient pads, melodic lead",
    taste: "hook viral, mezcla premium, sonido global, energia comercial y moderna",
    theme: "amor propio, deseo, fiesta y lifestyle",
    language: "es",
  },
};

function applyPricingConfig(rawConfig) {
  const incoming = rawConfig && typeof rawConfig === "object" ? rawConfig : {};
  pricingConfig = {
    ...DEFAULT_PRICING,
    ...incoming,
    module_usd: { ...DEFAULT_PRICING.module_usd, ...(incoming.module_usd || {}) },
    module_price_cop: { ...DEFAULT_PRICING.module_price_cop, ...(incoming.module_price_cop || {}) },
    music_duration_usd: { ...DEFAULT_PRICING.music_duration_usd, ...(incoming.music_duration_usd || {}) },
    music_duration_cop: { ...DEFAULT_PRICING.music_duration_cop, ...(incoming.music_duration_cop || {}) },
    video_engine_usd_per_second: {
      ...DEFAULT_PRICING.video_engine_usd_per_second,
      ...(incoming.video_engine_usd_per_second || {}),
    },
    video_price_cop: {
      ...DEFAULT_PRICING.video_price_cop,
      ...(incoming.video_price_cop || {}),
    },
    recharge_plans: Array.isArray(incoming.recharge_plans) && incoming.recharge_plans.length
      ? incoming.recharge_plans.map((value) => Math.max(5000, Math.round(Number(value) || 0))).filter(Boolean)
      : DEFAULT_PRICING.recharge_plans,
  };
}

async function loadPricingConfig() {
  try {
    const response = await fetch("/pricing/config");
    if (!response.ok) return;
    const data = await response.json();
    applyPricingConfig(data?.pricing);
  } catch {
    applyPricingConfig(DEFAULT_PRICING);
  }
}

function openPasswordResetFromUrl() {
  const params = new URLSearchParams(window.location.search);
  const resetToken = params.get("reset_token") || "";
  if (!resetToken) return false;

  openAuthModal("reset");
  if (authResetToken) authResetToken.value = resetToken;
  return true;
}

function showImageElement(imgEl, src) {
  if (!imgEl || !src) {
    hideImageElement(imgEl);
    return;
  }
  imgEl.src = src;
  imgEl.style.display = "block";
}

function attachImageFallback(imgEl) {
  if (!imgEl) return;
  imgEl.addEventListener("error", () => {
    hideImageElement(imgEl);
  });
}

function makeExampleTile(item, index) {
  const tile = document.createElement("article");
  tile.className = "hero-stage__tile";
  if (index === 0) {
    tile.classList.add("hero-stage__tile--wide");
  }

  const safeName = String(item?.name || "Ejemplo");
  const safeUrl = String(item?.url || "");
  const kind = String(item?.kind || "");

  if (kind === "video") {
    const video = document.createElement("video");
    video.autoplay = true;
    video.muted = true;
    video.loop = true;
    video.preload = "metadata";
    video.src = safeUrl;
    tile.appendChild(video);
  } else if (kind === "audio") {
    const audio = document.createElement("audio");
    audio.controls = true;
    audio.preload = "metadata";
    audio.src = safeUrl;
    tile.appendChild(audio);
  } else {
    const image = document.createElement("img");
    image.loading = "lazy";
    image.alt = safeName;
    image.src = safeUrl;
    tile.appendChild(image);
  }

  const caption = document.createElement("span");
  caption.className = "hero-stage__tile-caption";
  caption.textContent = safeName;
  tile.appendChild(caption);

  return tile;
}

function renderExamplesFallback(message) {
  if (!examplesGrid) return;
  examplesGrid.innerHTML = "";
  const tile = document.createElement("article");
  tile.className = "hero-stage__tile hero-stage__tile--wide hero-stage__tile--empty";
  const text = document.createElement("p");
  text.textContent = message;
  tile.appendChild(text);
  examplesGrid.appendChild(tile);
}

async function loadExamplesFromContenido() {
  if (!examplesGrid) return;

  try {
    const response = await fetch("/examples/library");
    if (!response.ok) {
      throw new Error("No se pudo cargar el panel de ejemplos");
    }

    const data = await response.json();
    const allItems = Array.isArray(data.examples) ? data.examples : [];
    if (!allItems.length) {
      renderExamplesFallback("Aun no hay ejemplos en la carpeta Contenido.");
      return;
    }

    const preferredOrder = { video: 0, image: 1, audio: 2 };
    allItems.sort((a, b) => {
      const pa = preferredOrder[a.kind] ?? 9;
      const pb = preferredOrder[b.kind] ?? 9;
      if (pa !== pb) return pa - pb;
      return String(a.name).localeCompare(String(b.name));
    });

    const visibleItems = allItems.slice(0, 6);
    examplesGrid.innerHTML = "";
    visibleItems.forEach((item, index) => {
      examplesGrid.appendChild(makeExampleTile(item, index));
    });
  } catch {
    renderExamplesFallback("No se pudo leer la carpeta Contenido en este momento.");
  }
}

[inputPreview, outputPreview, dropZonePreview, animDropZonePreview, influencerImagePreview].forEach((imgEl) => {
  attachImageFallback(imgEl);
  hideImageElement(imgEl);
});

function getRechargePlans() {
  const source = Array.isArray(pricingConfig?.recharge_plans) && pricingConfig.recharge_plans.length
    ? pricingConfig.recharge_plans
    : DEFAULT_PRICING.recharge_plans;
  const cleaned = source
    .map((value) => Math.max(5000, Math.round(Number(value) || 0)))
    .filter((value) => Number.isFinite(value) && value > 0);
  return cleaned.length ? cleaned : DEFAULT_PRICING.recharge_plans;
}

function getPricingCatalog() {
  const moduleUsd = pricingConfig?.module_usd || {};
  return [
    { key: "img2img", module: "Imagen a Imagen", usdBase: Number(moduleUsd.img2img ?? DEFAULT_PRICING.module_usd.img2img) },
    { key: "materials", module: "Materiales IA", usdBase: Number(moduleUsd.materials ?? DEFAULT_PRICING.module_usd.materials) },
    { key: "text2img", module: "Texto a Imagen", usdBase: Number(moduleUsd.text2img ?? DEFAULT_PRICING.module_usd.text2img) },
    { key: "intelligent_project", module: "Proyecto Inteligente", usdBase: Number(moduleUsd.intelligent_project ?? DEFAULT_PRICING.module_usd.intelligent_project) },
    { key: "influencer", module: "Influencer IA", usdBase: Number(moduleUsd.influencer ?? DEFAULT_PRICING.module_usd.influencer) },
    { key: "chat", module: "Pachy IA", usdBase: Number(moduleUsd.chat ?? DEFAULT_PRICING.module_usd.chat) },
  ];
}

function getImageToVideoEngines() {
  const engines = pricingConfig?.video_engine_usd_per_second || {};
  return [
    {
      id: "kwaivgi/kling-v3-video",
      engine: "Cinematic Pro",
      usdPerSecond: Number(engines["kwaivgi/kling-v3-video"] ?? DEFAULT_PRICING.video_engine_usd_per_second["kwaivgi/kling-v3-video"]),
      badge: "Premium",
      badgeClass: "premium",
    },
    {
      id: "wan-video/wan-2.2-i2v-fast",
      engine: "Video Economico",
      usdPerSecond: Number(engines["wan-video/wan-2.2-i2v-fast"] ?? DEFAULT_PRICING.video_engine_usd_per_second["wan-video/wan-2.2-i2v-fast"]),
      badge: "Economico",
      badgeClass: "economy",
    },
  ];
}

function getMusicDurationPricing() {
  const durations = pricingConfig?.music_duration_usd || {};
  return [
    { seconds: 180, usdBase: Number(durations[180] ?? durations["180"] ?? DEFAULT_PRICING.music_duration_usd[180]), label: "Automatico actual", featured: true },
  ];
}

function getWompiCoverageFactor() {
  let factorSum = 0;
  for (const amount of getRechargePlans()) {
    const fee = amount * Number(pricingConfig.wompi_percent || DEFAULT_PRICING.wompi_percent) + Number(pricingConfig.wompi_fixed_fee || DEFAULT_PRICING.wompi_fixed_fee);
    const feeWithIva = fee * (1 + Number(pricingConfig.wompi_iva_rate || DEFAULT_PRICING.wompi_iva_rate));
    const net = amount - feeWithIva;
    const factor = net > 0 ? amount / net : 1;
    factorSum += factor;
  }
  return factorSum / getRechargePlans().length;
}

const imageToVideoDurations = [5, 8, 15];

if (t2iStepsInput) {
  const clampTextSteps = () => {
    const raw = Number(t2iStepsInput.value || "4");
    const safe = Number.isFinite(raw) ? Math.max(1, Math.min(4, Math.round(raw))) : 4;
    t2iStepsInput.value = String(safe);
  };
  t2iStepsInput.addEventListener("input", clampTextSteps);
  t2iStepsInput.addEventListener("change", clampTextSteps);
  clampTextSteps();
}

function setMaterialModeState() {
  const isZones = materialModeEl && materialModeEl.value === "zones";
  if (!materialPlanEl) return;
  materialPlanEl.disabled = !isZones;
  materialPlanEl.placeholder = isZones
    ? "Ej: Material 1 en muro principal, Material 2 en zocalos."
    : "Opcional. En modo combinar, la IA mezcla ambos materiales de forma natural.";
}

function updateMaterialsCount() {
  if (!materialsCountEl) return;
  materialsCountEl.textContent = `${selectedMaterialNames.length}/2`;
}

function setMaterialsDropdownState(expanded) {
  if (!materialsToggleEl || !materialsPanelEl) return;
  materialsPanelEl.hidden = !expanded;
  materialsToggleEl.setAttribute("aria-expanded", String(expanded));
  if (materialsToggleIconEl) {
    materialsToggleIconEl.textContent = expanded ? "▴" : "▾";
  }
  if (expanded && materialsSearchEl) {
    requestAnimationFrame(() => materialsSearchEl.focus());
  }
}

function normalizeSearchText(value) {
  return String(value || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
}

function getFilteredMaterialItems() {
  const query = normalizeSearchText(materialSearchQuery);
  if (!query) return materialItems;

  return materialItems.filter((item) => {
    const brand = item.brand || (item.relative_path || "").split("/")[0] || "";
    const haystack = normalizeSearchText(`${item.name} ${brand} ${item.relative_path}`);
    return haystack.includes(query);
  });
}

function getFilteredIntelligentMaterialItems() {
  const query = normalizeSearchText(intelligentMaterialSearchQuery);
  if (!query) return materialItems;

  return materialItems.filter((item) => {
    const brand = item.brand || (item.relative_path || "").split("/")[0] || "";
    const haystack = normalizeSearchText(`${item.name} ${brand} ${item.relative_path}`);
    return haystack.includes(query);
  });
}

function renderSelectedMaterials() {
  if (!materialsSelectedEl) return;
  materialsSelectedEl.innerHTML = "";

  if (!selectedMaterialNames.length) {
    const note = document.createElement("p");
    note.className = "hint";
    note.textContent = "Aun no has seleccionado materiales.";
    materialsSelectedEl.appendChild(note);
    return;
  }

  for (const rel of selectedMaterialNames) {
    const item = materialItems.find((m) => m.relative_path === rel);
    if (!item) continue;

    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "material-chip";
    chip.textContent = `${item.name} ×`;
    chip.addEventListener("click", () => {
      const idx = selectedMaterialNames.indexOf(rel);
      if (idx >= 0) {
        selectedMaterialNames.splice(idx, 1);
        renderMaterialsLibrary();
        renderSelectedMaterials();
        updateMaterialsCount();
      }
    });
    materialsSelectedEl.appendChild(chip);
  }
}

function renderMaterialsLibrary() {
  if (!materialsLibraryEl) return;

  materialsLibraryEl.innerHTML = "";
  if (!materialItems.length) {
    const empty = document.createElement("p");
    empty.className = "hint";
    empty.textContent = "No se encontraron archivos en la carpeta Materiales.";
    materialsLibraryEl.appendChild(empty);
    return;
  }

  const filteredItems = getFilteredMaterialItems();
  if (!filteredItems.length) {
    const empty = document.createElement("p");
    empty.className = "hint";
    empty.textContent = "No hay coincidencias con tu busqueda.";
    materialsLibraryEl.appendChild(empty);
    return;
  }

  for (const item of filteredItems) {
    const card = document.createElement("button");
    card.type = "button";
    card.className = "material-card";
    card.setAttribute("aria-pressed", String(selectedMaterialNames.includes(item.relative_path)));
    if (selectedMaterialNames.includes(item.relative_path)) {
      card.classList.add("selected");
    }

    const brandLabel = String(item.brand || (item.relative_path || "").split("/")[0] || "General");
    card.innerHTML = `
      <img src="${item.url}" alt="${item.name}" loading="lazy" />
      <span>${brandLabel} · ${item.name}</span>
    `;

    const cardImage = card.querySelector("img");
    if (cardImage) {
      cardImage.addEventListener("error", () => {
        cardImage.style.display = "none";
      });
    }

    card.addEventListener("click", () => {
      const idx = selectedMaterialNames.indexOf(item.relative_path);
      if (idx >= 0) {
        selectedMaterialNames.splice(idx, 1);
      } else {
        if (selectedMaterialNames.length >= 2) {
          setStatus("Solo puedes seleccionar hasta 2 materiales", "failed");
          return;
        }
        selectedMaterialNames.push(item.relative_path);
      }

      renderMaterialsLibrary();
      renderSelectedMaterials();
      updateMaterialsCount();
    });

    materialsLibraryEl.appendChild(card);
  }
}

function updateIntelligentMaterialsCount() {
  if (!intelligentMaterialsCountEl) return;
  intelligentMaterialsCountEl.textContent = `${intelligentSelectedMaterialNames.length}/2`;
}

function setIntelligentMaterialsDropdownState(expanded) {
  if (!intelligentMaterialsToggleEl || !intelligentMaterialsPanelEl) return;
  intelligentMaterialsPanelEl.hidden = !expanded;
  intelligentMaterialsToggleEl.setAttribute("aria-expanded", String(expanded));
  if (intelligentMaterialsToggleIconEl) {
    intelligentMaterialsToggleIconEl.textContent = expanded ? "▴" : "▾";
  }
  if (expanded && intelligentMaterialsSearchEl) {
    requestAnimationFrame(() => intelligentMaterialsSearchEl.focus());
  }
}

function renderIntelligentSelectedMaterials() {
  if (!intelligentMaterialsSelectedEl) return;
  intelligentMaterialsSelectedEl.innerHTML = "";

  if (!intelligentSelectedMaterialNames.length) {
    const note = document.createElement("p");
    note.className = "hint";
    note.textContent = "Selecciona 1 o 2 materiales para Proyecto Inteligente.";
    intelligentMaterialsSelectedEl.appendChild(note);
    return;
  }

  for (const rel of intelligentSelectedMaterialNames) {
    const item = materialItems.find((m) => m.relative_path === rel);
    if (!item) continue;

    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "material-chip";
    chip.textContent = `${item.name} ×`;
    chip.addEventListener("click", () => {
      const idx = intelligentSelectedMaterialNames.indexOf(rel);
      if (idx >= 0) {
        intelligentSelectedMaterialNames.splice(idx, 1);
        renderIntelligentMaterialsLibrary();
        renderIntelligentSelectedMaterials();
        updateIntelligentMaterialsCount();
      }
    });
    intelligentMaterialsSelectedEl.appendChild(chip);
  }
}

function renderIntelligentMaterialsLibrary() {
  if (!intelligentMaterialsLibraryEl) return;

  intelligentMaterialsLibraryEl.innerHTML = "";
  if (!materialItems.length) {
    const empty = document.createElement("p");
    empty.className = "hint";
    empty.textContent = "No se encontraron archivos en la carpeta Materiales.";
    intelligentMaterialsLibraryEl.appendChild(empty);
    return;
  }

  const filteredItems = getFilteredIntelligentMaterialItems();
  if (!filteredItems.length) {
    const empty = document.createElement("p");
    empty.className = "hint";
    empty.textContent = "No hay coincidencias con tu busqueda.";
    intelligentMaterialsLibraryEl.appendChild(empty);
    return;
  }

  for (const item of filteredItems) {
    const card = document.createElement("button");
    card.type = "button";
    card.className = "material-card";
    card.setAttribute("aria-pressed", String(intelligentSelectedMaterialNames.includes(item.relative_path)));
    if (intelligentSelectedMaterialNames.includes(item.relative_path)) {
      card.classList.add("selected");
    }

    const brandLabel = String(item.brand || (item.relative_path || "").split("/")[0] || "General");
    card.innerHTML = `
      <img src="${item.url}" alt="${item.name}" loading="lazy" />
      <span>${brandLabel} · ${item.name}</span>
    `;

    const cardImage = card.querySelector("img");
    if (cardImage) {
      cardImage.addEventListener("error", () => {
        cardImage.style.display = "none";
      });
    }

    card.addEventListener("click", () => {
      const idx = intelligentSelectedMaterialNames.indexOf(item.relative_path);
      if (idx >= 0) {
        intelligentSelectedMaterialNames.splice(idx, 1);
      } else {
        if (intelligentSelectedMaterialNames.length >= 2) {
          setStatus("Solo puedes seleccionar hasta 2 materiales", "failed");
          return;
        }
        intelligentSelectedMaterialNames.push(item.relative_path);
      }

      renderIntelligentMaterialsLibrary();
      renderIntelligentSelectedMaterials();
      updateIntelligentMaterialsCount();
    });

    intelligentMaterialsLibraryEl.appendChild(card);
  }
}

async function loadMaterialsLibrary() {
  if (!materialsLibraryEl) return;

  try {
    const response = await fetch("/materials/library");
    if (!response.ok) {
      throw new Error(await response.text());
    }

    const data = await response.json();
    materialItems = Array.isArray(data.materials) ? data.materials : [];
    renderMaterialsLibrary();
    renderSelectedMaterials();
    updateMaterialsCount();
    renderIntelligentMaterialsLibrary();
    renderIntelligentSelectedMaterials();
    updateIntelligentMaterialsCount();
  } catch {
    materialItems = [];
    renderMaterialsLibrary();
    renderSelectedMaterials();
    updateMaterialsCount();
    renderIntelligentMaterialsLibrary();
    renderIntelligentSelectedMaterials();
    updateIntelligentMaterialsCount();
  }
}

if (materialModeEl) {
  materialModeEl.addEventListener("change", setMaterialModeState);
  setMaterialModeState();
}

if (materialsToggleEl && materialsPanelEl) {
  setMaterialsDropdownState(false);
  materialsToggleEl.addEventListener("click", () => {
    const expanded = materialsToggleEl.getAttribute("aria-expanded") === "true";
    setMaterialsDropdownState(!expanded);
  });
}

if (materialsSearchEl) {
  materialsSearchEl.addEventListener("input", () => {
    materialSearchQuery = materialsSearchEl.value || "";
    renderMaterialsLibrary();
  });
}

if (intelligentMaterialsToggleEl && intelligentMaterialsPanelEl) {
  setIntelligentMaterialsDropdownState(false);
  intelligentMaterialsToggleEl.addEventListener("click", () => {
    const expanded = intelligentMaterialsToggleEl.getAttribute("aria-expanded") === "true";
    setIntelligentMaterialsDropdownState(!expanded);
  });
}

if (intelligentMaterialsSearchEl) {
  intelligentMaterialsSearchEl.addEventListener("input", () => {
    intelligentMaterialSearchQuery = intelligentMaterialsSearchEl.value || "";
    renderIntelligentMaterialsLibrary();
  });
}

loadMaterialsLibrary();
loadExamplesFromContenido();

function usdToCopWithMargin(usd) {
  return usd
    * Number(pricingConfig.pricing_margin_multiplier || DEFAULT_PRICING.pricing_margin_multiplier)
    * getWompiCoverageFactor()
    * Number(pricingConfig.usd_to_cop || DEFAULT_PRICING.usd_to_cop);
}

function normalizeCop(value) {
  const amount = Number(value);
  if (!Number.isFinite(amount)) return null;
  return Math.max(0, Math.round(amount));
}

function getModuleCopPrice(moduleKey, usdFallback) {
  const direct = normalizeCop(pricingConfig.module_price_cop?.[moduleKey]);
  if (direct !== null) return direct;
  return toPsychologicalCop(usdToCopWithMargin(usdFallback));
}

function getMusicCopPrice(seconds, usdFallback) {
  const key = String(seconds);
  const direct = normalizeCop(pricingConfig.music_duration_cop?.[key]);
  if (direct !== null) return direct;
  return toPsychologicalCop(usdToCopWithMargin(usdFallback));
}

function getVideoCopPrice(engineId, seconds, usdFallback) {
  const key = String(seconds);
  const direct = normalizeCop(pricingConfig.video_price_cop?.[engineId]?.[key]);
  if (direct !== null) return direct;
  return toPsychologicalCop(usdToCopWithMargin(usdFallback));
}

function toPsychologicalCop(rawCop) {
  if (!Number.isFinite(rawCop) || rawCop <= 0) return 0;

  if (rawCop < 1000) {
    return Math.ceil(rawCop / 10) * 10;
  }

  if (rawCop < 10000) {
    const step = 100;
    const ceiling = Math.ceil(rawCop / step) * step;
    const candidate = ceiling - 10;
    return candidate >= rawCop ? candidate : ceiling + 90;
  }

  const step = 1000;
  const ceiling = Math.ceil(rawCop / step) * step;
  const candidate = ceiling - 100;
  return candidate >= rawCop ? candidate : ceiling + 900;
}

function formatCop(cop) {
  return new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 0,
  }).format(cop);
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

function setAuthStatus(text, state = "idle") {
  if (!authStatus) return;
  authStatus.textContent = text;
  authStatus.className = `status ${state}`;
}

function updateAuthTabUi() {
  if (!authTabLogin || !authTabRegister || !authSubmit || !authPassword) return;
  const isLogin = authMode === "login";
  const isRegister = authMode === "register";
  const isRecover = authMode === "recover";
  const isReset = authMode === "reset";
  authTabLogin.classList.toggle("auth-tab--active", isLogin);
  authTabRegister.classList.toggle("auth-tab--active", isRegister);
  authTabLogin.setAttribute("aria-selected", String(isLogin));
  authTabRegister.setAttribute("aria-selected", String(isRegister));
  authSubmit.textContent = isRegister ? "Crear cuenta" : isRecover ? "Enviar correo" : isReset ? "Restablecer contraseña" : "Ingresar";
  authPassword.setAttribute("autocomplete", isLogin ? "current-password" : "new-password");
  if (authRegisterFields) authRegisterFields.hidden = !isRegister;
  if (authPasswordConfirmWrap) authPasswordConfirmWrap.hidden = !isRegister;
  if (authRecoverWrap) authRecoverWrap.hidden = !isRecover;
  if (authResetWrap) authResetWrap.hidden = !isReset;
  if (authLogin?.parentElement) authLogin.parentElement.hidden = isRecover || isReset || isRegister;
  if (authEmail?.parentElement) authEmail.parentElement.hidden = !isRegister;
  if (authPassword?.parentElement) authPassword.parentElement.hidden = isRecover || isReset;
  if (authLogin) authLogin.required = isLogin;
  if (authPassword) authPassword.required = isLogin || isRegister;
  if (authPasswordConfirm) authPasswordConfirm.required = isRegister;
  if (authFirstName) authFirstName.required = isRegister;
  if (authLastName) authLastName.required = isRegister;
  if (authEmail) authEmail.required = isRegister;
  if (authRecoverEmail) authRecoverEmail.required = isRecover;
  if (authResetToken) authResetToken.required = isReset;
  if (authResetPassword) authResetPassword.required = isReset;
  if (authResetPasswordConfirm) authResetPasswordConfirm.required = isReset;
  if (authRecoverToggle) authRecoverToggle.hidden = isRecover || isReset;
}

function updateAuthUi() {
  const setAccountChipText = (text, fullText = "") => {
    if (!accountChip) return;
    const safeText = String(text || "").trim();
    const safeFullText = String(fullText || safeText).trim();
    accountChip.textContent = safeText;
    accountChip.title = safeFullText;
    accountChip.setAttribute("aria-label", safeFullText);
  };

  if (currentUser) {
    if (btnLogin) btnLogin.hidden = true;
    if (btnLogout) btnLogout.hidden = false;
    if (btnAccount) btnAccount.hidden = false;
    if (btnStudioImp) btnStudioImp.hidden = false;
    if (accountChip) {
      accountChip.hidden = false;
      const fullName = `${currentUser.first_name || ""} ${currentUser.last_name || ""}`.trim();
      const displayName = fullName || currentUser.username;
      setAccountChipText(
        `${displayName} · Saldo ${formatCop(currentUser.balance_cop || 0)}`,
        `${displayName} · Saldo ${formatCop(currentUser.balance_cop || 0)}`
      );
    }
    if (btnRecharge) btnRecharge.disabled = false;
    return;
  }

  if (btnLogin) btnLogin.hidden = false;
  if (btnLogout) btnLogout.hidden = true;
  if (btnAccount) btnAccount.hidden = true;
  if (btnStudioImp) btnStudioImp.hidden = true;
  if (accountChip) {
    accountChip.hidden = false;
    setAccountChipText("No has iniciado sesion");
  }
}

function openAuthModal(mode = "login") {
  if (!authModal) return;
  authMode = ["register", "recover", "reset"].includes(mode) ? mode : "login";
  updateAuthTabUi();
  setAuthStatus(
    authMode === "register"
      ? "Crea tu cuenta con email y contraseña."
      : authMode === "recover"
        ? "Escribe tu email registrado para recibir el enlace de recuperación."
        : authMode === "reset"
          ? "Crea una nueva contraseña con el token recibido por email."
          : "Ingresa con tu email para generar y recargar saldo.",
    "idle"
  );
  authModal.hidden = false;
  authModal.setAttribute("aria-hidden", "false");
  if (authMode === "recover") {
    authRecoverEmail?.focus();
  } else if (authMode === "reset") {
    authResetToken?.focus();
  } else {
    authLogin?.focus();
  }
}

function closeAuthModal() {
  if (!authModal) return;
  authModal.hidden = true;
  authModal.setAttribute("aria-hidden", "true");
}

function closeAccountModal() {
  if (!accountModal) return;
  accountModal.hidden = true;
  accountModal.setAttribute("aria-hidden", "true");
}

function setAccountPasswordStatus(text, state = "idle") {
  if (!accountPasswordStatus) return;
  accountPasswordStatus.textContent = text;
  accountPasswordStatus.className = `status ${state}`;
}

function setAccountProfileStatus(text, state = "idle") {
  if (!accountProfileStatus) return;
  accountProfileStatus.textContent = text;
  accountProfileStatus.className = `status ${state}`;
}

function setAccountDeleteStatus(text, state = "idle") {
  if (!accountDeleteStatus) return;
  accountDeleteStatus.textContent = text;
  accountDeleteStatus.className = `status ${state}`;
}

function formatDate(value) {
  if (!value) return "--";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "--";
  return date.toLocaleString("es-CO");
}

function cropText(value, maxLength = 220) {
  const text = String(value || "").trim();
  if (text.length <= maxLength) return text;
  return `${text.slice(0, maxLength - 1)}…`;
}

function escapeHtml(value) {
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function renderAccountChatHistory(historyItems) {
  if (!accountChatHistoryBody) return;
  const items = Array.isArray(historyItems) ? historyItems : [];
  accountChatHistoryBody.innerHTML = "";

  if (!items.length) {
    const row = document.createElement("tr");
    row.innerHTML = '<td colspan="4">Aun no hay conversaciones de Pachy IA registradas.</td>';
    accountChatHistoryBody.appendChild(row);
    return;
  }

  for (const item of items.slice(0, 120)) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${formatDate(item.created_at)}</td>
      <td>${escapeHtml(cropText(item.user_message, 200) || "-")}</td>
      <td>${escapeHtml(cropText(item.assistant_message, 220) || "-")}</td>
      <td>${escapeHtml(cropText(item.model, 70) || "-")}</td>
    `;
    accountChatHistoryBody.appendChild(row);
  }
}

function renderAccountSummary(data) {
  const user = data?.user || {};
  const generations = Array.isArray(data?.generations) ? data.generations : [];
  const chatHistoryItems = Array.isArray(data?.chat_history) ? data.chat_history : [];
  const balance = Number(data?.balance_cop || user.balance_cop || 0);

  if (accountFirstName) accountFirstName.value = user.first_name || "";
  if (accountLastName) accountLastName.value = user.last_name || "";
  if (accountEmail) accountEmail.value = user.email || "";
  if (accountPhone) accountPhone.value = user.phone || "";
  if (accountUsername) accountUsername.value = user.username || "";

  if (accountBalance) {
    accountBalance.textContent = `Saldo actual: ${formatCop(balance)}`;
  }

  if (accountGenerationsBody) {
    accountGenerationsBody.innerHTML = "";
    if (!generations.length) {
      const row = document.createElement("tr");
      row.innerHTML = `<td colspan="5">Aun no hay generaciones registradas.</td>`;
      accountGenerationsBody.appendChild(row);
    } else {
      for (const item of generations.slice(0, 120)) {
        const row = document.createElement("tr");
        const outputType = String(item.output_type || "");
        const outputId = String(item.id || "");
        const hasFile = Boolean(item.has_file);
        const isCompleted = String(item.status || "").toLowerCase() === "completed";
        const moduleName = String(item.module || "").toLowerCase();
        const meta = item?.meta && typeof item.meta === "object" ? item.meta : {};

        const hasImage = Boolean(meta.has_image ?? hasFile);
        const hasVideo = Boolean(meta.has_video);
        const hasReport = Boolean(meta.has_report);

        let fileCell = `<td class="gen-file-cell gen-file-cell--none">—</td>`;
        if (isCompleted && outputType && outputId) {
          if (moduleName === "intelligent_project") {
            const links = [];
            if (hasImage) {
              links.push(`<a class="gen-download-btn" href="/auth/downloads/${encodeURIComponent(outputType)}/${encodeURIComponent(outputId)}?asset=image" download title="Descargar render">⬇ Render</a>`);
            }
            if (hasVideo) {
              links.push(`<a class="gen-download-btn" href="/auth/downloads/${encodeURIComponent(outputType)}/${encodeURIComponent(outputId)}?asset=video" download title="Descargar video">⬇ Video</a>`);
            }
            if (hasReport) {
              links.push(`<a class="gen-download-btn" href="/auth/downloads/${encodeURIComponent(outputType)}/${encodeURIComponent(outputId)}?asset=report" download title="Descargar PDF">⬇ PDF</a>`);
            }
            if (links.length) {
              fileCell = `<td class="gen-file-cell">${links.join(" ")}</td>`;
            } else {
              fileCell = `<td class="gen-file-cell gen-file-cell--expired" title="Los archivos no estan disponibles en este momento.">⏳ Sin archivos</td>`;
            }
          } else if (hasFile) {
            fileCell = `<td class="gen-file-cell"><a class="gen-download-btn" href="/auth/downloads/${encodeURIComponent(outputType)}/${encodeURIComponent(outputId)}" download title="Descargar archivo">⬇ Descargar</a></td>`;
          } else {
            fileCell = `<td class="gen-file-cell gen-file-cell--expired" title="El archivo fue eliminado cuando Railway reinicio el contenedor. Configurar un Railway Volume evita esto.">⏳ Expirado</td>`;
          }
        }

        row.innerHTML = `
          <td>${formatDate(item.updated_at || item.created_at)}</td>
          <td>${item.module || "-"}</td>
          <td>${item.status || "-"}</td>
          <td>${formatCop(Number(item.amount_cop || 0))}</td>
          ${fileCell}
        `;
        accountGenerationsBody.appendChild(row);
      }
    }
  }

  renderAccountChatHistory(chatHistoryItems);
}

async function openAccountModal() {
  if (!accountModal) return;
  if (!currentUser) {
    openAuthModal("login");
    return;
  }

  try {
    const resp = await fetch("/auth/account");
    if (!resp.ok) {
      const err = await readApiError(resp);
      window.alert(`No se pudo cargar tu cuenta: ${err}`);
      return;
    }
    const data = await resp.json();
    currentUser = data?.user || currentUser;
    updateAuthUi();
    renderAccountSummary(data);
  } catch {
    window.alert("No se pudo cargar la informacion de tu cuenta.");
    return;
  }

  setAccountProfileStatus("Puedes actualizar tu perfil cuando quieras.", "idle");
  setAccountPasswordStatus("Puedes actualizar tu contraseña cuando quieras.", "idle");
  setAccountDeleteStatus("Esta accion es permanente y no se puede deshacer.", "idle");
  accountModal.hidden = false;
  accountModal.setAttribute("aria-hidden", "false");
}

function showConfirmDialog({ title, body, okLabel = "Confirmar", icon = "⚠️", inputRequired = false, inputMatch = "" }) {
  return new Promise((resolve) => {
    const dialog = document.getElementById("confirm-dialog");
    const titleEl = document.getElementById("confirm-dialog-title");
    const bodyEl = document.getElementById("confirm-dialog-body");
    const iconEl = document.getElementById("confirm-dialog-icon");
    const inputWrap = document.getElementById("confirm-dialog-input-wrap");
    const inputLabelEl = document.getElementById("confirm-dialog-input-label");
    const inputEl = document.getElementById("confirm-dialog-input");
    const cancelBtn = document.getElementById("confirm-dialog-cancel");
    const okBtn = document.getElementById("confirm-dialog-ok");

    if (!dialog || !titleEl || !bodyEl || !okBtn || !cancelBtn) {
      resolve(window.confirm(`${title}\n\n${body.replace(/<[^>]*>/g, "")}`));
      return;
    }

    titleEl.textContent = title;
    bodyEl.innerHTML = body;
    iconEl.textContent = icon;
    okBtn.textContent = okLabel;

    if (inputRequired && inputWrap && inputLabelEl && inputEl) {
      inputWrap.hidden = false;
      inputLabelEl.innerHTML = `Escribe <strong>${inputMatch}</strong> para confirmar:`;
      inputEl.value = "";
      inputEl.placeholder = inputMatch;
      okBtn.disabled = true;
    } else {
      if (inputWrap) inputWrap.hidden = true;
      okBtn.disabled = false;
    }

    dialog.hidden = false;
    dialog.setAttribute("aria-hidden", "false");

    function validate() {
      if (!inputRequired || !inputEl) return true;
      return inputEl.value.trim().toUpperCase() === String(inputMatch).toUpperCase();
    }

    function onInput() {
      okBtn.disabled = !validate();
    }

    function cleanup(result) {
      dialog.hidden = true;
      dialog.setAttribute("aria-hidden", "true");
      if (inputEl) inputEl.removeEventListener("input", onInput);
      cancelBtn.removeEventListener("click", onCancel);
      okBtn.removeEventListener("click", onOk);
      resolve(result);
    }

    function onCancel() { cleanup(false); }
    function onOk() { if (!validate()) return; cleanup(true); }

    if (inputRequired && inputEl) {
      inputEl.addEventListener("input", onInput);
      requestAnimationFrame(() => inputEl.focus());
    } else {
      requestAnimationFrame(() => okBtn.focus());
    }

    cancelBtn.addEventListener("click", onCancel);
    okBtn.addEventListener("click", onOk);
  });
}

async function deleteCurrentAccount() {
  if (!currentUser) {
    openAuthModal("login");
    return;
  }

  const balance = formatCop(Number(currentUser.balance_cop || 0));

  const firstOk = await showConfirmDialog({
    icon: "⚠️",
    title: "¿Eliminar tu cuenta?",
    body: `Esta acción es <strong>permanente e irreversible</strong>.<br><br>Perderás tu saldo de <strong>${balance}</strong> y todo tu historial de generaciones.`,
    okLabel: "Continuar",
  });
  if (!firstOk) return;

  const secondOk = await showConfirmDialog({
    icon: "🗑️",
    title: "Confirmación final",
    body: `Una vez eliminada, <strong>no podrás recuperar tu cuenta</strong> ni tu saldo.<br><br>Escribe <strong>ELIMINAR</strong> para confirmar:`,
    okLabel: "Eliminar cuenta",
    inputRequired: true,
    inputMatch: "ELIMINAR",
  });
  if (!secondOk) return;

  if (accountDeleteBtn) accountDeleteBtn.disabled = true;
  if (accountDeleteTopBtn) accountDeleteTopBtn.disabled = true;
  setAccountDeleteStatus("Eliminando tu cuenta...", "idle");

  try {
    const resp = await fetch("/auth/delete-account", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ confirm: true }),
    });

    if (!resp.ok) {
      const err = await readApiError(resp);
      throw new Error(err || "No se pudo eliminar la cuenta");
    }

    closeAccountModal();
    currentUser = null;
    updateAuthUi();
    stopWompiSyncLoop();
    setStatus("Cuenta eliminada correctamente.", "done");

    await showConfirmDialog({
      icon: "✅",
      title: "Cuenta eliminada",
      body: "Tu cuenta, saldo e historial de generaciones han sido eliminados correctamente.",
      okLabel: "Entendido",
    });

    openAuthModal("login");
  } catch (error) {
    const message = error instanceof Error ? error.message : "No se pudo eliminar la cuenta";
    setAccountDeleteStatus(message, "failed");
  } finally {
    if (accountDeleteBtn) accountDeleteBtn.disabled = false;
    if (accountDeleteTopBtn) accountDeleteTopBtn.disabled = false;
  }
}

function requireLogin(actionText) {
  if (currentUser) return true;
  setStatus(`Debes iniciar sesion para ${actionText}.`, "failed");
  openAuthModal("login");
  return false;
}

async function refreshCurrentUser() {
  try {
    const resp = await fetch("/auth/me");
    if (!resp.ok) {
      currentUser = null;
      chatHistoryPanelLoaded = false;
      renderChatHistoryPanel([]);
      updateAuthUi();
      stopWompiSyncLoop();
      return;
    }
    const data = await resp.json();
    currentUser = data?.user || null;
    updateAuthUi();
    if (currentUser) {
      startWompiSyncLoop();
    } else {
      chatHistoryPanelLoaded = false;
      renderChatHistoryPanel([]);
      stopWompiSyncLoop();
    }
  } catch {
    currentUser = null;
    chatHistoryPanelLoaded = false;
    renderChatHistoryPanel([]);
    updateAuthUi();
    stopWompiSyncLoop();
  }
}

function waitMs(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function confirmWompiReference(reference, transactionId = "") {
  const resp = await fetch("/payments/wompi/confirm", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reference, transaction_id: transactionId }),
  });

  if (!resp.ok) {
    const err = await readApiError(resp);
    throw new Error(err || "No se pudo confirmar el pago");
  }

  return resp.json();
}

async function waitForWompiApproval(reference, transactionId = "", maxWaitMs = WOMPI_APPROVAL_WAIT_MS, intervalMs = WOMPI_APPROVAL_POLL_MS) {
  const startedAt = Date.now();
  let lastStatus = "PENDING";

  while (Date.now() - startedAt <= maxWaitMs) {
    try {
      const data = await confirmWompiReference(reference, transactionId);
      const status = String(data?.status || "PENDING").toUpperCase();
      lastStatus = status;

      if (data?.credited) {
        return {
          credited: true,
          status,
          balance_cop: Number(data?.balance_cop || 0),
          already_applied: Boolean(data?.already_applied),
          waitedMs: Date.now() - startedAt,
        };
      }

      if (["DECLINED", "VOIDED", "ERROR", "FAILED"].includes(status)) {
        return {
          credited: false,
          status,
          waitedMs: Date.now() - startedAt,
        };
      }
    } catch {
      // Ignora errores transitorios para no cortar el polling.
    }

    await waitMs(intervalMs);
  }

  return {
    credited: false,
    status: lastStatus,
    timedOut: true,
    waitedMs: Date.now() - startedAt,
  };
}

async function watchWompiReference(reference, options = {}) {
  if (!reference || !currentUser) return;
  if (wompiWatchingRefs.has(reference)) return;

  const {
    transactionId = "",
    maxWaitMs = WOMPI_APPROVAL_WAIT_MS,
    intervalMs = WOMPI_APPROVAL_POLL_MS,
    showPendingTimeoutAlert = false,
    popupRef = null,
  } = options;

  wompiWatchingRefs.add(reference);
  let credited = false;

  try {
    const result = await waitForWompiApproval(reference, transactionId, maxWaitMs, intervalMs);
    credited = Boolean(result?.credited);

    if (credited && currentUser) {
      currentUser.balance_cop = Number(result.balance_cop || currentUser.balance_cop || 0);
      updateAuthUi();
      showPaymentNotice("Pago aprobado por Wompi. Tu saldo fue acreditado.", "success");
      return;
    }

    if (showPendingTimeoutAlert) {
      const safeStatus = String(result?.status || "PENDING");
      showPaymentNotice(`Tu pago sigue en ${safeStatus}. Se acreditara apenas Wompi lo marque aprobado.`, "warning", { durationMs: 7000 });
    }
  } finally {
    wompiWatchingRefs.delete(reference);
    if (popupRef && !popupRef.closed) {
      try {
        popupRef.close();
      } catch {
        // Ignorar si el navegador bloquea el cierre.
      }
    }
  }
}

function watchWompiPopupForReturn(popup, checkoutReference) {
  if (!popup || !checkoutReference) return;

  const startedAt = Date.now();
  const maxMs = 5 * 60 * 1000;
  const timer = setInterval(() => {
    if (Date.now() - startedAt > maxMs) {
      clearInterval(timer);
      return;
    }

    if (popup.closed) {
      clearInterval(timer);
      watchWompiReference(checkoutReference, {
        maxWaitMs: WOMPI_APPROVAL_WAIT_MS,
        intervalMs: WOMPI_APPROVAL_POLL_MS,
        showPendingTimeoutAlert: false,
      }).catch(() => {});
      return;
    }

    try {
      const href = String(popup.location.href || "");
      if (!href.startsWith(window.location.origin)) {
        return;
      }

      const redirected = new URL(href);
      const transactionId = redirected.searchParams.get("id") || redirected.searchParams.get("transaction_id") || "";
      const wompiRef = redirected.searchParams.get("wompi_ref") || redirected.searchParams.get("reference") || checkoutReference;

      clearInterval(timer);
      watchWompiReference(wompiRef, {
        transactionId,
        maxWaitMs: WOMPI_APPROVAL_WAIT_MS,
        intervalMs: WOMPI_APPROVAL_POLL_MS,
        showPendingTimeoutAlert: true,
        popupRef: popup,
      }).catch(() => {});
    } catch {
      // Mientras siga en dominio de Wompi, el navegador bloquea acceso al popup.
    }
  }, 1200);
}

async function handleWompiReturnFromCheckout() {
  const params = new URLSearchParams(window.location.search);
  const reference = params.get("wompi_ref") || params.get("reference") || "";
  const transactionId = params.get("id") || params.get("transaction_id") || "";

  if (!reference) return;
  if (!currentUser) return;

  try {
    await watchWompiReference(reference, {
      transactionId,
      maxWaitMs: WOMPI_APPROVAL_WAIT_MS,
      intervalMs: WOMPI_APPROVAL_POLL_MS,
      showPendingTimeoutAlert: true,
    });
  } catch {
    showPaymentNotice("No se pudo confirmar el estado de tu pago en Wompi.", "error", { durationMs: 7600 });
  } finally {
    const url = new URL(window.location.href);
    url.searchParams.delete("wompi_ref");
    url.searchParams.delete("reference");
    url.searchParams.delete("id");
    url.searchParams.delete("transaction_id");
    window.history.replaceState({}, "", url.toString());
  }
}

async function syncPendingWompiPayments(showToast = true) {
  if (!currentUser) return;

  try {
    const resp = await fetch("/payments/wompi/sync", { method: "POST" });
    if (!resp.ok) {
      return;
    }
    const data = await resp.json();
    const creditedCount = Number(data?.credited_count || 0);
    if (creditedCount > 0) {
      currentUser.balance_cop = Number(data?.balance_cop || currentUser.balance_cop || 0);
      updateAuthUi();
      if (showToast) {
        showPaymentNotice(`Se acreditaron ${creditedCount} recarga(s) pendiente(s) de Wompi a tu cuenta.`, "success");
      }
    }
  } catch {
    // No bloquea la carga del Studio si la sincronizacion falla.
  }
}

function stopWompiSyncLoop() {
  if (!wompiSyncTimer) return;
  clearInterval(wompiSyncTimer);
  wompiSyncTimer = null;
}

function startWompiSyncLoop() {
  if (!currentUser || wompiSyncTimer) return;

  wompiSyncTimer = setInterval(() => {
    syncPendingWompiPayments(false).catch(() => {});
  }, 15000);
}

function calculateRechargeCosts(amountCop) {
  const safeAmount = Math.max(5000, Math.round(Number(amountCop) || 0));
  return { safeAmount };
}

function getCapacityScenarios() {
  return [
    { engineId: "wan-video/wan-2.2-i2v-fast", seconds: 5, label: "Wan 2.2 I2V Fast · Más económico · 5 segundos" },
    { engineId: "kwaivgi/kling-v3-video", seconds: 5, label: "Kling V3 Cinematic · Premium · 5 segundos" },
    { engineId: "kwaivgi/kling-v3-video", seconds: 8, label: "Kling V3 Cinematic · Premium · 8 segundos" },
    { engineId: "kwaivgi/kling-v3-video", seconds: 15, label: "Kling V3 Cinematic · Premium · 15 segundos" },
  ].map((item) => {
    const perSecond = Number(
      pricingConfig?.video_engine_usd_per_second?.[item.engineId]
      ?? DEFAULT_PRICING.video_engine_usd_per_second[item.engineId]
      ?? 0
    );
    const usdBase = perSecond * item.seconds;
    const unitPrice = getVideoCopPrice(item.engineId, item.seconds, usdBase);
    return { ...item, unitPrice };
  });
}

function buildCapacityTextForAmount(amountCop) {
  const scenarios = getCapacityScenarios();
  const lines = scenarios.map((scenario) => {
    const unitPrice = Number(scenario.unitPrice || 0);
    const count = unitPrice > 0 ? Math.floor(amountCop / unitPrice) : 0;
    return `${scenario.label}: ${count} gen aprox. (${formatCop(unitPrice)} c/u)`;
  });
  return lines;
}

function renderPlanBanners() {
  if (!pricesPlanBanners) return;
  pricesPlanBanners.innerHTML = "";

  for (const amount of getRechargePlans()) {
    const card = document.createElement("article");
    card.className = "plan-banner";

    const lines = buildCapacityTextForAmount(amount);
    const list = lines.map((line) => `<li>${line}</li>`).join("");

    card.innerHTML = `
      <h5>Recarga ${formatCop(amount)}</h5>
      <ul>${list}</ul>
    `;
    pricesPlanBanners.appendChild(card);
  }
}

function renderRechargeSummary() {
  if (!rechargeAmount) return;
  const { safeAmount } = calculateRechargeCosts(rechargeAmount.value);
  if (rechargePayValue) rechargePayValue.textContent = formatCop(safeAmount);
  if (rechargeCreditValue) rechargeCreditValue.textContent = formatCop(safeAmount);

  if (rechargePlanCapacity) {
    const lines = buildCapacityTextForAmount(safeAmount);
    rechargePlanCapacity.innerHTML = lines.map((line) => `• ${line}`).join("<br />");
  }
}

function openRechargeModal() {
  if (!rechargeModal) return;
  renderRechargeSummary();
  rechargeModal.hidden = false;
  rechargeModal.setAttribute("aria-hidden", "false");
}

function closeRechargeModal() {
  if (!rechargeModal) return;
  rechargeModal.hidden = true;
  rechargeModal.setAttribute("aria-hidden", "true");
}

function renderPricesModal() {
  if (!pricesTableBody || !pricesVideoBody) return;

  pricesTableBody.innerHTML = "";
  for (const item of getPricingCatalog()) {
    const row = document.createElement("tr");
    let priceCell = item.label || "-";
    if (Number.isFinite(item.usdBase)) {
      priceCell = formatCop(getModuleCopPrice(item.key, item.usdBase));
    } else if (Number.isFinite(item.inputUsdPerMillion) && Number.isFinite(item.outputUsdPerMillion)) {
      const inputCop = formatCop(toPsychologicalCop(usdToCopWithMargin(item.inputUsdPerMillion)));
      const outputCop = formatCop(toPsychologicalCop(usdToCopWithMargin(item.outputUsdPerMillion)));
      priceCell = `Entrada: ${inputCop} / 1M tokens · Salida: ${outputCop} / 1M tokens`;
    }
    row.innerHTML = `
      <td>${item.module}</td>
      <td>${priceCell}</td>
    `;
    pricesTableBody.appendChild(row);
  }

  pricesVideoBody.innerHTML = "";
  for (const engine of getImageToVideoEngines()) {
    const durations = engine.id === "wan-video/wan-2.2-i2v-fast" ? [5] : imageToVideoDurations;
    for (const seconds of durations) {
      const usdBase = engine.usdPerSecond * seconds;
      const row = document.createElement("tr");
      const badge = `<span class="price-badge price-badge--${engine.badgeClass}">${engine.badge}</span>`;
      const videoCop = getVideoCopPrice(engine.id, seconds, usdBase);
      row.innerHTML = `
        <td>${engine.engine}<br />${badge}</td>
        <td>${seconds} segundos</td>
        <td>${formatCop(videoCop)}</td>
      `;
      pricesVideoBody.appendChild(row);
    }
  }

  if (pricesMusicBody) {
    pricesMusicBody.innerHTML = "";
    for (const item of getMusicDurationPricing()) {
      const row = document.createElement("tr");
      const musicCop = getMusicCopPrice(item.seconds, item.usdBase);
      const badge = item.featured
        ? ' <span class="price-badge price-badge--premium">Actual</span>'
        : "";
      row.innerHTML = `
        <td>${item.label} · ${item.seconds} segundos${badge}</td>
        <td>${formatCop(musicCop)}</td>
      `;
      pricesMusicBody.appendChild(row);
    }
  }

  if (pricesNote) {
    pricesNote.textContent = "Valores por generación en COP. Música IA comercial usa actualmente el tramo automático extendido de 180 segundos.";
  }
}

function openPricesModal() {
  if (!pricesModal) return;
  renderPricesModal();
  pricesModal.hidden = false;
  pricesModal.setAttribute("aria-hidden", "false");
}

function closePricesModal() {
  if (!pricesModal) return;
  pricesModal.hidden = true;
  pricesModal.setAttribute("aria-hidden", "true");
}

btnPrices?.addEventListener("click", openPricesModal);
pricesClose?.addEventListener("click", closePricesModal);
pricesModal?.addEventListener("click", (e) => {
  const target = e.target;
  if (target instanceof HTMLElement && target.dataset.closePrices === "true") {
    closePricesModal();
  }
});

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    closeChatHistoryModal();
    closePricesModal();
    closeRechargeModal();
    closeAuthModal();
    closeAccountModal();
  }
});

btnRecharge?.addEventListener("click", () => {
  if (!currentUser) {
    openAuthModal("login");
    return;
  }
  openRechargeModal();
});

btnLogin?.addEventListener("click", () => {
  openAuthModal("login");
});

authRecoverToggle?.addEventListener("click", () => {
  openAuthModal("recover");
});

btnAccount?.addEventListener("click", () => {
  openAccountModal();
});

btnStudioImp?.addEventListener("click", () => {
  if (!currentUser) {
    openAuthModal("login");
    return;
  }
  window.open("/studio-imp", "_blank", "noopener,noreferrer");
});

btnLogout?.addEventListener("click", async () => {
  try {
    const resp = await fetch("/auth/logout", { method: "POST" });
    if (!resp.ok) {
      const err = await readApiError(resp);
      window.alert(`No se pudo cerrar sesion: ${err}`);
      return;
    }
  } catch {
    window.alert("No se pudo cerrar sesion en este momento.");
    return;
  }

  currentUser = null;
  updateAuthUi();
  closeRechargeModal();
  setStatus("Sesion cerrada", "idle");
});

authTabLogin?.addEventListener("click", () => {
  authMode = "login";
  updateAuthTabUi();
});

authTabRegister?.addEventListener("click", () => {
  authMode = "register";
  updateAuthTabUi();
});

authClose?.addEventListener("click", closeAuthModal);
authModal?.addEventListener("click", (e) => {
  const target = e.target;
  if (target instanceof HTMLElement && target.dataset.closeAuth === "true") {
    closeAuthModal();
  }
});

authForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!authPassword || !authSubmit) return;

  if (authMode === "recover") {
    const email = (authRecoverEmail?.value || "").trim();
    if (!email) {
      setAuthStatus("Escribe tu email registrado.", "failed");
      return;
    }

    authSubmit.disabled = true;
    setAuthStatus("Enviando correo de recuperación...", "processing");

    try {
      const resp = await fetch("/auth/recover-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      if (!resp.ok) {
        const err = await readApiError(resp);
        setAuthStatus(err, "failed");
        authSubmit.disabled = false;
        return;
      }

      const data = await resp.json();
      setAuthStatus(data?.message || "Revisa tu email para continuar.", "completed");
      if (data?.delivery?.mode === "outbox" && data?.delivery?.file) {
        window.alert(`Correo generado localmente en: ${data.delivery.file}`);
      }
    } catch {
      setAuthStatus("No se pudo enviar el correo de recuperación.", "failed");
    } finally {
      authSubmit.disabled = false;
    }
    return;
  }

  if (authMode === "reset") {
    const token = (authResetToken?.value || "").trim();
    const newPassword = authResetPassword?.value || "";
    const confirmPassword = authResetPasswordConfirm?.value || "";

    if (!token || !newPassword || !confirmPassword) {
      setAuthStatus("Completa el token y la nueva contraseña.", "failed");
      return;
    }
    if (newPassword !== confirmPassword) {
      setAuthStatus("La confirmación de contraseña no coincide.", "failed");
      return;
    }

    authSubmit.disabled = true;
    setAuthStatus("Restableciendo contraseña...", "processing");

    try {
      const resp = await fetch("/auth/reset-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, new_password: newPassword, confirm_new_password: confirmPassword }),
      });

      if (!resp.ok) {
        const err = await readApiError(resp);
        setAuthStatus(err, "failed");
        authSubmit.disabled = false;
        return;
      }

      const data = await resp.json();
      setAuthStatus(`Contraseña actualizada para ${data.email || "tu cuenta"}.`, "completed");
      const url = new URL(window.location.href);
      url.searchParams.delete("reset_token");
      window.history.replaceState({}, "", url.toString());
      openAuthModal("login");
    } catch {
      setAuthStatus("No se pudo restablecer la contraseña.", "failed");
    } finally {
      authSubmit.disabled = false;
    }
    return;
  }

  const login = authLogin?.value.trim() || "";
  const password = authPassword.value;

  const isRegister = authMode === "register";
  const firstName = authFirstName?.value.trim() || "";
  const lastName = authLastName?.value.trim() || "";
  const passwordConfirm = authPasswordConfirm?.value || "";
  const registerEmail = authEmail?.value.trim() || login;

  if (!password) {
    setAuthStatus("Completa email y contraseña.", "failed");
    return;
  }

  if (!isRegister && !login) {
    setAuthStatus("Completa email y contraseña.", "failed");
    return;
  }

  if (isRegister) {
    if (!firstName || !lastName) {
      setAuthStatus("Completa nombres y apellidos para registrarte.", "failed");
      return;
    }
    if (!registerEmail) {
      setAuthStatus("Completa el email para registrarte.", "failed");
      return;
    }
    if (password !== passwordConfirm) {
      setAuthStatus("La confirmacion de contraseña no coincide.", "failed");
      return;
    }
  }

  authSubmit.disabled = true;
  setAuthStatus(authMode === "login" ? "Validando acceso..." : "Creando cuenta...", "processing");

  try {
    const endpoint = authMode === "login" ? "/auth/login" : "/auth/register";
    const payload = authMode === "login"
      ? { login, password }
      : {
          first_name: firstName,
          last_name: lastName,
          email: registerEmail,
          password,
          password_confirm: passwordConfirm,
        };
    const resp = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!resp.ok) {
      const err = await readApiError(resp);
      setAuthStatus(err, "failed");
      authSubmit.disabled = false;
      return;
    }

    const data = await resp.json();
    currentUser = data?.user || null;
    updateAuthUi();
    setAuthStatus("Sesion iniciada correctamente.", "completed");
    closeAuthModal();
    await refreshCurrentUser();
  } catch {
    setAuthStatus("No se pudo completar la autenticacion.", "failed");
  } finally {
    authSubmit.disabled = false;
  }
});

rechargeClose?.addEventListener("click", closeRechargeModal);
rechargeModal?.addEventListener("click", (e) => {
  const target = e.target;
  if (target instanceof HTMLElement && target.dataset.closeRecharge === "true") {
    closeRechargeModal();
  }
});

rechargeAmount?.addEventListener("change", renderRechargeSummary);

rechargeForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!rechargeAmount || !rechargeSubmit) return;
  if (!currentUser) {
    closeRechargeModal();
    openAuthModal("login");
    return;
  }

  const amount = Math.max(5000, Math.round(Number(rechargeAmount.value) || 0));
  rechargeSubmit.disabled = true;

  try {
    showPaymentNotice("Conectando con checkout seguro de Wompi...", "info", { durationMs: 4200 });
    const redirectUrl = `${window.location.origin}/studio`;
    const resp = await fetch("/payments/wompi/checkout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ amount_cop: amount, redirect_url: redirectUrl }),
    });

    if (!resp.ok) {
      const errorText = await readApiError(resp);
      showPaymentNotice(`No se pudo recargar: ${errorText}`, "error", { durationMs: 7600 });
      rechargeSubmit.disabled = false;
      return;
    }

    const data = await resp.json();
    if (!data.checkout_url) {
      showPaymentNotice("No se pudo obtener el checkout de Wompi.", "error", { durationMs: 7600 });
      rechargeSubmit.disabled = false;
      return;
    }

    const checkoutReference = String(data.reference || "").trim();

    const popup = window.open(
      data.checkout_url,
      "wompiCheckout",
      "popup=yes,width=520,height=760,menubar=no,toolbar=no,location=yes,status=no,resizable=yes,scrollbars=yes"
    );
    if (!popup) {
      showPaymentNotice("Abriendo pasarela de pago en la misma pestaña...", "info", { durationMs: 3600 });
      window.location.href = data.checkout_url;
      return;
    }
    popup.focus();
    watchWompiPopupForReturn(popup, checkoutReference);

    // Mientras el popup esta abierto, consultamos aprobacion para acreditar apenas Wompi confirme.
    watchWompiReference(checkoutReference, {
      maxWaitMs: WOMPI_APPROVAL_WAIT_MS,
      intervalMs: WOMPI_APPROVAL_POLL_MS,
      showPendingTimeoutAlert: false,
      popupRef: null,
    }).catch(() => {});
  } catch {
    showPaymentNotice("No se pudo recargar en este momento.", "error", { durationMs: 7600 });
    rechargeSubmit.disabled = false;
    return;
  }

  rechargeSubmit.disabled = false;
});

accountClose?.addEventListener("click", closeAccountModal);
accountModal?.addEventListener("click", (e) => {
  const target = e.target;
  if (target instanceof HTMLElement && target.dataset.closeAccount === "true") {
    closeAccountModal();
  }
});

accountDeleteBtn?.addEventListener("click", () => {
  deleteCurrentAccount();
});

accountDeleteTopBtn?.addEventListener("click", () => {
  deleteCurrentAccount();
});

accountProfileForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!accountProfileSubmit || !accountFirstName || !accountLastName || !accountEmail || !accountPhone || !accountUsername) return;

  const firstName = accountFirstName.value.trim();
  const lastName = accountLastName.value.trim();
  const email = accountEmail.value.trim();
  const phone = accountPhone.value.trim();
  const username = accountUsername.value.trim();

  if (!firstName || !lastName || !email || !username) {
    setAccountProfileStatus("Completa Nombres, Apellidos, Email y Usuario.", "failed");
    return;
  }

  accountProfileSubmit.disabled = true;
  setAccountProfileStatus("Actualizando perfil...", "processing");

  try {
    const resp = await fetch("/auth/profile", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        first_name: firstName,
        last_name: lastName,
        email,
        phone,
        username,
      }),
    });

    if (!resp.ok) {
      const err = await readApiError(resp);
      setAccountProfileStatus(err, "failed");
      accountProfileSubmit.disabled = false;
      return;
    }

    const data = await resp.json();
    const updatedUser = data?.user || null;
    if (updatedUser) {
      currentUser = { ...(currentUser || {}), ...updatedUser };
      updateAuthUi();
    }
    await openAccountModal();
    setAccountProfileStatus("Perfil actualizado correctamente.", "completed");
  } catch {
    setAccountProfileStatus("No se pudo actualizar el perfil.", "failed");
  } finally {
    accountProfileSubmit.disabled = false;
  }
});

accountPasswordForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!accountCurrentPassword || !accountNewPassword || !accountConfirmPassword || !accountPasswordSubmit) return;

  const currentPassword = accountCurrentPassword.value;
  const newPassword = accountNewPassword.value;
  const confirmPassword = accountConfirmPassword.value;

  if (!currentPassword || !newPassword || !confirmPassword) {
    setAccountPasswordStatus("Completa todos los campos para cambiar la contraseña.", "failed");
    return;
  }
  if (newPassword !== confirmPassword) {
    setAccountPasswordStatus("La nueva contraseña y su confirmacion no coinciden.", "failed");
    return;
  }

  accountPasswordSubmit.disabled = true;
  setAccountPasswordStatus("Actualizando contraseña...", "processing");

  try {
    const resp = await fetch("/auth/change-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
        confirm_new_password: confirmPassword,
      }),
    });

    if (!resp.ok) {
      const err = await readApiError(resp);
      setAccountPasswordStatus(err, "failed");
      accountPasswordSubmit.disabled = false;
      return;
    }

    accountCurrentPassword.value = "";
    accountNewPassword.value = "";
    accountConfirmPassword.value = "";
    setAccountPasswordStatus("Contraseña actualizada correctamente.", "completed");
  } catch {
    setAccountPasswordStatus("No se pudo actualizar la contraseña.", "failed");
  } finally {
    accountPasswordSubmit.disabled = false;
  }
});

function setMode(mode) {
  currentMode = mode;
  const isChat = mode === "chat";
  const isMusic = mode === "music";
  const isInfluencer = mode === "influencer";
  const isIntelligent = mode === "intelligent_project";

  tabImg2Img?.classList.toggle("active", mode === "img2img");
  tabImg2Vid?.classList.toggle("active", mode === "img2vid");
  tabInfluencer?.classList.toggle("active", isInfluencer);
  tabIntelligent?.classList.toggle("active", isIntelligent);
  tabTxt2Img?.classList.toggle("active", mode === "txt2img");
  tabMusic?.classList.toggle("active", isMusic);
  tabChat?.classList.toggle("active", isChat);

  tabImg2Img?.setAttribute("aria-selected", String(mode === "img2img"));
  tabImg2Vid?.setAttribute("aria-selected", String(mode === "img2vid"));
  tabInfluencer?.setAttribute("aria-selected", String(isInfluencer));
  tabIntelligent?.setAttribute("aria-selected", String(isIntelligent));
  tabTxt2Img?.setAttribute("aria-selected", String(mode === "txt2img"));
  tabMusic?.setAttribute("aria-selected", String(isMusic));
  tabChat?.setAttribute("aria-selected", String(isChat));

  paneImg2Img?.classList.toggle("active", mode === "img2img");
  paneImg2Vid?.classList.toggle("active", mode === "img2vid");
  paneInfluencer?.classList.toggle("active", isInfluencer);
  paneIntelligent?.classList.toggle("active", isIntelligent);
  paneTxt2Img?.classList.toggle("active", mode === "txt2img");
  paneMusic?.classList.toggle("active", isMusic);
  paneChat?.classList.toggle("active", isChat);

  if (paneImg2Img) paneImg2Img.hidden = mode !== "img2img";
  if (paneImg2Vid) paneImg2Vid.hidden = mode !== "img2vid";
  if (paneInfluencer) paneInfluencer.hidden = !isInfluencer;
  if (paneIntelligent) paneIntelligent.hidden = !isIntelligent;
  if (paneTxt2Img) paneTxt2Img.hidden = mode !== "txt2img";
  if (paneMusic) paneMusic.hidden = !isMusic;
  if (paneChat) paneChat.hidden = !isChat;

  if (resultShell) resultShell.hidden = isChat || isMusic || isInfluencer;
  if (musicShell) musicShell.hidden = !isMusic;
  if (chatShell) chatShell.hidden = !isChat;
}

tabImg2Img?.addEventListener("click", () => setMode("img2img"));
tabImg2Vid?.addEventListener("click", () => setMode("img2vid"));
tabInfluencer?.addEventListener("click", () => setMode("influencer"));
tabIntelligent?.addEventListener("click", () => setMode("intelligent_project"));
tabTxt2Img?.addEventListener("click", () => setMode("txt2img"));
tabMusic?.addEventListener("click", () => setMode("music"));
tabChat?.addEventListener("click", () => setMode("chat"));
btnSmartProject?.addEventListener("click", () => setMode("intelligent_project"));

function applyDroppedFile(file) {
  if (!file || !file.type.startsWith("image/") || !dropZoneInput) return;

  const dt = new DataTransfer();
  dt.items.add(file);
  dropZoneInput.files = dt.files;

  if (dropZoneFilename) dropZoneFilename.textContent = file.name || "imagen pegada";
  showImageElement(dropZonePreview, URL.createObjectURL(file));
  dropZone?.classList.add("drop-zone--has-file");
}

function applyAnimDroppedFile(file) {
  if (!file || !file.type.startsWith("image/") || !animDropZoneInput) return;

  const dt = new DataTransfer();
  dt.items.add(file);
  animDropZoneInput.files = dt.files;

  if (animDropZoneFilename) animDropZoneFilename.textContent = file.name || "imagen pegada";
  showImageElement(animDropZonePreview, URL.createObjectURL(file));
  animDropZone?.classList.add("drop-zone--has-file");
}

function applyInfluencerImage(file) {
  if (!file || !file.type.startsWith("image/") || !influencerImageInput) return;

  const dt = new DataTransfer();
  dt.items.add(file);
  influencerImageInput.files = dt.files;

  if (influencerImageFilename) influencerImageFilename.textContent = file.name || "imagen pegada";
  showImageElement(influencerImagePreview, URL.createObjectURL(file));
  influencerImageZone?.classList.add("drop-zone--has-file");
}

function applyInfluencerVideo(file) {
  if (!file || !file.type.startsWith("video/") || !influencerVideoInput) return;

  const dt = new DataTransfer();
  dt.items.add(file);
  influencerVideoInput.files = dt.files;

  if (influencerVideoFilename) influencerVideoFilename.textContent = file.name || "video seleccionado";
  if (influencerVideoPreview) {
    influencerVideoPreview.src = URL.createObjectURL(file);
    influencerVideoPreview.removeAttribute("hidden");
    influencerVideoPreview.load();
  }
  influencerVideoZone?.classList.add("drop-zone--has-file");
}

dropZone?.addEventListener("click", (e) => {
  if (e.target === dropZoneInput) return;
  dropZoneInput?.click();
});

dropZone?.addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    dropZoneInput?.click();
  }
});

dropZoneInput?.addEventListener("change", () => {
  if (dropZoneInput.files && dropZoneInput.files[0]) {
    applyDroppedFile(dropZoneInput.files[0]);
  }
});

dropZone?.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone?.classList.add("drop-zone--drag");
});

dropZone?.addEventListener("dragleave", () => {
  dropZone?.classList.remove("drop-zone--drag");
});

dropZone?.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone?.classList.remove("drop-zone--drag");
  const file = e.dataTransfer.files[0];
  applyDroppedFile(file);
});

animDropZone?.addEventListener("click", (e) => {
  if (e.target === animDropZoneInput) return;
  animDropZoneInput?.click();
});

animDropZone?.addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    animDropZoneInput?.click();
  }
});

animDropZoneInput?.addEventListener("change", () => {
  if (animDropZoneInput.files && animDropZoneInput.files[0]) {
    applyAnimDroppedFile(animDropZoneInput.files[0]);
  }
});

animDropZone?.addEventListener("dragover", (e) => {
  e.preventDefault();
  animDropZone?.classList.add("drop-zone--drag");
});

animDropZone?.addEventListener("dragleave", () => {
  animDropZone?.classList.remove("drop-zone--drag");
});

animDropZone?.addEventListener("drop", (e) => {
  e.preventDefault();
  animDropZone?.classList.remove("drop-zone--drag");
  const file = e.dataTransfer.files[0];
  applyAnimDroppedFile(file);
});

influencerImageZone?.addEventListener("click", (e) => {
  if (e.target === influencerImageInput) return;
  influencerImageInput?.click();
});

influencerImageZone?.addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    influencerImageInput?.click();
  }
});

influencerImageInput?.addEventListener("change", () => {
  if (influencerImageInput.files && influencerImageInput.files[0]) {
    applyInfluencerImage(influencerImageInput.files[0]);
  }
});

influencerImageZone?.addEventListener("dragover", (e) => {
  e.preventDefault();
  influencerImageZone?.classList.add("drop-zone--drag");
});

influencerImageZone?.addEventListener("dragleave", () => {
  influencerImageZone?.classList.remove("drop-zone--drag");
});

influencerImageZone?.addEventListener("drop", (e) => {
  e.preventDefault();
  influencerImageZone?.classList.remove("drop-zone--drag");
  const file = e.dataTransfer.files[0];
  applyInfluencerImage(file);
});

influencerVideoZone?.addEventListener("click", (e) => {
  if (e.target === influencerVideoInput) return;
  influencerVideoInput?.click();
});

influencerVideoZone?.addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    influencerVideoInput?.click();
  }
});

influencerVideoInput?.addEventListener("change", () => {
  if (influencerVideoInput.files && influencerVideoInput.files[0]) {
    applyInfluencerVideo(influencerVideoInput.files[0]);
  }
});

influencerVideoZone?.addEventListener("dragover", (e) => {
  e.preventDefault();
  influencerVideoZone?.classList.add("drop-zone--drag");
});

influencerVideoZone?.addEventListener("dragleave", () => {
  influencerVideoZone?.classList.remove("drop-zone--drag");
});

influencerVideoZone?.addEventListener("drop", (e) => {
  e.preventDefault();
  influencerVideoZone?.classList.remove("drop-zone--drag");
  const file = e.dataTransfer.files[0];
  applyInfluencerVideo(file);
});

document.addEventListener("paste", (e) => {
  const items = e.clipboardData && e.clipboardData.items;
  if (!items) return;
  for (const item of items) {
    if (item.type.startsWith("image/")) {
      e.preventDefault();
      const file = item.getAsFile();
      if (!file) break;

      if (currentMode === "img2vid") {
        applyAnimDroppedFile(file);
      } else if (currentMode === "influencer") {
        applyInfluencerImage(file);
      } else {
        applyDroppedFile(file);
      }
      break;
    }
  }
});

function nextLocalSequence() {
  const key = "iaimp_download_counter";
  const raw = window.localStorage.getItem(key);
  const current = Number(raw || "0");
  const safeCurrent = Number.isFinite(current) && current > 0 ? Math.floor(current) : 0;
  const next = safeCurrent + 1;
  window.localStorage.setItem(key, String(next));
  return next;
}

function formatEta(seconds) {
  if (seconds === null || seconds === undefined || Number.isNaN(seconds)) {
    return "--";
  }
  if (seconds <= 0) {
    return "0s";
  }
  if (seconds < 60) {
    return `${seconds}s`;
  }
  const minutes = Math.floor(seconds / 60);
  const remainder = seconds % 60;
  return `${minutes}m ${remainder}s`;
}

function elapsedSince(startedAt) {
  if (!startedAt) return 0;
  const start = new Date(startedAt).getTime();
  if (Number.isNaN(start)) return 0;
  const diff = Math.floor((Date.now() - start) / 1000);
  return Math.max(0, diff);
}

function setProgress(job) {
  const expected = Number(job.expected_total_seconds || 0);
  const elapsed = elapsedSince(job.started_at) || Number(job.elapsed_seconds || 0);
  const ratioProgress = expected > 0 ? Math.min(95, Math.round((elapsed / expected) * 95)) : 0;

  let progress = Number(job.progress || 0);
  if (job.status === "processing") {
    progress = Math.max(progress, ratioProgress);
  }
  if (job.status === "completed") {
    progress = 100;
  }

  progress = Math.max(0, Math.min(100, progress));
  progressFill.style.width = `${progress}%`;
  progressText.textContent = `${progress}%`;

  stageEl.textContent = `Etapa: ${job.stage || "procesando"}`;

  let eta = job.eta_seconds;
  if (job.status === "processing" && expected > 0) {
    eta = Math.max(0, expected - elapsed);
  }
  if (job.status === "completed") {
    eta = 0;
  }
  etaEl.textContent = `ETA: ${formatEta(eta)}`;
}

function setStatus(text, state) {
  statusEl.textContent = text;
  statusEl.className = `status ${state}`;
}

function hasConflictingNegativePrompt(value) {
  const lowered = value.toLowerCase();
  return lowered.includes("photorealistic") || lowered.includes("photo realistic") || lowered.includes("ultra realistic");
}

function stopPolling() {
  if (pollingTimer) {
    clearInterval(pollingTimer);
    pollingTimer = null;
  }
}

async function pollJob(jobId) {
  stopPolling();

  pollingTimer = setInterval(async () => {
    if (!activeRenderJobId || activeRenderJobId !== jobId) {
      stopPolling();
      return;
    }

    try {
      const response = await fetch(`/jobs/${jobId}`);
      if (!response.ok) {
        setStatus("Error consultando estado", "failed");
        stopPolling();
        return;
      }

      const job = await response.json();
      setProgress(job);

      if (job.status === "completed") {
        stopPolling();
        if (!activeRenderJobId || activeRenderJobId !== jobId) {
          return;
        }
        const imageUrl = `/jobs/${jobId}/image`;
        showImageElement(outputPreview, `${imageUrl}?t=${Date.now()}`);
        downloadLink.href = imageUrl;
        const sequence = Number(job.sequence || 0);
        const finalSequence = sequence > 0 ? sequence : nextLocalSequence();
        downloadLink.setAttribute("download", `IA-IMP-${finalSequence}.png`);
        downloadLink.classList.remove("disabled");

        setStatus("Imagen completada", "completed");

        currentAnimJobId = jobId;
        animStatusEl.textContent = "Imagen lista para convertir a video";
        animStatusEl.className = "status completed";
        animStatusEl.removeAttribute("hidden");
        animProgressWrap.setAttribute("hidden", "");
        animVideo.setAttribute("hidden", "");
        animVideo.src = "";
        animDownload.setAttribute("hidden", "");
        animDownload.classList.add("disabled");
        animBtn.disabled = false;

        submitBtn.disabled = false;
        textSubmitBtn.disabled = false;
      } else if (job.status === "failed") {
        stopPolling();
        if (!activeRenderJobId || activeRenderJobId !== jobId) {
          return;
        }
        setStatus(`Fallo: ${job.error || "error desconocido"}`, "failed");
        submitBtn.disabled = false;
        textSubmitBtn.disabled = false;
      } else {
        setStatus("Generando imagen...", "processing");
      }
    } catch {
      stopPolling();
      setStatus("Error de red al consultar estado", "failed");
      submitBtn.disabled = false;
      textSubmitBtn.disabled = false;
    }
  }, 1800);
}

async function createRender(endpoint, payload, inputPreviewUrl) {
  downloadLink.classList.add("disabled");
  hideImageElement(outputPreview);
  activeRenderJobId = null;

  if (inputPreviewUrl) {
    showImageElement(inputPreview, inputPreviewUrl);
  } else {
    hideImageElement(inputPreview);
  }

  progressFill.style.width = "4%";
  progressText.textContent = "4%";
  stageEl.textContent = "Etapa: subiendo solicitud";
  etaEl.textContent = "ETA: --";
  setStatus("Enviando solicitud...", "processing");

  const response = await fetch(endpoint, { method: "POST", body: payload });
  if (!response.ok) {
    const err = await readApiError(response);
    throw new Error(err || "No se pudo crear el job");
  }

  const data = await response.json();
  activeRenderJobId = data.job_id;
  setStatus("Job en cola...", "processing");
  stageEl.textContent = "Etapa: en cola";
  progressFill.style.width = "8%";
  progressText.textContent = "8%";
  await pollJob(data.job_id);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (!requireLogin("generar renders")) {
    return;
  }

  const promptInput = document.getElementById("prompt");
  if (!dropZoneInput.files || dropZoneInput.files.length === 0) {
    setStatus("Selecciona o pega una imagen (Ctrl+V)", "failed");
    dropZone.focus();
    return;
  }

  if (!promptInput.value.trim()) {
    setStatus("Escribe un prompt", "failed");
    return;
  }

  submitBtn.disabled = true;

  const formData = new FormData();
  formData.append("file", dropZoneInput.files[0]);
  formData.append("prompt", promptInput.value);
  formData.append("negative_prompt", document.getElementById("negative_prompt").value);
  formData.append("style", document.getElementById("style").value);
  formData.append("lighting_mode", document.getElementById("lighting-mode").value);
  formData.append("quality", document.getElementById("quality").value);
  formData.append("steps", document.getElementById("steps").value);
  formData.append("guidance_scale", document.getElementById("guidance_scale").value);

  const seedValue = document.getElementById("seed").value;
  if (seedValue !== "") {
    formData.append("seed", seedValue);
  }

  if (hasConflictingNegativePrompt(document.getElementById("negative_prompt").value)) {
    setStatus("Aviso: negative prompt conflictivo detectado", "processing");
  }

  try {
    const hasMaterials = selectedMaterialNames.length > 0;

    if (hasMaterials) {
      if (selectedMaterialNames.length < 1 || selectedMaterialNames.length > 2) {
        setStatus("Selecciona entre 1 y 2 materiales", "failed");
        submitBtn.disabled = false;
        return;
      }

      const mode = materialModeEl ? materialModeEl.value : "mix";
      const plan = materialPlanEl ? materialPlanEl.value.trim() : "";
      if (mode === "zones" && !plan) {
        setStatus("Describe las zonas para colocar cada material", "failed");
        submitBtn.disabled = false;
        return;
      }

      formData.append("material_mode", mode);
      formData.append("material_plan", plan);
      for (const materialName of selectedMaterialNames) {
        formData.append("material_names", materialName);
      }

      await createRender("/jobs/render-materials", formData, URL.createObjectURL(dropZoneInput.files[0]));
    } else {
      await createRender("/jobs/render", formData, URL.createObjectURL(dropZoneInput.files[0]));
    }

    dropZone.classList.remove("drop-zone--has-file");
    hideImageElement(dropZonePreview);
    dropZoneFilename.textContent = "";
  } catch (err) {
    setStatus(`Error: ${err}`, "failed");
    submitBtn.disabled = false;
  }
});

textForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (!requireLogin("generar imagenes desde texto")) {
    return;
  }

  const prompt = document.getElementById("t2i-prompt").value.trim();
  if (!prompt) {
    setStatus("Escribe un prompt para texto a imagen", "failed");
    return;
  }

  textSubmitBtn.disabled = true;

  const formData = new FormData();
  formData.append("prompt", prompt);
  formData.append("style", document.getElementById("t2i-style").value);
  formData.append("lighting_mode", document.getElementById("t2i-lighting-mode").value);
  formData.append("quality", document.getElementById("t2i-quality").value);
  formData.append("steps", String(Math.max(1, Math.min(4, Number(document.getElementById("t2i-steps").value || "4")))));

  const seedValue = document.getElementById("t2i-seed").value;
  if (seedValue !== "") {
    formData.append("seed", seedValue);
  }

  try {
    await createRender("/jobs/render-text", formData, "");
  } catch (err) {
    setStatus(`Error: ${err}`, "failed");
    textSubmitBtn.disabled = false;
  }
});

function stopAnimPolling() {
  if (animPollingTimer) {
    clearInterval(animPollingTimer);
    animPollingTimer = null;
  }
}

async function pollAnimation(animId) {
  stopAnimPolling();

  animPollingTimer = setInterval(async () => {
    try {
      const resp = await fetch(`/animate/${animId}`);
      if (!resp.ok) {
        animStatusEl.textContent = "Error consultando estado del video";
        animStatusEl.className = "status failed";
        stopAnimPolling();
        animBtn.disabled = false;
        return;
      }

      const anim = await resp.json();
      const backendProgress = Number(anim.progress || 0);
      const rawStage = String(anim.stage || "procesando");
      const normalizedAnimStage = rawStage.replace(/\s+en\s+replicate$/i, "");

      if (anim.status === "processing" || anim.status === "queued") {
        const step = anim.status === "queued" ? 2 : 4;
        animVisualProgress = Math.min(92, Math.max(animVisualProgress + step, backendProgress));
      } else if (anim.status === "completed") {
        animVisualProgress = 100;
      }

      animProgressFill.style.width = `${animVisualProgress}%`;
      animProgressText.textContent = `${animVisualProgress}%`;
  animStageEl.textContent = `Etapa: ${normalizedAnimStage}`;

      if (anim.status === "completed") {
        stopAnimPolling();
        animStatusEl.textContent = "Video listo";
        animStatusEl.className = "status completed";

        const videoUrl = `/animate/${animId}/video`;
        animVideo.src = `${videoUrl}?t=${Date.now()}`;
        animVideo.removeAttribute("hidden");
        animVideo.load();
        animVideo.play().catch(() => {});

        animDownload.href = videoUrl;
        animDownload.setAttribute("download", `IA-IMP-anim-${animId.slice(0, 8)}.mp4`);
        animDownload.classList.remove("disabled");
        animDownload.removeAttribute("hidden");
        animBtn.disabled = false;
      } else if (anim.status === "failed") {
        stopAnimPolling();
        animStatusEl.textContent = `Fallo: ${anim.error || "error desconocido"}`;
        animStatusEl.className = "status failed";
        animBtn.disabled = false;
      } else {
        animStatusEl.textContent = "Generando video...";
        animStatusEl.className = "status processing";
      }
    } catch {
      stopAnimPolling();
      animStatusEl.textContent = "Error de red al consultar animacion";
      animStatusEl.className = "status failed";
      animBtn.disabled = false;
    }
  }, 2500);
}

animBtn.addEventListener("click", async () => {
  if (!requireLogin("generar videos")) {
    return;
  }

  const hasAnimInputFile = animDropZoneInput.files && animDropZoneInput.files[0];

  if (!hasAnimInputFile && !currentAnimJobId) {
    animStatusEl.textContent = "Primero genera una imagen";
    animStatusEl.className = "status failed";
    animStatusEl.removeAttribute("hidden");
    return;
  }

  animBtn.disabled = true;
  animVideo.setAttribute("hidden", "");
  animVideo.src = "";
  animDownload.setAttribute("hidden", "");
  animDownload.classList.add("disabled");

  animStatusEl.textContent = "Iniciando animacion...";
  animStatusEl.className = "status processing";
  animStatusEl.removeAttribute("hidden");
  animProgressWrap.removeAttribute("hidden");
  animVisualProgress = 5;
  animProgressFill.style.width = "5%";
  animProgressText.textContent = "5%";
  animStageEl.textContent = "Etapa: enviando";

  const fd = new FormData();
  const selectedAnimModel = animModelEl.value;
  const selectedDuration = selectedAnimModel === "wan-video/wan-2.2-i2v-fast"
    ? "5"
    : (animDurationEl.value || "5");
  if (hasAnimInputFile) {
    fd.append("file", animDropZoneInput.files[0]);
  } else {
    fd.append("job_id", currentAnimJobId);
  }
  fd.append(
    "prompt",
    animPromptEl.value.trim() || "Camera slowly pans across the facade, gentle breeze in vegetation, cinematic sunset lighting"
  );
  fd.append("model", selectedAnimModel);
  fd.append("duration_seconds", selectedDuration);

  try {
    const resp = await fetch("/animate", { method: "POST", body: fd });
    if (!resp.ok) {
      const err = await readApiError(resp);
      animStatusEl.textContent = `Error: ${err}`;
      animStatusEl.className = "status failed";
      animBtn.disabled = false;
      return;
    }
    const data = await resp.json();
    await pollAnimation(data.anim_id);
  } catch {
    animStatusEl.textContent = "Error al iniciar animacion";
    animStatusEl.className = "status failed";
    animBtn.disabled = false;
  }
});

function syncAnimDurationOptions() {
  if (!animModelEl || !animDurationEl) return;
  const isWan22 = animModelEl.value === "wan-video/wan-2.2-i2v-fast";
  for (const option of Array.from(animDurationEl.options)) {
    const isFiveSeconds = option.value === "5";
    option.hidden = isWan22 && !isFiveSeconds;
    option.disabled = isWan22 && !isFiveSeconds;
  }
  if (isWan22) {
    animDurationEl.value = "5";
  }
}

animModelEl?.addEventListener("change", syncAnimDurationOptions);
syncAnimDurationOptions();

function stopMusicPolling() {
  if (musicPollingTimer) {
    clearInterval(musicPollingTimer);
    musicPollingTimer = null;
  }
}

async function pollMusic(musicId) {
  stopMusicPolling();

  musicPollingTimer = setInterval(async () => {
    try {
      const resp = await fetch(`/music/${musicId}`);
      if (!resp.ok) {
        musicStatusEl.textContent = "Error consultando estado musical";
        musicStatusEl.className = "status failed";
        stopMusicPolling();
        musicGenerateBtn.disabled = false;
        return;
      }

      const music = await resp.json();
      const backendProgress = Number(music.progress || 0);

      if (music.status === "processing" || music.status === "queued") {
        const step = music.status === "queued" ? 3 : 5;
        musicVisualProgress = Math.min(92, Math.max(musicVisualProgress + step, backendProgress));
      } else if (music.status === "completed") {
        musicVisualProgress = 100;
      }

      musicProgressFill.style.width = `${musicVisualProgress}%`;
      musicProgressText.textContent = `${musicVisualProgress}%`;
      musicStageEl.textContent = `Etapa: ${music.stage || "procesando"}`;

      if (music.status === "completed") {
        stopMusicPolling();
        musicStatusEl.textContent = "Audio listo";
        musicStatusEl.className = "status completed";

        const audioUrl = `/music/${musicId}/audio`;
        musicPlayer.src = `${audioUrl}?t=${Date.now()}`;
        musicPlayer.removeAttribute("hidden");
        musicPlayer.load();

        const modeLabel = music.mode === "song" ? "song" : "instrumental";
        musicDownload.href = audioUrl;
        musicDownload.setAttribute("download", `IA-IMP-${modeLabel}-${musicId.slice(0, 8)}.mp3`);
        musicDownload.classList.remove("disabled");
        musicDownload.removeAttribute("hidden");

        const modelInfo = music.model || "meta/musicgen";
        musicMetaEl.textContent = `Modo: ${music.mode || "instrumental"} · Modelo: ${modelInfo}`;
        musicGenerateBtn.disabled = false;
      } else if (music.status === "failed") {
        stopMusicPolling();
        musicStatusEl.textContent = `Fallo: ${music.error || "error desconocido"}`;
        musicStatusEl.className = "status failed";
        musicGenerateBtn.disabled = false;
      } else {
        musicStatusEl.textContent = "Generando musica...";
        musicStatusEl.className = "status processing";
      }
    } catch {
      stopMusicPolling();
      musicStatusEl.textContent = "Error de red al consultar audio";
      musicStatusEl.className = "status failed";
      musicGenerateBtn.disabled = false;
    }
  }, 2400);
}

musicTypeEl.addEventListener("change", () => {
  const isSong = musicTypeEl.value === "song";
  musicLyricsEl.placeholder = isSong
    ? "Escribe letra completa o ideas de versos/coro"
    : "Opcional: normalmente vacio para instrumental";
});

function applyMusicGenrePreset() {
  if (!musicGenreEl) return;
  const preset = MUSIC_GENRE_PRESETS[musicGenreEl.value];
  if (!preset) return;
  if (musicMoodEl) musicMoodEl.value = preset.mood;
  if (musicBpmEl) musicBpmEl.value = preset.bpm;
  if (musicInstrumentsEl) musicInstrumentsEl.value = preset.instruments;
  if (musicTasteEl) musicTasteEl.value = preset.taste;
  if (musicThemeEl) musicThemeEl.value = preset.theme;
  if (musicLanguageEl && musicTypeEl?.value === "song") musicLanguageEl.value = preset.language;
}

musicGenreEl?.addEventListener("change", applyMusicGenrePreset);
applyMusicGenrePreset();

musicForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (!requireLogin("generar musica")) {
    return;
  }

  musicGenerateBtn.disabled = true;
  musicPlayer.setAttribute("hidden", "");
  musicPlayer.src = "";
  musicDownload.setAttribute("hidden", "");
  musicDownload.classList.add("disabled");

  musicStatusEl.textContent = "Iniciando generacion musical...";
  musicStatusEl.className = "status processing";
  musicProgressWrap.removeAttribute("hidden");
  musicVisualProgress = 6;
  musicProgressFill.style.width = "6%";
  musicProgressText.textContent = "6%";
  musicStageEl.textContent = "Etapa: enviando";

  const fd = new FormData();
  const selectedMusicPreset = MUSIC_GENRE_PRESETS[musicGenreEl.value] || null;
  fd.append("mode", musicTypeEl.value);
  fd.append("genre", selectedMusicPreset?.genre || musicGenreEl.value || "pop comercial");
  fd.append("mood", musicMoodEl.value.trim() || "uplifting and emotional");
  fd.append("instruments", musicInstrumentsEl.value.trim() || "synth bass, drums, piano");
  fd.append("user_taste", musicTasteEl.value.trim() || "modern production and clean mix");
  fd.append("duration_seconds", "180");
  fd.append("language", musicLanguageEl.value || "es");
  fd.append("theme", musicThemeEl.value.trim() || "superacion personal");
  fd.append("custom_lyrics", musicLyricsEl.value.trim());

  const bpmRaw = musicBpmEl.value.trim();
  if (bpmRaw) {
    fd.append("bpm", bpmRaw);
  }

  try {
    const resp = await fetch("/music/generate", { method: "POST", body: fd });
    if (!resp.ok) {
      const err = await readApiError(resp);
      musicStatusEl.textContent = `Error: ${err}`;
      musicStatusEl.className = "status failed";
      musicGenerateBtn.disabled = false;
      return;
    }
    const data = await resp.json();
    await pollMusic(data.music_id);
  } catch {
    musicStatusEl.textContent = "Error al iniciar generacion musical";
    musicStatusEl.className = "status failed";
    musicGenerateBtn.disabled = false;
  }
});

function stopInfluencerPolling() {
  if (influencerPollingTimer) {
    clearInterval(influencerPollingTimer);
    influencerPollingTimer = null;
  }
}

async function pollInfluencer(influencerId) {
  stopInfluencerPolling();

  const tick = async () => {
    try {
      const resp = await fetch(`/influencer/${influencerId}`);
      if (!resp.ok) {
        influencerStatus.textContent = "Error consultando estado influencer";
        influencerStatus.className = "status failed";
        stopInfluencerPolling();
        influencerGenerateBtn.disabled = false;
        return;
      }

      const item = await resp.json();
      const backendProgress = Number(item.progress || 0);

      if (item.status === "processing" || item.status === "queued") {
        const step = item.status === "queued" ? 3 : 5;
        influencerVisualProgress = Math.min(92, Math.max(influencerVisualProgress + step, backendProgress));
      } else if (item.status === "completed") {
        influencerVisualProgress = 100;
      }

      influencerProgressFill.style.width = `${influencerVisualProgress}%`;
      influencerProgressText.textContent = `${influencerVisualProgress}%`;
      influencerStage.textContent = `Etapa: ${item.stage || "procesando"}`;

      if (item.status === "completed") {
        stopInfluencerPolling();
        influencerStatus.textContent = "Influencer listo";
        influencerStatus.className = "status completed";

        const videoUrl = `/influencer/${influencerId}/video`;
        influencerResultVideo.src = `${videoUrl}?t=${Date.now()}`;
        influencerResultVideo.removeAttribute("hidden");
        influencerResultVideo.load();

        influencerDownload.href = videoUrl;
        influencerDownload.setAttribute("download", `IA-IMP-influencer-${influencerId.slice(0, 8)}.mp4`);
        influencerDownload.classList.remove("disabled");
        influencerDownload.removeAttribute("hidden");
        influencerGenerateBtn.disabled = false;
      } else if (item.status === "failed") {
        stopInfluencerPolling();
        influencerVisualProgress = 0;
        influencerProgressFill.style.width = "0%";
        influencerProgressText.textContent = "Error";
        influencerStage.textContent = `Fallo: ${item.error || "error desconocido"}`;
        influencerStatus.textContent = `Fallo: ${item.error || "error desconocido"}`;
        influencerStatus.className = "status failed";
        influencerGenerateBtn.disabled = false;
      } else {
        influencerStatus.textContent = "Generando influencer...";
        influencerStatus.className = "status processing";
      }
    } catch {
      stopInfluencerPolling();
      influencerStatus.textContent = "Error de red al consultar influencer";
      influencerStatus.className = "status failed";
      influencerGenerateBtn.disabled = false;
    }
  };

  await tick();
  if (influencerPollingTimer) {
    return;
  }

  influencerPollingTimer = setInterval(tick, 2500);
}

async function ensureVideoDurationLimit(file, maxSeconds) {
  const tempUrl = URL.createObjectURL(file);
  try {
    const duration = await new Promise((resolve, reject) => {
      const probe = document.createElement("video");
      probe.preload = "metadata";
      probe.src = tempUrl;
      probe.onloadedmetadata = () => resolve(probe.duration);
      probe.onerror = () => reject(new Error("No se pudo leer la duracion del video"));
    });
    return Number(duration) <= maxSeconds;
  } finally {
    URL.revokeObjectURL(tempUrl);
  }
}

if (influencerForm) {
  influencerForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!requireLogin("generar influencers")) {
      return;
    }

    if (!influencerImageInput.files || !influencerImageInput.files[0]) {
      influencerStatus.textContent = "Sube o pega la imagen del personaje";
      influencerStatus.className = "status failed";
      return;
    }

    if (!influencerVideoInput.files || !influencerVideoInput.files[0]) {
      influencerStatus.textContent = "Sube el video guia";
      influencerStatus.className = "status failed";
      return;
    }

    const videoFile = influencerVideoInput.files[0];
    try {
      const validDuration = await ensureVideoDurationLimit(videoFile, 15);
      if (!validDuration) {
        influencerStatus.textContent = "El video guia debe durar maximo 15 segundos";
        influencerStatus.className = "status failed";
        return;
      }
    } catch {
      influencerStatus.textContent = "No se pudo validar duracion del video";
      influencerStatus.className = "status failed";
      return;
    }

    if (!influencerConsent.checked) {
      influencerStatus.textContent = "Debes confirmar consentimiento y derechos";
      influencerStatus.className = "status failed";
      return;
    }

    const instructionText = (influencerInstruction.value || "").toLowerCase();
    const blockedTerms = ["famoso", "famosa", "celebridad", "actor", "actriz", "cantante", "persona real", "farandula"];
    if (blockedTerms.some((term) => instructionText.includes(term))) {
      influencerStatus.textContent = "Solo se permiten personajes creados/originales";
      influencerStatus.className = "status failed";
      return;
    }

    influencerGenerateBtn.disabled = true;
    influencerResultVideo.setAttribute("hidden", "");
    influencerResultVideo.src = "";
    influencerDownload.setAttribute("hidden", "");
    influencerDownload.classList.add("disabled");

    influencerStatus.textContent = "Iniciando generacion influencer...";
    influencerStatus.className = "status processing";
    influencerProgressWrap.removeAttribute("hidden");
    influencerVisualProgress = 6;
    influencerProgressFill.style.width = "6%";
    influencerProgressText.textContent = "6%";
    influencerStage.textContent = "Etapa: enviando";

    const fd = new FormData();
    fd.append("reference_image", influencerImageInput.files[0]);
    fd.append("source_video", videoFile);
    fd.append("instruction_prompt", influencerInstruction.value.trim());
    fd.append("character_mode", "original");
    fd.append("resolution", influencerResolution.value);
    fd.append("target_fps", influencerFps.value);
    fd.append("turbo", "false");
    fd.append("consent_confirmed", "true");

    try {
      const resp = await fetch("/influencer/create", { method: "POST", body: fd });
      if (!resp.ok) {
        const err = await readApiError(resp);
        influencerStatus.textContent = `Error: ${err}`;
        influencerStatus.className = "status failed";
        influencerGenerateBtn.disabled = false;
        return;
      }

      const data = await resp.json();
      await pollInfluencer(data.influencer_id);
    } catch {
      influencerStatus.textContent = "Error al iniciar influencer";
      influencerStatus.className = "status failed";
      influencerGenerateBtn.disabled = false;
    }
  });
}

function formatChatMessageWithLinks(text) {
  const raw = String(text || "");
  const escaped = raw
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  // Convert [https://...] and plain https://... links into clickable anchors.
  const withBracketLinks = escaped.replace(/\[(https?:\/\/[^\]\s]+)\]/g, (_match, url) => {
    return `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`;
  });

  const withInternalLinks = withBracketLinks.replace(/(^|[\s(])(\/chat\/files\/[A-Za-z0-9._-]+)/g, (_match, prefix, path) => {
    return `${prefix}<a href="${path}" target="_blank" rel="noopener noreferrer">${path}</a>`;
  });

  return withInternalLinks.replace(/(^|[\s(])((https?:\/\/)[^\s<]+)/g, (match, prefix, url) => {
    if (prefix.includes('href="')) return match;
    return `${prefix}<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`;
  });
}

function appendMessage(role, text) {
  const bubble = document.createElement("div");
  bubble.className = `chat-bubble ${role}`;
  if (role === "assistant") {
    bubble.innerHTML = formatChatMessageWithLinks(text);
  } else {
    bubble.textContent = text;
  }
  chatMessages.appendChild(bubble);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function groupChatHistoryByConversation(rows) {
  const groups = new Map();
  for (const item of rows) {
    const convId = String(item?.conversation_id || `legacy-${item?.id || Math.random().toString(36).slice(2)}`);
    if (!groups.has(convId)) {
      groups.set(convId, []);
    }
    groups.get(convId).push(item);
  }

  const grouped = Array.from(groups.entries()).map(([conversationId, messages]) => {
    const sorted = messages.slice().sort((a, b) => Number(a.id || 0) - Number(b.id || 0));
    const first = sorted[0] || {};
    const last = sorted[sorted.length - 1] || {};
    return {
      conversationId,
      messages: sorted,
      preview: cropText(first.user_message, 90) || "Conversación",
      createdAt: String(first.created_at || ""),
      updatedAt: String(last.created_at || first.created_at || ""),
      model: cropText(last.model, 70) || "-",
    };
  });

  grouped.sort((a, b) => String(b.updatedAt).localeCompare(String(a.updatedAt)));
  return grouped;
}

function renderChatHistoryDetail(group) {
  if (!chatHistoryDetail) return;
  chatHistoryDetail.innerHTML = "";

  if (!group || !Array.isArray(group.messages) || !group.messages.length) {
    chatHistoryDetail.innerHTML = '<p class="chat-history-empty">Selecciona una conversación para ver todo el detalle.</p>';
    return;
  }

  for (const item of group.messages) {
    const entry = document.createElement("article");
    entry.className = "chat-history-detail-entry";
    entry.innerHTML = `
      <div class="chat-history-meta">
        <span>${escapeHtml(formatDate(item.created_at))}</span>
        <span>Modelo: ${escapeHtml(cropText(item.model, 70) || "-")}</span>
      </div>
      <p><strong>Tú:</strong> ${escapeHtml(String(item.user_message || "-"))}</p>
      <p><strong>Pachy IA:</strong> ${escapeHtml(String(item.assistant_message || "-"))}</p>
    `;
    chatHistoryDetail.appendChild(entry);
  }
}

function renderChatHistoryPanel(items) {
  if (!chatHistoryList) return;
  chatHistoryList.innerHTML = "";

  const rows = Array.isArray(items) ? items : [];
  const grouped = groupChatHistoryByConversation(rows);
  if (!grouped.length) {
    const empty = document.createElement("p");
    empty.className = "chat-history-empty";
    empty.textContent = "Aun no tienes conversaciones guardadas.";
    chatHistoryList.appendChild(empty);
    renderChatHistoryDetail(null);
    return;
  }

  const selectedConversationId = chatHistoryList.dataset.selectedConversationId || grouped[0].conversationId;
  let selected = grouped.find((g) => g.conversationId === selectedConversationId) || grouped[0];

  for (const group of grouped.slice(0, 120)) {
    const card = document.createElement("article");
    card.className = "chat-history-item";
    if (group.conversationId === selected.conversationId) {
      card.classList.add("is-active");
    }
    card.innerHTML = `
      <div class="chat-history-meta">
        <span>${escapeHtml(formatDate(group.updatedAt))}</span>
        <span>${group.messages.length} mensajes</span>
      </div>
      <p><strong>${escapeHtml(group.preview)}</strong></p>
      <p>Modelo reciente: ${escapeHtml(group.model)}</p>
    `;
    card.addEventListener("click", () => {
      chatHistoryList.dataset.selectedConversationId = group.conversationId;
      renderChatHistoryPanel(rows);
    });
    chatHistoryList.appendChild(card);
  }

  chatHistoryList.dataset.selectedConversationId = selected.conversationId;
  renderChatHistoryDetail(selected);
}

async function loadChatHistoryPanel(force = false) {
  if (!currentUser) {
    renderChatHistoryPanel([]);
    chatHistoryPanelLoaded = false;
    return;
  }
  if (chatHistoryPanelLoaded && !force) return;

  try {
    if (chatHistoryList) {
      chatHistoryList.innerHTML = '<p class="chat-history-empty">Cargando historial...</p>';
    }
    const resp = await fetch("/chat/history");
    if (!resp.ok) {
      const err = await readApiError(resp);
      throw new Error(err || "No se pudo cargar historial");
    }
    const data = await resp.json();
    renderChatHistoryPanel(Array.isArray(data?.items) ? data.items : []);
    chatHistoryPanelLoaded = true;
  } catch (error) {
    const text = error instanceof Error ? error.message : "No se pudo cargar historial";
    if (chatHistoryList) {
      chatHistoryList.innerHTML = `<p class="chat-history-empty">${text}</p>`;
    }
  }
}

function openChatHistoryModal() {
  if (!chatHistoryModal) return;
  chatHistoryModal.hidden = false;
  chatHistoryModal.setAttribute("aria-hidden", "false");
  chatHistoryToggle?.setAttribute("aria-expanded", "true");
  loadChatHistoryPanel(false);
}

function closeChatHistoryModal() {
  if (!chatHistoryModal) return;
  chatHistoryModal.hidden = true;
  chatHistoryModal.setAttribute("aria-hidden", "true");
  chatHistoryToggle?.setAttribute("aria-expanded", "false");
}

function formatBytes(value) {
  const size = Number(value || 0);
  if (!Number.isFinite(size) || size <= 0) return "0 B";
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

function renderChatAttachments() {
  if (!chatAttachList) return;
  chatAttachList.innerHTML = "";
  if (!chatAttachedFiles.length) {
    const empty = document.createElement("span");
    empty.className = "chat-attach-empty";
    empty.textContent = "Sin adjuntos";
    chatAttachList.appendChild(empty);
    return;
  }

  for (const file of chatAttachedFiles) {
    const item = document.createElement("div");
    item.className = "chat-attach-item";
    item.textContent = `${file.name} (${formatBytes(file.size)})`;
    chatAttachList.appendChild(item);
  }
}

function setChatAttachmentsFromInput(fileList) {
  const incoming = Array.from(fileList || []);
  if (!incoming.length) return;

  const merged = [...chatAttachedFiles, ...incoming];
  const unique = [];
  const seen = new Set();
  for (const file of merged) {
    const key = `${file.name}|${file.size}|${file.type}|${file.lastModified}`;
    if (seen.has(key)) continue;
    seen.add(key);
    unique.push(file);
  }

  if (unique.length > 5) {
    window.alert("Puedes adjuntar hasta 5 archivos por mensaje.");
  }

  const validated = unique.slice(0, 5).filter((file) => {
    if ((file.size || 0) > 10 * 1024 * 1024) {
      window.alert(`El archivo ${file.name} supera el limite de 10 MB.`);
      return false;
    }
    return true;
  });

  chatAttachedFiles = validated;
  renderChatAttachments();
  if (chatAttachInput) {
    const dt = new DataTransfer();
    for (const file of chatAttachedFiles) dt.items.add(file);
    chatAttachInput.files = dt.files;
  }
}

function clearChatAttachments() {
  chatAttachedFiles = [];
  if (chatAttachInput) chatAttachInput.value = "";
  renderChatAttachments();
}

chatAttachBtn?.addEventListener("click", () => {
  chatAttachInput?.click();
});

chatAttachInput?.addEventListener("change", () => {
  setChatAttachmentsFromInput(chatAttachInput.files);
});

chatHistoryToggle?.addEventListener("click", () => {
  openChatHistoryModal();
});

chatHistoryClose?.addEventListener("click", () => {
  closeChatHistoryModal();
});

chatHistoryModal?.addEventListener("click", (e) => {
  const target = e.target;
  if (target instanceof HTMLElement && target.dataset.closeChatHistory === "true") {
    closeChatHistoryModal();
  }
});

chatHistoryRefresh?.addEventListener("click", () => {
  loadChatHistoryPanel(true);
});

chatNewConversationBtn?.addEventListener("click", () => {
  chatHistory.length = 0;
  activeConversationId = `conv-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  chatMessages.innerHTML = "";
  appendMessage("assistant", "Nueva conversación iniciada. ¿Qué quieres crear con Pachy IA?");
  chatStatus.textContent = "Listo";
  chatStatus.className = "status completed";
});

closeChatHistoryModal();

renderChatAttachments();

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (!requireLogin("usar Pachy IA")) {
    return;
  }

  const message = chatInput.value.trim();
  if (!message && !chatAttachedFiles.length) return;

  const attachmentLabel = chatAttachedFiles.length
    ? `\nAdjuntos: ${chatAttachedFiles.map((file) => file.name).join(", ")}`
    : "";
  const shownUserMessage = message || "(Mensaje con adjuntos)";

  appendMessage("user", `${shownUserMessage}${attachmentLabel}`.trim());
  chatHistory.push({ role: "user", text: `${shownUserMessage}${attachmentLabel}`.trim() });
  chatInput.value = "";
  chatSendBtn.disabled = true;
  if (chatAttachBtn) chatAttachBtn.disabled = true;
  chatStatus.textContent = "Pensando...";
  chatStatus.className = "status processing";
  let sentOk = false;

  const context = chatHistory.slice(-8).map((m) => `${m.role}: ${m.text}`).join("\n");
  if (!activeConversationId) {
    activeConversationId = `conv-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  }

  try {
    let resp;
    if (chatAttachedFiles.length) {
      const formData = new FormData();
      formData.append("message", message);
      formData.append("context", context);
      formData.append("conversation_id", activeConversationId);
      for (const file of chatAttachedFiles) {
        formData.append("files", file, file.name);
      }
      resp = await fetch("/chat/message", {
        method: "POST",
        body: formData,
      });
    } else {
      resp = await fetch("/chat/message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, context, conversation_id: activeConversationId }),
      });
    }

    if (!resp.ok) {
      const err = await readApiError(resp);
      appendMessage("assistant", `Error: ${err}`);
      chatStatus.textContent = "Error";
      chatStatus.className = "status failed";
      chatSendBtn.disabled = false;
      if (chatAttachBtn) chatAttachBtn.disabled = false;
      return;
    }

    const data = await resp.json();
    const answer = data.answer || "No hay respuesta disponible.";
    appendMessage("assistant", answer);
    chatHistory.push({ role: "assistant", text: answer });
    chatHistoryPanelLoaded = false;
    if (chatHistoryModal && !chatHistoryModal.hidden) {
      loadChatHistoryPanel(true);
    }
    chatStatus.textContent = "Listo";
    chatStatus.className = "status completed";
    sentOk = true;
  } catch {
    appendMessage("assistant", "Error de red al consultar IA-IMP.");
    chatStatus.textContent = "Error de red";
    chatStatus.className = "status failed";
  } finally {
    chatSendBtn.disabled = false;
    if (chatAttachBtn) chatAttachBtn.disabled = false;
    if (sentOk) {
      clearChatAttachments();
    }
  }
});

function stopIntelligentPolling() {
  if (intelligentPollingTimer) {
    clearInterval(intelligentPollingTimer);
    intelligentPollingTimer = null;
  }
}

function resetIntelligentLinks() {
  if (intelligentLinksEl) intelligentLinksEl.hidden = true;
  if (intelligentVideoLinkEl) {
    intelligentVideoLinkEl.href = "#";
    intelligentVideoLinkEl.classList.add("disabled");
  }
  if (intelligentReportLinkEl) {
    intelligentReportLinkEl.href = "#";
    intelligentReportLinkEl.classList.add("disabled");
  }
}

function renderIntelligentQuantities(rows) {
  if (!intelligentQuantitiesEl) return;
  const items = Array.isArray(rows) ? rows : [];
  if (!items.length) {
    intelligentQuantitiesEl.textContent = "Aun sin estimaciones.";
    return;
  }
  const chunks = items.map((row) => {
    const material = row?.material || "Material";
    const zona = row?.zona || "Zona";
    const m2 = Number(row?.m2_estimados || 0);
    return `${material}: ${zona} - ${m2} m2`;
  });
  intelligentQuantitiesEl.textContent = chunks.join(" | ");
}

function pollIntelligentProject(jobId) {
  stopIntelligentPolling();
  intelligentPollingTimer = setInterval(async () => {
    try {
      const resp = await fetch(`/intelligent-project/${jobId}`);
      if (!resp.ok) {
        const err = await readApiError(resp);
        if (intelligentStatusEl) {
          intelligentStatusEl.textContent = `Error: ${err}`;
          intelligentStatusEl.className = "status failed";
        }
        stopIntelligentPolling();
        if (intelligentSubmitBtn) intelligentSubmitBtn.disabled = false;
        return;
      }

      const data = await resp.json();
      const progress = Number(data.progress || 0);
      if (intelligentStatusEl) {
        intelligentStatusEl.textContent = `Proyecto Inteligente: ${data.stage || "procesando"} (${progress}%)`;
        intelligentStatusEl.className = "status processing";
      }

      progressFill.style.width = `${Math.max(0, Math.min(100, progress))}%`;
      progressText.textContent = `${Math.max(0, Math.min(100, progress))}%`;
      stageEl.textContent = `Etapa: ${data.stage || "procesando"}`;
      etaEl.textContent = "ETA: --";
      setStatus("Proyecto Inteligente en ejecución...", "processing");

      if (data.status === "completed") {
        stopIntelligentPolling();
        showImageElement(outputPreview, `/jobs/${jobId}/image?t=${Date.now()}`);
        hideImageElement(inputPreview);
        downloadLink.href = `/jobs/${jobId}/image`;
        downloadLink.setAttribute("download", `IA-IMP-proyecto-${jobId.slice(0, 8)}.png`);
        downloadLink.classList.remove("disabled");
        setStatus("Proyecto Inteligente completado", "completed");

        if (intelligentLinksEl) intelligentLinksEl.hidden = false;
        if (intelligentReportLinkEl) {
          intelligentReportLinkEl.href = `/intelligent-project/${jobId}/report`;
          intelligentReportLinkEl.classList.remove("disabled");
        }
        if (intelligentVideoLinkEl) {
          if (data.output_video) {
            intelligentVideoLinkEl.href = `/intelligent-project/${jobId}/video`;
            intelligentVideoLinkEl.classList.remove("disabled");
          } else {
            intelligentVideoLinkEl.href = "#";
            intelligentVideoLinkEl.classList.add("disabled");
          }
        }
        renderIntelligentQuantities(data.quantities || []);
        if (intelligentStatusEl) {
          intelligentStatusEl.textContent = "Proyecto Inteligente completado.";
          intelligentStatusEl.className = "status completed";
        }
        if (intelligentSubmitBtn) intelligentSubmitBtn.disabled = false;
      } else if (data.status === "failed") {
        stopIntelligentPolling();
        const err = data.error || "error desconocido";
        setStatus(`Fallo: ${err}`, "failed");
        if (intelligentStatusEl) {
          intelligentStatusEl.textContent = `Fallo: ${err}`;
          intelligentStatusEl.className = "status failed";
        }
        if (intelligentSubmitBtn) intelligentSubmitBtn.disabled = false;
      }
    } catch {
      stopIntelligentPolling();
      if (intelligentStatusEl) {
        intelligentStatusEl.textContent = "Error de red consultando el proyecto.";
        intelligentStatusEl.className = "status failed";
      }
      if (intelligentSubmitBtn) intelligentSubmitBtn.disabled = false;
    }
  }, 2000);
}

intelligentForm?.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (!requireLogin("crear Proyecto Inteligente")) {
    return;
  }

  const prompt = String(intelligentPromptEl?.value || "").trim();
  if (!prompt) {
    if (intelligentStatusEl) {
      intelligentStatusEl.textContent = "Describe el concepto del proyecto.";
      intelligentStatusEl.className = "status failed";
    }
    return;
  }

  const materialNames = [...intelligentSelectedMaterialNames].slice(0, 2);
  if (!materialNames.length) {
    if (intelligentStatusEl) {
      intelligentStatusEl.textContent = "Selecciona al menos 1 material del catálogo.";
      intelligentStatusEl.className = "status failed";
    }
    return;
  }

  if (intelligentSubmitBtn) intelligentSubmitBtn.disabled = true;
  resetIntelligentLinks();
  renderIntelligentQuantities([]);
  setStatus("Creando Proyecto Inteligente...", "processing");
  progressFill.style.width = "8%";
  progressText.textContent = "8%";
  stageEl.textContent = "Etapa: en cola";
  etaEl.textContent = "ETA: --";

  if (intelligentStatusEl) {
    intelligentStatusEl.textContent = "Enviando solicitud...";
    intelligentStatusEl.className = "status processing";
  }

  try {
    const resp = await fetch("/intelligent-project/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt,
        material_names: materialNames,
        include_video: Boolean(intelligentIncludeVideoEl?.checked),
        duration_seconds: Number(intelligentDurationEl?.value || 5),
      }),
    });

    if (!resp.ok) {
      const err = await readApiError(resp);
      throw new Error(err || "No se pudo crear el proyecto inteligente");
    }

    const data = await resp.json();
    const jobId = data.job_id;
    if (!jobId) {
      throw new Error("Respuesta sin job_id");
    }

    if (intelligentStatusEl) {
      intelligentStatusEl.textContent = "Proyecto en cola...";
      intelligentStatusEl.className = "status processing";
    }
    pollIntelligentProject(jobId);
    setMode("intelligent_project");
  } catch (err) {
    if (intelligentSubmitBtn) intelligentSubmitBtn.disabled = false;
    const message = err instanceof Error ? err.message : "No se pudo crear el proyecto";
    if (intelligentStatusEl) {
      intelligentStatusEl.textContent = message;
      intelligentStatusEl.className = "status failed";
    }
    setStatus(message, "failed");
  }
});

appendMessage("assistant", "Hola, soy Pachy IA. Puedo ayudarte con ideas arquitectonicas, prompts, distribucion espacial y materiales.");
updateAuthTabUi();
updateAuthUi();
  loadPricingConfig().then(() => {
    renderPlanBanners();
    renderPricesModal();
    renderRechargeSummary();
    return refreshCurrentUser();
  }).then(() => {
    return syncPendingWompiPayments(false);
  }).then(() => {
    const hadResetToken = openPasswordResetFromUrl();
    if (!hadResetToken) {
      handleWompiReturnFromCheckout();
    }
  });
setMode("img2img");
