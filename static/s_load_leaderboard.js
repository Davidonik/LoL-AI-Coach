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
          console.log(data);
            for (let i = 0; i < Math.min(10, data.board.length); i++) {
                leaderboard_display.innerHTML += `
                    <div class="llb-row">
                      <!-- Summoner -->
                      <div class="llb-cell">
                        <div class="llb-sum">
                          <div class="llb-name">
                            ${data.board[i].ign_.gameName} <span class="llb-tag">${data.board[i].ign_.tagLine}</span>
                          </div>
                        </div>
                      </div>
                          
                      <!-- KDA -->
                      <div class="llb-cell">
                        <span class="llb-kda">${(data.board[i].KDA_.kills + data.board[i].KDA_.assists)/Math.max(data.board[i].KDA_.deaths, 1)}</span>
                        <span class="llb-kda-detail">${data.board[i].KDA_.kills} / ${data.board[i].KDA_.deaths} / ${data.board[i].KDA_.assists}</span>
                      </div>
                          
                      <!-- Damage -->
                      <div class="llb-cell llb-right">
                        <span class="llb-chip">${data.board[i].total_.totalDamageDealtToChampions}</span>
                      </div>
                          
                      <!-- Gold -->
                      <div class="llb-cell llb-right">
                        <span class="llb-chip">${data.board[i].total_.goldEarned}</span>
                      </div>
                          
                      <!-- Turrets -->
                      <div class="llb-cell llb-right">
                        <span class="llb-chip">${data.board[i].total_.turretKills}</span>
                      </div>
                          
                      <!-- First Blood -->
                      <div class="llb-cell llb-right">
                        <span class="llb-chip">${data.board[i].firstBloodKill}</span>
                        </div>
                          
                      <div class="llb-cell llb-right">
                        <span class="llb-chip">${data.board[i].objectives}</span>
                      </div>
                          
                      <!-- Objectives Stolen -->
                      <div class="llb-cell llb-right">
                        <span class="llb-chip">${data.board[i].total_.objectivesStolen}</span>
                      </div>
                    </div>
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
