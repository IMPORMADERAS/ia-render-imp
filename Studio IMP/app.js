const mediaInput = document.getElementById("mediaInput");
const undoBtn = document.getElementById("undoBtn");
const redoBtn = document.getElementById("redoBtn");
const saveProjectBtn = document.getElementById("saveProjectBtn");
const openProjectBtn = document.getElementById("openProjectBtn");
const projectFileInput = document.getElementById("projectFileInput");
const exportMp4 = document.getElementById("exportMp4");
const exportPreset = document.getElementById("exportPreset");
const exportColorPreset = document.getElementById("exportColorPreset");
const exportStatus = document.getElementById("exportStatus");
const mediaName = document.getElementById("mediaName");
const activeClipInfo = document.getElementById("activeClipInfo");
const videoPreview = document.getElementById("videoPreview");
const imagePreview = document.getElementById("imagePreview");
const exportOverlay = document.getElementById("exportOverlay");
const exportOverlayTitle = document.getElementById("exportOverlayTitle");
const exportOverlayFill = document.getElementById("exportOverlayFill");
const exportOverlayPercent = document.getElementById("exportOverlayPercent");
const exportOverlayEta = document.getElementById("exportOverlayEta");
const stopBtn = document.getElementById("stopBtn");
const playPause = document.getElementById("playPause");
const pauseBtn = document.getElementById("pauseBtn");
const timeDisplay = document.getElementById("timeDisplay");
const playhead = document.getElementById("playhead");
const trimStartInput = document.getElementById("trimStart");
const trimEndInput = document.getElementById("trimEnd");
const applyTrim = document.getElementById("applyTrim");
const filterPreset = document.getElementById("filterPreset");
const brightnessInput = document.getElementById("brightness");
const contrastInput = document.getElementById("contrast");
const saturationInput = document.getElementById("saturation");
const videoFadeInInput = document.getElementById("videoFadeIn");
const videoFadeOutInput = document.getElementById("videoFadeOut");
const audioFadeInInput = document.getElementById("audioFadeIn");
const audioFadeOutInput = document.getElementById("audioFadeOut");
const fadeOverlay = document.getElementById("fadeOverlay");
const addText = document.getElementById("addText");
const copyTextClip = document.getElementById("copyTextClip");
const pasteTextClip = document.getElementById("pasteTextClip");
const textItems = document.getElementById("textItems");
const textLayer = document.getElementById("textLayer");
const baseVolumeInput = document.getElementById("baseVolume");
const keyframeList = document.getElementById("keyframeList");
const clearKeys = document.getElementById("clearKeys");
const mediaBin = document.getElementById("mediaBin");
const addVideoTrack = document.getElementById("addVideoTrack");
const addAudioTrack = document.getElementById("addAudioTrack");
const addImageMedia = document.getElementById("addImageMedia");
const addTextTrackBtn = document.getElementById("addTextTrack");
const timelineZoom = document.getElementById("timelineZoom");
const videoTracks = document.getElementById("videoTracks");
const imageTracks = document.getElementById("imageTracks");
const audioTracks = document.getElementById("audioTracks");
const textTracksTimeline = document.getElementById("textTracksTimeline");
const timelineCanvas = document.getElementById("timelineCanvas");
const timelineRuler = document.getElementById("timelineRuler");
const timelineScroll = document.getElementById("timelineScroll");
const timelinePlayheadLine = document.getElementById("timelinePlayheadLine");

let pixelsPerSecond = 80;
const MIN_TIMELINE_WIDTH = 800;
const TRACK_LABEL_WIDTH_PX = 92;
const DEFAULT_TEXT_FONT = "Manrope";
const TEXT_TRACK_NAME_PREFIX = "T";
const IS_MOBILE_LAYOUT = window.matchMedia("(max-width: 900px)").matches;
const IS_MOBILE_UA = /Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent || "");
const IS_MOBILE_DEVICE = IS_MOBILE_LAYOUT || IS_MOBILE_UA;
const MOBILE_UI_FRAME_MS = 66;
const MOBILE_VIDEO_SEEK_TOLERANCE = 0.55;
const TEXT_FONT_OPTIONS = [
  { value: "Manrope", label: "Manrope" },
  { value: "Chakra Petch", label: "Chakra Petch" },
  { value: "Poppins", label: "Poppins" },
  { value: "Montserrat", label: "Montserrat" },
  { value: "Oswald", label: "Oswald" },
  { value: "Bebas Neue", label: "Bebas Neue" },
  { value: "Playfair Display", label: "Playfair Display" },
  { value: "Merriweather", label: "Merriweather" },
  { value: "Anton", label: "Anton" },
  { value: "Rubik Mono One", label: "Rubik Mono One" }
];

const state = {
  tracks: [],
  textTracks: [],
  textClips: [],
  activeTrackId: null,
  activeClipId: null,
  activeTextTrackId: null,
  activeTextClipId: null,
  copiedTextClip: null,
  previewClipId: null,
  previewAudioClipId: null,
  playback: {
    isTimelinePlaying: false,
    timelineTime: 0,
    lastFrameMs: 0,
    lastUiFrameMs: 0,
    rafId: null
  },
  drag: {
    kind: null,
    clipId: null,
    trackId: null,
    pointerOffsetSeconds: 0
  },
  playheadDrag: {
    active: false
  },
  history: {
    undoStack: [],
    redoStack: [],
    maxSnapshots: 80,
    applying: false
  },
  lastSelectionKind: "media",
  isExporting: false
};

let draggingTextId = null;
let dragOffsetX = 0;
let dragOffsetY = 0;
const timelineAudioPlayers = new Map();
let exportAudioContext = null;
let exportAudioDestination = null;
const exportAudioSourceNodes = new WeakMap();

// Bloquear clic derecho
    document.addEventListener('contextmenu', function(e) {
    e.preventDefault();
    });

    // Bloquear teclas comunes de inspección (F12, Ctrl+Shift+I, Ctrl+Shift+J, Ctrl+U)
    document.addEventListener('keydown', function(e) {
    // F12
    if (e.keyCode === 123) {
        e.preventDefault();
        return false;
    }
    // Ctrl+Shift+I/J/C
    if (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'J' || e.key === 'C')) {
        e.preventDefault();
        return false;
    }
    // Ctrl+U
    if (e.ctrlKey && e.key === 'u') {
        e.preventDefault();
        return false;
    }
    });

function getExportAudioBus() {
  if (!exportAudioContext || exportAudioContext.state === "closed") {
    exportAudioContext = new AudioContext();
    exportAudioDestination = exportAudioContext.createMediaStreamDestination();
  }
  return {
    context: exportAudioContext,
    destination: exportAudioDestination
  };
}

function connectElementToExportBus(element) {
  if (!element) {
    return;
  }

  const { context, destination } = getExportAudioBus();
  let sourceNode = exportAudioSourceNodes.get(element);

  if (!sourceNode) {
    sourceNode = context.createMediaElementSource(element);
    exportAudioSourceNodes.set(element, sourceNode);
  }

  sourceNode.disconnect();
  sourceNode.connect(destination);
  if (!IS_MOBILE_DEVICE) {
    sourceNode.connect(context.destination);
  }
}

function prepareExportAudioRouting() {
  connectElementToExportBus(videoPreview);

  state.tracks.forEach((track) => {
    if (track.type !== "audio") {
      return;
    }

    track.clips.forEach((clip) => {
      const player = getOrCreateAudioPlayer(clip);
      connectElementToExportBus(player);
    });
  });
}

function setExportStatus(message) {
  exportStatus.textContent = message;
}

function formatEta(seconds) {
  const safe = Math.max(0, Math.round(seconds || 0));
  const mins = Math.floor(safe / 60);
  const secs = safe % 60;
  return `${mins}:${String(secs).padStart(2, "0")}`;
}

function setExportOverlayProgress(percent, title, etaText) {
  const safe = clamp(Number(percent) || 0, 0, 100);
  if (title) {
    exportOverlayTitle.textContent = title;
  }
  exportOverlayFill.style.width = `${safe}%`;
  exportOverlayPercent.textContent = `${Math.floor(safe)}%`;
  if (typeof etaText === "string") {
    exportOverlayEta.textContent = etaText;
  }
}

function resetExportOverlay() {
  setExportOverlayProgress(0, "Rendering...", "Tiempo restante: calculando...");
}

function setExportingState(isExporting) {
  state.isExporting = isExporting;
  document.body.classList.toggle("is-exporting", isExporting);
  exportOverlay.classList.toggle("visible", isExporting);
  exportOverlay.setAttribute("aria-hidden", isExporting ? "false" : "true");
  if (!isExporting) {
    resetExportOverlay();
  }

  const controls = Array.from(document.querySelectorAll("button, input, select, textarea"));
  controls.forEach((control) => {
    if (isExporting) {
      control.dataset.prevDisabled = control.disabled ? "1" : "0";
      control.disabled = true;
      return;
    }

    const prev = control.dataset.prevDisabled;
    if (prev === "0") {
      control.disabled = false;
    } else if (prev === "1") {
      control.disabled = true;
    } else {
      control.disabled = false;
    }
    delete control.dataset.prevDisabled;
  });
}

function hasTimelineContent() {
  return getAllClips().length > 0 || state.textClips.length > 0;
}

function projectSnapshot() {
  return JSON.stringify({
    tracks: state.tracks,
    textTracks: state.textTracks,
    textClips: state.textClips,
    activeTrackId: state.activeTrackId,
    activeClipId: state.activeClipId,
    activeTextTrackId: state.activeTextTrackId,
    activeTextClipId: state.activeTextClipId,
    copiedTextClip: state.copiedTextClip,
    previewClipId: state.previewClipId,
    timelineTime: state.playback.timelineTime,
    pixelsPerSecond
  });
}

function applySnapshot(snapshotText) {
  const snapshot = JSON.parse(snapshotText);
  state.history.applying = true;

  state.tracks = snapshot.tracks || [];
  state.textTracks = snapshot.textTracks || [];
  state.textClips = snapshot.textClips || [];
  state.activeTrackId = snapshot.activeTrackId || null;
  state.activeClipId = snapshot.activeClipId || null;
  state.activeTextTrackId = snapshot.activeTextTrackId || null;
  state.activeTextClipId = snapshot.activeTextClipId || null;
  state.copiedTextClip = snapshot.copiedTextClip || null;
  state.previewClipId = snapshot.previewClipId || null;
  state.playback.timelineTime = snapshot.timelineTime || 0;
  pixelsPerSecond = snapshot.pixelsPerSecond || 80;
  timelineZoom.value = String(pixelsPerSecond);
  ensureTextTracks();

  state.history.applying = false;

  renderTimeline();
  renderMediaBin();
  renderTextInspector();
  renderKeyframes();
  setTimelineTime(state.playback.timelineTime, { forceSeek: true });
}

function getTextTrackById(trackId) {
  return state.textTracks.find((track) => track.id === trackId) || null;
}

function createTextTrackModel() {
  const count = state.textTracks.length + 1;
  return {
    id: uid(),
    name: `${TEXT_TRACK_NAME_PREFIX}${count}`,
    locked: false
  };
}

function ensureTextTracks() {
  if (!state.textTracks.length) {
    state.textTracks.push(createTextTrackModel());
  }

  if (!getTextTrackById(state.activeTextTrackId)) {
    state.activeTextTrackId = state.textTracks[0].id;
  }

  const fallbackTrackId = state.textTracks[0].id;
  state.textClips.forEach((clip) => {
    if (!getTextTrackById(clip.trackId)) {
      clip.trackId = fallbackTrackId;
    }
  });
}

function addTextTrack(options = {}) {
  const { recordHistory = false } = options;
  if (recordHistory) {
    pushHistorySnapshot();
  }

  const track = createTextTrackModel();
  state.textTracks.push(track);
  state.activeTextTrackId = track.id;
  renderTimeline();
  return track;
}

function removeTextTrack(trackId) {
  if (state.textTracks.length <= 1) {
    return;
  }

  const index = state.textTracks.findIndex((track) => track.id === trackId);
  if (index < 0) {
    return;
  }

  pushHistorySnapshot();
  state.textTracks.splice(index, 1);

  const fallbackTrackId = state.textTracks[0].id;
  state.textClips.forEach((clip) => {
    if (clip.trackId === trackId) {
      clip.trackId = fallbackTrackId;
    }
  });

  if (state.activeTextTrackId === trackId) {
    state.activeTextTrackId = fallbackTrackId;
  }

  renderTextInspector();
  renderTextLayer();
  renderTimeline();
}

