// ============================================================
// STATE & ELEMENT REFERENCES
// ============================================================
const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("fileInput");
const progressTrack = document.getElementById("progressTrack");
const progressFill = document.getElementById("progressFill");
const docStatus = document.getElementById("docStatus");
const docStatusText = document.getElementById("docStatusText");

const chatLog = document.getElementById("chatLog");
const emptyState = document.getElementById("emptyState");
const composerForm = document.getElementById("composerForm");
const questionInput = document.getElementById("question-input");
const questionError = document.getElementById("question-error");
const askBtn = document.getElementById("askBtn");

const toastRegion = document.getElementById("toastRegion");

let hasDocument = false;

// ============================================================
// PERSONALIZATION — theme (light / dark / auto)
// ============================================================
function applyTheme(choice) {
  const resolved = choice === "auto"
    ? (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")
    : choice;
  document.body.setAttribute("data-theme", resolved);
  document.querySelectorAll("[data-theme-choice]").forEach(btn => {
    btn.setAttribute("aria-pressed", String(btn.dataset.themeChoice === choice));
  });
  localStorage.setItem("ledger-theme", choice);
}

document.querySelectorAll("[data-theme-choice]").forEach(btn => {
  btn.addEventListener("click", () => applyTheme(btn.dataset.themeChoice));
});

// React live if the user picked "auto" and their OS theme changes
window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
  if (localStorage.getItem("ledger-theme") === "auto") applyTheme("auto");
});

applyTheme(localStorage.getItem("ledger-theme") || "light");

// ============================================================
// PERSONALIZATION — density (comfortable / compact)
// ============================================================
function applyDensity(choice) {
  document.documentElement.style.setProperty("--density", choice === "compact" ? "0.6" : "1");
  document.querySelectorAll("[data-density-choice]").forEach(btn => {
    btn.setAttribute("aria-pressed", String(btn.dataset.densityChoice === choice));
  });
  localStorage.setItem("ledger-density", choice);
}

document.querySelectorAll("[data-density-choice]").forEach(btn => {
  btn.addEventListener("click", () => applyDensity(btn.dataset.densityChoice));
});

applyDensity(localStorage.getItem("ledger-density") || "comfortable");

// ============================================================
// TOASTS — success/error confirmation
// ============================================================
function showToast(message, type = "default", duration = 3500) {
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  toastRegion.appendChild(toast);
  setTimeout(() => toast.remove(), duration);
}

// ============================================================
// UPLOAD — drag & drop, click, and keyboard support
// ============================================================
dropzone.addEventListener("click", () => fileInput.click());

dropzone.addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    fileInput.click();
  }
});

["dragenter", "dragover"].forEach(evt => {
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });
});

["dragleave", "drop"].forEach(evt => {
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
  });
});

dropzone.addEventListener("drop", (e) => {
  const file = e.dataTransfer.files[0];
  if (file) handleUpload(file);
});

fileInput.addEventListener("change", () => {
  if (fileInput.files[0]) handleUpload(fileInput.files[0]);
});

async function handleUpload(file) {
  if (file.type !== "application/pdf") {
    showToast("Please upload a PDF file.", "error");
    return;
  }

  // Staged progress bar — gives a sense of real progress while
  // the actual request (which we can't measure step-by-step) is in flight.
  progressTrack.classList.add("active");
  progressFill.style.width = "0%";
  const stages = [
    { pct: 20, label: "Uploading document…" },
    { pct: 55, label: "Reading pages…" },
    { pct: 85, label: "Indexing content…" },
  ];
  let stageIndex = 0;
  docStatus.dataset.state = "working";
  docStatusText.textContent = stages[0].label;
  progressFill.style.width = stages[0].pct + "%";

  const stageTimer = setInterval(() => {
    stageIndex++;
    if (stageIndex < stages.length) {
      progressFill.style.width = stages[stageIndex].pct + "%";
      docStatusText.textContent = stages[stageIndex].label;
    }
  }, 900);

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch("/upload", { method: "POST", body: formData });
    const result = await response.json();
    clearInterval(stageTimer);

    if (!response.ok) throw new Error(result.error || "Upload failed.");

    progressFill.style.width = "100%";
    docStatusText.textContent = `Ready: ${file.name}`;
    hasDocument = true;
    questionInput.disabled = false;
    askBtn.disabled = false;
    showToast("Document processed successfully.", "success");
    setTimeout(() => progressTrack.classList.remove("active"), 600);
  } catch (err) {
    clearInterval(stageTimer);
    progressTrack.classList.remove("active");
    docStatus.dataset.state = "empty";
    showToast(err.message || "Something went wrong uploading your file.", "error");
  }
}

