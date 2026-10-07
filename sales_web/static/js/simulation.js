// ============================================================
// SIMULATION STATE
// ============================================================

let sessionId =
    window.SIMULATION_CONFIG?.sessionId || null;

let isRecording = false;
let isProcessing = false;
let isSpeaking = false;
let mediaRecorder = null;
let audioChunks = [];
let audioContext = null;
let analyser = null;
let waveformAnimFrame = null;

// Model readiness
let sttReady = false;
let ttsReady = false;


// ============================================================
// DOM ELEMENTS
// ============================================================

const loadingOverlay =
    document.getElementById("simLoadingOverlay");

const loadingText =
    document.getElementById("simLoadingText");

const personalityBadge =
    document.getElementById("simPersonalityBadge");

const difficultyBadge =
    document.getElementById("simDifficultyBadge");

const buyerName =
    document.getElementById("simBuyerName");

const buyerSubtitle =
    document.getElementById("simBuyerSubtitle");

const avatarPulse =
    document.getElementById("simAvatarPulse");

const statusEl =
    document.getElementById("simStatus");

const statusText =
    document.getElementById("simStatusText");

const waveformEl =
    document.getElementById("simWaveform");

const micBtn =
    document.getElementById("simMicBtn");

const endCallBtn =
    document.getElementById("simEndCallBtn");

const transcriptMessages =
    document.getElementById("simTranscriptMessages");

const transcriptPanel =
    document.getElementById("simTranscriptPanel");

const sttBadge =
    document.getElementById("sttBadge");

const ttsBadge =
    document.getElementById("ttsBadge");


// ============================================================
// CSRF
// ============================================================

function getCookie(name) {

    const cookies =
        document.cookie.split(";");

    for (let cookie of cookies) {

        cookie = cookie.trim();

        if (cookie.startsWith(name + "=")) {

            return decodeURIComponent(
                cookie.substring(name.length + 1)
            );
        }
    }

    return null;
}


// ============================================================
// WAVEFORM SETUP
// ============================================================

function createWaveformBars() {

    waveformEl.innerHTML = "";

    for (let i = 0; i < 32; i++) {

        const bar =
            document.createElement("div");

        bar.className = "sim-wave-bar";

        waveformEl.appendChild(bar);
    }
}

createWaveformBars();


// ============================================================
// SET STATUS
// ============================================================

function setStatus(state, text) {

    statusEl.className =
        "sim-status " + state;

    const icons = {
        "": "⏳",
        "listening": "🎙",
        "speaking": "🔊",
        "processing": "⏳",
    };

    statusText.textContent = text;

    const iconSpan =
        statusEl.querySelector(
            ".sim-status-icon"
        );

    if (iconSpan) {
        iconSpan.textContent =
            icons[state] || "⏳";
    }
}


// ============================================================
// ADD TRANSCRIPT
// ============================================================

function addTranscript(role, text, isInterim) {

    const msg =
        document.createElement("div");

    msg.className = "sim-transcript-msg";

    const roleEl =
        document.createElement("span");

    roleEl.className =
        "sim-transcript-role " +
        (role === "assistant" ? "buyer" : "you");

    roleEl.textContent =
        role === "assistant" ? "BUYER" : "YOU";

    const textEl =
        document.createElement("span");

    textEl.className =
        "sim-transcript-text" +
        (isInterim ? " interim" : "");

    textEl.textContent = text;

    msg.appendChild(roleEl);
    msg.appendChild(textEl);

    transcriptMessages.appendChild(msg);

    transcriptPanel.scrollTop =
        transcriptPanel.scrollHeight;

    return msg;
}


// ============================================================
// FORMAT TEXT
// ============================================================

function formatText(value) {

    if (!value) {
        return "";
    }

    return value
        .replaceAll("_", " ")
        .replace(/\b\w/g, letter =>
            letter.toUpperCase()
        );
}


// ============================================================
// CHECK MODEL STATUS
// ============================================================

