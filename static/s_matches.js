document.addEventListener("DOMContentLoaded", async () => {
  const matchList = document.getElementById("matchList");
  const loading = document.getElementById("loading");

  const home = document.getElementById('home');
  const leaderboard = document.getElementById('leaderboard');

  if (home){
    home.addEventListener("click", () => {
      window.location.href = "http://127.0.0.1:5000/";
    });
  }

  if (leaderboard){
    leaderboard.addEventListener("click", () => {
      window.location.href = "http://127.0.0.1:5000/leaderboard";
    });
  }

  try {
        // Update the loading text in the H2
        if (statusHeader) {
            statusHeader.textContent = "Fetching Match History...";
        }

        const response = await fetch("http://127.0.0.1:5000/api/get_matches", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            credentials: "include",
            // Assuming your backend uses the session/cookies to identify the player, 
            // the empty body is fine, otherwise you might need to send a 'puuid' here.
            body: JSON.stringify({}) 
        });
        
        const data = await response.json();

        if (response.ok && data.matches && data.matches.length > 0) {
            // Success: Update the header and render matches
            if (statusHeader) {
                statusHeader.textContent = "Recent Matches";
            }
            
            data.matches.forEach((m) => {
                // Determine win/loss status and CSS classes
                const isWin = m.win;
                const resultText = isWin ? 'VICTORY' : 'DEFEAT';
                const resultClass = isWin ? 'bg-green-700 hover:bg-green-600' : 'bg-red-700 hover:bg-red-600';
                
                // Calculate KDA display (rounded to two decimal places)
                const kdaValue = (m.kda || (m.kills + m.assists) / (m.deaths || 1)).toFixed(2);
                
                // Convert duration from seconds to minutes and seconds
                const totalSeconds = m.gameDuration;
                const minutes = Math.floor(totalSeconds / 60);
                const seconds = totalSeconds % 60;
                const durationText = `${minutes}m ${seconds}s`;

                const card = document.createElement("div");
                // Use Tailwind classes for styling based on Win/Loss
                card.className = `p-4 rounded-lg shadow-lg flex justify-between items-center ${resultClass} text-white transition duration-300 ease-in-out cursor-pointer`;
                
                card.innerHTML = `
                    <div class="flex flex-col space-y-1">
                        <span class="text-xl font-bold">${resultText}</span>
                        <span class="text-sm italic">${m.champion || 'Unknown Champion'}</span>
                    </div>
                    
                    <div class="text-center">
                        <p class="text-xl font-mono">${m.kills} / ${m.deaths} / ${m.assists}</p>
                        <p class="text-sm font-semibold text-gray-200">K/D/A: ${kdaValue}</p>
                    </div>
                    
                    <div class="text-right">
                        <p class="text-sm">Duration:</p>
                        <p class="font-semibold">${durationText}</p>
                    </div>
                `;
                matchList.appendChild(card);
            });
        } else if (data.matches && data.matches.length === 0) {
            if (statusHeader) statusHeader.textContent = "No Matches Found.";
        } else {
            // Handle API error/bad response
            if (statusHeader) {
                statusHeader.textContent = data.error || "Failed to load matches.";
            }
        }
    } catch (err) {
        // Handle network error
        console.error("Fetch error:", err);
        if (statusHeader) {
            statusHeader.textContent = "Network error fetching matches.";
        }
    }
});