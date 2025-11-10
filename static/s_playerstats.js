document.addEventListener("DOMContentLoaded", async () => {
    const stats_div = document.getElementById("stats");
    const traits_section = document.getElementById("traits-section");

    // Show loading text immediately
    stats_div.innerText = "Loading stats...";

    try {
        const response = await fetch("https://lol-ai-coach.onrender.com/api/player/stats", {
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

            for (const [key, value] of Object.entries(data.traits_)) {
                traits_section.innerHTML += `
                    <div class="flex justify-between w-full">
                        <span class="font-semibold text-gray-300 text-right w-1/2 pr-2 capitalize">${key}:</span>
                        <span class="text-gray-200 text-left w-1/2 pl-2 capitalize">${value}</span>
                    </div>
                `;
            }
        } else {
            stats_div.innerText = "No stats available";
        }
    } catch (error) {
        console.error("Error during fetch:", error);
        stats_div.innerText = "Failed to load stats";
    }
});