async function checkModelStatus() {

    try {

        const response =
            await fetch(
                "/api/voice/status/",
                {
                    method: "GET",
                    credentials: "same-origin",
                }
            );

        if (!response.ok) {

            throw new Error(
                "Model status check failed."
            );
        }

        const data =
            await response.json();

        sttReady = data.stt_ready;
        ttsReady = data.tts_ready;

        // Update badges
        updateModelBadge(
            sttBadge,
            "🎙 STT: " + data.stt_model,
            data.stt_ready
        );

        updateModelBadge(
            ttsBadge,
            "🔊 TTS: " + data.tts_model,
            data.tts_ready
        );

        return (
            data.stt_ready &&
            data.tts_ready
        );

    } catch (error) {

        console.error(
            "MODEL STATUS ERROR:",
            error
        );

        return false;
    }
}


function updateModelBadge(
    badge,
    text,
    ready
) {

    badge.textContent = text;

    badge.className =
        "sim-model-badge " +
        (ready ? "ready" : "loading");
}


// ============================================================
// LOAD MODELS
// ============================================================

async function loadModels() {

    loadingText.textContent =
        "Loading Whisper STT model...";

    try {

        const csrfToken =
            getCookie("csrftoken");

        const response =
            await fetch(
                "/api/voice/load-models/",
                {
                    method: "POST",
                    credentials: "same-origin",
                    headers: {
                        "X-CSRFToken":
                            csrfToken,
                    },
                }
            );

        if (!response.ok) {

            const err =
                await response.json()
                    .catch(() => ({}));

            throw new Error(
                err.error ||
                "Failed to load models."
            );
        }

        const data =
            await response.json();

        sttReady = data.stt_ready;
        ttsReady = data.tts_ready;

        updateModelBadge(
            sttBadge,
            "🎙 STT: " +
                (data.stt_model || "Whisper"),
            data.stt_ready
        );

        updateModelBadge(
            ttsBadge,
            "🔊 TTS: " +
                (data.tts_model || "Kokoro"),
            data.tts_ready
        );

        return true;

    } catch (error) {

        console.error(
            "LOAD MODELS ERROR:",
            error
        );

        loadingText.textContent =
            "Error: " + error.message;

        updateModelBadge(
            sttBadge,
            "🎙 STT: Error",
            false
        );

        sttBadge.className =
            "sim-model-badge error";

        return false;
    }
}


// ============================================================
// LOAD SESSION DETAILS
// ============================================================

async function loadSessionDetails() {

    if (!sessionId) {

        window.location.href =
            "/training/setup/";

        return;
    }

    try {

        const response =
            await fetch(
                `/api/sessions/${sessionId}/`,
                {
                    method: "GET",
                    credentials: "same-origin",
                }
            );

        if (!response.ok) {

            throw new Error(
                "Session not found."
            );
        }

        const session =
            await response.json();

        personalityBadge.textContent =
            formatText(
                session.personality
            );

        difficultyBadge.textContent =
            formatText(
                session.difficulty
            );

        buyerName.textContent =
            session.client_name ||
            "AI Buyer";

        buyerSubtitle.textContent =
            formatText(
                session.personality
            ) +
            " · " +
            formatText(
                session.difficulty
            );

    } catch (error) {

        console.error(
            "SESSION ERROR:",
            error
        );

        window.location.href =
            "/training/setup/";
    }
}


// ============================================================
// LOAD EXISTING MESSAGES
// ============================================================

async function loadExistingMessages() {

    if (!sessionId) {
        return;
    }

    try {

        const response =
            await fetch(
                `/api/sessions/${sessionId}/messages/`,
                {
                    method: "GET",
                    credentials: "same-origin",
                }
            );

        if (!response.ok) {
            return;
        }

        const data =
            await response.json();

        data.messages.forEach(
            message => {

                addTranscript(
                    message.role,
                    message.content,
                    false
                );
            }
        );

        // Speak the last assistant message (opening)
        const lastAssistant =
            data.messages
                .filter(m => m.role === "assistant")
                .pop();

        if (lastAssistant && ttsReady) {

            await speakText(
                lastAssistant.content
            );
        }

    } catch (error) {

        console.error(
            "LOAD MESSAGES ERROR:",
            error
        );
    }
}


// ============================================================
// START RECORDING
// ============================================================

