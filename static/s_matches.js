document.addEventListener("DOMContentLoaded", () => {
  const home = document.getElementById('home');
  const leaderboard = document.getElementById('leaderboard');
  const review = document.getElementById('review');

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
});