document.addEventListener("DOMContentLoaded", () => {
  const home = document.getElementById('home');
  const leaderboard = document.getElementById('leaderboard');
  const dashboard = document.getElementById('dashboard');

  if (home){
    home.addEventListener("click", () => {
      window.location.href = "https://lol-ai-coach.onrender.com/";
    });
  }
  if (leaderboard){
    leaderboard.addEventListener("click", () => {
      window.location.href = "https://lol-ai-coach.onrender.com/leaderboard";
    });
  }
  if (dashboard){
    dashboard.addEventListener("click", () => {
      window.location.href = "https://lol-ai-coach.onrender.com/dashboard";
    });
  }
})