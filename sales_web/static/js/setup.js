// ============================================================
// SETUP STATE
// ============================================================

let selectedPersonality = null;
let selectedDifficulty = "medium";
let selectedLength = "quick";
let selectedFocus = null;


// ============================================================
// DOM
// ============================================================

const freshCard =
    document.getElementById("freshCard");

const resumeCard =
    document.getElementById("resumeCard");

const freshSessionButton =
    document.getElementById("freshSessionButton");

const resumeSessionButton =
    document.getElementById("resumeSessionButton");

const freshSetup =
    document.getElementById("freshSetup");

const resumePanel =
    document.getElementById("resumePanel");

const personalityContainer =
    document.getElementById("personalityContainer");

const startTrainingButton =
    document.getElementById("startTrainingButton");

const activeSessionsContainer =
    document.getElementById("activeSessionsContainer");

const activeSessionBadge =
    document.getElementById("activeSessionBadge");


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
// SHOW FRESH SETUP
// ============================================================

function showFreshSetup() {

    freshSetup.style.display = "block";
    resumePanel.style.display = "none";

    freshCard.classList.add("active");
    resumeCard.classList.remove("active");

}


// ============================================================
// SHOW RESUME
// ============================================================

async function showResumePanel() {

    freshSetup.style.display = "none";
    resumePanel.style.display = "block";

    freshCard.classList.remove("active");
    resumeCard.classList.add("active");

    await loadActiveSessions();
}


// ============================================================
// LOAD PERSONALITIES
// ============================================================

async function loadPersonalities() {

    try {

        const response =
            await fetch(
                "/api/personalities/",
                {
                    method: "GET",
                    credentials: "same-origin",
                }
            );

        if (!response.ok) {

            throw new Error(
                "Failed to load personalities."
            );
        }

        const data =
            await response.json();

        personalityContainer.innerHTML = "";

        data.personalities.forEach(
            personality => {

                const card =
                    document.createElement("div");

                card.className =
                    "personality-card";

                card.dataset.personality =
                    personality.id;

                card.innerHTML = `
                    <div class="personality-name">
                        ${personality.name}
                    </div>

                    <div class="personality-description">
                        ${personality.description}
                    </div>
                `;

                card.addEventListener(
                    "click",
                    function () {

                        selectPersonality(
                            personality.id,
                            card
                        );

                    }
                );

                personalityContainer.appendChild(
                    card
                );

            }
        );

    } catch (error) {

        console.error(
            "PERSONALITY ERROR:",
            error
        );

        personalityContainer.innerHTML = `
            <div class="loading">
                Failed to load buyer personalities.
            </div>
        `;
    }
}


// ============================================================
// SELECT PERSONALITY
// ============================================================

function selectPersonality(
    personality,
    selectedCard
) {

    selectedPersonality =
        personality;

    document
        .querySelectorAll(
            ".personality-card"
        )
        .forEach(
            card => {

                card.classList.remove(
                    "selected"
                );

            }
        );

    selectedCard.classList.add(
        "selected"
    );

    updateStartButton();

}


// ============================================================
// DIFFICULTY
// ============================================================

document
    .querySelectorAll(
        "[data-difficulty]"
    )
    .forEach(
        button => {

            button.addEventListener(
                "click",
                function () {

                    document
                        .querySelectorAll(
                            "[data-difficulty]"
                        )
                        .forEach(
                            item => {

                                item.classList.remove(
                                    "selected"
                                );

                            }
                        );

                    this.classList.add(
                        "selected"
                    );

                    selectedDifficulty =
                        this.dataset.difficulty;

                }
            );

        }
    );


// ============================================================
// SESSION LENGTH
// ============================================================

document
    .querySelectorAll(
        "[data-length]"
    )
    .forEach(
        button => {

            button.addEventListener(
                "click",
                function () {

                    document
                        .querySelectorAll(
                            "[data-length]"
                        )
                        .forEach(
                            item => {

                                item.classList.remove(
                                    "selected"
                                );

                            }
                        );

                    this.classList.add(
                        "selected"
                    );

                    selectedLength =
                        this.dataset.length;

                }
            );

        }
    );


// ============================================================
// FOCUS AREA
// ============================================================

document
    .querySelectorAll(
        "[data-focus]"
    )
    .forEach(
        button => {

            button.addEventListener(
                "click",
                function () {

                    // Clicking selected focus
                    // removes selection.

                    if (
                        selectedFocus ===
                        this.dataset.focus
                    ) {

                        selectedFocus = null;

                        this.classList.remove(
                            "selected"
                        );

                        return;
                    }

                    document
                        .querySelectorAll(
                            "[data-focus]"
                        )
                        .forEach(
                            item => {

                                item.classList.remove(
                                    "selected"
                                );

                            }
                        );

                    this.classList.add(
                        "selected"
                    );

                    selectedFocus =
                        this.dataset.focus;

                }
            );

        }
    );


