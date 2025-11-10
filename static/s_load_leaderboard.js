document.addEventListener("DOMContentLoaded", async () => {
    const stats_div = document.getElementById("stats");
    const leaderboard_display = document.getElementById("leaderboard-display");

    try {
        const response = await fetch("http://127.0.0.1:5000/api/leaderboard", {
            method: "GET",
            headers: {
                "Content-Type": "application/json"
            },
            credentials: "include",
        });

        const data = await response.json();

        if (data) {
            for (let i = 0; i < Math.min(10, data.board.length); i++) {
                leaderboard_display.innerHTML += `
                    <code for each row of stats>
                `;
            }
        } else {
            stats_div.innerText = "Leaderboard was unable to load";
        }
    } catch (error) {
        console.error("Error during fetch:", error);
        stats_div.innerText = "Failed to load stats";
    }
});