// ============================================================
// CHAT — real-time validation, skeleton loading, message rendering
// ============================================================
function addMessage(text, role) {
  emptyState.style.display = "none";
  const bubble = document.createElement("div");
  bubble.className = `msg ${role}`;
  bubble.textContent = text;
  chatLog.appendChild(bubble);
  chatLog.scrollTop = chatLog.scrollHeight;
  return bubble;
}

function addSkeleton() {
  const skeleton = document.createElement("div");
  skeleton.className = "skeleton-msg";
  skeleton.id = "thinkingSkeleton";
  skeleton.innerHTML = `<div class="skeleton-line"></div><div class="skeleton-line"></div>`;
  chatLog.appendChild(skeleton);
  chatLog.scrollTop = chatLog.scrollHeight;
}

function removeSkeleton() {
  const skeleton = document.getElementById("thinkingSkeleton");
  if (skeleton) skeleton.remove();
}

// Real-time validation: clear the error as soon as the user starts typing again
questionInput.addEventListener("input", () => {
  if (questionInput.value.trim()) {
    questionInput.setAttribute("aria-invalid", "false");
    questionError.textContent = "";
  }
});

composerForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const question = questionInput.value.trim();

  if (!question) {
    questionInput.setAttribute("aria-invalid", "true");
    questionError.textContent = "Type a question before sending.";
    questionInput.focus();
    return;
  }

  if (!hasDocument) {
    showToast("Upload a document first.", "error");
    return;
  }

  addMessage(question, "user");
  questionInput.value = "";
  questionInput.focus();

  setLoading(true);
  addSkeleton();

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const result = await response.json();
    removeSkeleton();

    if (!response.ok) throw new Error(result.error || "Something went wrong.");
    addMessage(result.answer, "assistant");
  } catch (err) {
    removeSkeleton();
    addMessage(err.message || "Something went wrong. Please try again.", "error");
  } finally {
    setLoading(false);
  }
});

function setLoading(isLoading) {
  askBtn.disabled = isLoading;
  askBtn.classList.toggle("loading", isLoading);
}

// ============================================================
// ONBOARDING — dismissible, revisitable guided tour
// ============================================================
const tourSteps = [
  { target: "#dropzone", text: "Start here — drag a PDF in, or click to choose a file from your computer." },
  { target: "#question-input", text: "Once your document is processed, ask a question about it here in plain English." },
  { target: "[data-theme-choice='dark']", text: "Prefer dark mode, or want it to follow your system setting? Change it any time here." },
];
let tourIndex = 0;

const tourOverlay = document.getElementById("tourOverlay");
const tourTooltip = document.getElementById("tourTooltip");
const tourText = document.getElementById("tourText");
const tourStepCount = document.getElementById("tourStepCount");
const tourNextBtn = document.getElementById("tourNextBtn");
const tourSkipBtn = document.getElementById("tourSkipBtn");
const restartTourBtn = document.getElementById("restartTourBtn");

function showTourStep(index) {
  const step = tourSteps[index];
  const targetEl = document.querySelector(step.target);
  if (!targetEl) return;

  const rect = targetEl.getBoundingClientRect();
  tourTooltip.style.top = `${Math.min(rect.bottom + 12, window.innerHeight - 160)}px`;
  tourTooltip.style.left = `${Math.min(rect.left, window.innerWidth - 300)}px`;
  tourText.textContent = step.text;
  tourStepCount.textContent = `Step ${index + 1} of ${tourSteps.length}`;
  tourNextBtn.querySelector(".btn-label").textContent =
    index === tourSteps.length - 1 ? "Done" : "Next";

  tourOverlay.classList.add("active");
  tourTooltip.style.display = "block";
  targetEl.focus({ preventScroll: true });
}

function startTour() {
  tourIndex = 0;
  showTourStep(tourIndex);
}

function endTour() {
  tourOverlay.classList.remove("active");
  tourTooltip.style.display = "none";
  localStorage.setItem("ledger-tour-seen", "true");
}

tourNextBtn.addEventListener("click", () => {
  tourIndex++;
  if (tourIndex >= tourSteps.length) {
    endTour();
  } else {
    showTourStep(tourIndex);
  }
});

tourSkipBtn.addEventListener("click", endTour);
tourOverlay.addEventListener("click", endTour);
restartTourBtn.addEventListener("click", startTour);

// Auto-start only on a user's first-ever visit
if (!localStorage.getItem("ledger-tour-seen")) {
  setTimeout(startTour, 500);
}