// ============================================================
// START BUTTON
// ============================================================

function updateStartButton() {

    startTrainingButton.disabled =
        !selectedPersonality;

}


// ============================================================
// CREATE SESSION
// ============================================================

async function startTraining() {

    if (!selectedPersonality) {

        alert(
            "Please select a buyer personality."
        );

        return;
    }

    startTrainingButton.disabled =
        true;

    startTrainingButton.textContent =
        "Starting...";

    const csrfToken =
        getCookie("csrftoken");

    try {

        const response =
            await fetch(
                "/api/sessions/",
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

                        personality:
                            selectedPersonality,

                        difficulty:
                            selectedDifficulty,

                        focus_area:
                            selectedFocus,

                        session_length:
                            selectedLength,

                    }),
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            throw new Error(
                data.error ||
                "Failed to create session."
            );
        }

        // IMPORTANT:
        // Go to actual training page.

        window.location.href =
            `/training/${data.session_id}/`;

    } catch (error) {

        console.error(
            "CREATE SESSION ERROR:",
            error
        );

        alert(
            error.message
        );

        startTrainingButton.disabled =
            false;

        startTrainingButton.textContent =
            "Start training →";
    }
}


// ============================================================
// LOAD ACTIVE SESSIONS
// ============================================================

async function loadActiveSessions() {

    activeSessionsContainer.innerHTML = `
        <div class="loading">
            Loading active sessions...
        </div>
    `;

    try {

        const response =
            await fetch(
                "/api/sessions/active/",
                {
                    method: "GET",
                    credentials: "same-origin",
                }
            );

        if (!response.ok) {

            throw new Error(
                "Failed to load active sessions."
            );
        }

        const data =
            await response.json();

        const sessions =
            data.sessions || [];

        activeSessionBadge.textContent =
            `${sessions.length} in progress`;

        activeSessionsContainer.innerHTML = "";

        if (sessions.length === 0) {

            activeSessionsContainer.innerHTML = `
                <div class="no-sessions">
                    No unfinished training sessions.
                    <br><br>
                    Start a fresh session to begin training.
                </div>
            `;

            return;
        }

        sessions.forEach(
            session => {

                const item =
                    document.createElement("div");

                item.className =
                    "active-session";

                const focus =
                    session.focus_area
                        ? formatText(
                            session.focus_area
                        )
                        : "General";

                const difficulty =
                    formatText(
                        session.difficulty
                    );

                const personality =
                    formatText(
                        session.personality
                    );

                const length =
                    formatText(
                        session.session_length
                    );

                const startedAt =
                    formatDate(
                        session.started_at
                    );

                item.innerHTML = `

                    <div class="active-session-info">

                        <h3>
                            ${session.client_name}
                        </h3>

                        <p>
                            ${personality}
                            ·
                            ${difficulty}
                            ·
                            ${focus}
                            ·
                            ${length}
                        </p>

                        <div class="session-meta">
                            Started ${startedAt}
                        </div>

                    </div>

                    <button
                        class="resume-button"
                        type="button"
                    >
                        Resume →
                    </button>

                `;

                const button =
                    item.querySelector(
                        ".resume-button"
                    );

                button.addEventListener(
                    "click",
                    function () {

                        resumeSession(
                            session.id
                        );

                    }
                );

                activeSessionsContainer.appendChild(
                    item
                );

            }
        );

    } catch (error) {

        console.error(
            "ACTIVE SESSION ERROR:",
            error
        );

        activeSessionsContainer.innerHTML = `
            <div class="no-sessions">
                Failed to load active sessions.
            </div>
        `;
    }
}


// ============================================================
// RESUME SESSION
// ============================================================

function resumeSession(sessionId) {

    window.location.href =
        `/training/${sessionId}/`;
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
// FORMAT DATE
// ============================================================

function formatDate(value) {

    if (!value) {
        return "";
    }

    const date =
        new Date(value);

    return date.toLocaleString(
        undefined,
        {
            day: "2-digit",
            month: "short",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit",
        }
    );
}


// ============================================================
// EVENT LISTENERS
// ============================================================

freshSessionButton.addEventListener(
    "click",
    showFreshSetup
);

resumeSessionButton.addEventListener(
    "click",
    showResumePanel
);

startTrainingButton.addEventListener(
    "click",
    startTraining
);


// ============================================================
// INITIALIZE
// ============================================================

async function initialize() {

    await loadPersonalities();

    // Load count for the resume card.

    try {

        const response =
            await fetch(
                "/api/sessions/active/",
                {
                    credentials: "same-origin"
                }
            );

        if (response.ok) {

            const data =
                await response.json();

            const count =
                data.sessions.length;

            activeSessionBadge.textContent =
                `${count} in progress`;
        }

    } catch (error) {

        console.error(
            "ACTIVE SESSION COUNT ERROR:",
            error
        );
    }

    showFreshSetup();
}

initialize();