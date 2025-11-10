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
            leaderboard_display.innerHTML = await data;
        } else {
            stats_div.innerText = "Leaderboard was unable to load";
        }
    } catch (error) {
        console.error("Error during fetch:", error);
        stats_div.innerText = "Failed to load stats";
    }
});
