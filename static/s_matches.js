document.addEventListener("DOMContentLoaded", async () => {
  const matchList = document.getElementById("matchList");
  const loading = document.getElementById("loading");

  const home = document.getElementById('home');
  const leaderboard = document.getElementById('leaderboard');

  if (home){
    home.addEventListener("click", () => {
      window.location.href = "http://127.0.0.1:5000/home";
    });
  }

  if (leaderboard){
    leaderboard.addEventListener("click", () => {
      window.location.href = "http://127.0.0.1:5000/leaderboard";
    });
  }
})