function pushHistorySnapshot() {
  if (state.history.applying) {
    return;
  }

  const current = projectSnapshot();
  const undoStack = state.history.undoStack;
  if (undoStack.length && undoStack[undoStack.length - 1] === current) {
    return;
  }

  undoStack.push(current);
  if (undoStack.length > state.history.maxSnapshots) {
    undoStack.shift();
  }
  state.history.redoStack = [];
}

function undoProject() {
  if (!state.history.undoStack.length) {
    return;
  }

  if (state.playback.isTimelinePlaying) {
    stopTimelinePlayback();
  }

  const current = projectSnapshot();
  const previous = state.history.undoStack.pop();
  state.history.redoStack.push(current);
  applySnapshot(previous);
}

function redoProject() {
  if (!state.history.redoStack.length) {
    return;
  }

  if (state.playback.isTimelinePlaying) {
    stopTimelinePlayback();
  }

  const current = projectSnapshot();
  const next = state.history.redoStack.pop();
  state.history.undoStack.push(current);
  applySnapshot(next);
}

const audioPreview = new Audio();
audioPreview.preload = "auto";

function uid() {
  if (window.crypto && window.crypto.randomUUID) {
    return window.crypto.randomUUID();
  }
  return `${Date.now()}-${Math.floor(Math.random() * 1_000_000)}`;
}

function formatTime(seconds) {
  const safe = Math.max(0, seconds || 0);
  const m = Math.floor(safe / 60);
  const s = Math.floor(safe % 60);
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function isBlobUrl(url) {
  return typeof url === "string" && url.startsWith("blob:");
}

function blobToDataUrl(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result || ""));
    reader.onerror = () => reject(new Error("FILE_READER_ERROR"));
    reader.readAsDataURL(blob);
  });
}

async function sourceUrlToDataUrl(sourceUrl) {
  const response = await fetch(sourceUrl);
  const blob = await response.blob();
  return blobToDataUrl(blob);
}

async function dataUrlToBlob(dataUrl) {
  const response = await fetch(dataUrl);
  return response.blob();
}

function cleanupClipSourceUrls(tracks) {
  (tracks || []).forEach((track) => {
    (track.clips || []).forEach((clip) => {
      if (isBlobUrl(clip.sourceUrl)) {
        URL.revokeObjectURL(clip.sourceUrl);
      }
    });
  });
}

function resetProjectMediaPlayers() {
  timelineAudioPlayers.forEach((player) => {
    player.pause();
  });
  timelineAudioPlayers.clear();
}

function getTrackMediaKindFromModel(track) {
  if (!track) {
    return "video";
  }
  if (track.type !== "video") {
    return track.type;
  }
  if (track.mediaKind === "image") {
    return "image";
  }
  return "video";
}

function getTimestampForFilename() {
  const now = new Date();
  const y = now.getFullYear();
  const m = String(now.getMonth() + 1).padStart(2, "0");
  const d = String(now.getDate()).padStart(2, "0");
  const h = String(now.getHours()).padStart(2, "0");
  const min = String(now.getMinutes()).padStart(2, "0");
  const s = String(now.getSeconds()).padStart(2, "0");
  return `${y}${m}${d}-${h}${min}${s}`;
}

function detectMediaType(file) {
  if (file.type.startsWith("image/")) {
    return "image";
  }
  if (file.type.startsWith("video/")) {
    return "video";
  }
  if (file.type.startsWith("audio/")) {
    return "audio";
  }

  const lower = file.name.toLowerCase();
  if (
    lower.endsWith(".png") ||
    lower.endsWith(".jpg") ||
    lower.endsWith(".jpeg") ||
    lower.endsWith(".webp") ||
    lower.endsWith(".gif") ||
    lower.endsWith(".bmp")
  ) {
    return "image";
  }
  if (lower.endsWith(".mp3") || lower.endsWith(".wav") || lower.endsWith(".ogg") || lower.endsWith(".m4a")) {
    return "audio";
  }
  return "video";
}

function getTrackTypeForClip(type) {
  if (type === "audio") {
    return "audio";
  }
  return "video";
}

function getTrackById(trackId) {
  return state.tracks.find((track) => track.id === trackId) || null;
}

function getTrackMediaKind(track) {
  if (!track) {
    return null;
  }
  if (track.type === "video") {
    return track.mediaKind === "image" ? "image" : "video";
  }
  return track.type;
}

function getAllClips() {
  return state.tracks.flatMap((track) => track.clips);
}

function getClipById(clipId) {
  for (const track of state.tracks) {
    const clip = track.clips.find((item) => item.id === clipId);
    if (clip) {
      return { track, clip };
    }
  }
  return null;
}

function getTextClipById(textClipId) {
  return state.textClips.find((item) => item.id === textClipId) || null;
}

function getTrackClipsSorted(track) {
  return [...track.clips].sort((a, b) => a.timelineStart - b.timelineStart);
}

function isAnyAudioTrackSolo() {
  return state.tracks.some((track) => track.type === "audio" && track.solo);
}

function isTrackAudible(track) {
  if (track.type !== "audio") {
    return true;
  }

  if (track.muted) {
    return false;
  }

  if (isAnyAudioTrackSolo()) {
    return track.solo;
  }

  return true;
}

function getAudioFadeMultiplier(clip, localTime) {
  const timeFromStart = Math.max(0, localTime - clip.trimStart);
  const timeToEnd = Math.max(0, clip.trimEnd - localTime);

  let fadeMultiplier = 1;
  if (clip.fades.audioFadeIn > 0 && timeFromStart < clip.fades.audioFadeIn) {
    fadeMultiplier *= timeFromStart / clip.fades.audioFadeIn;
  }
  if (clip.fades.audioFadeOut > 0 && timeToEnd < clip.fades.audioFadeOut) {
    fadeMultiplier *= timeToEnd / clip.fades.audioFadeOut;
  }
  return clamp(fadeMultiplier, 0, 1);
}

function getVideoFadeOpacity(clip, localTime) {
  if (!clip || !clip.fades) {
    return 0;
  }

  const timeFromStart = Math.max(0, localTime - clip.trimStart);
  const timeToEnd = Math.max(0, clip.trimEnd - localTime);

  let opacity = 0;
  if (clip.fades.videoFadeIn > 0 && timeFromStart < clip.fades.videoFadeIn) {
    opacity = Math.max(opacity, 1 - timeFromStart / clip.fades.videoFadeIn);
  }
  if (clip.fades.videoFadeOut > 0 && timeToEnd < clip.fades.videoFadeOut) {
    opacity = Math.max(opacity, 1 - timeToEnd / clip.fades.videoFadeOut);
  }

  return clamp(opacity, 0, 1);
}

function getOrCreateAudioPlayer(clip) {
  if (timelineAudioPlayers.has(clip.id)) {
    return timelineAudioPlayers.get(clip.id);
  }

  const player = new Audio();
  player.src = clip.sourceUrl;
  player.preload = "auto";
  player.crossOrigin = "anonymous";
  player.loop = false;
  timelineAudioPlayers.set(clip.id, player);
  return player;
}

function stopAllTimelineAudio() {
  timelineAudioPlayers.forEach((player) => {
    player.pause();
  });
}

function syncTimelineAudio(projectTime) {
  const activeAudioClipIds = new Set();

  state.tracks.forEach((track) => {
    if (track.type !== "audio" || !isTrackAudible(track)) {
      return;
    }

    track.clips.forEach((clip) => {
      const start = clip.timelineStart;
      const end = clip.timelineStart + getClipEffectiveDuration(clip);
      if (projectTime < start || projectTime >= end) {
        return;
      }

      const localTime = clip.trimStart + (projectTime - clip.timelineStart);
      const player = getOrCreateAudioPlayer(clip);
      const drift = Math.abs((player.currentTime || 0) - localTime);
      if (drift > 0.25) {
        try {
          player.currentTime = localTime;
        } catch {
          // Ignore transient metadata seek errors.
        }
      }

      const keyVolume = getVolumeAtTime(clip, localTime);
      const gain = getAudioFadeMultiplier(clip, localTime);
      player.volume = clamp(keyVolume * gain, 0, 1);

      if (player.paused) {
        player.play().catch(() => {});
      }

      activeAudioClipIds.add(clip.id);
    });
  });

  timelineAudioPlayers.forEach((player, clipId) => {
    if (!activeAudioClipIds.has(clipId)) {
      player.pause();
    }
  });
}

function toggleTrackProperty(trackId, property) {
  pushHistorySnapshot();
  const track = getTrackById(trackId);
  if (!track) {
    return;
  }

  track[property] = !track[property];
  renderTimeline();
  updateFadeVisualAndAudio();
}

function renderMediaBin() {
  mediaBin.innerHTML = "";
  const clips = getAllClips();

  clips.forEach((clip) => {
    const item = document.createElement("li");
    item.className = "media-bin-item";
    if (state.activeClipId === clip.id) {
      item.classList.add("active");
    }
    item.textContent = `${clip.name} (${clip.type.toUpperCase()})`;
    item.addEventListener("click", () => {
      selectClip(clip.id);
    });
    mediaBin.appendChild(item);
  });
}

function resolveTimelineClip(projectTime) {
  const visibleVideoTracks = state.tracks.filter((track) => track.type === "video" && track.visible);
  if (!visibleVideoTracks.length) {
    return null;
  }

  for (let t = visibleVideoTracks.length - 1; t >= 0; t -= 1) {
    const track = visibleVideoTracks[t];
    const clips = getTrackClipsSorted(track);
    for (const clip of clips) {
      const start = clip.timelineStart;
      const end = clip.timelineStart + getClipEffectiveDuration(clip);
      if (projectTime >= start && projectTime < end) {
        const local = clip.trimStart + (projectTime - clip.timelineStart);
        return {
          track,
          clip,
          localTime: clamp(local, clip.trimStart, clip.trimEnd)
        };
      }
    }
  }

  return null;
}

function getPreviewClipRef() {
  if (!state.previewClipId) {
    return null;
  }
  return getClipById(state.previewClipId);
}

function getPreviewAudioClipRef() {
  if (!state.previewAudioClipId) {
    return null;
  }
  return getClipById(state.previewAudioClipId);
}

function resolveTimelineAudioClip(projectTime) {
  const audioTrackList = state.tracks.filter((track) => track.type === "audio");
  if (!audioTrackList.length) {
    return null;
  }

  for (let t = audioTrackList.length - 1; t >= 0; t -= 1) {
    const track = audioTrackList[t];
    if (!isTrackAudible(track)) {
      continue;
    }

    const clips = getTrackClipsSorted(track);
    for (const clip of clips) {
      const start = clip.timelineStart;
      const end = clip.timelineStart + getClipEffectiveDuration(clip);
      if (projectTime >= start && projectTime < end) {
        const local = clip.trimStart + (projectTime - clip.timelineStart);
        return {
          track,
          clip,
          localTime: clamp(local, clip.trimStart, clip.trimEnd)
        };
      }
    }
  }

  return null;
}

function getProjectDuration() {
  const clips = getAllClips();
  const textEnd = state.textClips.length
    ? Math.max(...state.textClips.map((clip) => clip.start + clip.duration))
    : 0;

  if (!clips.length && textEnd <= 0) {
    return 10;
  }

  const mediaEnd = clips.length
    ? clips.reduce((max, clip) => Math.max(max, clip.timelineStart + getClipEffectiveDuration(clip)), 0)
    : 0;

  return Math.max(10, mediaEnd, textEnd);
}

function getProjectWidthPx() {
  return Math.max(MIN_TIMELINE_WIDTH, Math.ceil(getProjectDuration() * pixelsPerSecond));
}

function getClipEffectiveDuration(clip) {
  return Math.max(0.01, clip.trimEnd - clip.trimStart);
}

