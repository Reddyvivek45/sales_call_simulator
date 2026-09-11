document.addEventListener(
    "DOMContentLoaded",
    function () {

        initializeScoreBars();
        initializeScoreCircle();

        initializeAnalyzer();

    }
);


/* ============================================================
   ANALYZER
   ============================================================ */

function initializeAnalyzer() {

    const page =
        document.querySelector(
            ".analysis-page"
        );

    if (!page) {
        return;
    }

    const sessionId =
        page.dataset.sessionId;

    const analysisExists =
        page.dataset.analysisExists === "true";

    if (!sessionId) {
        return;
    }

    /*
     * If analysis already exists in DB,
     * DO NOT call Ollama.
     */
    if (analysisExists) {
        return;
    }

    startAnalysisGeneration(
        sessionId
    );
}


/* ============================================================
   START GENERATION
   ============================================================ */

async function startAnalysisGeneration(
    sessionId
) {

    const loadingMessage =
        document.querySelector(
            "#loading-message"
        );

    const errorBox =
        document.querySelector(
            "#analysis-generation-error"
        );

    try {

        if (loadingMessage) {

            loadingMessage.textContent =
                "Reviewing your sales conversation...";

        }

        const response =
            await fetch(
                `/analysis/${sessionId}/generate/`,
                {
                    method: "POST",
                    headers: {
                        "X-CSRFToken":
                            getCSRFToken(),
                        "Content-Type":
                            "application/json",
                    },
                    body: JSON.stringify({}),
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            throw new Error(
                data.error ||
                "Failed to generate analysis."
            );

        }

        if (
            data.status ===
            "completed"
        ) {

            if (loadingMessage) {

                loadingMessage.textContent =
                    "Analysis complete. Loading report...";

            }

            /*
             * Reload the page.
             *
             * The GET request will now find
             * the analysis in PostgreSQL and
             * will NOT call Ollama again.
             */
            setTimeout(
                function () {

                    window.location.reload();

                },
                400
            );

            return;
        }

        throw new Error(
            "Unexpected analyzer response."
        );

    }
    catch (error) {

        console.error(
            "Session Analyzer:",
            error
        );

        if (errorBox) {

            errorBox.textContent =
                error.message ||
                "Unable to generate session analysis.";

            errorBox.classList.remove(
                "hidden"
            );

        }

        if (loadingMessage) {

            loadingMessage.textContent =
                "Analysis could not be completed.";

        }

    }

}


/* ============================================================
   CSRF
   ============================================================ */

function getCSRFToken() {

    const name = "csrftoken";

    const cookies =
        document.cookie.split(";");

    for (
        let cookie of cookies
    ) {

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

    return "";

}


/* ============================================================
   SCORE BARS
   ============================================================ */

function initializeScoreBars() {

    const bars =
        document.querySelectorAll(
            ".score-fill"
        );

    bars.forEach(
        function (bar) {

            const score =
                parseFloat(
                    bar.dataset.score
                );

            if (
                Number.isNaN(score)
            ) {
                return;
            }

            setTimeout(
                function () {

                    bar.style.width =
                        `${Math.min(
                            Math.max(
                                score,
                                0
                            ),
                            100
                        )}%`;

                },
                150
            );

        }
    );

}


/* ============================================================
   OVERALL SCORE CIRCLE
   ============================================================ */

function initializeScoreCircle() {

    const circle =
        document.querySelector(
            ".score-circle"
        );

    if (!circle) {
        return;
    }

    const score =
        parseFloat(
            circle.dataset.score
        );

    if (
        Number.isNaN(score)
    ) {
        return;
    }

    const clampedScore =
        Math.min(
            Math.max(
                score,
                0
            ),
            100
        );

    const degrees =
        clampedScore * 3.6;

    circle.style.background =
        `conic-gradient(
            currentColor ${degrees}deg,
            #e5e7eb ${degrees}deg
        )`;

}