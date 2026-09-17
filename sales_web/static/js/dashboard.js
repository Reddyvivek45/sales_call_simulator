// ========================================
// CHART INSTANCES
// ========================================

let scoreChart = null;
let skillChart = null;


// ========================================
// LOAD DASHBOARD
// ========================================

document.addEventListener("DOMContentLoaded", function () {
    loadDashboard();
});


async function loadDashboard() {

    try {

        const response = await fetch("/dashboard/data/");

        if (!response.ok) {
            throw new Error("Failed to load dashboard data.");
        }

        const data = await response.json();

        updateStats(data);

        renderScoreChart(data.score_progress);

        renderSkillChart(data.skill_performance);

    } catch (error) {

        console.error(
            "Dashboard error:",
            error
        );

    }
}


// ========================================
// UPDATE STAT CARDS
// ========================================

function updateStats(data) {

    document.getElementById("average-score").textContent =
        data.average_score !== null
            ? data.average_score
            : "—";

    document.getElementById("sessions-completed").textContent =
        data.sessions_completed;

    document.getElementById("best-score").textContent =
        data.best_score !== null
            ? data.best_score
            : "—";
}


// ========================================
// SCORE PROGRESS CHART
// ========================================

function renderScoreChart(scoreProgress) {

    const canvas = document.getElementById(
        "score-progress-chart"
    );

    if (!canvas) {
        return;
    }

    // Destroy previous chart if it exists
    if (scoreChart) {
        scoreChart.destroy();
    }

    scoreChart = new Chart(canvas, {

        type: "line",

        data: {

            labels: scoreProgress.labels || [],

            datasets: [
                {
                    label: "Score",

                    data: scoreProgress.scores || [],

                    borderColor: "#131c2e",

                    backgroundColor:
                        "rgba(37, 99, 235, 0.1)",

                    tension: 0.3,

                    fill: true,

                    pointRadius: 4,

                    pointHoverRadius: 6
                }
            ]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            scales: {

                y: {

                    min: 0,

                    max: 100,

                    ticks: {
                        stepSize: 20
                    }

                }

            },

            plugins: {

                legend: {
                    display: false
                }

            }

        }

    });
}


// ========================================
// SKILL PERFORMANCE CHART
// ========================================

function renderSkillChart(data) {

    const canvas = document.getElementById(
        "skill-performance-chart"
    );

    if (!canvas) {
        return;
    }

    // Destroy previous chart if it exists
    if (skillChart) {
        skillChart.destroy();
    }

    skillChart = new Chart(canvas, {

        type: "bar",

        data: {

            labels: data.labels || [],

            datasets: [
                {
                    label: "Skill Score",

                    data: data.scores || [],

                    borderRadius: 6,

                    backgroundColor: "#122141",

                    barThickness: 24
                }
            ]

        },

        options: {

            indexAxis: "y",

            responsive: true,

            maintainAspectRatio: false,

            scales: {

                x: {

                    min: 0,

                    max: 100,

                    ticks: {
                        stepSize: 20
                    },

                    grid: {
                        color: "#e5e7eb"
                    }

                },

                y: {

                    grid: {
                        display: false
                    },

                    ticks: {

                        font: {
                            size: 12
                        }

                    }

                }

            },

            plugins: {

                legend: {
                    display: false
                },

                tooltip: {

                    callbacks: {

                        label: function (context) {

                            return (
                                " Score: " +
                                context.raw
                            );

                        }

                    }

                }

            }

        }

    });
}