function addTrack(type, options = {}) {
  const { mediaKind } = options;
  const resolvedMediaKind = type === "video" ? mediaKind || "video" : type;
  const count = state.tracks.filter((track) => {
    if (track.type !== type) {
      return false;
    }
    if (type === "video") {
      return getTrackMediaKind(track) === resolvedMediaKind;
    }
    return true;
  }).length + 1;

  const track = {
    id: uid(),
    type,
    mediaKind: resolvedMediaKind,
    name: `${resolvedMediaKind === "video" ? "V" : resolvedMediaKind === "image" ? "I" : "A"}${count}`,
    visible: true,
    muted: false,
    solo: false,
    locked: false,
    clips: []
  };
  state.tracks.push(track);

  if (!state.activeTrackId) {
    state.activeTrackId = track.id;
  }

  renderTimeline();
  return track;
}

function removeTrack(trackId) {
  pushHistorySnapshot();
  const index = state.tracks.findIndex((track) => track.id === trackId);
  if (index < 0) {
    return;
  }

  const [removedTrack] = state.tracks.splice(index, 1);
  removedTrack.clips.forEach((clip) => {
    URL.revokeObjectURL(clip.sourceUrl);
  });

  if (!state.tracks.length) {
    addTrack("video");
    addTrack("audio");
  }

  if (state.activeTrackId === trackId) {
    state.activeTrackId = state.tracks[0].id;
  }

  const preview = getPreviewClipRef();
  if (!preview) {
    state.previewClipId = null;
  }

  const active = getActiveClipRef();
  if (!active) {
    state.activeClipId = null;
    mediaName.textContent = "Sin archivo cargado";
    activeClipInfo.textContent = "Sin clip seleccionado";
    videoPreview.removeAttribute("src");
    videoPreview.load();
    updateTransport();
    renderTextInspector();
    renderKeyframes();
    renderTextLayer();
  }

  renderTimeline();
  renderMediaBin();
}

function getOrCreateTargetTrackForClip(clipType) {
  const targetKind = getTrackTypeForClip(clipType);
  const activeTrack = getTrackById(state.activeTrackId);

  if (clipType === "image") {
    if (activeTrack && activeTrack.type === "video" && getTrackMediaKind(activeTrack) === "image") {
      return activeTrack;
    }

    const sameKindTrack = state.tracks.find(
      (track) => track.type === "video" && getTrackMediaKind(track) === "image"
    );
    if (sameKindTrack) {
      return sameKindTrack;
    }

    return addTrack("video", { mediaKind: "image" });
  }

  if (activeTrack && activeTrack.type === targetKind) {
    if (targetKind !== "video" || getTrackMediaKind(activeTrack) === "video") {
      return activeTrack;
    }
  }

  const sameTypeTrack = state.tracks.find((track) => {
    if (track.type !== targetKind) {
      return false;
    }
    if (targetKind === "video") {
      return getTrackMediaKind(track) === "video";
    }
    return true;
  });

  if (sameTypeTrack) {
    return sameTypeTrack;
  }

  if (targetKind === "video") {
    return addTrack("video", { mediaKind: "video" });
  }

  return addTrack(targetKind);
}

function getTrackEnd(track) {
  if (!track.clips.length) {
    return 0;
  }
  return track.clips.reduce((max, clip) => Math.max(max, clip.timelineStart + getClipEffectiveDuration(clip)), 0);
}

async function buildProjectSavePayload() {
  const tracks = [];

  for (const track of state.tracks) {
    const clipList = [];
    for (const clip of track.clips) {
      const sourceDataUrl = await sourceUrlToDataUrl(clip.sourceUrl);
      clipList.push({
        ...clip,
        sourceDataUrl
      });
    }

    tracks.push({
      ...track,
      mediaKind: getTrackMediaKindFromModel(track),
      clips: clipList
    });
  }

  return {
    format: "studio-imp-project",
    version: 1,
    savedAt: new Date().toISOString(),
    pixelsPerSecond,
    playback: {
      timelineTime: state.playback.timelineTime || 0
    },
    active: {
      trackId: state.activeTrackId,
      clipId: state.activeClipId,
      textTrackId: state.activeTextTrackId,
      textClipId: state.activeTextClipId
    },
    tracks,
    textTracks: state.textTracks,
    textClips: state.textClips,
    copiedTextClip: state.copiedTextClip
  };
}

