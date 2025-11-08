document.addEventListener("DOMContentLoaded", async () => {
  const matchList = document.getElementById("matchList");
  const loading = document.getElementById("loading");

  try {
    const response = await fetch("/get_matche");
    const data = await response.json();

    if (response.ok && data.matches) {
      loading.remove();
      data.matches.forEach((m) => {
        const card = document.createElement("div");
        card.className = "match-card";
        card.innerHTML = `
          <h4>${m.champion}</h4>
          <p>K/D/A: ${m.kills}/${m.deaths}/${m.assists}</p>
          <p>Duration: ${(m.gameDuration / 60).toFixed(1)} min</p>
          <p class="${m.win ? 'win' : 'loss'}">${m.win ? 'WIN' : 'LOSS'}</p>
        `;
        matchList.appendChild(card);
      });
    } else {
      loading.innerText = data.error || "Failed to load matches.";
    }
  } catch (err) {
    console.error(err);
    loading.innerText = "Network error fetching matches.";
  }
});