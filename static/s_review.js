document.addEventListener("DOMContentLoaded", () => {
  const home = document.getElementById('home');
  const leaderboard = document.getElementById('leaderboard');
  const dashboard = document.getElementById('dashboard');

  if (home){
    home.addEventListener("click", () => {
      window.location.href = "/";
    });
  }
  if (leaderboard){
    leaderboard.addEventListener("click", () => {
      window.location.href = "/leaderboard";
    });
  }
  if (dashboard){
    dashboard.addEventListener("click", () => {
      window.location.href = "/dashboard";
    });
  }
})