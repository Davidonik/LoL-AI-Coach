document.addEventListener("DOMContentLoaded", async () => {
    const stats_div = document.getElementById("stats");
    const leaderboard_display = document.getElementById("leaderboard-display");

    function shortenNumber(num) {
      if (num === null || num === undefined || isNaN(num)) return "-";
      const absNum = Math.abs(num);

      if (absNum >= 1_000_000_000) return (num / 1_000_000_000).toFixed(1).replace(/\.0$/, "") + "B";
      if (absNum >= 1_000_000) return (num / 1_000_000).toFixed(1).replace(/\.0$/, "") + "M";
      if (absNum >= 1_000) return (num / 1_000).toFixed(1).replace(/\.0$/, "") + "K";
      return num.toString();
    }

    try {
        const response = await fetch("/leaderboard", {
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
                      <div class="llb-sum">
                        <img class="llb-ava" src="/static/media/HelmetBro.png" alt="">
                        <div class="llb-name">
                          ${data.board[i].ign_.gameName}
                          <span class="llb-tag">${data.board[i].ign_.tagLine}</span>
                        </div>
                      </div>

                      <!-- K/D/A + KDA -->
                      <div class="llb-kda-wrap">
                        <div class="llb-kda-line"><span class="llb-k">${shortenNumber(data.board[i].KDA_.kills)}</span>/<span class="llb-d">${shortenNumber(data.board[i].KDA_.deaths)}</span>/<span class="llb-a">${shortenNumber(data.board[i].KDA_.assists)}</span></div>
                        <div class="llb-kda">${((data.board[i].KDA_.kills + data.board[i].KDA_.assists) / Math.max(data.board[i].KDA_.deaths, 1)).toFixed(2)}</div>
                      </div>

                      <!-- Damage -->
                      <div><span class="llb-chip">${shortenNumber(data.board[i].total_.totalDamageDealtToChampions)}</span></div>

                      <!-- Gold -->
                      <div><span class="llb-chip">${shortenNumber(data.board[i].total_.goldEarned)}</span></div>

                      <!-- Turrets -->
                      <div><span class="llb-chip">${shortenNumber(data.board[i].total_.turretKills)}</span></div>

                      <!-- First blood -->
                      <div><span class="llb-chip">${shortenNumber(data.board[i].firstBloodKill)}</span></div>

                      <!-- Objectives -->
                      <div><span class="llb-chip">${shortenNumber(data.board[i].objectives)}</span></div>

                      <!-- Objectives stolen -->
                      <div><span class="llb-chip">${shortenNumber(data.board[i].total_.objectivesStolen)}</span></div>
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
