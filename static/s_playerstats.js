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
            // If data is an object, convert to string for display
            stats_div.innerText = ""
            document.getElementById("total-kda-reviewed").innerText = `Total KDA Reviewed: ${data.KDA_.total_kda_reviewed}`;
            document.getElementById("last20-kda").innerText = `Last 20 Avg KDA: ${data.KDA_.last20}`;

            // Average Stats
            document.getElementById("avg-stats").innerHTML = `
              <li>Kills: ${data.avg_.kills}</li>
              <li>Assists: ${data.avg_.assists}</li>
              <li>Deaths: ${data.avg_.deaths}</li>
              <li>CS@10: ${data.avg_["cs@10"]}</li>
              <li>CS/Min: ${data.avg_.cs_per_min}</li>
              <li>Gold/Min: ${data.avg_.gold_per_min}</li>
            `;

            // Total Stats
            document.getElementById("total-stats").innerHTML = `
              <li>Damage Done: ${data.total_.dmg_done}</li>
              <li>Towers Taken: ${data.total_.towers_taken}</li>
              <li>Gold: ${data.total_.gold}</li>
              <li>Objectives: ${data.total_.objectives}</li>
              <li>Objective Steals: ${data.total_.objective_steals}</li>
              <li>First Bloods: ${data.total_.first_bloods}</li>
              <li>Feats: ${data.total_.feats}</li>
            `;
        } else {
            stats_div.innerText = "No stats available";
        }
    } catch (error) {
        console.error("Error during fetch:", error);
        stats_div.innerText = "Failed to load stats";
    }
});
