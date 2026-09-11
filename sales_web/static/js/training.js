// ============================================================
// TRAINING STATE
// ============================================================

let sessionId =
    window.TRAINING_CONFIG?.sessionId || null;

let isGenerating = false;


// ============================================================
// DOM
// ============================================================

const personalityBadge =
    document.getElementById(
        "personalityBadge"
    );

const difficultyBadge =
    document.getElementById(
        "difficultyBadge"
    );

const focusBadge =
    document.getElementById(
        "focusBadge"
    );

const messagesContainer =
    document.getElementById(
        "messages"
    );

const messageInput =
    document.getElementById(
        "messageInput"
    );

const sendButton =
    document.getElementById(
        "sendButton"
    );

const endTrainingButton =
    document.getElementById(
        "endTraining"
    );


// ============================================================
// CSRF
// ============================================================

function getCookie(name) {

    const cookies =
        document.cookie.split(";");

    for (let cookie of cookies) {

        cookie = cookie.trim();

        if (
            cookie.startsWith(
                name + "="
            )
        ) {

            return decodeURIComponent(
                cookie.substring(
                    name.length + 1
                )
            );
        }
    }

    return null;
}


// ============================================================
// SCROLL
// ============================================================

function scrollToBottom() {

    if (!messagesContainer) {
        return;
    }

    messagesContainer.scrollTop =
        messagesContainer.scrollHeight;
}


// ============================================================
// ADD MESSAGE
// ============================================================

function addMessage(
    role,
    content
) {

    const messageElement =
        document.createElement("div");

    messageElement.className =
        `message ${role}`;

    const contentElement =
        document.createElement("div");

    contentElement.className =
        "message-content";

    contentElement.textContent =
        content;

    messageElement.appendChild(
        contentElement
    );

    messagesContainer.appendChild(
        messageElement
    );

    scrollToBottom();

    return contentElement;
}


// ============================================================
// LOAD SESSION DETAILS
// ============================================================

async function loadSessionDetails() {

    if (!sessionId) {

        console.error(
            "Session ID is missing."
        );

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

        focusBadge.textContent =
            session.focus_area
                ? formatText(
                    session.focus_area
                )
                : "General";

    } catch (error) {

        console.error(
            "SESSION ERROR:",
            error
        );

        alert(
            error.message
        );

        window.location.href =
            "/training/setup/";
    }
}


// ============================================================
// LOAD HISTORY
// ============================================================

async function loadHistory() {

    if (!sessionId) {
        return;
    }

    messagesContainer.innerHTML = `
        <div class="loading">
            Loading conversation...
        </div>
    `;

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

            throw new Error(
                "Failed to load conversation."
            );
        }

        const data =
            await response.json();

        messagesContainer.innerHTML =
            "";

        data.messages.forEach(
            message => {

                addMessage(
                    message.role,
                    message.content
                );

            }
        );

        scrollToBottom();

    } catch (error) {

        console.error(
            "HISTORY ERROR:",
            error
        );

        messagesContainer.innerHTML = `
            <div class="loading">
                Failed to load conversation.
            </div>
        `;
    }
}


// ============================================================
// SEND MESSAGE
// ============================================================

async function sendMessage() {

    if (isGenerating) {
        return;
    }

    if (!sessionId) {

        alert(
            "Session not found."
        );

        return;
    }

    const message =
        messageInput.value.trim();

    if (!message) {
        return;
    }

    addMessage(
        "user",
        message
    );

    messageInput.value =
        "";

    isGenerating =
        true;

    sendButton.disabled =
        true;

    const assistantContent =
        addMessage(
            "assistant",
            ""
        );

    const csrfToken =
        getCookie("csrftoken");

    try {

        const response =
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
                        message:
                            message,
                    }),

                }
            );

        if (!response.ok) {

            const errorData =
                await response
                    .json()
                    .catch(
                        () => ({})
                    );

            throw new Error(
                errorData.error ||
                "Chat request failed."
            );
        }

        const reader =
            response.body.getReader();

        const decoder =
            new TextDecoder();

        let buffer = "";

        while (true) {

            const {
                value,
                done
            } = await reader.read();

            if (done) {
                break;
            }

            buffer +=
                decoder.decode(
                    value,
                    {
                        stream: true
                    }
                );

            const lines =
                buffer.split("\n");

            buffer =
                lines.pop();

            for (
                const line of lines
            ) {

                if (!line.trim()) {
                    continue;
                }

                const event =
                    JSON.parse(line);

                if (
                    event.type ===
                    "token"
                ) {

                    assistantContent
                        .textContent +=
                        event.content;

                    scrollToBottom();
                }

                if (
                    event.type ===
                    "error"
                ) {

                    throw new Error(
                        event.content
                    );
                }
            }
        }

    } catch (error) {

        console.error(
            "CHAT ERROR:",
            error
        );

        assistantContent.textContent =
            "Error: " +
            error.message;

    } finally {

        isGenerating =
            false;

        sendButton.disabled =
            false;

        messageInput.focus();
    }
}


// ============================================================
// END SESSION
// ============================================================

async function endTraining() {

    if (!sessionId) {
        return;
    }

    if (
        !confirm(
            "Are you sure you want to end this training session?"
        )
    ) {

        return;
    }

    const csrfToken =
        getCookie("csrftoken");

    try {

        const response =
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

        const data =
            await response.json();

        if (!response.ok) {

            throw new Error(
                data.error ||
                "Failed to end session."
            );
        }

        // Analyzer can replace this later.

        window.location.href =
            "/history/";

    } catch (error) {

        console.error(
            "END SESSION ERROR:",
            error
        );

        alert(
            error.message
        );
    }
}


// ============================================================
// FORMAT
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
// EVENTS
// ============================================================

if (sendButton) {

    sendButton.addEventListener(
        "click",
        sendMessage
    );
}

if (endTrainingButton) {

    endTrainingButton.addEventListener(
        "click",
        endTraining
    );
}

if (messageInput) {

    messageInput.addEventListener(
        "keydown",
        function(event) {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                sendMessage();
            }
        }
    );
}


// ============================================================
// INITIALIZE
// ============================================================

async function initialize() {

    await loadSessionDetails();

    await loadHistory();

    messageInput.focus();
}

initialize();