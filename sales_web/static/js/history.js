document.addEventListener("DOMContentLoaded", function () {
    loadHistory();
});


async function loadHistory() {

    const container = document.getElementById(
        "historyContainer"
    );

    if (!container) {
        return;
    }

    try {

        const response = await fetch(
            "/history/data/"
        );

        if (!response.ok) {
            throw new Error(
                "Failed to load history."
            );
        }

        const data = await response.json();

        renderHistory(
            data.sessions || []
        );

    } catch (error) {

        console.error(
            "History error:",
            error
        );

        container.innerHTML = `
            <div class="history-error">
                Failed to load session history.
            </div>
        `;
    }
}


function renderHistory(sessions) {

    const container = document.getElementById(
        "historyContainer"
    );

    if (!container) {
        return;
    }


    if (sessions.length === 0) {

        container.innerHTML = `
            <div class="no-history">
                No completed sessions yet.
            </div>
        `;

        return;
    }


    container.innerHTML = sessions
        .map(session => {

            const analysed =
                session.analysis_status === "analysed";


            const statusClass =
                analysed
                    ? "analysed"
                    : "pending";


            const statusText =
                analysed
                    ? "Analysed"
                    : "Analysis Pending";


            const score =
                analysed &&
                session.score !== null
                    ? `${session.score}`
                    : "—";


            const date =
                formatDate(
                    session.started_at
                );


            return `
                <div class="history-card">

                    <div class="history-main">

                        <div class="history-title">

                            <span
                                class="status-dot ${statusClass}"
                            ></span>

                            <h3>
                                ${escapeHtml(
                                    session.product_name
                                )}
                            </h3>

                        </div>


                        <div class="history-meta">

                            <span>
                                ${escapeHtml(
                                    session.personality
                                )}
                            </span>

                            <span>
                                ${escapeHtml(
                                    session.difficulty
                                )}
                            </span>

                            <span>
                                ${date}
                            </span>

                        </div>


                        <div
                            class="history-status ${statusClass}"
                        >
                            ${statusText}
                        </div>

                    </div>


                    <div class="history-score">

                        <span class="score-label">
                            Score
                        </span>

                        <strong>
                            ${score}
                        </strong>

                    </div>


                    <div class="history-action">

                        ${
                            analysed
                            ? `
                                <a
                                    href="/analysis/${session.id}/"
                                    class="history-button"
                                >
                                    View Analysis →
                                </a>
                              `
                            : `
                                <a
                                    href="/history/${session.id}/"
                                    class="history-button secondary"
                                >
                                    View Session →
                                </a>
                              `
                        }

                    </div>

                </div>
            `;

        })
        .join("");
}


function formatDate(value) {

    if (!value) {
        return "—";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return "—";
    }

    return date.toLocaleDateString(
        "en-IN",
        {
            day: "2-digit",
            month: "short",
            year: "numeric"
        }
    );
}


function escapeHtml(value) {

    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}