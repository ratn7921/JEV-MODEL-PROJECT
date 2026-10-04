// Jev Model Q&A Prediction Dashboard JavaScript

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const presetSelect = document.getElementById("presetSelect");
  const contextInput = document.getElementById("contextInput");
  const questionInput = document.getElementById("questionInput");
  const answersContainer = document.getElementById("answersContainer");
  const addAnswerBtn = document.getElementById("addAnswerBtn");
  const verificationInput = document.getElementById("verificationInput");
  const qaForm = document.getElementById("qaForm");
  const resetBtn = document.getElementById("resetBtn");
  const submitBtn = document.getElementById("submitBtn");

  // Output Elements
  const emptyState = document.getElementById("emptyState");
  const loadingState = document.getElementById("loadingState");
  const outputContent = document.getElementById("outputContent");
  const latencyBadge = document.getElementById("latencyBadge");
  const latencyValue = document.getElementById("latencyValue");
  const topChoiceId = document.getElementById("topChoiceId");
  const topChoiceText = document.getElementById("topChoiceText");
  const topConfidenceVal = document.getElementById("topConfidenceVal");
  const probabilityBars = document.getElementById("probabilityBars");
  const scoreRatingVal = document.getElementById("scoreRatingVal");
  const scoreConfidenceVal = document.getElementById("scoreConfidenceVal");
  const noulAffirmativeVal = document.getElementById("noulAffirmativeVal");
  const noulProbVal = document.getElementById("noulProbVal");
  const toggleJsonBtn = document.getElementById("toggleJsonBtn");
  const jsonDrawer = document.getElementById("jsonDrawer");
  const jsonCode = document.getElementById("jsonCode");

  // Mode & Settings Elements
  const modeBadge = document.getElementById("modeBadge");
  const modeText = document.getElementById("modeText");
  const openSettingsBtn = document.getElementById("openSettingsBtn");
  const closeSettingsBtn = document.getElementById("closeSettingsBtn");
  const settingsModal = document.getElementById("settingsModal");
  const apiKeyInput = document.getElementById("apiKeyInput");
  const forceSimCheckbox = document.getElementById("forceSimCheckbox");
  const saveSettingsBtn = document.getElementById("saveSettingsBtn");

  let presetsData = [];

  // Local storage keys
  const STORAGE_KEY_API = "jev_typesafe_api_key";
  const STORAGE_KEY_FORCE_SIM = "jev_force_sim";

  // Initialize Settings
  function initSettings() {
    const savedKey = localStorage.getItem(STORAGE_KEY_API) || "";
    const savedForceSim = localStorage.getItem(STORAGE_KEY_FORCE_SIM) === "true";
    apiKeyInput.value = savedKey;
    forceSimCheckbox.checked = savedForceSim;
    updateModeDisplay(savedKey, savedForceSim);
  }

  function updateModeDisplay(key, forceSim) {
    if (forceSim || !key) {
      modeBadge.className = "mode-badge simulation";
      modeText.textContent = "Simulation Mode";
    } else {
      modeBadge.className = "mode-badge live";
      modeText.textContent = "Live Jev Model";
    }
  }

  // Fetch Status from Backend
  async function checkServerStatus() {
    try {
      const res = await fetch("/api/status");
      const data = await res.json();
      const localKey = localStorage.getItem(STORAGE_KEY_API);
      const localForceSim = localStorage.getItem(STORAGE_KEY_FORCE_SIM) === "true";

      if (data.live_mode_active && !localForceSim) {
        modeBadge.className = "mode-badge live";
        modeText.textContent = "Live Jev Model";
      } else if (!localKey || localForceSim) {
        modeBadge.className = "mode-badge simulation";
        modeText.textContent = "Simulation Mode";
      }
    } catch (err) {
      console.warn("Could not check status:", err);
    }
  }

  // Answer Options Management
  function getAnswerRows() {
    return Array.from(answersContainer.querySelectorAll(".answer-row"));
  }

  function reindexAnswerRows() {
    const rows = getAnswerRows();
    rows.forEach((row, index) => {
      const charCode = 65 + index; // A, B, C, D...
      const id = String.fromCharCode(charCode);
      const badge = row.querySelector(".answer-badge");
      const input = row.querySelector(".answer-input");
      if (badge) badge.textContent = id;
      if (input) {
        input.dataset.id = id;
        input.placeholder = `Candidate answer option ${id}...`;
      }
      const deleteBtn = row.querySelector(".btn-icon");
      if (deleteBtn) {
        deleteBtn.disabled = rows.length <= 2;
        deleteBtn.style.opacity = rows.length <= 2 ? "0.3" : "1";
      }
    });
  }

  function createAnswerRow(id = "A", text = "") {
    const row = document.createElement("div");
    row.className = "answer-row";
    row.innerHTML = `
      <span class="answer-badge">${id}</span>
      <input type="text" class="answer-input" data-id="${id}" value="${text.replace(/"/g, '&quot;')}" placeholder="Candidate answer option ${id}..." required />
      <button type="button" class="btn-icon delete-answer-btn" title="Remove option">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
      </button>
    `;

    const deleteBtn = row.querySelector(".delete-answer-btn");
    deleteBtn.addEventListener("click", () => {
      if (getAnswerRows().length > 2) {
        row.remove();
        reindexAnswerRows();
      }
    });

    return row;
  }

  function setAnswerOptions(answers) {
    answersContainer.innerHTML = "";
    if (!answers || answers.length === 0) {
      answers = [
        { id: "A", text: "" },
        { id: "B", text: "" }
      ];
    }
    answers.forEach((ans, idx) => {
      const char = ans.id || String.fromCharCode(65 + idx);
      answersContainer.appendChild(createAnswerRow(char, ans.text || ""));
    });
    reindexAnswerRows();
  }

  addAnswerBtn.addEventListener("click", () => {
    const count = getAnswerRows().length;
    const nextChar = String.fromCharCode(65 + count);
    answersContainer.appendChild(createAnswerRow(nextChar, ""));
    reindexAnswerRows();
  });

  // Load Presets
  async function loadPresets() {
    try {
      const res = await fetch("/api/presets");
      const data = await res.json();
      presetsData = data.presets || [];

      presetSelect.innerHTML = `<option value="">-- Choose a realistic scenario --</option>`;
      presetsData.forEach((p, idx) => {
        const opt = document.createElement("option");
        opt.value = idx;
        opt.textContent = `${p.title} (${p.expected_choice ? 'Suggested: ' + p.expected_choice : ''})`;
        presetSelect.appendChild(opt);
      });

      // Default load first preset
      if (presetsData.length > 0) {
        applyPreset(0);
        presetSelect.value = "0";
      }
    } catch (err) {
      console.error("Failed to load presets:", err);
    }
  }

  function applyPreset(index) {
    const preset = presetsData[index];
    if (!preset) return;

    contextInput.value = preset.context || "";
    questionInput.value = preset.question || "";
    verificationInput.value = preset.verification_question || "";
    setAnswerOptions(preset.candidate_answers || []);
  }

  presetSelect.addEventListener("change", (e) => {
    const idx = parseInt(e.target.value, 10);
    if (!isNaN(idx)) {
      applyPreset(idx);
    }
  });

  // Form Submission & Jev Prediction
  qaForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const question = questionInput.value.trim();
    const context = contextInput.value.trim();
    const verification = verificationInput.value.trim();

    const rows = getAnswerRows();
    const candidateAnswers = rows.map((r) => {
      const input = r.querySelector(".answer-input");
      return {
        id: input.dataset.id,
        text: input.value.trim()
      };
    }).filter(a => a.text.length > 0);

    if (candidateAnswers.length < 2) {
      alert("Please enter at least 2 valid candidate answers.");
      return;
    }

    // Show loading state
    emptyState.classList.add("hidden");
    outputContent.classList.add("hidden");
    loadingState.classList.remove("hidden");
    submitBtn.disabled = true;

    const apiKey = localStorage.getItem(STORAGE_KEY_API) || "";
    const forceSim = localStorage.getItem(STORAGE_KEY_FORCE_SIM) === "true";

    const payload = {
      question: question,
      context: context,
      candidate_answers: candidateAnswers,
      verification_statement: verification,
      api_key: apiKey,
      force_simulation: forceSim
    };

    try {
      const response = await fetch("/api/suggest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const result = await response.json();

      if (!response.ok || result.error) {
        throw new Error(result.error || "Failed to predict answer with Jev model.");
      }

      renderPrediction(result);
    } catch (err) {
      alert("Error: " + err.message);
      emptyState.classList.remove("hidden");
    } finally {
      loadingState.classList.add("hidden");
      submitBtn.disabled = false;
    }
  });

  // Render Prediction
  function renderPrediction(data) {
    outputContent.classList.remove("hidden");

    // Latency
    if (data.latency_ms !== undefined) {
      latencyValue.textContent = data.latency_ms;
      latencyBadge.classList.remove("hidden");
    }

    // Winning Answer Hero Card
    topChoiceId.textContent = data.selected_id;
    topChoiceText.textContent = data.suggested_text;
    const confPct = Math.round((data.confidence || 0) * 100);
    topConfidenceVal.textContent = `${confPct}%`;

    // Probability Bars
    probabilityBars.innerHTML = "";
    const probs = data.probabilities || {};
    const criteria = data.criteria || {};

    // Sort entries by probability descending
    const sortedEntries = Object.entries(probs).sort((a, b) => b[1] - a[1]);

    sortedEntries.forEach(([id, prob]) => {
      const pct = Math.round(prob * 100);
      const isWinner = id === data.selected_id;
      const text = criteria[id] || "";

      const row = document.createElement("div");
      row.className = "prob-row";
      row.innerHTML = `
        <div class="prob-info">
          <div class="prob-label">
            <span class="prob-badge">${id}</span>
            <span>${text.length > 55 ? text.substring(0, 52) + '...' : text}</span>
          </div>
          <span class="prob-val">${pct}% (${(prob).toFixed(4)})</span>
        </div>
        <div class="prob-track">
          <div class="prob-fill ${isWinner ? 'winner' : ''}" style="width: ${pct}%"></div>
        </div>
      `;
      probabilityBars.appendChild(row);
    });

    // Score Primitive
    if (data.score) {
      scoreRatingVal.textContent = data.score.rating || "N/A";
      const sConf = Math.round((data.score.confidence || 0) * 100);
      scoreConfidenceVal.textContent = `${sConf}% confidence`;
    }

    // Noul Primitive
    if (data.noul) {
      const isAffirmative = data.noul.is_affirmative;
      noulAffirmativeVal.innerHTML = isAffirmative 
        ? `<span style="color: #34d399;">✓ Sound & Supported</span>` 
        : `<span style="color: #f43f5e;">✕ Potential Conflict</span>`;
      const nProb = Math.round((data.noul.probability || 0) * 100);
      noulProbVal.textContent = `${nProb}% (Calibrated)`;
    }

    // Raw JSON Inspector
    jsonCode.textContent = JSON.stringify(data, null, 2);
  }

  // Toggle JSON Accordion
  toggleJsonBtn.addEventListener("click", () => {
    jsonDrawer.classList.toggle("hidden");
  });

  // Reset Button
  resetBtn.addEventListener("click", () => {
    contextInput.value = "";
    questionInput.value = "";
    verificationInput.value = "";
    setAnswerOptions([
      { id: "A", text: "" },
      { id: "B", text: "" }
    ]);
    emptyState.classList.remove("hidden");
    outputContent.classList.add("hidden");
    latencyBadge.classList.add("hidden");
  });

  // Settings Modal Handlers
  openSettingsBtn.addEventListener("click", () => {
    settingsModal.classList.remove("hidden");
  });

  closeSettingsBtn.addEventListener("click", () => {
    settingsModal.classList.add("hidden");
  });

  settingsModal.querySelector(".modal-backdrop").addEventListener("click", () => {
    settingsModal.classList.add("hidden");
  });

  saveSettingsBtn.addEventListener("click", () => {
    const key = apiKeyInput.value.trim();
    const forceSim = forceSimCheckbox.checked;

    localStorage.setItem(STORAGE_KEY_API, key);
    localStorage.setItem(STORAGE_KEY_FORCE_SIM, forceSim ? "true" : "false");

    updateModeDisplay(key, forceSim);
    settingsModal.classList.add("hidden");
  });

  // Bootstrapping
  initSettings();
  checkServerStatus();
  loadPresets();
});
