document.addEventListener("DOMContentLoaded", () => {
  const home = document.getElementById('home');
  const leaderboard = document.getElementById('leaderboard');
  const review = document.getElementById('review');

  if (review){
    home.addEventListener("click", () => {
      window.location.href = "https://lol-ai-coach.onrender.com/review";
    });
  }

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
});