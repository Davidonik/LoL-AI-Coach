document.addEventListener("DOMContentLoaded", () => {
  const matchList = document.getElementById("matchList");
  const loading = document.getElementById("loading");

  const home = document.getElementById('home');
  const leaderboard = document.getElementById('leaderboard');
  const review = document.getElementById('review');
  const roast = false

  if (review){
    home.addEventListener("click", () => {
      window.location.href = "http://127.0.0.1:5000/review";
    });
  }

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

  const mySwitch = document.getElementById("mySwitch");
  const status = document.getElementById("status");

  mySwitch.addEventListener("change", () => {
    if (mySwitch.checked) {
      status.innerText = "Roast Switch is ON";
      roast = true
    } else {
      status.innerText = "Roast Switch is OFF";
      roast = false
    }
    });
});