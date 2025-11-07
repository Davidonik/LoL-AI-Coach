async function fetchData() {
  const summoner = document.getElementById("summonerInput").value.trim();
  const resultDiv = document.getElementById("result");

  if (!summoner) {
    resultDiv.innerHTML = `<p class="text-red-400 text-center mx-auto">Please enter a Summoner name.</p>`;
    return;
  }

  resultDiv.innerHTML = `<p>Loading data for <b>${summoner}</b>...</p>`;

  try {
    const response = await fetch(`/analyze?summoner=${encodeURIComponent(summoner)}`);
    const data = await response.json();

    if (data.error) {
      resultDiv.innerHTML = `<p class="text-red-400 text-center mx-auto" >${data.error}</p>`;
    } else {
      resultDiv.innerHTML = `
        <div class="fade-in">
          <h2 class="text-2xl font-bold mb-3">${data.summoner}'s Match Summary</h2>
          <p><b>Champion:</b> ${data.champion} <span class="text-gray-400">(${data.champion_title})</span></p>
          <p><b>KDA:</b> ${data.kda}</p>
          <p><b>Gold Earned:</b> ${data.gold.toLocaleString()}</p>
          <p><b>Damage to Champions:</b> ${data.damage.toLocaleString()}</p>
          <p class="italic text-blue-300 mt-3">${data.feedback}</p>
        </div>
      `;
    }
  } catch (err) {
    resultDiv.innerHTML = `<p class="text-red-400 text-center mx-auto">Could not find summoner. Please check your Riot ID</p>`;
  }
}