async function startRecording() {

    if (isRecording || isProcessing || isSpeaking) {
        return;
    }

    try {

        const stream =
            await navigator.mediaDevices
                .getUserMedia({
                    audio: {
                        channelCount: 1,
                        sampleRate: 16000,
                    },
                });

        // Audio context for visualization
        audioContext =
            new (window.AudioContext ||
                window.webkitAudioContext)();

        const source =
            audioContext.createMediaStreamSource(
                stream
            );

        analyser =
            audioContext.createAnalyser();

        analyser.fftSize = 64;

        source.connect(analyser);

        // MediaRecorder
        mediaRecorder =
            new MediaRecorder(
                stream,
                {
                    mimeType:
                        MediaRecorder.isTypeSupported(
                            "audio/webm;codecs=opus"
                        )
                            ? "audio/webm;codecs=opus"
                            : "audio/webm",
                }
            );

        audioChunks = [];

        mediaRecorder.ondataavailable =
            function (event) {

                if (event.data.size > 0) {
                    audioChunks.push(
                        event.data
                    );
                }
            };

        mediaRecorder.onstop =
            async function () {

                // Stop visualization
                cancelAnimationFrame(
                    waveformAnimFrame
                );

                waveformEl.classList.remove(
                    "active",
                    "listening"
                );

                // Stop mic stream
                stream.getTracks()
                    .forEach(
                        t => t.stop()
                    );

                if (audioContext) {

                    audioContext.close();
                    audioContext = null;
                }

                // Process audio
                if (audioChunks.length > 0) {

                    const audioBlob =
                        new Blob(
                            audioChunks,
                            {
                                type:
                                    "audio/webm",
                            }
                        );

                    await processAudio(
                        audioBlob
                    );
                }
            };

        mediaRecorder.start(250);

        isRecording = true;

        micBtn.classList.add("recording");

        setStatus(
            "listening",
            "Listening..."
        );

        waveformEl.classList.add(
            "active",
            "listening"
        );

        avatarPulse.classList.remove(
            "active"
        );

        // Start visualization
        animateWaveform();

    } catch (error) {

        console.error(
            "MIC ERROR:",
            error
        );

        setStatus(
            "",
            "Microphone access denied"
        );
    }
}


// ============================================================
// STOP RECORDING
// ============================================================

function stopRecording() {

    if (
        !isRecording ||
        !mediaRecorder
    ) {
        return;
    }

    isRecording = false;

    micBtn.classList.remove("recording");

    mediaRecorder.stop();
}


// ============================================================
// ANIMATE WAVEFORM
// ============================================================

function animateWaveform() {

    if (!analyser) {
        return;
    }

    const bars =
        waveformEl.querySelectorAll(
            ".sim-wave-bar"
        );

    const bufferLength =
        analyser.frequencyBinCount;

    const dataArray =
        new Uint8Array(bufferLength);

    function draw() {

        waveformAnimFrame =
            requestAnimationFrame(draw);

        analyser.getByteFrequencyData(
            dataArray
        );

        bars.forEach(
            (bar, i) => {

                const value =
                    dataArray[
                        i % bufferLength
                    ] || 0;

                const height =
                    Math.max(
                        4,
                        (value / 255) * 42
                    );

                bar.style.height =
                    height + "px";
            }
        );
    }

    draw();
}


// ============================================================
// ANIMATE SPEAKING WAVEFORM (synthetic)
// ============================================================

function animateSpeakingWaveform() {

    waveformEl.classList.add(
        "active",
        "speaking"
    );

    waveformEl.classList.remove(
        "listening"
    );

    const bars =
        waveformEl.querySelectorAll(
            ".sim-wave-bar"
        );

    function draw() {

        waveformAnimFrame =
            requestAnimationFrame(draw);

        bars.forEach(
            (bar, i) => {

                const t = Date.now() / 200;

                const height =
                    8 +
                    Math.sin(t + i * 0.5) *
                    14 +
                    Math.random() * 6;

                bar.style.height =
                    Math.max(4, height) +
                    "px";
            }
        );
    }

    draw();
}


// ============================================================
// PROCESS AUDIO (STT -> RAG -> TTS)
// ============================================================

