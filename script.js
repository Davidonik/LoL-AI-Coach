async function fetchData() {
  const summoner = document.getElementById("summonerInput").value;
  const resultDiv = document.getElementById("result");
  const button = document.querySelector("button");

  resultDiv.innerHTML = `<p>Loading data for <b>${summoner}</b>...</p>`;
  button.disabled = true;

  try {
    const response = await fetch(`/analyze?summoner=${summoner}`);
    const data = await response.json();

    if (data.error) {
      resultDiv.innerHTML = `<p class="error">⚠️ ${data.error}</p>`;
    } else {
      resultDiv.innerHTML = `
        <div class="card">
          <h2>${data.summoner}'s Match Summary</h2>
          <p><strong>Champion:</strong> ${data.champion} (${data.champion_title})</p>
          <p><strong>KDA:</strong> ${data.kda}</p>
          <p><strong>Gold Earned:</strong> ${data.gold.toLocaleString()}</p>
          <p><strong>Damage to Champions:</strong> ${data.damage.toLocaleString()}</p>
          <p class="feedback">${data.feedback}</p>
        </div>
      `;
    }
  } catch (err) {
    resultDiv.innerHTML = `<p class="error">❌ Error fetching data. Please try again later.</p>`;
  } finally {
    button.disabled = false;
  }
}
