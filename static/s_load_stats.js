document.addEventListener("DOMContentLoaded", async () => {
    const stats_display = document.getElementById("match-stats-display");

    try {
        const response = await fetch("http://127.0.0.1:5000/api/matchdata", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            credentials: "include",
            body: JSON.stringify({
                "matchid": stats_display.dataset.matchid,
          }),
        });

        const data = await response.json();

        if (data) {
            console.log(data)
            stats_display.innerHTML = `
                <span class="text-green-400 font-extrabold">${ data.kills }</span>
                <span class="text-red-400 font-extrabold">${ data.deaths }</span>
                <span class="text-blue-400 font-extrabold">${ data.assists }}</span>
                ${data.gamedurationminutes}:${data.gamedurationseconds}
            `;

        } else {
            stats_display.innerText = "Leaderboard was unable to load";
        }
    } catch (error) {
        console.error("Error during fetch:", error);
        stats_display.innerText = "Failed to load stats";
    }
});