async function processAudio(audioBlob) {

    isProcessing = true;

    micBtn.disabled = true;

    setStatus(
        "processing",
        "Processing your speech..."
    );

    const csrfToken =
        getCookie("csrftoken");

    try {

        // ---------------------------------------------------
        // STEP 1 — STT (Whisper)
        // ---------------------------------------------------

        setStatus(
            "processing",
            "Transcribing..."
        );

        const formData =
            new FormData();

        formData.append(
            "audio",
            audioBlob,
            "recording.webm"
        );

        const sttResponse =
            await fetch(
                `/api/voice/stt/`,
                {
                    method: "POST",
                    credentials: "same-origin",
                    headers: {
                        "X-CSRFToken":
                            csrfToken,
                    },
                    body: formData,
                }
            );

        if (!sttResponse.ok) {

            const err =
                await sttResponse.json()
                    .catch(() => ({}));

            throw new Error(
                err.error ||
                "STT failed."
            );
        }

        const sttData =
            await sttResponse.json();

        const userText =
            sttData.text?.trim();

        if (!userText) {

            setStatus(
                "",
                "No speech detected. Try again."
            );

            isProcessing = false;
            micBtn.disabled = false;

            return;
        }

        // Show user transcript
        addTranscript(
            "user",
            userText,
            false
        );

        // ---------------------------------------------------
        // STEP 2 — RAG CHAT (existing pipeline)
        // ---------------------------------------------------

        setStatus(
            "processing",
            "Buyer is thinking..."
        );

        avatarPulse.classList.add(
            "active"
        );

        const chatResponse =
            await fetch(
                `/api/chat/${sessionId}/`,
                {
                    method: "POST",
                    credentials: "same-origin",
                    headers: {
                        "Content-Type":
                            "application/json",
                        "X-CSRFToken":
                            csrfToken,
                    },
                    body: JSON.stringify({
                        message: userText,
                    }),
                }
            );

        if (!chatResponse.ok) {

            throw new Error(
                "Chat request failed."
            );
        }

        // Read streamed response
        const reader =
            chatResponse.body.getReader();

        const decoder =
            new TextDecoder();

        let buffer = "";
        let fullResponse = "";

        while (true) {

            const { value, done } =
                await reader.read();

            if (done) {
                break;
            }

            buffer +=
                decoder.decode(
                    value,
                    { stream: true }
                );

            const lines =
                buffer.split("\n");

            buffer = lines.pop();

            for (const line of lines) {

                if (!line.trim()) {
                    continue;
                }

                const event =
                    JSON.parse(line);

                if (
                    event.type === "token"
                ) {

                    fullResponse +=
                        event.content;
                }

                if (
                    event.type === "error"
                ) {

                    throw new Error(
                        event.content
                    );
                }
            }
        }

        avatarPulse.classList.remove(
            "active"
        );

        // Show buyer transcript
        addTranscript(
            "assistant",
            fullResponse,
            false
        );

        // ---------------------------------------------------
        // STEP 3 — TTS (Kokoro)
        // ---------------------------------------------------

        await speakText(fullResponse);

    } catch (error) {

        console.error(
            "PROCESS ERROR:",
            error
        );

        setStatus(
            "",
            "Error: " + error.message
        );

        avatarPulse.classList.remove(
            "active"
        );

    } finally {

        isProcessing = false;
        micBtn.disabled = false;
    }
}


// ============================================================
// SPEAK TEXT (TTS)
// ============================================================

