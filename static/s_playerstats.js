document.addEventListener("DOMContentLoaded", async () => {
    const stats_div = document.getElementById("stats");

    // Show loading text immediately
    stats_div.innerText = "Loading stats...";

    try {
        const response = await fetch("http://127.0.0.1:5000/api/player/stats", {
            method: "GET",
            headers: {
                "Content-Type": "application/json"
            },
            credentials: "include",
        });

        const data = await response.json();

        if (data) {
            console.log(data)
            // If data is an object, convert to string for display
            stats_div.innerText = ""
            kda_ = (data.KDA_.kills + data.KDA_.assists)/data.KDA_.deaths;
            if (!kda_) {
                kda_ = 0.0;
            }
            document.getElementById("total-kda-reviewed").innerText = `Total KDA Reviewed: ${kda_}`;

            // Average Stats
            document.getElementById("avg-stats").innerHTML = `
              <li>Kills: ${data.KDA_.kills}</li>
              <li>Assists: ${data.KDA_.assists}</li>
              <li>Deaths: ${data.KDA_.deaths}</li>
            `;

            // Total Stats
            document.getElementById("total-stats").innerHTML = `
              <li>Damage Done: ${data.total_.totalDamageDealtToChampions}</li>
              <li>Towers Taken: ${data.total_.turretKills}</li>
              <li>Gold: ${data.total_.goldEarned}</li>
              <li>Objective Steals: ${data.total_.objectivesStolen}</li>
              <li>First Bloods: ${data.firstBloodKill}</li>
            `;
        } else {
            stats_div.innerText = "No stats available";
        }
    } catch (error) {
        console.error("Error during fetch:", error);
        stats_div.innerText = "Failed to load stats";
    }
});
