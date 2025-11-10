document.addEventListener("DOMContentLoaded", () => {
  const home = document.getElementById('home');
  const leaderboard = document.getElementById('leaderboard');
  const dashboard = document.getElementById('dashboard');

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
  if (dashboard){
    dashboard.addEventListener("click", () => {
      window.location.href = "http://127.0.0.1:5000/dashboard";
    });
  }
})