async function speakText(text) {

    if (!text || !ttsReady) {

        setStatus(
            "",
            "Ready — Press mic to speak"
        );

        return;
    }

    isSpeaking = true;

    setStatus(
        "speaking",
        "Buyer is speaking..."
    );

    avatarPulse.classList.add("active");

    animateSpeakingWaveform();

    const csrfToken =
        getCookie("csrftoken");

    try {

        const response =
            await fetch(
                "/api/voice/tts/",
                {
                    method: "POST",
                    credentials: "same-origin",
                    headers: {
                        "Content-Type":
                            "application/json",
                        "X-CSRFToken":
                            csrfToken,
                    },
                    body: JSON.stringify({
                        text: text,
                    }),
                }
            );

        if (!response.ok) {

            throw new Error(
                "TTS failed."
            );
        }

        const audioBlob =
            await response.blob();

        const audioUrl =
            URL.createObjectURL(
                audioBlob
            );

        const audio =
            new Audio(audioUrl);

        await new Promise(
            (resolve, reject) => {

                audio.onended = resolve;
                audio.onerror = reject;
                audio.play();

            }
        );

        URL.revokeObjectURL(audioUrl);

    } catch (error) {

        console.error(
            "TTS ERROR:",
            error
        );

        // Fallback to browser TTS
        if (
            "speechSynthesis" in window
        ) {

            const utterance =
                new SpeechSynthesisUtterance(
                    text
                );

            utterance.rate = 0.95;

            await new Promise(
                resolve => {

                    utterance.onend =
                        resolve;

                    speechSynthesis.speak(
                        utterance
                    );
                }
            );
        }

    } finally {

        isSpeaking = false;

        avatarPulse.classList.remove(
            "active"
        );

        cancelAnimationFrame(
            waveformAnimFrame
        );

        waveformEl.classList.remove(
            "active",
            "speaking",
            "listening"
        );

        setStatus(
            "",
            "Ready — Press mic to speak"
        );
    }
}


// ============================================================
// END SESSION
// ============================================================

async function endSimulation() {

    if (!sessionId) {
        return;
    }

    if (
        !confirm(
            "End this voice simulation session?"
        )
    ) {
        return;
    }

    // Stop any recording
    if (isRecording) {
        stopRecording();
    }

    const csrfToken =
        getCookie("csrftoken");

    try {

        await fetch(
            `/api/sessions/${sessionId}/end/`,
            {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "X-CSRFToken":
                        csrfToken,
                },
            }
        );

        window.location.href =
            "/history/";

    } catch (error) {

        console.error(
            "END ERROR:",
            error
        );

        alert(error.message);
    }
}


// ============================================================
// EVENT LISTENERS
// ============================================================

// Push-to-talk: hold mic button

micBtn.addEventListener(
    "mousedown",
    function () {
        startRecording();
    }
);

micBtn.addEventListener(
    "mouseup",
    function () {
        stopRecording();
    }
);

micBtn.addEventListener(
    "mouseleave",
    function () {

        if (isRecording) {
            stopRecording();
        }
    }
);

// Touch support
micBtn.addEventListener(
    "touchstart",
    function (e) {
        e.preventDefault();
        startRecording();
    }
);

micBtn.addEventListener(
    "touchend",
    function (e) {
        e.preventDefault();
        stopRecording();
    }
);

// Click toggle (for accessibility)
micBtn.addEventListener(
    "click",
    function () {

        // If push-to-talk already
        // handled, do nothing.
        // This is a fallback for
        // tap interactions.
    }
);

endCallBtn.addEventListener(
    "click",
    endSimulation
);

// Spacebar push-to-talk
document.addEventListener(
    "keydown",
    function (event) {

        if (
            event.code === "Space" &&
            !event.repeat &&
            !isProcessing &&
            !isSpeaking &&
            event.target.tagName !== "INPUT" &&
            event.target.tagName !== "TEXTAREA"
        ) {

            event.preventDefault();
            startRecording();
        }
    }
);

document.addEventListener(
    "keyup",
    function (event) {

        if (event.code === "Space") {

            event.preventDefault();
            stopRecording();
        }
    }
);


// ============================================================
// INITIALIZE
// ============================================================

async function initialize() {

    loadingText.textContent =
        "Loading session details...";

    await loadSessionDetails();

    loadingText.textContent =
        "Loading voice models (this may take a minute)...";

    const modelsLoaded =
        await loadModels();

    if (!modelsLoaded) {

        loadingText.textContent =
            "⚠ Models failed to load. " +
            "Make sure the backend is running " +
            "with Whisper and Kokoro installed.";

        return;
    }

    // Hide overlay
    loadingOverlay.classList.add("hidden");

    setStatus(
        "",
        "Loading conversation..."
    );

    await loadExistingMessages();

    micBtn.disabled = false;

    setStatus(
        "",
        "Ready — Hold mic or press Space to speak"
    );
}

initialize();