async function saveProjectToFile() {
  if (state.isExporting) {
    return;
  }

  if (!hasTimelineContent()) {
    setExportStatus("No hay contenido para guardar");
    return;
  }

  try {
    setExportStatus("Guardando proyecto...");
    const payload = await buildProjectSavePayload();
    const blob = new Blob([JSON.stringify(payload)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `studio-imp-project-${getTimestampForFilename()}.iaimp`;
    link.click();
    URL.revokeObjectURL(url);
    setExportStatus("Proyecto guardado");
  } catch {
    setExportStatus("Error al guardar proyecto");
  }
}

function ensureLoadedProjectBaseStructure(projectData) {
  if (!projectData || typeof projectData !== "object") {
    throw new Error("PROJECT_INVALID");
  }

  if (!Array.isArray(projectData.tracks) || !Array.isArray(projectData.textTracks) || !Array.isArray(projectData.textClips)) {
    throw new Error("PROJECT_INVALID");
  }
}

async function hydrateLoadedTrackClip(clip) {
  const sourceDataUrl = clip.sourceDataUrl || "";
  if (!sourceDataUrl || typeof sourceDataUrl !== "string") {
    throw new Error("PROJECT_MEDIA_MISSING");
  }

  const blob = await dataUrlToBlob(sourceDataUrl);
  const objectUrl = URL.createObjectURL(blob);
  return {
    ...clip,
    sourceUrl: objectUrl,
    sourceDataUrl: undefined
  };
}

async function openProjectFromObject(projectData) {
  ensureLoadedProjectBaseStructure(projectData);

  if (state.playback.isTimelinePlaying) {
    stopTimelinePlayback();
  }

  resetProjectMediaPlayers();
  cleanupClipSourceUrls(state.tracks);

  const restoredTracks = [];
  for (const rawTrack of projectData.tracks) {
    const restoredClips = [];
    const rawClips = Array.isArray(rawTrack.clips) ? rawTrack.clips : [];
    for (const clip of rawClips) {
      const restoredClip = await hydrateLoadedTrackClip(clip);
      restoredClips.push(restoredClip);
    }

    const mediaKind = rawTrack.type === "video"
      ? rawTrack.mediaKind === "image"
        ? "image"
        : "video"
      : rawTrack.type;

    restoredTracks.push({
      ...rawTrack,
      mediaKind,
      clips: restoredClips
    });
  }

  state.tracks = restoredTracks;
  state.textTracks = Array.isArray(projectData.textTracks) ? projectData.textTracks : [];
  state.textClips = Array.isArray(projectData.textClips) ? projectData.textClips : [];
  state.copiedTextClip = projectData.copiedTextClip || null;

  ensureTextTracks();

  const loadedActiveTrackId = projectData.active && projectData.active.trackId;
  const loadedActiveClipId = projectData.active && projectData.active.clipId;
  const loadedActiveTextTrackId = projectData.active && projectData.active.textTrackId;
  const loadedActiveTextClipId = projectData.active && projectData.active.textClipId;

  state.activeTrackId = getTrackById(loadedActiveTrackId)
    ? loadedActiveTrackId
    : state.tracks[0]
      ? state.tracks[0].id
      : null;

  state.activeClipId = getClipById(loadedActiveClipId) ? loadedActiveClipId : null;

  state.activeTextTrackId = getTextTrackById(loadedActiveTextTrackId)
    ? loadedActiveTextTrackId
    : state.textTracks[0].id;

  state.activeTextClipId = getTextClipById(loadedActiveTextClipId) ? loadedActiveTextClipId : null;

  state.previewClipId = state.activeClipId;
  state.previewAudioClipId = null;

  pixelsPerSecond = clamp(Number(projectData.pixelsPerSecond) || 80, 40, 220);
  timelineZoom.value = String(pixelsPerSecond);

  const loadedTime =
    projectData.playback && Number.isFinite(projectData.playback.timelineTime)
      ? projectData.playback.timelineTime
      : 0;
  state.playback.timelineTime = clamp(loadedTime, 0, getProjectDuration());

  state.history.undoStack = [];
  state.history.redoStack = [];

  renderTimeline();
  renderMediaBin();
  renderTextInspector();
  renderKeyframes();
  renderTextLayer();

  if (state.activeClipId) {
    selectClip(state.activeClipId);
  } else {
    mediaName.textContent = "Sin archivo cargado";
    activeClipInfo.textContent = "Sin clip seleccionado";
    videoPreview.removeAttribute("src");
    videoPreview.load();
    imagePreview.removeAttribute("src");
    fadeOverlay.style.opacity = "0";
    updateTransport();
  }

  setTimelineTime(state.playback.timelineTime, { forceSeek: true });
  pushHistorySnapshot();
}

async function openProjectFromFile(file) {
  const text = await file.text();
  const data = JSON.parse(text);
  await openProjectFromObject(data);
}

function getMediaDuration(file, type) {
  if (type === "image") {
    return Promise.resolve(5);
  }

  return new Promise((resolve) => {
    const element = document.createElement(type === "audio" ? "audio" : "video");
    const src = URL.createObjectURL(file);

    const onDone = () => {
      const d = Number.isFinite(element.duration) ? element.duration : 0;
      URL.revokeObjectURL(src);
      resolve(Math.max(0.01, d || 10));
    };

    element.preload = "metadata";
    element.src = src;
    element.addEventListener("loadedmetadata", onDone, { once: true });
    element.addEventListener("error", onDone, { once: true });
  });
}

function createClip(file, type, duration, timelineStart) {
  return {
    id: uid(),
    type,
    name: file.name,
    sourceUrl: URL.createObjectURL(file),
    duration,
    timelineStart,
    trimStart: 0,
    trimEnd: duration,
    filter: {
      brightness: 100,
      contrast: 100,
      saturation: 100,
      sepia: 0,
      hueRotate: 0,
      grayscale: 0
    },
    fades: {
      videoFadeIn: 1,
      videoFadeOut: 1,
      audioFadeIn: 1,
      audioFadeOut: 1
    },
    textTracks: [],
    baseVolume: 1,
    audioKeyframes: []
  };
}

function selectTrack(trackId) {
  state.activeTrackId = trackId;
  renderTimeline();
}

function syncClipToInspector(clip) {
  trimStartInput.value = clip.trimStart.toFixed(2);
  trimEndInput.value = clip.trimEnd.toFixed(2);

  brightnessInput.value = clip.filter.brightness;
  contrastInput.value = clip.filter.contrast;
  saturationInput.value = clip.filter.saturation;
  baseVolumeInput.value = clip.baseVolume;

  videoFadeInInput.value = clip.fades.videoFadeIn;
  videoFadeOutInput.value = clip.fades.videoFadeOut;
  audioFadeInInput.value = clip.fades.audioFadeIn;
  audioFadeOutInput.value = clip.fades.audioFadeOut;
}

function applyFiltersForClip(clip) {
  const f = clip.filter;
  const filterString = `brightness(${f.brightness}%) contrast(${f.contrast}%) saturate(${f.saturation}%) sepia(${f.sepia}%) hue-rotate(${f.hueRotate}deg) grayscale(${f.grayscale}%)`;
  videoPreview.style.filter = filterString;
  imagePreview.style.filter = filterString;
}

function setPreviewMode(mode) {
  if (mode === "image") {
    imagePreview.style.display = "block";
    videoPreview.style.display = "none";
    videoPreview.pause();
    return;
  }

  imagePreview.style.display = "none";
  videoPreview.style.display = "block";
}

function selectClip(clipId) {
  const found = getClipById(clipId);
  if (!found) {
    return;
  }

  state.lastSelectionKind = "media";
  state.activeClipId = clipId;
  state.previewClipId = clipId;
  state.activeTrackId = found.track.id;
  state.playback.timelineTime = found.clip.timelineStart;

  mediaName.textContent = found.clip.name;
  activeClipInfo.textContent = `Pista ${found.track.name} | ${found.clip.type.toUpperCase()} | Duracion ${found.clip.duration.toFixed(2)}s`;

  if (found.clip.type === "image") {
    setPreviewMode("image");
    if (imagePreview.src !== found.clip.sourceUrl) {
      imagePreview.src = found.clip.sourceUrl;
    }
    fadeOverlay.style.opacity = "0";
  } else {
    setPreviewMode("video");
    if (videoPreview.src !== found.clip.sourceUrl) {
      videoPreview.src = found.clip.sourceUrl;
    }
    videoPreview.currentTime = found.clip.trimStart;
  }

  syncClipToInspector(found.clip);
  applyFiltersForClip(found.clip);
  renderTextInspector();
  renderKeyframes();
  renderTimeline();
  renderMediaBin();
  updateTransport();
}

function getActiveClipRef() {
  if (!state.activeClipId) {
    return null;
  }
  return getClipById(state.activeClipId);
}

function removeMediaClipById(clipId) {
  if (!clipId) {
    return false;
  }

  const found = getClipById(clipId);
  if (!found || found.track.locked) {
    return false;
  }

  pushHistorySnapshot();

  found.track.clips = found.track.clips.filter((item) => item.id !== clipId);

  if (found.clip.type === "audio" && timelineAudioPlayers.has(clipId)) {
    const player = timelineAudioPlayers.get(clipId);
    player.pause();
    timelineAudioPlayers.delete(clipId);
  }

  if (isBlobUrl(found.clip.sourceUrl)) {
    URL.revokeObjectURL(found.clip.sourceUrl);
  }

  if (state.previewClipId === clipId) {
    state.previewClipId = null;
  }

  const wasActive = state.activeClipId === clipId;
  if (wasActive) {
    state.activeClipId = null;
  }

  const remaining = getAllClips();
  if (wasActive && remaining.length) {
    selectClip(remaining[0].id);
    return true;
  }

  if (!remaining.length) {
    state.activeClipId = null;
    state.previewClipId = null;
    mediaName.textContent = "Sin archivo cargado";
    activeClipInfo.textContent = "Sin clip seleccionado";
    videoPreview.pause();
    videoPreview.removeAttribute("src");
    videoPreview.load();
    imagePreview.removeAttribute("src");
    fadeOverlay.style.opacity = "0";
  }

  renderTimeline();
  renderMediaBin();
  renderKeyframes();
  renderTextLayer();
  updateTransport();
  return true;
}

function removeActiveTextClip() {
  const activeText = getTextClipById(state.activeTextClipId);
  if (!activeText) {
    return false;
  }

  const track = getTextTrackById(activeText.trackId);
  if (track && track.locked) {
    return false;
  }

  pushHistorySnapshot();
  state.textClips = state.textClips.filter((item) => item.id !== activeText.id);
  if (state.activeTextClipId === activeText.id) {
    state.activeTextClipId = state.textClips.length ? state.textClips[0].id : null;
  }

  renderTextInspector();
  renderTextLayer();
  renderTimeline();
  return true;
}

function deleteCurrentSelection() {
  let deleted = false;

  if (state.lastSelectionKind === "text") {
    deleted = removeActiveTextClip();
    if (!deleted) {
      deleted = removeMediaClipById(state.activeClipId);
    }
  } else {
    deleted = removeMediaClipById(state.activeClipId);
    if (!deleted) {
      deleted = removeActiveTextClip();
    }
  }

  if (deleted) {
    setExportStatus("Elemento eliminado");
  }
}

function setPreset(name) {
  const active = getActiveClipRef();
  if (!active) {
    return;
  }

  const presets = {
    none: { brightness: 100, contrast: 100, saturation: 100, sepia: 0, hueRotate: 0, grayscale: 0 },
    cinematicWarm: { brightness: 105, contrast: 125, saturation: 115, sepia: 14, hueRotate: -8, grayscale: 0 },
    tealOrange: { brightness: 105, contrast: 130, saturation: 125, sepia: 10, hueRotate: 12, grayscale: 0 },
    monoNoir: { brightness: 100, contrast: 145, saturation: 0, sepia: 0, hueRotate: 0, grayscale: 35 }
  };

  active.clip.filter = { ...presets[name] };
  syncClipToInspector(active.clip);
  applyFiltersForClip(active.clip);
}

function updateTransport() {
  const projectDuration = getProjectDuration();
  const projectWidthPx = getProjectWidthPx();
  const totalCanvasWidthPx = projectWidthPx + TRACK_LABEL_WIDTH_PX;
  if (!projectDuration) {
    timeDisplay.textContent = "00:00 / 00:00";
    playhead.value = 0;
    renderRuler(totalCanvasWidthPx, TRACK_LABEL_WIDTH_PX);
    timelinePlayheadLine.style.left = `${TRACK_LABEL_WIDTH_PX}px`;
    return;
  }

  const t = clamp(state.playback.timelineTime, 0, projectDuration);
  timeDisplay.textContent = `${formatTime(t)} / ${formatTime(projectDuration)}`;
  playhead.value = projectDuration ? (t / projectDuration) * 100 : 0;

  const x = TRACK_LABEL_WIDTH_PX + t * pixelsPerSecond;
  renderRuler(totalCanvasWidthPx, TRACK_LABEL_WIDTH_PX);
  timelinePlayheadLine.style.left = `${x}px`;
}

function getVolumeAtTime(clip, time) {
  if (!clip.audioKeyframes.length) {
    return clip.baseVolume;
  }

  const sorted = [...clip.audioKeyframes].sort((a, b) => a.time - b.time);
  if (time <= sorted[0].time) {
    return sorted[0].volume;
  }
  if (time >= sorted[sorted.length - 1].time) {
    return sorted[sorted.length - 1].volume;
  }

  for (let i = 0; i < sorted.length - 1; i += 1) {
    const current = sorted[i];
    const next = sorted[i + 1];
    if (time >= current.time && time <= next.time) {
      const range = Math.max(0.001, next.time - current.time);
      const ratio = (time - current.time) / range;
      return current.volume + (next.volume - current.volume) * ratio;
    }
  }

  return clip.baseVolume;
}

function updateFadeVisualAndAudio() {
  const preview = getPreviewClipRef();
  if (!preview) {
    fadeOverlay.style.opacity = "0";
    videoPreview.volume = 0;
    return;
  }

  const track = preview.track;
  const clip = preview.clip;
  const isImageClip = clip.type === "image";
  const t = isImageClip
    ? clip.trimStart + clamp(state.playback.timelineTime - clip.timelineStart, 0, getClipEffectiveDuration(clip))
    : videoPreview.currentTime;
  const start = clip.trimStart;
  const end = clip.trimEnd;
  const timeFromStart = Math.max(0, t - start);
  const timeToEnd = Math.max(0, end - t);

  let blackOpacity = 0;
  if (clip.fades.videoFadeIn > 0 && timeFromStart < clip.fades.videoFadeIn) {
    blackOpacity = Math.max(blackOpacity, 1 - timeFromStart / clip.fades.videoFadeIn);
  }
  if (clip.fades.videoFadeOut > 0 && timeToEnd < clip.fades.videoFadeOut) {
    blackOpacity = Math.max(blackOpacity, 1 - timeToEnd / clip.fades.videoFadeOut);
  }
  fadeOverlay.style.opacity = clamp(blackOpacity, 0, 1).toFixed(3);

  const keyframeVolume = getVolumeAtTime(clip, t);
  let fadeMultiplier = 1;
  if (clip.fades.audioFadeIn > 0 && timeFromStart < clip.fades.audioFadeIn) {
    fadeMultiplier *= timeFromStart / clip.fades.audioFadeIn;
  }
  if (clip.fades.audioFadeOut > 0 && timeToEnd < clip.fades.audioFadeOut) {
    fadeMultiplier *= timeToEnd / clip.fades.audioFadeOut;
  }
  const trackAudible = isTrackAudible(track);
  if (isImageClip) {
    videoPreview.volume = 0;
  } else {
    videoPreview.volume = trackAudible ? clamp(keyframeVolume * fadeMultiplier, 0, 1) : 0;
  }

  if (t >= end) {
    if (isImageClip) {
      return;
    }
    if (state.playback.isTimelinePlaying) {
      return;
    }
    videoPreview.currentTime = start;
    videoPreview.pause();
  }
}

function renderTextLayer() {
  textLayer.innerHTML = "";
  const currentTime = state.playback.timelineTime || 0;

  state.textClips.forEach((clip) => {
    const end = clip.start + clip.duration;
    if (currentTime < clip.start || currentTime > end) {
      return;
    }

    const el = document.createElement("div");
    el.className = "overlay-text";
    el.textContent = clip.text;
    el.style.left = `${clip.x}%`;
    el.style.top = `${clip.y}%`;
    el.style.fontSize = `${clip.size}px`;
    el.style.color = clip.color;
    el.style.fontFamily = `"${clip.fontFamily || DEFAULT_TEXT_FONT}", sans-serif`;

    const progress = clamp((currentTime - clip.start) / Math.max(0.001, clip.duration), 0, 1);
    const entryRatio = Math.min(1, progress / 0.2);
    const animation = clip.animation || "none";
    if (animation === "fade") {
      el.style.opacity = String(entryRatio);
    } else if (animation === "slideUp") {
      const yOffset = (1 - entryRatio) * 26;
      el.style.opacity = String(entryRatio);
      el.style.transform = `translate(-50%, calc(-50% + ${yOffset}px))`;
    } else if (animation === "zoomIn") {
      const scale = 0.72 + 0.28 * entryRatio;
      el.style.opacity = String(entryRatio);
      el.style.transform = `translate(-50%, -50%) scale(${scale})`;
    }

    el.dataset.id = clip.id;
    if (state.activeTextClipId === clip.id) {
      el.style.outline = "2px solid #006633";
    }
    textLayer.appendChild(el);
  });
}

function setTimelineTime(projectTime, options = {}) {
  const { forceSeek = true, autoPlay = false } = options;
  const projectDuration = getProjectDuration();
  const safeTime = clamp(projectTime, 0, projectDuration);
  state.playback.timelineTime = safeTime;

  const resolved = resolveTimelineClip(safeTime);
  if (!resolved) {
    fadeOverlay.style.opacity = "1";
    if (!state.playback.isTimelinePlaying) {
      videoPreview.pause();
    }
    updateTransport();
    renderTextLayer();
    if (state.playback.isTimelinePlaying) {
      syncTimelineAudio(safeTime);
    } else {
      stopAllTimelineAudio();
    }
    return;
  }

  const isImageClip = resolved.clip.type === "image";
  const sourceChanged = isImageClip
    ? imagePreview.src !== resolved.clip.sourceUrl
    : videoPreview.src !== resolved.clip.sourceUrl;
  state.previewClipId = resolved.clip.id;

  if (isImageClip) {
    setPreviewMode("image");
    if (sourceChanged) {
      imagePreview.src = resolved.clip.sourceUrl;
    }

    applyFiltersForClip(resolved.clip);
    updateFadeVisualAndAudio();
    updateTransport();
    renderTextLayer();

    if (state.playback.isTimelinePlaying) {
      syncTimelineAudio(safeTime);
    } else {
      stopAllTimelineAudio();
    }
    return;
  }

  setPreviewMode("video");
  if (sourceChanged) {
    videoPreview.src = resolved.clip.sourceUrl;
  }

  const drift = Math.abs((videoPreview.currentTime || 0) - resolved.localTime);
  const seekTolerance = IS_MOBILE_DEVICE ? MOBILE_VIDEO_SEEK_TOLERANCE : 0.2;
  const needsSeek = forceSeek || sourceChanged || drift > seekTolerance;

  if (needsSeek) {
    try {
      videoPreview.currentTime = resolved.localTime;
    } catch {
      videoPreview.addEventListener(
        "loadedmetadata",
        () => {
          videoPreview.currentTime = resolved.localTime;
          if (autoPlay || state.playback.isTimelinePlaying) {
            videoPreview.play().catch(() => {});
          }
        },
        { once: true }
      );
    }
  }

  if ((autoPlay || state.playback.isTimelinePlaying) && videoPreview.paused) {
    videoPreview.play().catch(() => {});
  }

  applyFiltersForClip(resolved.clip);
  updateFadeVisualAndAudio();
  updateTransport();
  renderTextLayer();

  if (state.playback.isTimelinePlaying) {
    syncTimelineAudio(safeTime);
  } else {
    stopAllTimelineAudio();
  }
}

function getTimelineSecondsFromPointer(clientX) {
  const rect = timelineCanvas.getBoundingClientRect();
  const x = clientX - rect.left - TRACK_LABEL_WIDTH_PX;
  return Math.max(0, x / pixelsPerSecond);
}

function scrubTimelineFromPointer(clientX) {
  const targetSeconds = getTimelineSecondsFromPointer(clientX);
  setTimelineTime(targetSeconds);
}

function beginPlayheadDrag(clientX) {
  state.playheadDrag.active = true;
  if (state.playback.isTimelinePlaying) {
    stopTimelinePlayback();
  }
  scrubTimelineFromPointer(clientX);
}

function stopTimelinePlayback() {
  state.playback.isTimelinePlaying = false;
  state.playback.lastFrameMs = 0;
  state.playback.lastUiFrameMs = 0;
  if (state.playback.rafId) {
    cancelAnimationFrame(state.playback.rafId);
    state.playback.rafId = null;
  }
  videoPreview.pause();
  stopAllTimelineAudio();
}

function timelinePlaybackFrame(timestamp) {
  if (!state.playback.isTimelinePlaying) {
    return;
  }

  if (IS_MOBILE_DEVICE && state.playback.lastUiFrameMs && timestamp - state.playback.lastUiFrameMs < MOBILE_UI_FRAME_MS) {
    state.playback.rafId = requestAnimationFrame(timelinePlaybackFrame);
    return;
  }

  if (!state.playback.lastFrameMs) {
    state.playback.lastFrameMs = timestamp;
  }

  const deltaSeconds = (timestamp - state.playback.lastFrameMs) / 1000;
  state.playback.lastFrameMs = timestamp;

  const projectDuration = getProjectDuration();
  let nextTime = state.playback.timelineTime + deltaSeconds;

  // On mobile Safari, using the native player clock reduces jitter caused by frequent seeks.
  if (IS_MOBILE_DEVICE) {
    const preview = getPreviewClipRef();
    if (
      preview &&
      preview.clip.type === "video" &&
      Number.isFinite(videoPreview.currentTime) &&
      !videoPreview.paused
    ) {
      nextTime = clamp(
        preview.clip.timelineStart + (videoPreview.currentTime - preview.clip.trimStart),
        0,
        projectDuration
      );
    }
  }
  state.playback.lastUiFrameMs = timestamp;

  if (nextTime >= projectDuration) {
    setTimelineTime(projectDuration, { forceSeek: false });
    stopTimelinePlayback();
    return;
  }

  setTimelineTime(nextTime, { forceSeek: false, autoPlay: true });
  state.playback.rafId = requestAnimationFrame(timelinePlaybackFrame);
}

function startTimelinePlayback() {
  const projectDuration = getProjectDuration();
  if (!projectDuration) {
    return;
  }

  if (state.playback.timelineTime >= projectDuration) {
    state.playback.timelineTime = 0;
  }

  state.playback.isTimelinePlaying = true;
  state.playback.lastFrameMs = 0;
  setTimelineTime(state.playback.timelineTime, { forceSeek: true, autoPlay: true });
  syncTimelineAudio(state.playback.timelineTime);
  state.playback.rafId = requestAnimationFrame(timelinePlaybackFrame);
}

function getExportProfile() {
  const preset = exportPreset ? exportPreset.value : "landscape";
  if (preset === "square") {
    return { id: "square", width: 1200, height: 1200, label: "1:1" };
  }
  if (preset === "vertical") {
    return { id: "vertical", width: 1080, height: 1920, label: "9:16" };
  }
  return { id: "landscape", width: 1920, height: 1080, label: "16:9" };
}

function getExportRuntimeConfig(profile) {
  if (!IS_MOBILE_DEVICE) {
    return {
      width: profile.width,
      height: profile.height,
      fps: 30,
      videoBitsPerSecond: 16_000_000,
      audioBitsPerSecond: 320_000,
      modeLabel: "Calidad alta"
    };
  }

  const maxLongEdge = 960;
  const longEdge = Math.max(profile.width, profile.height);
  const scale = longEdge > maxLongEdge ? maxLongEdge / longEdge : 1;

  return {
    width: Math.max(540, Math.round(profile.width * scale)),
    height: Math.max(540, Math.round(profile.height * scale)),
    fps: 20,
    videoBitsPerSecond: 3_500_000,
    audioBitsPerSecond: 128_000,
    modeLabel: "Modo movil fluido"
  };
}

function getExportColorProfile() {
  const preset = exportColorPreset ? exportColorPreset.value : "neutral";
  if (preset === "reels") {
    return {
      id: "reels",
      label: "Reels Boost",
      filter: "brightness(1.06) contrast(1.16) saturate(1.22)"
    };
  }
  if (preset === "tiktok") {
    return {
      id: "tiktok",
      label: "TikTok Punch",
      filter: "brightness(1.04) contrast(1.2) saturate(1.28)"
    };
  }
  if (preset === "youtube") {
    return {
      id: "youtube",
      label: "YouTube Clean",
      filter: "brightness(1.02) contrast(1.1) saturate(1.12)"
    };
  }
  return {
    id: "neutral",
    label: "Neutral",
    filter: "none"
  };
}

function getBestExportMimeType() {
  const candidates = [
    "video/mp4;codecs=avc1.42E01E,mp4a.40.2",
    "video/mp4",
    "video/webm;codecs=vp9,opus",
    "video/webm"
  ];

  for (const type of candidates) {
    if (MediaRecorder.isTypeSupported(type)) {
      return type;
    }
  }
  return "";
}

function drawTextLayerOnCanvas(ctx, width, height, time) {
  state.textClips.forEach((clip) => {
    const end = clip.start + clip.duration;
    if (time < clip.start || time > end) {
      return;
    }

    const progress = clamp((time - clip.start) / Math.max(0.001, clip.duration), 0, 1);
    const entryRatio = Math.min(1, progress / 0.2);
    const animation = clip.animation || "none";

    const x = (clip.x / 100) * width;
    const y = (clip.y / 100) * height;
    let drawY = y;
    let scale = 1;
    let alpha = 1;

    if (animation === "fade") {
      alpha = entryRatio;
    } else if (animation === "slideUp") {
      drawY = y + (1 - entryRatio) * 26;
      alpha = entryRatio;
    } else if (animation === "zoomIn") {
      scale = 0.72 + 0.28 * entryRatio;
      alpha = entryRatio;
    }

    ctx.save();
    ctx.translate(x, drawY);
    ctx.scale(scale, scale);
    ctx.globalAlpha = alpha;
    ctx.fillStyle = clip.color || "#ffffff";
    ctx.font = `700 ${clip.size || 42}px "${clip.fontFamily || DEFAULT_TEXT_FONT}", sans-serif`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";

    const lines = String(clip.text || "").split("\n");
    const lineHeight = Math.max(18, (clip.size || 42) * 1.2);
    const startY = -((lines.length - 1) * lineHeight) / 2;

    lines.forEach((line, index) => {
      const yOffset = startY + index * lineHeight;
      ctx.strokeStyle = "rgba(0,0,0,0.45)";
      ctx.lineWidth = Math.max(1, (clip.size || 42) * 0.08);
      ctx.strokeText(line, 0, yOffset);
      ctx.fillText(line, 0, yOffset);
    });

    ctx.restore();
  });
}

async function waitForTimelineStop(maxWaitMs, onTick) {
  await new Promise((resolve, reject) => {
    const start = Date.now();
    const timer = setInterval(() => {
      if (typeof onTick === "function") {
        onTick();
      }

      if (!state.playback.isTimelinePlaying) {
        clearInterval(timer);
        resolve();
        return;
      }

      if (Date.now() - start > maxWaitMs) {
        clearInterval(timer);
        reject(new Error("EXPORT_TIMEOUT"));
      }
    }, 100);
  });
}

async function exportTimeline() {
  if (state.isExporting) {
    return;
  }

  if (!hasTimelineContent()) {
    setExportStatus("Sin clips para exportar");
    return;
  }

  if (state.playback.isTimelinePlaying) {
    stopTimelinePlayback();
  }

  const mimeType = getBestExportMimeType();
  if (!mimeType) {
    setExportStatus("Export no soportado en este navegador");
    return;
  }

  const profile = getExportProfile();
  const runtimeConfig = getExportRuntimeConfig(profile);
  const colorProfile = getExportColorProfile();
  const exportWidth = runtimeConfig.width;
  const exportHeight = runtimeConfig.height;
  const exportFps = runtimeConfig.fps;
  const videoBitsPerSecond = runtimeConfig.videoBitsPerSecond;
  const audioBitsPerSecond = runtimeConfig.audioBitsPerSecond;
  const projectDuration = Math.max(1, getProjectDuration());
  const maxWaitMs = Math.ceil(projectDuration * 1000 + 20000);

  let progressTimer = null;
  let paintTimer = null;
  let exportStartMs = 0;

  try {
    setExportingState(true);
    setExportStatus("Exportando...");
    setExportOverlayProgress(
      0,
      `Rendering ${profile.label} ${exportWidth}x${exportHeight} | ${colorProfile.label} | ${runtimeConfig.modeLabel}`
    );
    exportStartMs = Date.now();
    stopAllTimelineAudio();
    state.playback.timelineTime = 0;
    setTimelineTime(0, { forceSeek: true });

    const exportCanvas = document.createElement("canvas");
    exportCanvas.width = exportWidth;
    exportCanvas.height = exportHeight;
    const ctx = exportCanvas.getContext("2d", { alpha: false });
    if (!ctx) {
      throw new Error("CANVAS_CONTEXT");
    }

    const frameDelay = Math.max(16, Math.round(1000 / exportFps));

    const paintFrame = () => {
      ctx.fillStyle = "#000000";
      ctx.fillRect(0, 0, exportWidth, exportHeight);

      const frameTime = state.playback.timelineTime || 0;
      const activeFrameClip = resolveTimelineClip(frameTime);

      if (activeFrameClip && activeFrameClip.clip.type === "image") {
        if (imagePreview.complete && imagePreview.naturalWidth > 0 && imagePreview.src === activeFrameClip.clip.sourceUrl) {
          ctx.filter = colorProfile.filter;
          const sourceW = imagePreview.naturalWidth;
          const sourceH = imagePreview.naturalHeight;
          const scale = Math.min(exportWidth / sourceW, exportHeight / sourceH);
          const drawW = sourceW * scale;
          const drawH = sourceH * scale;
          const drawX = (exportWidth - drawW) / 2;
          const drawY = (exportHeight - drawH) / 2;
          ctx.drawImage(imagePreview, drawX, drawY, drawW, drawH);
          ctx.filter = "none";
        }
      } else if (
        activeFrameClip &&
        videoPreview.readyState >= 2 &&
        videoPreview.videoWidth > 0 &&
        videoPreview.videoHeight > 0 &&
        videoPreview.src === activeFrameClip.clip.sourceUrl
      ) {
        ctx.filter = colorProfile.filter;
        const sourceW = videoPreview.videoWidth;
        const sourceH = videoPreview.videoHeight;
        const scale = Math.min(exportWidth / sourceW, exportHeight / sourceH);
        const drawW = sourceW * scale;
        const drawH = sourceH * scale;
        const drawX = (exportWidth - drawW) / 2;
        const drawY = (exportHeight - drawH) / 2;
        ctx.drawImage(videoPreview, drawX, drawY, drawW, drawH);
        ctx.filter = "none";
      }

      if (activeFrameClip) {
        const fadeOpacity = getVideoFadeOpacity(activeFrameClip.clip, activeFrameClip.localTime);
        if (fadeOpacity > 0) {
          ctx.save();
          ctx.globalAlpha = fadeOpacity;
          ctx.fillStyle = "#000000";
          ctx.fillRect(0, 0, exportWidth, exportHeight);
          ctx.restore();
        }
      }

      drawTextLayerOnCanvas(ctx, exportWidth, exportHeight, state.playback.timelineTime || 0);
      paintTimer = window.setTimeout(paintFrame, frameDelay);
    };

    paintFrame();

    const stream = exportCanvas.captureStream(exportFps);
    prepareExportAudioRouting();
    const { context, destination } = getExportAudioBus();
    await context.resume();
    destination.stream.getAudioTracks().forEach((track) => stream.addTrack(track));

    const chunks = [];
    const recorder = new MediaRecorder(stream, {
      mimeType,
      videoBitsPerSecond,
      audioBitsPerSecond
    });

    recorder.addEventListener("dataavailable", (event) => {
      if (event.data && event.data.size > 0) {
        chunks.push(event.data);
      }
    });

    const recorderDone = new Promise((resolve, reject) => {
      recorder.addEventListener("error", () => reject(new Error("RECORDER_ERROR")), { once: true });
      recorder.addEventListener("stop", resolve, { once: true });
    });

    progressTimer = setInterval(() => {
      const pct = Math.min(100, Math.floor((state.playback.timelineTime / projectDuration) * 100));
      const elapsedSec = (Date.now() - exportStartMs) / 1000;
      const eta = pct >= 2 ? (elapsedSec * (100 - pct)) / pct : projectDuration;
      const etaText = pct >= 100 ? "Tiempo restante: 0:00" : `Tiempo restante: ${formatEta(eta)}`;
      setExportStatus(
        `Exportando ${profile.label} ${exportWidth}x${exportHeight} | ${colorProfile.label}... ${pct}%`
      );
      setExportOverlayProgress(pct, null, etaText);
    }, 500);

    recorder.start(200);
    state.playback.timelineTime = 0;
    setTimelineTime(0, { forceSeek: true, autoPlay: false });
    startTimelinePlayback();
    await waitForTimelineStop(maxWaitMs);

    if (recorder.state !== "inactive") {
      recorder.stop();
    }
    await recorderDone;

    if (paintTimer) {
      clearTimeout(paintTimer);
      paintTimer = null;
    }

    if (progressTimer) {
      clearInterval(progressTimer);
      progressTimer = null;
    }

    if (!chunks.length) {
      throw new Error("EXPORT_EMPTY");
    }

    const blob = new Blob(chunks, { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    const extension = mimeType.includes("mp4") ? "mp4" : "webm";
    link.download = `studio-cut-export-${profile.id}-${colorProfile.id}-${exportWidth}x${exportHeight}.${extension}`;
    link.click();
    URL.revokeObjectURL(url);

    if (extension === "mp4") {
      setExportStatus(`Export MP4 ${profile.label} | ${colorProfile.label} completado`);
    } else {
      setExportStatus(
        `Export listo en WebM (${profile.label} | ${colorProfile.label}). MP4 no disponible en este navegador.`
      );
    }
  } catch (error) {
    if (progressTimer) {
      clearInterval(progressTimer);
    }
    if (paintTimer) {
      clearTimeout(paintTimer);
    }
    stopTimelinePlayback();
    if (error && error.message === "EXPORT_TIMEOUT") {
      setExportStatus("Export cancelado por timeout. Reduce duracion o divide en partes.");
      return;
    }
    setExportStatus("Error al exportar");
  } finally {
    if (progressTimer) {
      clearInterval(progressTimer);
    }
    if (paintTimer) {
      clearTimeout(paintTimer);
    }
    setExportingState(false);
  }
}

function createTextClipAt(time) {
  ensureTextTracks();
  pushHistorySnapshot();
  const targetTrackId = getTextTrackById(state.activeTextTrackId)
    ? state.activeTextTrackId
    : state.textTracks[0].id;
  const clip = {
    id: uid(),
    text: "Nuevo texto",
    trackId: targetTrackId,
    start: Math.max(0, time),
    duration: 5,
    x: 35,
    y: 30,
    size: 42,
    color: "#ffffff",
    fontFamily: DEFAULT_TEXT_FONT,
    animation: "none"
  };

  state.textClips.push(clip);
  state.lastSelectionKind = "text";
  state.activeTextTrackId = targetTrackId;
  state.activeTextClipId = clip.id;
  renderTextInspector();
  renderTextLayer();
  renderTimeline();
}

function copyActiveTextClip() {
  const active = getTextClipById(state.activeTextClipId);
  if (!active) {
    return;
  }

  state.copiedTextClip = {
    text: active.text,
    trackId: active.trackId,
    duration: active.duration,
    x: active.x,
    y: active.y,
    size: active.size,
    color: active.color,
    fontFamily: active.fontFamily || DEFAULT_TEXT_FONT,
    animation: active.animation || "none"
  };
}

function pasteCopiedTextClip() {
  if (!state.copiedTextClip) {
    return;
  }

  ensureTextTracks();

  pushHistorySnapshot();

  const targetTrackId = getTextTrackById(state.activeTextTrackId)
    ? state.activeTextTrackId
    : state.textTracks[0].id;

  const pasted = {
    id: uid(),
    ...state.copiedTextClip,
    trackId: targetTrackId,
    start: Math.max(0, state.playback.timelineTime)
  };

  state.textClips.push(pasted);
  state.lastSelectionKind = "text";
  state.activeTextTrackId = targetTrackId;
  state.activeTextClipId = pasted.id;
  renderTextInspector();
  renderTextLayer();
  renderTimeline();
}

function renderTextInspector() {
  ensureTextTracks();
  textItems.innerHTML = "";
  if (!state.textClips.length) {
    return;
  }

  state.textClips.forEach((clip) => {
    const container = document.createElement("div");
    container.className = "text-item";
    if (state.activeTextClipId === clip.id) {
      container.style.outline = "2px solid rgba(0, 102, 51, 0.55)";
    }

    container.addEventListener("click", (event) => {
      // Ignore clicks on interactive controls so select/inputs work normally.
      if (event.target.closest("textarea, input, select, button, option")) {
        return;
      }
      state.lastSelectionKind = "text";
      state.activeTextClipId = clip.id;
      renderTextInspector();
      renderTextLayer();
      renderTimeline();
    });

    const textArea = document.createElement("textarea");
    textArea.value = clip.text;
    textArea.addEventListener("input", (event) => {
      clip.text = event.target.value;
      renderTextLayer();
      renderTimeline();
    });

    const sizeInput = document.createElement("input");
    sizeInput.type = "range";
    sizeInput.min = "16";
    sizeInput.max = "96";
    sizeInput.value = String(clip.size);
    sizeInput.addEventListener("input", (event) => {
      clip.size = Number(event.target.value);
      renderTextLayer();
    });

    const colorInput = document.createElement("input");
    colorInput.type = "color";
    colorInput.value = clip.color;
    colorInput.addEventListener("input", (event) => {
      clip.color = event.target.value;
      renderTextLayer();
    });

    const fontSelect = document.createElement("select");
    fontSelect.innerHTML = TEXT_FONT_OPTIONS.map(
      (font) => `<option value="${font.value}">Fuente: ${font.label}</option>`
    ).join("");
    fontSelect.value = clip.fontFamily || DEFAULT_TEXT_FONT;
    fontSelect.addEventListener("change", (event) => {
      pushHistorySnapshot();
      clip.fontFamily = event.target.value;
      renderTextLayer();
    });

    const trackSelect = document.createElement("select");
    trackSelect.innerHTML = state.textTracks
      .map((track) => `<option value="${track.id}">Pista: ${track.name}</option>`)
      .join("");
    trackSelect.value = clip.trackId || state.textTracks[0].id;
    trackSelect.addEventListener("change", (event) => {
      const track = getTextTrackById(event.target.value);
      if (!track) {
        return;
      }
      pushHistorySnapshot();
      clip.trackId = track.id;
      state.activeTextTrackId = track.id;
      renderTimeline();
    });

    const animationSelect = document.createElement("select");
    animationSelect.innerHTML = `
      <option value="none">Animacion: Ninguna</option>
      <option value="fade">Animacion: Fade In</option>
      <option value="slideUp">Animacion: Slide Up</option>
      <option value="zoomIn">Animacion: Zoom In</option>
    `;
    animationSelect.value = clip.animation || "none";
    animationSelect.addEventListener("change", (event) => {
      pushHistorySnapshot();
      clip.animation = event.target.value;
      renderTextLayer();
    });

    const centerBtn = document.createElement("button");
    centerBtn.className = "secondary";
    centerBtn.textContent = "Centrar en Canvas";
    centerBtn.addEventListener("click", () => {
      pushHistorySnapshot();
      clip.x = 50;
      clip.y = 50;
      renderTextLayer();
      renderTextInspector();
    });

    const timeWrap = document.createElement("div");
    timeWrap.className = "row";

    const startInput = document.createElement("input");
    startInput.type = "number";
    startInput.min = "0";
    startInput.step = "0.1";
    startInput.value = String(clip.start.toFixed(2));
    startInput.addEventListener("input", (event) => {
      clip.start = Math.max(0, Number(event.target.value));
      renderTextLayer();
      renderTimeline();
    });

    const durationInput = document.createElement("input");
    durationInput.type = "number";
    durationInput.min = "0.5";
    durationInput.step = "0.1";
    durationInput.value = String(clip.duration.toFixed(2));
    durationInput.addEventListener("input", (event) => {
      clip.duration = Math.max(0.5, Number(event.target.value));
      renderTextLayer();
      renderTimeline();
    });

    const removeBtn = document.createElement("button");
    removeBtn.className = "danger";
    removeBtn.textContent = "Eliminar";
    removeBtn.addEventListener("click", () => {
      pushHistorySnapshot();
      state.textClips = state.textClips.filter((item) => item.id !== clip.id);
      if (state.activeTextClipId === clip.id) {
        state.activeTextClipId = state.textClips.length ? state.textClips[0].id : null;
      }
      renderTextInspector();
      renderTextLayer();
      renderTimeline();
    });

    timeWrap.appendChild(startInput);
    timeWrap.appendChild(durationInput);

    container.appendChild(textArea);
    container.appendChild(sizeInput);
    container.appendChild(colorInput);
    container.appendChild(fontSelect);
    container.appendChild(trackSelect);
    container.appendChild(animationSelect);
    container.appendChild(centerBtn);
    container.appendChild(timeWrap);
    container.appendChild(removeBtn);
    textItems.appendChild(container);
  });
}

function renderKeyframes() {
  keyframeList.innerHTML = "";
  const active = getActiveClipRef();
  if (!active) {
    return;
  }

  const sorted = [...active.clip.audioKeyframes].sort((a, b) => a.time - b.time);
  sorted.forEach((k, idx) => {
    const li = document.createElement("li");
    li.innerHTML = `<span>${idx + 1}. ${k.time.toFixed(2)}s -> ${k.volume.toFixed(2)}</span>`;
    const remove = document.createElement("button");
    remove.className = "danger";
    remove.textContent = "X";
    remove.addEventListener("click", () => {
      active.clip.audioKeyframes = active.clip.audioKeyframes.filter((item) => item !== k);
      renderKeyframes();
      renderTimeline();
    });
    li.appendChild(remove);
    keyframeList.appendChild(li);
  });
}

function renderRuler(canvasWidthPx, zeroX) {
  timelineRuler.innerHTML = "";

  const minSecond = 0;
  const maxSecond = Math.ceil((canvasWidthPx - zeroX) / pixelsPerSecond) + 1;

  for (let i = minSecond; i <= maxSecond; i += 1) {
    const x = zeroX + i * pixelsPerSecond;
    if (x < -2 || x > canvasWidthPx + 2) {
      continue;
    }

    const tick = document.createElement("div");
    tick.className = `ruler-tick ${i % 5 === 0 ? "major" : ""}`;
    tick.style.left = `${x}px`;
    timelineRuler.appendChild(tick);

    if (i % 5 === 0) {
      const label = document.createElement("div");
      label.className = "ruler-label";
      label.textContent = `${i}s`;
      label.style.left = `${x}px`;
      timelineRuler.appendChild(label);
    }
  }
}

function buildTrackLine(track, widthPx) {
  const line = document.createElement("div");
  line.className = `track-line ${track.type === "audio" ? "audio-line" : ""}`;
  if (track.type === "audio" && !isTrackAudible(track)) {
    line.classList.add("track-muted");
  }
  line.dataset.trackId = track.id;
  line.style.width = `${widthPx}px`;

  if (state.activeTrackId === track.id) {
    line.classList.add("active-track");
  }

  track.clips.forEach((clip) => {
    const clipEl = document.createElement("div");
    clipEl.className = `clip-block ${clip.type}`;

    if (state.activeClipId === clip.id) {
      clipEl.classList.add("active-clip");
    }

    const leftPx = clip.timelineStart * pixelsPerSecond;
    const widthClipPx = getClipEffectiveDuration(clip) * pixelsPerSecond;

    clipEl.style.left = `${leftPx}px`;
    clipEl.style.width = `${Math.max(24, widthClipPx)}px`;
    clipEl.textContent = clip.name;
    clipEl.dataset.clipId = clip.id;
    clipEl.dataset.trackId = track.id;

    if (state.drag.clipId === clip.id) {
      clipEl.classList.add("dragging");
    }

    if (clip.type === "audio") {
      clip.audioKeyframes.forEach((k) => {
        const dot = document.createElement("div");
        dot.className = "key-dot";
        const x = leftPx + k.time * pixelsPerSecond;
        const y = (1 - k.volume) * 100;
        dot.style.left = `${x}px`;
        dot.style.top = `${y}%`;
        line.appendChild(dot);
      });
    }

    line.appendChild(clipEl);
  });

  return line;
}

function buildTextTrackLine(track, widthPx) {
  const line = document.createElement("div");
  line.className = "track-line";
  line.dataset.trackId = track.id;
  line.dataset.kind = "text-track";
  line.style.width = `${widthPx}px`;

  if (state.activeTextTrackId === track.id) {
    line.classList.add("active-track");
  }

  if (track.locked) {
    line.classList.add("track-muted");
  }

  state.textClips
    .filter((clip) => clip.trackId === track.id)
    .forEach((clip) => {
    const clipEl = document.createElement("div");
    clipEl.className = "clip-block text";
    if (state.activeTextClipId === clip.id) {
      clipEl.classList.add("active-clip");
    }

    const leftPx = clip.start * pixelsPerSecond;
    const widthClipPx = clip.duration * pixelsPerSecond;
    clipEl.style.left = `${leftPx}px`;
    clipEl.style.width = `${Math.max(24, widthClipPx)}px`;
    clipEl.textContent = clip.text;
    clipEl.dataset.textClipId = clip.id;
    clipEl.dataset.kind = "text";

    line.appendChild(clipEl);
    });

  return line;
}

function renderTimeline() {
  ensureTextTracks();
  videoTracks.innerHTML = "";
  imageTracks.innerHTML = "";
  audioTracks.innerHTML = "";
  textTracksTimeline.innerHTML = "";

  const projectDuration = getProjectDuration();
  const widthPx = getProjectWidthPx();
  const totalCanvasWidthPx = widthPx + TRACK_LABEL_WIDTH_PX;
  timelineCanvas.style.width = `${totalCanvasWidthPx}px`;
  renderRuler(totalCanvasWidthPx, TRACK_LABEL_WIDTH_PX);

  const videos = state.tracks.filter(
    (track) => track.type === "video" && getTrackMediaKind(track) === "video"
  );
  const images = state.tracks.filter(
    (track) => track.type === "video" && getTrackMediaKind(track) === "image"
  );
  const audios = state.tracks.filter((track) => track.type === "audio");

  videos.forEach((track) => {
    const wrapper = document.createElement("div");
    wrapper.className = "timeline-track";

    const label = document.createElement("div");
    label.className = "track-label";

    const name = document.createElement("span");
    name.className = "track-name";
    name.textContent = track.name;
    name.addEventListener("click", () => selectTrack(track.id));

    const remove = document.createElement("button");
    remove.className = "track-remove";
    remove.textContent = "Eliminar";
    remove.addEventListener("click", () => removeTrack(track.id));

    const visibleBtn = document.createElement("button");
    visibleBtn.className = `track-btn ${track.visible ? "active" : ""}`;
    visibleBtn.textContent = "VIS";
    visibleBtn.addEventListener("click", () => toggleTrackProperty(track.id, "visible"));

    const lockBtn = document.createElement("button");
    lockBtn.className = `track-btn ${track.locked ? "active" : ""}`;
    lockBtn.textContent = "LOCK";
    lockBtn.addEventListener("click", () => toggleTrackProperty(track.id, "locked"));

    label.appendChild(name);
    label.appendChild(visibleBtn);
    label.appendChild(lockBtn);
    label.appendChild(remove);

    const line = buildTrackLine(track, widthPx);

    wrapper.appendChild(label);
    wrapper.appendChild(line);
    videoTracks.appendChild(wrapper);
  });

  images.forEach((track) => {
    const wrapper = document.createElement("div");
    wrapper.className = "timeline-track";

    const label = document.createElement("div");
    label.className = "track-label";

    const name = document.createElement("span");
    name.className = "track-name";
    name.textContent = track.name;
    name.addEventListener("click", () => selectTrack(track.id));

    const remove = document.createElement("button");
    remove.className = "track-remove";
    remove.textContent = "Eliminar";
    remove.addEventListener("click", () => removeTrack(track.id));

    const visibleBtn = document.createElement("button");
    visibleBtn.className = `track-btn ${track.visible ? "active" : ""}`;
    visibleBtn.textContent = "VIS";
    visibleBtn.addEventListener("click", () => toggleTrackProperty(track.id, "visible"));

    const lockBtn = document.createElement("button");
    lockBtn.className = `track-btn ${track.locked ? "active" : ""}`;
    lockBtn.textContent = "LOCK";
    lockBtn.addEventListener("click", () => toggleTrackProperty(track.id, "locked"));

    label.appendChild(name);
    label.appendChild(visibleBtn);
    label.appendChild(lockBtn);
    label.appendChild(remove);

    const line = buildTrackLine(track, widthPx);

    wrapper.appendChild(label);
    wrapper.appendChild(line);
    imageTracks.appendChild(wrapper);
  });

  audios.forEach((track) => {
    const wrapper = document.createElement("div");
    wrapper.className = "timeline-track";

    const label = document.createElement("div");
    label.className = "track-label";

    const name = document.createElement("span");
    name.className = "track-name";
    name.textContent = track.name;
    name.addEventListener("click", () => selectTrack(track.id));

    const remove = document.createElement("button");
    remove.className = "track-remove";
    remove.textContent = "Eliminar";
    remove.addEventListener("click", () => removeTrack(track.id));

    const muteBtn = document.createElement("button");
    muteBtn.className = `track-btn ${track.muted ? "active" : ""}`;
    muteBtn.textContent = "M";
    muteBtn.addEventListener("click", () => toggleTrackProperty(track.id, "muted"));

    const soloBtn = document.createElement("button");
    soloBtn.className = `track-btn ${track.solo ? "active" : ""}`;
    soloBtn.textContent = "S";
    soloBtn.addEventListener("click", () => toggleTrackProperty(track.id, "solo"));

    const lockBtn = document.createElement("button");
    lockBtn.className = `track-btn ${track.locked ? "active" : ""}`;
    lockBtn.textContent = "LOCK";
    lockBtn.addEventListener("click", () => toggleTrackProperty(track.id, "locked"));

    label.appendChild(name);
    label.appendChild(muteBtn);
    label.appendChild(soloBtn);
    label.appendChild(lockBtn);
    label.appendChild(remove);

    const line = buildTrackLine(track, widthPx);

    wrapper.appendChild(label);
    wrapper.appendChild(line);
    audioTracks.appendChild(wrapper);
  });

  state.textTracks.forEach((track) => {
    const textWrapper = document.createElement("div");
    textWrapper.className = "timeline-track";

    const textLabel = document.createElement("div");
    textLabel.className = "track-label";

    const name = document.createElement("span");
    name.className = "track-name";
    name.textContent = track.name;
    name.addEventListener("click", () => {
      state.activeTextTrackId = track.id;
      renderTimeline();
    });

    const lockBtn = document.createElement("button");
    lockBtn.className = `track-btn ${track.locked ? "active" : ""}`;
    lockBtn.textContent = "LOCK";
    lockBtn.addEventListener("click", () => {
      pushHistorySnapshot();
      track.locked = !track.locked;
      renderTimeline();
    });

    const remove = document.createElement("button");
    remove.className = "track-remove";
    remove.textContent = "Eliminar";
    remove.addEventListener("click", () => removeTextTrack(track.id));

    textLabel.appendChild(name);
    textLabel.appendChild(lockBtn);
    textLabel.appendChild(remove);

    const textLine = buildTextTrackLine(track, widthPx);
    textWrapper.appendChild(textLabel);
    textWrapper.appendChild(textLine);
    textTracksTimeline.appendChild(textWrapper);
  });

  updateTransport();
}

async function importFiles(fileList) {
  pushHistorySnapshot();
  for (const file of fileList) {
    const clipType = detectMediaType(file);
    const track = getOrCreateTargetTrackForClip(clipType);
    const duration = await getMediaDuration(file, clipType);
    const timelineStart = getTrackEnd(track);
    const clip = createClip(file, clipType, duration, timelineStart);
    track.clips.push(clip);

    if (!state.activeClipId) {
      selectClip(clip.id);
    }
  }

  renderTimeline();
  renderMediaBin();
}

function beginClipDrag(event, clipId, trackId) {
  const found = getClipById(clipId);
  if (!found) {
    return;
  }

  if (found.track.locked) {
    return;
  }

  const line = event.target.closest(".track-line");
  if (!line) {
    return;
  }

  const lineRect = line.getBoundingClientRect();
  const pointerSeconds = (event.clientX - lineRect.left) / pixelsPerSecond;
  const offset = pointerSeconds - found.clip.timelineStart;

  pushHistorySnapshot();
  state.drag.kind = "media";
  state.drag.clipId = clipId;
  state.drag.trackId = trackId;
  state.drag.pointerOffsetSeconds = offset;

  selectClip(clipId);
  renderTimeline();
}

function beginTextClipDrag(event, textClipId) {
  const clip = getTextClipById(textClipId);
  if (!clip) {
    return;
  }

  const sourceTrack = getTextTrackById(clip.trackId);
  if (sourceTrack && sourceTrack.locked) {
    return;
  }

  const line = event.target.closest(".track-line");
  if (!line) {
    return;
  }

  const lineRect = line.getBoundingClientRect();
  const pointerSeconds = (event.clientX - lineRect.left) / pixelsPerSecond;
  const offset = pointerSeconds - clip.start;

  pushHistorySnapshot();
  state.drag.kind = "text";
  state.drag.clipId = textClipId;
  state.drag.trackId = clip.trackId;
  state.drag.pointerOffsetSeconds = offset;
  state.lastSelectionKind = "text";
  state.activeTextTrackId = clip.trackId;
  state.activeTextClipId = textClipId;
  renderTextInspector();
  renderTextLayer();
  renderTimeline();
}

function onClipDragMove(event) {
  if (!state.drag.clipId) {
    return;
  }

  if (state.drag.kind === "text") {
    const clip = getTextClipById(state.drag.clipId);
    if (!clip) {
      return;
    }

    const lines = Array.from(textTracksTimeline.querySelectorAll('.track-line[data-kind="text-track"]'));
    if (!lines.length) {
      return;
    }

    let targetLine = lines.find((line) => {
      const lineRect = line.getBoundingClientRect();
      return event.clientY >= lineRect.top && event.clientY <= lineRect.bottom;
    });

    if (!targetLine) {
      targetLine = lines.find((line) => line.dataset.trackId === (clip.trackId || state.activeTextTrackId)) || lines[0];
    }

    const targetTrack = getTextTrackById(targetLine.dataset.trackId);
    if (targetTrack && targetTrack.locked) {
      return;
    }

    const rect = targetLine.getBoundingClientRect();
    const pointerSeconds = (event.clientX - rect.left) / pixelsPerSecond;
    clip.start = Math.max(0, pointerSeconds - state.drag.pointerOffsetSeconds);
    if (targetTrack) {
      clip.trackId = targetTrack.id;
      state.activeTextTrackId = targetTrack.id;
    }
    renderTimeline();
    renderTextLayer();
    renderTextInspector();

    if (event.clientX > rect.right - 30) {
      timelineScroll.scrollLeft += 20;
    } else if (event.clientX < rect.left + 30) {
      timelineScroll.scrollLeft -= 20;
    }

    return;
  }

  const found = getClipById(state.drag.clipId);
  const track = getTrackById(state.drag.trackId);
  if (!found || !track) {
    return;
  }

  if (track.locked) {
    return;
  }

  const line = document.querySelector(`.track-line[data-track-id="${track.id}"]`);
  if (!line) {
    return;
  }

  const rect = line.getBoundingClientRect();
  const pointerSeconds = (event.clientX - rect.left) / pixelsPerSecond;
  const nextStart = Math.max(0, pointerSeconds - state.drag.pointerOffsetSeconds);

  found.clip.timelineStart = nextStart;
  renderTimeline();

  if (event.clientX > rect.right - 30) {
    timelineScroll.scrollLeft += 20;
  } else if (event.clientX < rect.left + 30) {
    timelineScroll.scrollLeft -= 20;
  }
}

function endClipDrag() {
  if (!state.drag.clipId) {
    return;
  }

  state.drag.kind = null;
  state.drag.clipId = null;
  state.drag.trackId = null;
  state.drag.pointerOffsetSeconds = 0;
  renderTimeline();
}

mediaInput.addEventListener("change", async (event) => {
  const files = Array.from(event.target.files || []);
  if (!files.length) {
    return;
  }

  await importFiles(files);
  event.target.value = "";
});

addVideoTrack.addEventListener("click", () => {
  const track = addTrack("video");
  state.activeTrackId = track.id;
  renderTimeline();
});

addAudioTrack.addEventListener("click", () => {
  const track = addTrack("audio");
  state.activeTrackId = track.id;
  renderTimeline();
});

addImageMedia.addEventListener("click", () => {
  const track = addTrack("video", { mediaKind: "image" });
  state.activeTrackId = track.id;
  renderTimeline();
});

videoTracks.addEventListener("mousedown", (event) => {
  const clipEl = event.target.closest(".clip-block");
  if (!clipEl) {
    return;
  }
  beginClipDrag(event, clipEl.dataset.clipId, clipEl.dataset.trackId);
});

imageTracks.addEventListener("mousedown", (event) => {
  const clipEl = event.target.closest(".clip-block");
  if (!clipEl) {
    return;
  }
  beginClipDrag(event, clipEl.dataset.clipId, clipEl.dataset.trackId);
});

audioTracks.addEventListener("mousedown", (event) => {
  const clipEl = event.target.closest(".clip-block");
  if (!clipEl) {
    return;
  }
  beginClipDrag(event, clipEl.dataset.clipId, clipEl.dataset.trackId);
});

textTracksTimeline.addEventListener("mousedown", (event) => {
  const clipEl = event.target.closest('[data-kind="text"]');
  if (!clipEl) {
    return;
  }
  beginTextClipDrag(event, clipEl.dataset.textClipId);
});

videoTracks.addEventListener("click", (event) => {
  const clipEl = event.target.closest(".clip-block");
  const line = event.target.closest(".track-line");

  if (clipEl) {
    selectClip(clipEl.dataset.clipId);
    return;
  }
  if (line) {
    selectTrack(line.dataset.trackId);
  }
});

imageTracks.addEventListener("click", (event) => {
  const clipEl = event.target.closest(".clip-block");
  const line = event.target.closest(".track-line");

  if (clipEl) {
    selectClip(clipEl.dataset.clipId);
    return;
  }
  if (line) {
    selectTrack(line.dataset.trackId);
  }
});

audioTracks.addEventListener("click", (event) => {
  const clipEl = event.target.closest(".clip-block");
  const line = event.target.closest(".track-line");

  if (clipEl) {
    selectClip(clipEl.dataset.clipId);
    return;
  }

  if (line) {
    const trackId = line.dataset.trackId;
    selectTrack(trackId);

    const active = getActiveClipRef();
    const track = getTrackById(trackId);
    if (!track || !active || active.track.id !== trackId || state.drag.clipId || track.locked) {
      return;
    }

    const rect = line.getBoundingClientRect();
    const x = clamp((event.clientX - rect.left) / rect.width, 0, 1);
    const y = clamp((event.clientY - rect.top) / rect.height, 0, 1);

    pushHistorySnapshot();
    active.clip.audioKeyframes.push({
      time: x * active.clip.duration,
      volume: 1 - y
    });
    renderKeyframes();
    renderTimeline();
  }
});

textTracksTimeline.addEventListener("click", (event) => {
  const clipEl = event.target.closest('[data-kind="text"]');
  const line = event.target.closest('.track-line[data-kind="text-track"]');

  if (clipEl) {
    const clip = getTextClipById(clipEl.dataset.textClipId);
    state.lastSelectionKind = "text";
    state.activeTextClipId = clipEl.dataset.textClipId;
    if (clip) {
      state.activeTextTrackId = clip.trackId;
    }
    renderTextInspector();
    renderTextLayer();
    renderTimeline();
    return;
  }

  if (line) {
    state.activeTextTrackId = line.dataset.trackId;
    renderTimeline();
  }
});

window.addEventListener("mousemove", (event) => {
  if (state.playheadDrag.active) {
    scrubTimelineFromPointer(event.clientX);
  }

  onClipDragMove(event);

  if (!draggingTextId) {
    return;
  }

  const rect = textLayer.getBoundingClientRect();
  if (!rect.width || !rect.height) {
    return;
  }

  const text = getTextClipById(draggingTextId);
  if (!text) {
    return;
  }

  const xPct = ((event.clientX - rect.left - dragOffsetX) / rect.width) * 100;
  const yPct = ((event.clientY - rect.top - dragOffsetY) / rect.height) * 100;

  text.x = clamp(xPct, 0, 95);
  text.y = clamp(yPct, 0, 95);
  renderTextLayer();
  renderTextInspector();
});

window.addEventListener("mouseup", () => {
  state.playheadDrag.active = false;
  endClipDrag();
  draggingTextId = null;
});

timelineRuler.addEventListener("mousedown", (event) => {
  beginPlayheadDrag(event.clientX);
});

timelinePlayheadLine.addEventListener("mousedown", (event) => {
  event.stopPropagation();
  beginPlayheadDrag(event.clientX);
});

playPause.addEventListener("click", () => {
  if (!hasTimelineContent()) {
    return;
  }

  if (!state.playback.isTimelinePlaying) {
    startTimelinePlayback();
  }
});

pauseBtn.addEventListener("click", () => {
  if (state.playback.isTimelinePlaying) {
    stopTimelinePlayback();
  }
});

stopBtn.addEventListener("click", () => {
  stopTimelinePlayback();
  setTimelineTime(0, { forceSeek: true });
});

videoPreview.addEventListener("timeupdate", () => {
  if (state.playback.isTimelinePlaying) {
    if (!state.isExporting) {
      const preview = getPreviewClipRef();
      if (preview) {
        state.playback.timelineTime = clamp(
          preview.clip.timelineStart + (videoPreview.currentTime - preview.clip.trimStart),
          0,
          getProjectDuration()
        );
      }
    }
    updateTransport();
    updateFadeVisualAndAudio();
    renderTextLayer();
    return;
  }

  updateFadeVisualAndAudio();
  renderTextLayer();
});

videoPreview.addEventListener("loadedmetadata", () => {
  const preview = getPreviewClipRef();
  if (!preview) {
    return;
  }

  if (preview.clip.type === "image") {
    return;
  }

  preview.clip.duration = Math.max(0.01, videoPreview.duration || preview.clip.duration);
  preview.clip.trimStart = clamp(preview.clip.trimStart, 0, preview.clip.duration);
  preview.clip.trimEnd = clamp(preview.clip.trimEnd, preview.clip.trimStart, preview.clip.duration);

  const active = getActiveClipRef();
  if (active && active.clip.id === preview.clip.id) {
    syncClipToInspector(preview.clip);
  }

  if (state.playback.isTimelinePlaying) {
    setTimelineTime(state.playback.timelineTime);
  }

  updateTransport();
  renderTimeline();
});

playhead.addEventListener("input", () => {
  const projectDuration = getProjectDuration();
  if (!projectDuration) {
    return;
  }

  const target = (Number(playhead.value) / 100) * projectDuration;
  setTimelineTime(target);
});

exportMp4.addEventListener("click", () => {
  exportTimeline();
});

undoBtn.addEventListener("click", () => {
  undoProject();
});

redoBtn.addEventListener("click", () => {
  redoProject();
});

saveProjectBtn.addEventListener("click", () => {
  saveProjectToFile();
});

openProjectBtn.addEventListener("click", () => {
  projectFileInput.click();
});

projectFileInput.addEventListener("change", async (event) => {
  const file = event.target.files && event.target.files[0];
  event.target.value = "";

  if (!file) {
    return;
  }

  try {
    setExportStatus("Abriendo proyecto...");
    await openProjectFromFile(file);
    setExportStatus("Proyecto abierto");
  } catch {
    setExportStatus("Archivo invalido o corrupto");
  }
});

applyTrim.addEventListener("click", () => {
  const active = getActiveClipRef();
  if (!active) {
    return;
  }

  pushHistorySnapshot();

  const clip = active.clip;
  const start = clamp(Number(trimStartInput.value), 0, clip.duration);
  const end = clamp(Number(trimEndInput.value), 0, clip.duration);

  clip.trimStart = Math.min(start, end);
  clip.trimEnd = Math.max(start, end);

  state.playback.timelineTime = clip.timelineStart;
  setTimelineTime(state.playback.timelineTime);
  renderTimeline();
});

filterPreset.addEventListener("change", (event) => {
  setPreset(event.target.value);
});

[brightnessInput, contrastInput, saturationInput].forEach((input) => {
  input.addEventListener("input", () => {
    const active = getActiveClipRef();
    if (!active) {
      return;
    }

    active.clip.filter.brightness = Number(brightnessInput.value);
    active.clip.filter.contrast = Number(contrastInput.value);
    active.clip.filter.saturation = Number(saturationInput.value);
    applyFiltersForClip(active.clip);
  });
});

videoFadeInInput.addEventListener("input", () => {
  const active = getActiveClipRef();
  if (active) {
    active.clip.fades.videoFadeIn = Number(videoFadeInInput.value);
  }
});

videoFadeOutInput.addEventListener("input", () => {
  const active = getActiveClipRef();
  if (active) {
    active.clip.fades.videoFadeOut = Number(videoFadeOutInput.value);
  }
});

audioFadeInInput.addEventListener("input", () => {
  const active = getActiveClipRef();
  if (active) {
    active.clip.fades.audioFadeIn = Number(audioFadeInInput.value);
  }
});

audioFadeOutInput.addEventListener("input", () => {
  const active = getActiveClipRef();
  if (active) {
    active.clip.fades.audioFadeOut = Number(audioFadeOutInput.value);
  }
});

addText.addEventListener("click", () => {
  createTextClipAt(state.playback.timelineTime);
});

copyTextClip.addEventListener("click", () => {
  copyActiveTextClip();
});

pasteTextClip.addEventListener("click", () => {
  pasteCopiedTextClip();
});

textLayer.addEventListener("mousedown", (event) => {
  const target = event.target.closest(".overlay-text");
  if (!target) {
    return;
  }

  const id = target.dataset.id;
  const rect = textLayer.getBoundingClientRect();
  const track = getTextClipById(id);

  if (!track || !rect.width || !rect.height) {
    return;
  }

  state.activeTextClipId = id;
  state.lastSelectionKind = "text";
  draggingTextId = id;
  dragOffsetX = event.clientX - rect.left - (track.x / 100) * rect.width;
  dragOffsetY = event.clientY - rect.top - (track.y / 100) * rect.height;
  renderTextInspector();
  renderTimeline();
});

window.addEventListener("keydown", (event) => {
  if (state.isExporting) {
    return;
  }

  const tag = event.target && event.target.tagName ? event.target.tagName.toLowerCase() : "";
  if (tag === "input" || tag === "textarea" || tag === "select") {
    return;
  }

  if (event.key === "Delete" || event.key === "Del") {
    event.preventDefault();
    deleteCurrentSelection();
    return;
  }

  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "c") {
    copyActiveTextClip();
  }

  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "v") {
    pasteCopiedTextClip();
  }

  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "z") {
    event.preventDefault();
    undoProject();
  }

  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "y") {
    event.preventDefault();
    redoProject();
  }
});

baseVolumeInput.addEventListener("input", () => {
  const active = getActiveClipRef();
  if (active) {
    active.clip.baseVolume = Number(baseVolumeInput.value);
  }
});

clearKeys.addEventListener("click", () => {
  const active = getActiveClipRef();
  if (!active) {
    return;
  }

  pushHistorySnapshot();

  active.clip.audioKeyframes = [];
  renderKeyframes();
  renderTimeline();
});

addTrack("video");
addTrack("audio");
addTextTrack();
videoPreview.setAttribute("playsinline", "");
videoPreview.setAttribute("webkit-playsinline", "");
setPreviewMode("video");
renderTimeline();
renderMediaBin();
updateTransport();
pushHistorySnapshot();
